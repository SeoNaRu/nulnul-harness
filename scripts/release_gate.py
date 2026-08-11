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
ACTIVATION_BENCHMARK = ROOT / "evals/benchmarks/activation/run_activation.py"


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


def _median(runs: list[dict], field: str) -> float:
    values = sorted(run.get(field) for run in runs if isinstance(run.get(field), (int, float)))
    if not values:
        raise ValueError(f"Release Gate performance evidence lacks {field}")
    middle = len(values) // 2
    return values[middle] if len(values) % 2 else (values[middle - 1] + values[middle]) / 2


def _change(candidate: float, baseline: float) -> float:
    if baseline <= 0:
        raise ValueError("Release Gate performance baseline must be positive")
    return round(100 * (candidate / baseline - 1), 2)


def _matches(run: dict, required: dict) -> bool:
    return all(run.get(field) == expected for field, expected in required.items())


def validate_activation_gate(cases: dict | None = None, minimum_rounds: int | None = None) -> dict:
    if cases is None or minimum_rounds is None:
        spec = importlib.util.spec_from_file_location("run_activation", ACTIVATION_BENCHMARK)
        benchmark = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(benchmark)
        cases = benchmark.CASES
        minimum_rounds = benchmark.MIN_ROUNDS
    positives = sum(case.get("expect_activation") is True for case in cases.values())
    negatives = sum(case.get("expect_activation") is False for case in cases.values())
    fast = [case for case in cases.values() if case.get("category") == "fast-path"]
    if len(cases) < 10 or positives < 4 or negatives < 4:
        raise ValueError("Release Gate activation matrix must cover at least 10 cases in both directions")
    if minimum_rounds < 3:
        raise ValueError("Release Gate activation benchmark must repeat every case at least 3 times")
    if not fast or any(
        "docs/nulnul/checkpoint.json" not in case.get("required_reads", ())
        or "docs/nulnul/project.md" not in case.get("forbidden_reads", ())
        for case in fast
    ):
        raise ValueError("Release Gate activation matrix lacks a bounded fast-path read check")
    return {"case_count": len(cases), "positive_cases": positives, "negative_cases": negatives,
            "minimum_rounds": minimum_rounds}


def validate_activation_results(payload: dict, evolution: dict) -> dict:
    validate_learning_gate(payload, evolution)
    method = payload.get("method", {})
    required_runs = method.get("runs_per_arm")
    arms = payload.get("arms")
    if not isinstance(required_runs, int) or required_runs < 3 or not isinstance(arms, list):
        raise ValueError("Release Gate activation evidence needs at least 3 runs per arm")
    accepted = [arm for arm in arms if arm.get("decision") == "accepted"]
    if len(accepted) != 1:
        raise ValueError("Release Gate activation evidence needs exactly one accepted arm")
    arm = accepted[0]
    runs = arm.get("runs", [])
    if len(runs) < required_runs or not all(
        run.get("correct") is True and run.get("forbidden_reads") == [] for run in runs
    ):
        raise ValueError("Release Gate accepted activation arm is not exact and bounded in every run")
    for rejected in (item for item in arms if item.get("decision") in {"rejected", "baseline-failed"}):
        if not any(run.get("correct") is False for run in rejected.get("runs", [])):
            raise ValueError("Release Gate rejected activation arm lacks a reproduced failure")
    medians = arm.get("medians", {})
    for field in ("elapsed_seconds", "input_tokens", "output_tokens", "reasoning_output_tokens"):
        if medians.get(field) != _median(runs, field):
            raise ValueError(f"Release Gate activation median mismatch: {field}")
    comparison = payload.get("paired_comparison", {})
    champion = comparison.get("champion", {}).get("runs", [])
    candidate = comparison.get("candidate", {}).get("runs", [])
    maximum_change = comparison.get("maximum_input_change_percent")
    champion_by_pair = {run.get("pair"): run for run in champion}
    candidate_by_pair = {run.get("pair"): run for run in candidate}
    if None in champion_by_pair or champion_by_pair.keys() != candidate_by_pair.keys():
        raise ValueError("Release Gate activation evidence has mismatched paired runs")
    eligible_pairs = [
        pair for pair in champion_by_pair
        if champion_by_pair[pair].get("correct") is True
        and candidate_by_pair[pair].get("correct") is True
    ]
    if len(eligible_pairs) < required_runs:
        raise ValueError("Release Gate activation evidence needs paired champion and candidate runs")
    paired = _paired_changes(
        [champion_by_pair[pair] for pair in eligible_pairs],
        [candidate_by_pair[pair] for pair in eligible_pairs],
        ("input_tokens",),
    )
    if not isinstance(maximum_change, (int, float)) or paired["input_tokens"] > maximum_change:
        raise ValueError("Release Gate activation candidate exceeds its paired input-token budget")
    if not all(run.get("correct") is True and run.get("forbidden_reads") == [] for run in candidate):
        raise ValueError("Release Gate activation candidate changed behavior or read scope")
    return {
        "live_status": "passed",
        "accepted_arm": arm["id"],
        "exact_runs": len(runs),
        "median_elapsed_seconds": medians["elapsed_seconds"],
        "median_input_tokens": medians["input_tokens"],
        "paired_input_change_percent": paired["input_tokens"],
        "comparable_pairs": len(eligible_pairs),
    }


def _paired_changes(champion: list[dict], candidate: list[dict], fields) -> dict:
    champion_by_pair = {run.get("pair"): run for run in champion}
    candidate_by_pair = {run.get("pair"): run for run in candidate}
    if None in champion_by_pair or champion_by_pair.keys() != candidate_by_pair.keys():
        raise ValueError("Release Gate paired evidence has mismatched pair identifiers")
    return {
        field: _median([
            {field: _change(candidate_by_pair[pair][field], champion_by_pair[pair][field])}
            for pair in champion_by_pair
        ], field)
        for field in fields
    }


def validate_performance_gate(payload: dict) -> dict:
    comparisons = payload.get("comparisons")
    if not isinstance(comparisons, list) or not comparisons:
        raise ValueError("Release Gate performance comparisons are missing")
    results = {}
    for comparison in comparisons:
        champion = comparison.get("champion", {}).get("runs", [])
        candidate = comparison.get("candidate", {}).get("runs", [])
        minimum = comparison.get("minimum_runs")
        required = comparison.get("required", {})
        limits = comparison.get("metrics", {})
        if not isinstance(minimum, int) or minimum < 1 or min(len(champion), len(candidate)) < minimum:
            raise ValueError(f"Release Gate performance comparison {comparison.get('id')} lacks runs")
        if not isinstance(required, dict) or not all(
            _matches(run, required) for run in champion + candidate
        ):
            raise ValueError(f"Release Gate performance comparison {comparison.get('id')} changed behavior")
        fields = tuple(limits)
        if comparison.get("mode") == "paired":
            changes = _paired_changes(champion, candidate, fields)
        elif comparison.get("mode") == "median":
            changes = {field: _change(_median(candidate, field), _median(champion, field)) for field in fields}
        else:
            raise ValueError(f"Release Gate performance comparison {comparison.get('id')} has invalid mode")
        if any(not isinstance(limit.get("maximum_change_percent"), (int, float))
               or changes[field] > limit["maximum_change_percent"] for field, limit in limits.items()):
            raise ValueError(f"Release Gate performance comparison {comparison.get('id')} regressed")
        results[comparison["id"]] = changes
    if not all(control.get("passed") is True for control in payload.get("controls", [])):
        raise ValueError("Release Gate performance control failed")
    return {"status": "passed", "comparisons": results}


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
    performance = json.loads(
        (ROOT / "evals/benchmarks/performance.json").read_text(encoding="utf-8")
    )
    activation = json.loads(
        (ROOT / "evals/benchmarks/activation/results.json").read_text(encoding="utf-8")
    )
    evolution = json.loads((ROOT / "docs/nulnul/evolution.json").read_text(encoding="utf-8"))
    evidence = json.loads((ROOT / "evals/benchmarks/claude-adopt/evidence.json").read_text(encoding="utf-8"))
    version = json.loads((ROOT / "plugins/nulnul-harness/.codex-plugin/plugin.json").read_text(encoding="utf-8"))["version"]
    validate_learning_gate(learning, evolution)
    validate_claude_gate(evidence, version)
    score = calculate(cases, results)
    score["performance_gate"] = validate_performance_gate(performance)
    score["activation_gate"] = {
        **validate_activation_gate(),
        **validate_activation_results(activation, evolution),
    }
    print(json.dumps(score, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
