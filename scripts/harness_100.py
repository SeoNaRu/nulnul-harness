#!/usr/bin/env python3
"""Calculate the evidence-backed nulnul Harness 100 release score."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def calculate(cases_payload: dict, results_payload: dict) -> dict:
    cases = cases_payload["cases"]
    results = {item["case_id"]: item for item in results_payload["results"]}
    possible = sum(case["harness_100_weight"] for case in cases)
    if possible != 100:
        raise ValueError(f"Harness 100 weights must total 100, got {possible}")

    earned = 0
    checks = []
    for case in cases:
        result = results.get(case["id"], {})
        passed = result.get("status") == "passed"
        weight = case["harness_100_weight"]
        earned += weight if passed else 0
        checks.append(
            {
                "case_id": case["id"],
                "kind": case["kind"],
                "weight": weight,
                "status": result.get("status", "missing"),
            }
        )

    return {
        "score": earned,
        "possible": possible,
        "release_ready": earned == possible,
        "checks": checks,
    }


def main() -> None:
    cases = json.loads((ROOT / "evals/cases.json").read_text(encoding="utf-8"))
    results = json.loads((ROOT / "evals/results.json").read_text(encoding="utf-8"))
    print(json.dumps(calculate(cases, results), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
