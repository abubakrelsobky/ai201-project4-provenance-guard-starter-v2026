#!/usr/bin/env python3
"""
Criterion 4: the appeal path, three trials.  <- UNIT 8, MILESTONE 3

    python app.py                 # in one terminal
    python check_appeals.py       # in another

run_eval.py only sends /submit, and an appeal needs a content_id from a real
submission first. So each trial submits 10 texts, appeals every one, then reads
the audit log back and checks two things per appeal:

    recorded    the log has an `appeal` entry for that content_id with
                status `under_review`
    changed     the original decision's guess or label is different from what
                /submit returned (target: at most 3 of 10)
"""

import datetime as dt
import json
import sys

import requests

import config
import scenarios

URL = f"http://{config.HOST}:{config.PORT}"
TEXTS = next(s for s in scenarios.SCENARIOS if s["criterion"] == 3)["texts"]


def one_trial(trial):
    results = []
    for i, text in enumerate(TEXTS, 1):
        sub = requests.post(f"{URL}/submit", timeout=90,
                            json={"text": text, "creator_id": f"eval_appeal_{i}"}).json()
        app = requests.post(f"{URL}/appeal", timeout=30, json={
            "content_id": sub["content_id"],
            "reasoning": f"Trial {trial}: I wrote this myself.",
        })
        entries = [e for e in requests.get(f"{URL}/log", timeout=30).json()["entries"]
                   if e.get("content_id") == sub["content_id"]]
        decided = next(e for e in entries if e.get("status") == "decided")
        appeal = [e for e in entries if e.get("event") == "appeal"]
        results.append({
            "content_id": sub["content_id"],
            "appeal_status_code": app.status_code,
            "appeal_response": app.json(),
            "recorded": bool(appeal) and appeal[-1]["status"] == "under_review",
            "changed": decided["guess"] != sub["guess"] or decided["label"] != sub["label"],
        })
    return results


def main():
    trials = [one_trial(t) for t in (1, 2, 3)]
    lines = ["# Criterion 4 — appeals", "",
             "- Produced by: `check_appeals.py::one_trial`",
             "- Service: `app.py::submit`, `app.py::appeal`, `app.py::get_log`",
             f"- 3 trials of 10 appeals · {dt.datetime.now():%Y-%m-%d %H:%M}", ""]
    for n, res in enumerate(trials, 1):
        rec = sum(r["recorded"] for r in res)
        chg = sum(r["changed"] for r in res)
        print(f"trial {n}: recorded {rec}/10, changed {chg}/10")
        lines += [f"**Trial {n}:** recorded {rec}/10, changed {chg}/10", "",
                  "```json", json.dumps(res, indent=2), "```", ""]
    config.RESULTS_DIR.mkdir(exist_ok=True)
    path = config.RESULTS_DIR / f"appeals_{dt.datetime.now():%Y-%m-%d_%H%M}_{(sys.argv[1] if len(sys.argv) > 1 else "before")}.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {path.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
