#!/usr/bin/env python3
"""Calculate the evidence-backed nulnul Release Gate release score."""

import importlib.util
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEARNING_VALIDATOR = (
    ROOT / "plugins/nulnul-harness/skills/nulnul-harness/scripts/validate_learning_loop.py"
)
CLAUDE_EVIDENCE_VALIDATOR = ROOT / "scripts/claude_adopt_evidence.py"
ACTIVATION_BENCHMARK = ROOT / "evals/benchmarks/activation/run_activation.py"
EXPERIENCE_VALIDATOR = (
    ROOT / "plugins/nulnul-harness/skills/nulnul-harness/scripts/validate_experience_digest.py"
)
GENERALIZATION_VALIDATOR = (
    ROOT / "plugins/nulnul-harness/skills/nulnul-harness/scripts/validate_generalization_gate.py"
)
AUTONOMOUS_VALIDATOR = (
    ROOT / "plugins/nulnul-harness/skills/nulnul-harness/scripts/validate_autonomous_evolution.py"
)
EVOLUTION_COMPACTOR = (
    ROOT / "plugins/nulnul-harness/skills/nulnul-harness/scripts/compact_evolution_state.py"
)
PERSONAL_VALIDATOR = (
    ROOT / "plugins/nulnul-harness/skills/nulnul-harness/scripts/personal_adaptation.py"
)
PERSONAL_ADOPTION_VALIDATOR = ROOT / "scripts/personal_adopt_evidence.py"
META_EVOLUTION_VALIDATOR = (
    ROOT / "plugins/nulnul-harness/skills/nulnul-harness/scripts/validate_meta_evolution.py"
)
META_ADOPTION_VALIDATOR = ROOT / "scripts/meta_adopt_evidence.py"
PLUGIN = ROOT / "plugins/nulnul-harness"
BEHAVIOR_BOUNDARIES = ROOT / "evals/behavior-boundaries"
RELEASE_GATE = ROOT / "scripts/release_gate.py"
BEHAVIOR_RUNNER = BEHAVIOR_BOUNDARIES / "run_ab.py"
BEHAVIOR_SCHEMA = BEHAVIOR_BOUNDARIES / "decision.schema.json"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def plugin_tree_sha256(root: Path = PLUGIN) -> str:
    digest = hashlib.sha256()
    for path in sorted(
        item for item in root.rglob("*")
        if item.is_file() and "__pycache__" not in item.parts and item.suffix != ".pyc"
    ):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(4, "big"))
        digest.update(relative)
        content = path.read_bytes()
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


def public_evidence_is_current(evidence: dict, version: str, archive_sha256: str) -> bool:
    installed_version = evidence.get("plugin_version") or evidence.get("installed_plugin", {}).get("version")
    return (
        installed_version == version
        and evidence.get("distribution", {}).get("asset_sha256") == archive_sha256
    )


def validate_behavior_boundary_gate(
    preregistration: dict,
    cases: dict,
    results: dict,
    version: str,
    archive_sha256: str,
) -> dict:
    if preregistration.get("schema_version") != 1 or results.get("schema_version") != 1:
        raise ValueError("Behavior boundary evidence must use schema version 1")
    if results.get("episode_id") != preregistration.get("episode_id"):
        raise ValueError("Behavior boundary episode identity mismatch")
    budget = preregistration.get("budget", {})
    if (
        budget.get("max_candidates") != 1
        or budget.get("max_generations") != 1
        or budget.get("counterbalanced_rounds", 0) < 4
        or budget.get("max_model_invocations", 0) > 17
        or budget.get("permission_delta") != []
        or budget.get("external_writes") != 0
        or budget.get("new_dependencies") != 0
        or budget.get("new_services") != 0
        or budget.get("holdout_access") is not False
    ):
        raise ValueError("Behavior boundary budget is not bounded")
    expected_cases = set(preregistration.get("primary_cases", [])) | set(
        preregistration.get("candidate_controls", [])
    )
    if set(cases) != expected_cases:
        raise ValueError("Behavior boundary case inventory mismatch")
    candidate = results.get("candidate", {})
    if results.get("decision") == "NO_PROMOTION":
        evaluated_version = candidate.get("plugin_version")
        digest_fields = {
            "skill_sha256", "plugin_tree_sha256", "archive_sha256",
            "preregistration_sha256", "cases_sha256", "release_gate_sha256",
            "behavior_runner_sha256", "behavior_schema_sha256",
            "activation_runner_sha256", "sanitized_result_sha256",
        }
        behavior = results.get("behavior", {})
        invocations = results.get("model_invocations")
        if (
            results.get("status") != "rejected"
            or results.get("candidate_removed") is not True
            or results.get("raw_transcript_retained") is not False
            or results.get("permission_delta") != []
            or not isinstance(evaluated_version, str)
            or not evaluated_version
            or candidate.get("plugin_tree_sha256") == plugin_tree_sha256()
            or any(
                not isinstance(candidate.get(field), str)
                or len(candidate[field]) != 64
                or any(character not in "0123456789abcdef" for character in candidate[field])
                for field in digest_fields
            )
            or isinstance(invocations, bool)
            or not isinstance(invocations, int)
            or not 0 < invocations <= budget["max_model_invocations"]
            or behavior.get("candidate_correct_runs", budget["counterbalanced_rounds"])
            >= budget["counterbalanced_rounds"]
            or results.get("fast_resume_performance", {}).get("status") != "not_run"
        ):
            raise ValueError("Rejected behavior candidate was not closed safely")
        verdicts = results.get("learning_verdicts")
        if not isinstance(verdicts, list) or not verdicts:
            raise ValueError("Rejected behavior candidate lacks its learning verdict")
        return {
            "status": "passed",
            "decision": "NO_PROMOTION",
            "product_behavior_promoted": False,
            "candidate_id": results.get("candidate_id"),
            "evaluated_version": evaluated_version,
            "candidate_removed": True,
            "completed_model_invocations": invocations,
        }
    skill = PLUGIN / "skills/nulnul-harness/SKILL.md"
    expected_identity = {
        "plugin_version": version,
        "skill_sha256": file_sha256(skill),
        "plugin_tree_sha256": plugin_tree_sha256(),
        "archive_sha256": archive_sha256,
        "preregistration_sha256": file_sha256(BEHAVIOR_BOUNDARIES / "preregistration.json"),
        "cases_sha256": file_sha256(BEHAVIOR_BOUNDARIES / "cases.json"),
        "release_gate_sha256": file_sha256(RELEASE_GATE),
        "behavior_runner_sha256": file_sha256(BEHAVIOR_RUNNER),
        "behavior_schema_sha256": file_sha256(BEHAVIOR_SCHEMA),
        "activation_runner_sha256": file_sha256(ACTIVATION_BENCHMARK),
    }
    for field, expected in expected_identity.items():
        if candidate.get(field) != expected:
            raise ValueError(f"Behavior boundary candidate identity mismatch: {field}")
    behavior = results.get("behavior", {})
    performance = results.get("fast_resume_performance", {})
    invocations = results.get("model_invocations")
    if (
        results.get("status") != "passed"
        or results.get("decision") != "PROVISIONAL"
        or results.get("raw_transcript_retained") is not False
        or results.get("permission_delta") != []
        or isinstance(invocations, bool)
        or not isinstance(invocations, int)
        or not 0 < invocations <= budget["max_model_invocations"]
        or behavior.get("rounds_per_arm") != budget["counterbalanced_rounds"]
        or not isinstance(behavior.get("champion_correct_runs"), int)
        or behavior["champion_correct_runs"] >= budget["counterbalanced_rounds"]
        or behavior.get("candidate_correct_runs") != budget["counterbalanced_rounds"]
        or behavior.get("candidate_primary_decisions")
        != budget["counterbalanced_rounds"] * budget["primary_cases_per_arm"]
        or behavior.get("candidate_control_decisions") != budget["candidate_control_cases"]
        or behavior.get("unselected_optional_skill_activations") != 0
        or behavior.get("selected_optional_skill_activations") != 1
        or behavior.get("candidate_nulnul_activation_runs")
        != budget["counterbalanced_rounds"] + 1
        or performance.get("rounds") != 4
        or performance.get("candidate_correct_runs") != 4
        or performance.get("forbidden_read_runs") != 0
        or performance.get("eligible_pairs") != 4
    ):
        raise ValueError("Behavior boundary candidate did not pass its frozen Gate")
    paired_change = performance.get("paired_input_change_percent")
    if not isinstance(paired_change, (int, float)) or paired_change > 20:
        raise ValueError("Behavior boundary fast-resume input cost regressed")
    verdicts = results.get("learning_verdicts")
    if not isinstance(verdicts, list) or not verdicts:
        raise ValueError("Behavior boundary evidence lacks its champion learning verdict")
    return {
        "status": "passed",
        "decision": results["decision"],
        "product_behavior_promoted": True,
        "candidate_id": results.get("candidate_id"),
        "plugin_tree_sha256": candidate["plugin_tree_sha256"],
        "behavior_decisions": behavior["candidate_primary_decisions"] + behavior["candidate_control_decisions"],
        "fast_resume_rounds": performance["candidate_correct_runs"],
    }


def load_evolution():
    sys.path.insert(0, str(EVOLUTION_COMPACTOR.parent))
    spec = importlib.util.spec_from_file_location("compact_evolution_state", EVOLUTION_COMPACTOR)
    loader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loader)
    return loader.read_full(ROOT / "docs/nulnul/evolution.json")


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


def validate_generalization_gate(manifest: dict, results: dict) -> dict:
    spec = importlib.util.spec_from_file_location(
        "validate_generalization_gate", GENERALIZATION_VALIDATOR
    )
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    errors = validator.validate(manifest, results, ROOT)
    if errors:
        raise ValueError("Generalization Gate failed: " + "; ".join(errors))
    return {
        "status": "passed",
        "decision": results["decision"],
        "scope": results["scope"],
        "harness_wide_generalization": results["harness_wide_generalization"],
    }


def validate_autonomous_gate(evolution: dict) -> dict:
    spec = importlib.util.spec_from_file_location(
        "validate_autonomous_evolution", AUTONOMOUS_VALIDATOR
    )
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    errors = validator.validate(evolution)
    if errors:
        raise ValueError("Bounded Autonomous Evolution Gate failed: " + "; ".join(errors))
    episodes = validator.summarize(evolution)
    if not episodes:
        raise ValueError("Bounded Autonomous Evolution Gate needs one recorded episode")
    return {"status": "passed", "episodes": episodes}


def validate_personal_gate(preregistration: dict, results: dict) -> dict:
    spec = importlib.util.spec_from_file_location("personal_adaptation", PERSONAL_VALIDATOR)
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    errors = validator.validate_evidence(preregistration, results, ROOT)
    if errors:
        raise ValueError("Personal Evolution Gate failed: " + "; ".join(errors))
    return {
        "status": "passed",
        "decision": results["personal_gate"]["decision"],
        "adaptation_id": results["personal_adaptation"]["adaptation_id"],
        "fresh_project_reuse": results["fresh_project_adoption"]["completion_check_passed"],
    }


def validate_public_personal_adoption(evidence: dict, version: str) -> dict:
    spec = importlib.util.spec_from_file_location(
        "personal_adopt_evidence", PERSONAL_ADOPTION_VALIDATOR
    )
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    errors = validator.validate(evidence, version)
    if errors:
        raise ValueError("Public Personal Evolution adoption failed: " + "; ".join(errors))
    return {
        "status": "passed",
        "adaptation_id": evidence["adaptation"]["adaptation_id"],
        "fresh_project_reuse": evidence["fresh_project"]["verified_resume"],
        "negative_project": evidence["negative_project"]["decision"],
        "revocation_control": evidence["revocation_control"]["decision"],
    }


def validate_meta_evolution_gate(preregistration: dict, results: dict, evidence: dict) -> dict:
    spec = importlib.util.spec_from_file_location("validate_meta_evolution", META_EVOLUTION_VALIDATOR)
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    errors = validator.validate(preregistration, results, evidence, ROOT)
    if errors:
        raise ValueError("Cross-project Meta Evolution Gate failed: " + "; ".join(errors))
    return {
        "status": "passed",
        "decision": results["meta_gate"]["decision"],
        "generalization_scope": results["generalization_gate"]["decision"],
        "flat_checks": results["baseline_comparison"]["flat_lookup"]["compatibility_checks_executed"],
        "meta_checks": results["baseline_comparison"]["meta_selector"]["compatibility_checks_executed"],
        "live_cycle": results["live_cycle"]["downstream_completion_passed"],
    }


def validate_public_meta_adoption(evidence: dict, preregistration: dict, version: str) -> dict:
    spec = importlib.util.spec_from_file_location("meta_adopt_evidence", META_ADOPTION_VALIDATOR)
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    errors = validator.validate(evidence, preregistration, version)
    if errors:
        raise ValueError("Public Meta Evolution adoption failed: " + "; ".join(errors))
    project = evidence["project_m"]
    return {
        "status": "passed",
        "version": version,
        "flat_checks": project["flat_lookup"]["compatibility_checks_executed"],
        "meta_checks": project["meta_selector"]["compatibility_checks_executed"],
        "no_relevant": evidence["no_relevant_control"]["status"],
        "conflict": evidence["conflict_control"]["status"],
        "rollback": evidence["rollback_control"]["rolled_back_to"],
    }


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


def validate_observable_evolution(payload: dict) -> dict:
    evidence = payload.get("observable_evolution", {})
    champion = evidence.get("champion", {})
    runs = champion.get("runs", [])
    broad = champion.get("broad_test_commands", [])
    exact = champion.get("exact_completion_check_invocations", [])
    if len(runs) < 3 or len(broad) != len(runs) or len(exact) != len(runs):
        raise ValueError("Release Gate observable evidence needs three aligned champion runs")
    spec = importlib.util.spec_from_file_location("validate_experience_digest", EXPERIENCE_VALIDATOR)
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    for run in runs + evidence.get("candidate", {}).get("runs", []):
        errors = validator.validate(run)
        if errors:
            raise ValueError("Release Gate Experience Digest failed: " + "; ".join(errors))
    if broad == exact or not all(value == 0 for value in exact):
        raise ValueError("Release Gate observable evidence did not reproduce the attribution error")
    owners = []
    for run in runs:
        stages = {stage["stage"]: stage for stage in run["stages"]}
        resume = stages.get("resume", {})
        verification = stages.get("verification", {})
        if (
            resume.get("owner") != "navigator"
            or resume.get("completion_check_invocations") != 0
            or verification.get("owner") != "gate"
            or verification.get("completion_check_invocations") != 1
            or "completion_check_missing" not in run.get("signals", [])
        ):
            raise ValueError("Release Gate observable evidence cannot distinguish check ownership")
        owners.append({"navigator": 0, "gate": 1})
    divergence = evidence.get("first_divergence")
    if divergence != {"status": "unknown", "stage": None}:
        raise ValueError("Release Gate observable evidence must preserve unknown divergence")
    if evidence.get("candidate", {}).get("decision") != "rejected":
        raise ValueError("Release Gate observable evidence lost the rejected Navigator candidate")
    causal = evidence.get("causal_attribution_1_4_1", {})
    measurements = causal.get("measurements", {})
    for condition in ("baseline", "resolvable_wrapper"):
        measured = measurements.get(condition, {})
        aligned = (
            measured.get("navigator_completion_checks") == [0, 0, 0]
            and measured.get("gate_completion_checks") == [1, 1, 1]
            and measured.get("implementation_completed") == [True, True, True]
            and measured.get("verification_stage_entered") == [False, False, False]
            and measured.get("final_synthesis_observed") == [True, True, True]
            and measured.get("behavior_passed") == [True, True, True]
        )
        if not aligned:
            raise ValueError("Release Gate causal attribution evidence is incomplete or misaligned")
    candidate = causal.get("candidate", {})
    if (
        causal.get("status") != "completed"
        or causal.get("diagnosis") != "final_action_ordering_supported"
        or causal.get("first_divergence") != {"status": "unknown", "stage": None}
        or causal.get("gate_decision") != "rejected"
        or candidate.get("navigator_completion_checks") != [0]
        or candidate.get("decision") != "rejected_early"
    ):
        raise ValueError("Release Gate causal attribution decision is not supported")
    truth = evidence.get("checkpoint_truth_1_4_2", {})
    champion_truth = truth.get("champion_measurements", {})
    candidate_truth = truth.get("candidate_measurements", {})
    controls = truth.get("deterministic_controls", {})
    if (
        truth.get("status") != "candidate_gate_passed"
        or truth.get("diagnosis") != "real_checkpoint_truth_defect"
        or champion_truth.get("unverified_mutated_repository_state_accepted_for_fast_resume")
        != [True, True, True]
        or champion_truth.get("navigator_completion_check_invocations") != [0, 0, 0]
        or candidate_truth.get("unverified_mutated_repository_state_accepted_for_fast_resume")
        != [False, False, False]
        or candidate_truth.get("task_behavior_passed") != [True, True, True]
        or candidate_truth.get("read_scope_passed") != [True, True, True]
        or candidate_truth.get("fast_path_ready_after_gate") != [True, True, True]
        or candidate_truth.get("direct_completion_check_invocations") != [0, 0, 0]
        or not controls
        or not all(value is expected for value, expected in (
            (controls.get("clean_verified_state_fast_resumes"), True),
            (controls.get("pre_check_mutation_fast_resumes"), False),
            (controls.get("failed_check_fast_resumes"), False),
            (controls.get("unknown_state_fast_resumes"), False),
            (controls.get("old_nonempty_evidence_fast_resumes"), False),
            (controls.get("missing_receipt_fast_resumes"), False),
        ))
        or truth.get("candidate_decision") != "accepted_by_independent_gate"
    ):
        raise ValueError("Release Gate checkpoint-truth evidence is incomplete or unsafe")
    return {
        "status": "passed", "runs": len(runs), "owners": owners[0],
        "causal_diagnosis": causal["diagnosis"],
        "checkpoint_truth_diagnosis": truth["diagnosis"],
        "unverified_mutated_state_acceptance": 0,
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
    generalization_manifest = json.loads(
        (ROOT / "evals/generalization/manifest.json").read_text(encoding="utf-8")
    )
    generalization_results = json.loads(
        (ROOT / "evals/generalization/results.json").read_text(encoding="utf-8")
    )
    failed_holdout = json.loads(
        (ROOT / "evals/generalization/results-ruby-failed.json").read_text(encoding="utf-8")
    )
    evolution = load_evolution()
    evidence = json.loads((ROOT / "evals/benchmarks/claude-adopt/evidence.json").read_text(encoding="utf-8"))
    personal_preregistration = json.loads(
        (ROOT / "evals/personal-evolution/preregistration.json").read_text(encoding="utf-8")
    )
    personal_results = json.loads(
        (ROOT / "evals/personal-evolution/results.json").read_text(encoding="utf-8")
    )
    public_personal_adoption = json.loads(
        (ROOT / "evals/personal-evolution/public-adoption.json").read_text(encoding="utf-8")
    )
    additional_personal = [
        (
            json.loads((ROOT / f"evals/personal-evolution/{name}/preregistration.json").read_text(encoding="utf-8")),
            json.loads((ROOT / f"evals/personal-evolution/{name}/results.json").read_text(encoding="utf-8")),
        )
        for name in ("transactional-migration", "learning-verdicts")
    ]
    meta_preregistration = json.loads((ROOT / "evals/meta-evolution/preregistration.json").read_text(encoding="utf-8"))
    meta_results = json.loads((ROOT / "evals/meta-evolution/results.json").read_text(encoding="utf-8"))
    cross_project_evidence = json.loads((ROOT / "evals/meta-evolution/cross-project-evidence.json").read_text(encoding="utf-8"))
    meta_release_preregistration = json.loads(
        (ROOT / "evals/meta-evolution/release-preregistration.json").read_text(encoding="utf-8")
    )
    version = json.loads((ROOT / "plugins/nulnul-harness/.codex-plugin/plugin.json").read_text(encoding="utf-8"))["version"]
    archive = ROOT / "dist" / f"nulnul-harness-{version}.zip"
    if not archive.is_file():
        raise ValueError(f"Current candidate archive is missing: {archive.name}")
    archive_sha256 = file_sha256(archive)
    behavior_preregistration = json.loads(
        (BEHAVIOR_BOUNDARIES / "preregistration.json").read_text(encoding="utf-8")
    )
    behavior_cases = json.loads((BEHAVIOR_BOUNDARIES / "cases.json").read_text(encoding="utf-8"))
    behavior_results = json.loads((BEHAVIOR_BOUNDARIES / "results.json").read_text(encoding="utf-8"))
    validate_learning_gate(learning, evolution)
    validate_learning_gate(failed_holdout, evolution)
    validate_learning_gate(meta_results, evolution)
    validate_learning_gate(behavior_results, evolution)
    validate_claude_gate(evidence, evidence["plugin_version"])
    score = calculate(cases, results)
    score["performance_gate"] = validate_performance_gate(performance)
    score["activation_gate"] = {
        "status": "passed",
        **validate_activation_gate(),
        **validate_activation_results(activation, evolution),
    }
    score["observable_evolution_gate"] = validate_observable_evolution(activation)
    score["generalization_gate"] = validate_generalization_gate(
        generalization_manifest, generalization_results
    )
    score["bounded_autonomous_evolution_gate"] = validate_autonomous_gate(evolution)
    score["personal_evolution_gate"] = validate_personal_gate(
        personal_preregistration, personal_results
    )
    score["additional_personal_evolution_gates"] = [
        validate_personal_gate(preregistration, result)
        for preregistration, result in additional_personal
    ]
    score["cross_project_meta_evolution_gate"] = validate_meta_evolution_gate(
        meta_preregistration, meta_results, cross_project_evidence
    )
    score["behavior_boundary_evaluation_gate"] = validate_behavior_boundary_gate(
        behavior_preregistration, behavior_cases, behavior_results, version, archive_sha256
    )
    score["public_personal_adoption_gate"] = validate_public_personal_adoption(
        public_personal_adoption, public_personal_adoption["installed_plugin"]["version"]
    )
    local_candidate_ready = all(
        gate.get("status") == "passed"
        for gate in (
            score["performance_gate"],
            score["activation_gate"],
            score["observable_evolution_gate"],
            score["generalization_gate"],
            score["bounded_autonomous_evolution_gate"],
            score["personal_evolution_gate"],
            score["cross_project_meta_evolution_gate"],
            score["behavior_boundary_evaluation_gate"],
        )
    )
    score["published_baseline_release_ready"] = score["release_ready"]
    score["local_candidate_ready"] = local_candidate_ready
    blockers = []
    claude_current = public_evidence_is_current(evidence, version, archive_sha256)
    score["public_claude_adoption_gate"] = {
        "status": "passed" if claude_current else "stale",
        "version": evidence["plugin_version"],
        "asset_sha256": evidence.get("distribution", {}).get("asset_sha256"),
    }
    public_meta_path = ROOT / "evals/meta-evolution/public-adoption.json"
    meta_current = False
    if public_meta_path.is_file():
        public_meta = json.loads(public_meta_path.read_text(encoding="utf-8"))
        meta_version = public_meta.get("installed_plugin", {}).get("version")
        score["public_meta_adoption_gate"] = validate_public_meta_adoption(
            public_meta, meta_release_preregistration, meta_version
        )
        meta_current = public_evidence_is_current(public_meta, version, archive_sha256)
        if not meta_current:
            score["public_meta_adoption_gate"]["status"] = "stale"
    else:
        score["public_meta_adoption_gate"] = {"status": "missing"}
    changelog_unreleased = "## Unreleased" in (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    prerelease = "-" in version
    if not claude_current:
        blockers.append("Exact-version public Claude adoption evidence is missing.")
    if not meta_current:
        blockers.append("Exact-version public cross-project Meta adoption evidence is missing.")
    if changelog_unreleased:
        blockers.append("The changelog still contains an Unreleased candidate.")
    if prerelease:
        blockers.append("A prerelease cannot close the final Release Gate.")
    score["release_ready"] = bool(
        score["published_baseline_release_ready"]
        and local_candidate_ready
        and claude_current
        and meta_current
        and not changelog_unreleased
        and not prerelease
    )
    if blockers:
        score["release_ready"] = False
        score["release_blockers"] = blockers
    print(json.dumps(score, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
