"""
What one submission costs — measured, not estimated. (Capstone, Milestone 3.)

Provenance Guard calls no paid API: both signals run on this machine. So the
real cost of a run is compute — seconds of CPU and wall-clock time per
submission. This script measures it from the service's own audit log:

  1. Send N submissions (default 10) to a running service, one at a time.
  2. Read back the audit entries those requests wrote.
  3. Average duration_ms and cpu_ms over the warm runs. The first scored
     request after a restart loads GPT-2 and is reported on its own line —
     it's a one-off per process, not a per-run cost.

With the service running (python app.py) in another terminal:

    python measure_cost.py            # 10 runs
    python measure_cost.py -n 20

Each run uses its own creator_id, so the 5-per-minute rate limit (which is
keyed on creator_id) never interrupts the measurement.
"""

import argparse
import statistics
import sys
import time

import requests

import audit

# One ordinary paragraph of human writing, ~100 words — the size of a typical
# short post. Fixed, so two runs of this script measure the same work.
TEXT = (
    "We got to the campsite about four, later than planned because the "
    "ferry was running behind. The pitch was fine, a bit sloped, but there "
    "was a tap nearby and the toilets were clean enough. Putting the tent up "
    "took longer than it should have, mostly because nobody had read the "
    "instructions since last summer. By the time the stove was going it was "
    "nearly dark, so dinner was pasta with whatever was left in the cool "
    "box. Nobody complained. We sat outside until the midges drove us in, "
    "and I fell asleep listening to rain on the flysheet."
)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    p.add_argument("-n", type=int, default=10, help="number of runs (default 10)")
    p.add_argument("--url", default="http://127.0.0.1:5000")
    args = p.parse_args()

    tag = f"cost-{time.strftime('%Y%m%d-%H%M%S')}"
    print(f"Sending {args.n} submissions to {args.url}/submit  (creator prefix {tag})")
    for i in range(1, args.n + 1):
        try:
            r = requests.post(f"{args.url}/submit",
                              json={"text": TEXT, "creator_id": f"{tag}-{i:02d}"},
                              timeout=120)
        except requests.RequestException as exc:
            print(f"  run {i}: request failed — {exc}. Is `python app.py` running?")
            return 1
        print(f"  run {i:>2}: HTTP {r.status_code}")

    runs = [e for e in audit.read_entries()
            if str(e.get("creator_id", "")).startswith(tag + "-")]
    if len(runs) != args.n:
        print(f"\nExpected {args.n} log entries, found {len(runs)}. "
              "Is the service writing to this checkout's logs/audit.jsonl?")
        return 1

    cold = [e for e in runs if e.get("cold_start")]
    warm = [e for e in runs if not e.get("cold_start") and e.get("http_status") == 200]

    def stats(field):
        vals = [e[field] for e in warm]
        return statistics.mean(vals), min(vals), max(vals)

    print(f"\nText: {len(TEXT)} characters. Warm runs: {len(warm)}. Cold runs: {len(cold)}.")
    for e in cold:
        print(f"  cold start (loads GPT-2): duration {e['duration_ms']:.0f} ms, "
              f"CPU {e['cpu_ms']:.0f} ms")
    if not warm:
        print("No warm runs to average.")
        return 1
    print(f"\n{'per warm run':<14}{'mean':>10}{'min':>10}{'max':>10}")
    for field in ("duration_ms", "cpu_ms", "model_ms", "style_ms"):
        mean, lo, hi = stats(field)
        print(f"{field:<14}{mean:>10.1f}{lo:>10.1f}{hi:>10.1f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
