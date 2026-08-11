#!/usr/bin/env python3
"""Calculate the evidence-backed nulnul Release Gate release score."""

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEARNING_VALIDATOR = (
    ROOT / "plugins/nulnul-harness/skills/nulnul-harness/scripts/validate_learning_loop.py"
)
CLAUDE_EVIDENCE_VALIDATOR = ROOT / "scripts/claude_adopt_evidence.py"


def validate_learning_gate(results_payload: dict, evolution_payload: dict) -> None:
    spec = importlib.util.spec_from_file_location("validate_learning_loop", LEARNING_VALIDATOR)
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    errors = validator.validate(results_payload, evolution_payload)
    if errors:
        raise ValueError("Release Gate learning loop failed: " + "; ".join(errors))


def validate_claude_gate(evidence_payload: dict, version: str) -> None:
    spec = importlib.util.spec_from_file_location("claude_adopt_evidence", CLAUDE_EVIDENCE_VALIDATOR)
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    errors = validator.validate(evidence_payload, version)
    if errors:
        raise ValueError("Release Gate Claude evidence failed: " + "; ".join(errors))


def calculate(cases_payload: dict, results_payload: dict) -> dict:
    cases = cases_payload["cases"]
    results = {item["case_id"]: item for item in results_payload["results"]}
    possible = sum(case["release_gate_weight"] for case in cases)
    if possible != 100:
        raise ValueError(f"Release Gate weights must total 100, got {possible}")

    earned = 0
    checks = []
    for case in cases:
        result = results.get(case["id"], {})
        passed = result.get("status") == "passed"
        weight = case["release_gate_weight"]
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
    learning = json.loads(
        (ROOT / "evals/benchmarks/setup-baseline/results.json").read_text(encoding="utf-8")
    )
    evolution = json.loads((ROOT / "docs/nulnul/evolution.json").read_text(encoding="utf-8"))
    evidence = json.loads((ROOT / "evals/benchmarks/claude-adopt/evidence.json").read_text(encoding="utf-8"))
    version = json.loads((ROOT / "plugins/nulnul-harness/.codex-plugin/plugin.json").read_text(encoding="utf-8"))["version"]
    validate_learning_gate(learning, evolution)
    validate_claude_gate(evidence, version)
    print(json.dumps(calculate(cases, results), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
