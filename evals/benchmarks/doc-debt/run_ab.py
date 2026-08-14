#!/usr/bin/env python3
"""Compare the released and current documentation-debt detector."""

import argparse
import datetime
import json
import statistics
import subprocess
import time
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = "plugins/nulnul-harness/skills/nulnul-harness/scripts/check_doc_debt.py"


def load_released(ref):
    result = subprocess.run(
        ["git", "show", f"{ref}:{SCRIPT}"], cwd=ROOT, capture_output=True, text=True, check=True
    )
    module = types.ModuleType("released_doc_debt")
    exec(compile(result.stdout, f"{ref}:{SCRIPT}", "exec"), module.__dict__)
    return module


def load_current():
    module = types.ModuleType("current_doc_debt")
    source = (ROOT / SCRIPT).read_text(encoding="utf-8")
    exec(compile(source, SCRIPT, "exec"), module.__dict__)
    return module


def measure(module):
    started = time.perf_counter()
    result = module.check(ROOT)
    return {"elapsed_seconds": round(time.perf_counter() - started, 4), "result": result}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--champion-ref", default="v2.1.0")
    parser.add_argument("--rounds", type=int, default=4)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.rounds < 4 or args.rounds % 2:
        parser.error("--rounds must be an even number of at least 4")

    arms = {"champion": load_released(args.champion_ref), "candidate": load_current()}
    runs = []
    for round_index in range(1, args.rounds + 1):
        order = ("champion", "candidate") if round_index % 2 else ("candidate", "champion")
        for arm in order:
            runs.append({"round": round_index, "arm": arm, **measure(arms[arm])})

    expected = [run["result"] for run in runs]
    behavior_equal = all(result == expected[0] for result in expected[1:])
    medians = {
        arm: statistics.median(
            run["elapsed_seconds"] for run in runs if run["arm"] == arm
        )
        for arm in arms
    }
    improvement = round(100 * (1 - medians["candidate"] / medians["champion"]), 2)
    payload = {
        "schema_version": 1,
        "run_date": datetime.date.today().isoformat(),
        "champion_ref": args.champion_ref,
        "method": f"{args.rounds} counterbalanced in-process checks on the same tracked repository",
        "primary_metric": "median elapsed seconds",
        "runs": runs,
        "medians": medians,
        "improvement_percent": improvement,
        "behavior_equal": behavior_equal,
        "decision": "accepted" if behavior_equal and improvement > 0 else "rejected",
        "learning_verdicts": [{"id": "doc-debt-lazy-scan", "status": "accepted" if behavior_equal and improvement > 0 else "regressed"}],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    raise SystemExit(payload["decision"] != "accepted")


if __name__ == "__main__":
    main()
