"""
Run the capstone criteria (C1–C5 in criteria.md) — one trial per call.

    python run_capstone_trials.py --trial 1
    python run_capstone_trials.py --trial 2
    python run_capstone_trials.py --trial 3

Follows "How every trial is run" in criteria.md to the letter:

  1. Starts the service with the documented command (`python app.py`) and
     stops it afterwards, so every trial begins from a fresh restart: empty
     rate-limit counts, GPT-2 not loaded. Refuses to run if something is
     already listening on the port.
  2. Sends every request one at a time and records exactly which audit-log
     lines that request added.
  3. Order: the 10 bad requests (C1, C2, C4) → GET /health (C4) → the 10 short
     posts (C3) → one throwaway submission → `python measure_cost.py` (C5).

Bodies are built here in Python and sent as UTF-8 bytes, so nothing passes
through a shell that could mangle emoji or Cyrillic.

Writes results/capstone_trial_<n>_<timestamp>.json (every request, response
and log line) and .md (the per-criterion counts and verdicts). This script
checks each target exactly as criteria.md words it. It does not change one.
"""

import argparse
import json
import os
import re
import socket
import statistics
import subprocess
import sys
import time
from pathlib import Path

import requests

import config

ROOT = Path(__file__).resolve().parent
CHILD_ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}
URL = f"http://{config.HOST}:{config.PORT}"
LOG = config.AUDIT_LOG

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


# ── The fixed inputs from criteria.md. `{n}` is the trial number. ─────────────

BAD = [  # (id, kind, raw JSON body as a Python value)
    ("B1", "body", "please check my essay"),
    ("B2", "body", 42),
    ("B3", "text", {"text": "asdf qwer zxcv hjkl uiop", "creator_id": "t{n}-b3"}),
    ("B4", "body", [{"text": "A perfectly normal sentence about my weekend plans.",
                     "creator_id": "b4"}]),
    ("B5", "text", {"text": "ok", "creator_id": "t{n}-b5"}),
    ("B6", "text", {"text": "12345 67890 2024", "creator_id": "t{n}-b6"}),
    ("B7", "text", {"text": "#### **** //// ~~~~", "creator_id": "t{n}-b7"}),
    ("B8", "text", {"text": "Привет, как дела? Всё хорошо, спасибо.", "creator_id": "t{n}-b8"}),
    ("B9", "text", {"text": "lol k", "creator_id": "t{n}-b9"}),
    ("B10", "text", {"text": "👍👍👍 nice 👍👍", "creator_id": "t{n}-b10"}),
]

POSTS = [
    "Ran 5k in 24:10 this morning, new PB!",
    "Can't make it tonight, sorry. Next week?",
    "Flight 2B delayed 3 hrs. Ugh, again.",
    "Best ramen in town, hands down. 10/10.",
    "Mum's birthday is on the 14th, don't forget!",
    "Got 92% on the stats midterm!!",
    "Room 4.12 is double-booked at 3pm.",
    "Café on Rue Cler was closed. Went home.",
    "New phone, who dis? 😂 Text me back.",
    "Done. Finally. Sleeping now. Goodnight, everyone.",
]


def fill(value, n):
    """Substitute the trial number into every creator_id."""
    if isinstance(value, str):
        return value.replace("{n}", str(n))
    if isinstance(value, list):
        return [fill(v, n) for v in value]
    if isinstance(value, dict):
        return {k: fill(v, n) for k, v in value.items()}
    return value


# ── Service lifecycle ─────────────────────────────────────────────────────────

def port_in_use() -> bool:
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex((config.HOST, config.PORT)) == 0


def start_service(out_path: Path) -> subprocess.Popen:
    out = out_path.open("w", encoding="utf-8")
    proc = subprocess.Popen([sys.executable, "app.py"], cwd=ROOT,
                            stdout=out, stderr=subprocess.STDOUT, env=CHILD_ENV)
    for _ in range(60):
        try:
            if requests.get(f"{URL}/health", timeout=1).ok:
                return proc
        except requests.RequestException:
            pass
        time.sleep(0.5)
    stop_service(proc)
    raise SystemExit("service didn't answer /health within 30 s")


def stop_service(proc: subprocess.Popen) -> None:
    # `python app.py` runs Flask's reloader, which starts a child process.
    # Kill the whole tree, or the child keeps the port.
    if sys.platform == "win32":
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                       capture_output=True)
    else:
        proc.terminate()
    proc.wait(timeout=15)
    for _ in range(20):
        if not port_in_use():
            return
        time.sleep(0.5)


# ── One request, with the log lines it added ──────────────────────────────────

def log_lines() -> list[str]:
    if not LOG.exists():
        return []
    return LOG.read_text(encoding="utf-8").splitlines()


def send(body) -> dict:
    before = len(log_lines())
    raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
    r = requests.post(f"{URL}/submit", data=raw, timeout=120,
                      headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        resp = r.json()
    except ValueError:
        resp = {"_raw": r.text[:300]}
    added = [json.loads(l) for l in log_lines()[before:] if l.strip()]
    return {"body": body, "status": r.status_code, "response": resp,
            "log_added": added}


# ── The trial ─────────────────────────────────────────────────────────────────

def run_trial(n: int) -> dict:
    stamp = time.strftime("%Y-%m-%d_%H%M%S")
    if port_in_use():
        raise SystemExit(f"something is already on {URL} — stop it first, "
                         "every trial has to start from a fresh restart")

    proc = start_service(ROOT / "results" / f"capstone_trial_{n}_{stamp}_server.txt")
    try:
        health_start = requests.get(f"{URL}/health", timeout=5).json()

        bad = []
        for bid, kind, body in BAD:
            res = send(fill(body, n))
            res.update(id=bid, kind=kind)
            bad.append(res)
            print(f"  {bid:<4} {kind:<5} -> {res['status']}  "
                  f"{len(res['log_added'])} log line(s)")

        health_after_bad = requests.get(f"{URL}/health", timeout=5).json()
        print(f"  /health after bad set: detector_loaded="
              f"{health_after_bad['detector_loaded']}")

        posts = []
        for i, text in enumerate(POSTS, 1):
            res = send({"text": text, "creator_id": f"t{n}-p{i}"})
            res.update(id=f"P{i}")
            posts.append(res)
            print(f"  P{i:<3} -> {res['status']}  {res['response'].get('guess', '')}")

        warm = send({"text": "Warm-up submission, excluded from the C5 numbers on "
                             "purpose. It just makes sure GPT-2 is loaded.",
                     "creator_id": f"t{n}-warm"})

        mc = subprocess.run([sys.executable, "measure_cost.py"], cwd=ROOT,
                            capture_output=True, text=True, encoding="utf-8",
                            env=CHILD_ENV)
        prefix = re.search(r"creator prefix (\S+)\)", mc.stdout)
        cost_entries = []
        if prefix:
            cost_entries = [json.loads(l) for l in log_lines()
                            if f'"creator_id": "{prefix.group(1)}-' in l]
        print("  measure_cost.py exit", mc.returncode,
              f"({len(cost_entries)} entries)")
    finally:
        stop_service(proc)

    return {"trial": n, "stamp": stamp, "health_start": health_start,
            "bad": bad, "health_after_bad": health_after_bad, "posts": posts,
            "warm": warm, "measure_cost_stdout": mc.stdout,
            "cost_entries": cost_entries}


# ── Scoring each criterion exactly as criteria.md words it ────────────────────

def score(t: dict) -> dict:
    out = {}

    # C1: 10/10 get 400, 0 get 500, 0 come back with guess or label.
    ok = [b for b in t["bad"] if b["status"] == 400
          and "guess" not in b["response"] and "label" not in b["response"]]
    out["C1"] = {
        "count": len(ok), "of": 10,
        "n500": sum(b["status"] == 500 for b in t["bad"]),
        "labelled": [b["id"] for b in t["bad"] if "guess" in b["response"]],
        "statuses": {b["id"]: b["status"] for b in t["bad"]},
        "met": len(ok) == 10,
    }

    # C2: exactly one new entry: rejected, 400, numeric duration_ms, right reason.
    def c2_ok(b):
        if len(b["log_added"]) != 1:
            return False
        e = b["log_added"][0]
        right_reason = (e.get("reason") == "body_not_object") if b["kind"] == "body" \
            else (bool(e.get("reason")) and e.get("reason") != "body_not_object")
        return (e.get("status") == "rejected" and e.get("http_status") == 400
                and isinstance(e.get("duration_ms"), (int, float)) and right_reason)
    passing = [b["id"] for b in t["bad"] if c2_ok(b)]
    out["C2"] = {
        "count": len(passing), "of": 10,
        "failing": {b["id"]: [{k: e.get(k) for k in ("status", "http_status", "reason",
                                                      "duration_ms")}
                              for e in b["log_added"]]
                    for b in t["bad"] if b["id"] not in passing},
        "met": len(passing) == 10,
    }

    # C3: at most 1 of the 10 posts gets a 400. A 429 is a miss.
    refused = [p["id"] for p in t["posts"] if p["status"] == 400]
    n429 = sum(p["status"] == 429 for p in t["posts"])
    out["C3"] = {
        "refused": len(refused), "refused_ids": refused, "n429": n429,
        "statuses": {p["id"]: p["status"] for p in t["posts"]},
        "met": len(refused) <= 1 and n429 == 0,
    }

    # C4: all 10 bad requests log duration_ms < 5, then detector_loaded false.
    durs = {b["id"]: (b["log_added"][0].get("duration_ms") if b["log_added"] else None)
            for b in t["bad"]}
    under = [k for k, v in durs.items() if isinstance(v, (int, float)) and v < 5]
    loaded = t["health_after_bad"]["detector_loaded"]
    out["C4"] = {
        "under_5ms": len(under), "of": 10, "durations": durs,
        "detector_loaded_after": loaded,
        "detector_loaded_at_start": t["health_start"]["detector_loaded"],
        "met": len(under) == 10 and loaded is False,
    }

    # C5: warm mean duration_ms <= 300 and no single run > 500.
    d = [e["duration_ms"] for e in t["cost_entries"]
         if e.get("http_status") == 200 and not e.get("cold_start")]
    out["C5"] = {
        "runs": len(d),
        "mean": round(statistics.mean(d), 1) if d else None,
        "max": max(d) if d else None,
        "min": min(d) if d else None,
        "met": len(d) == 10 and statistics.mean(d) <= 300 and max(d) <= 500,
    }
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trial", type=int, required=True)
    n = ap.parse_args().trial

    print(f"Trial {n}: starting a fresh service with `python app.py`")
    t = run_trial(n)
    s = score(t)
    t["scores"] = s

    base = ROOT / "results" / f"capstone_trial_{n}_{t['stamp']}"
    base.with_suffix(".json").write_text(
        json.dumps(t, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        f"# Capstone trial {n} — {t['stamp']}", "",
        "Produced by `run_capstone_trials.py`. Full requests, responses and "
        "log lines are in the matching `.json`.", "",
        "| Criterion | Result | Met |", "|---|---|---|",
        f"| C1 | {s['C1']['count']}/10 refused cleanly; 500s: {s['C1']['n500']}; "
        f"labelled: {', '.join(s['C1']['labelled']) or 'none'} | {s['C1']['met']} |",
        f"| C2 | {s['C2']['count']}/10 with one correct record; failing: "
        f"{', '.join(s['C2']['failing']) or 'none'} | {s['C2']['met']} |",
        f"| C3 | {s['C3']['refused']}/10 refused ({', '.join(s['C3']['refused_ids']) or 'none'}); "
        f"429s: {s['C3']['n429']} | {s['C3']['met']} |",
        f"| C4 | {s['C4']['under_5ms']}/10 under 5 ms; detector_loaded after bad set: "
        f"{s['C4']['detector_loaded_after']} | {s['C4']['met']} |",
        f"| C5 | mean {s['C5']['mean']} ms, max {s['C5']['max']} ms over "
        f"{s['C5']['runs']} warm runs | {s['C5']['met']} |",
        "", "## measure_cost.py output", "", "```", t["measure_cost_stdout"].strip(), "```",
    ]
    base.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("\n" + "\n".join(lines[5:10]))
    print(f"\nWrote {base.with_suffix('.md').name} and .json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
