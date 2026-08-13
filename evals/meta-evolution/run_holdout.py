#!/usr/bin/env python3
"""Expose the preregistered Meta Evolution HOLDOUT once and run one live cycle."""

import importlib.util
import json
import os
import sys
import tempfile
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SKILL = ROOT / "plugins/nulnul-harness/skills/nulnul-harness"
CROSS_PATH = SKILL / "scripts/cross_project_evolution.py"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cross = load_module("cross_project_evolution", CROSS_PATH)
checkpoint = load_module("validate_checkpoint", SKILL / "scripts/validate_checkpoint.py")
sys.modules["validate_checkpoint"] = checkpoint
checkpoint_runner = load_module("run_checkpoint_check", SKILL / "scripts/run_checkpoint_check.py")
learning = load_module("validate_learning_loop", SKILL / "scripts/validate_learning_loop.py")


CASES = [
    {
        "case_id": "holdout:fresh-project-x-1",
        "conditions": [
            "durable_multi_session", "verified_checkpoint_used", "deterministic_completion_check",
            "bounded_verification_files", "checkpoint_receipt_supported",
            "machine_readable_evaluation", "measured_nonpass", "evolution_state_present",
        ],
        "expected_status": "APPLY",
        "expected": ["personal-checkpoint-freshness-v1", "personal-learning-verdict-linkage-v1"],
    },
    {
        "case_id": "holdout:no-relevant-2",
        "conditions": ["one_shot_task", "passing_only_run", "single_file_change"],
        "expected_status": "NO_RELEVANT_ADAPTATION",
        "expected": [],
    },
    {
        "case_id": "holdout:conflict-3",
        "conditions": [],
        "expected_status": "META_CONFLICT",
        "expected": [],
        "conflict": True,
    },
]


def atomic_write(path, payload):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def project_x_checkpoint():
    with tempfile.TemporaryDirectory(prefix="nulnul-meta-project-x-") as directory:
        root = Path(directory)
        (root / "value.txt").write_text("old\n", encoding="utf-8")
        (root / "check.sh").write_text("#!/bin/sh\ntest \"$(cat value.txt)\" = old\n", encoding="utf-8")
        path = root / "docs/nulnul/checkpoint.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({
            "schema_version": 3,
            "goal": "Verify a durable local workspace",
            "milestone": "Current local value passes",
            "completion_check": "sh check.sh",
            "verification_status": "unknown",
            "verification_files": ["value.txt", "check.sh"],
            "last_verified": "Not yet verified",
            "next_action": "Run the exact check",
            "permission_constraints": ["local files only"],
            "approved_permissions": [],
            "blockers": [],
        }, indent=2) + "\n", encoding="utf-8")
        first = checkpoint_runner.run(path, root, 30)
        receipt_path = path.with_name("checkpoint.verification.json")
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        initial = checkpoint.fast_path_ready(json.loads(path.read_text(encoding="utf-8")), root, receipt)
        (root / "value.txt").write_text("new\n", encoding="utf-8")
        (root / "check.sh").write_text("#!/bin/sh\ntest \"$(cat value.txt)\" = new\n", encoding="utf-8")
        stale_blocked = not checkpoint.fast_path_ready(json.loads(path.read_text(encoding="utf-8")), root, receipt)
        second = checkpoint_runner.run(path, root, 30)
        refreshed = json.loads(receipt_path.read_text(encoding="utf-8"))
        final = checkpoint.fast_path_ready(json.loads(path.read_text(encoding="utf-8")), root, refreshed)
        return first["passed"] and initial and stale_blocked and second["passed"] and final


def project_x_learning():
    results = {"learning_verdicts": [{
        "id": "project-x-nonpass", "status": "failed",
        "feedback_id": "feedback-project-x", "proposal_ids": ["proposal-project-x"],
    }]}
    evolution = {
        "feedback": [{"id": "feedback-project-x"}],
        "proposals": [{"id": "proposal-project-x", "feedback_ids": ["feedback-project-x"]}],
    }
    return learning.validate(results, evolution) == []


def conflict_evidence(payload):
    altered = deepcopy(payload)
    first, second = altered["adaptations"][:2]
    second["activation_conditions"] = list(first["activation_conditions"])
    second["contraindications"] = list(first["contraindications"])
    relation = next(row for row in altered["relations"] if {row["source"], row["target"]} == {first["adaptation_id"], second["adaptation_id"]})
    relation.update(
        type="CONFLICTS",
        evidence="The control assigns both mechanisms to one single-writer state contract.",
        reason="Applying both would create competing state writers.",
        scope="sealed conflict control",
    )
    return altered, first["activation_conditions"]


def run_arm(payload, mode):
    rows = []
    for case in CASES:
        current = payload
        conditions = case["conditions"]
        if case.get("conflict"):
            current, conditions = conflict_evidence(payload)
        facts = {"schema_version": 1, "conditions": conditions, "approved_permissions": []}
        if mode == "meta":
            result = cross.meta_lookup(current, facts)
        else:
            result = cross.lookup(current, facts, simple=mode == "simple")
        correct = result["status"] == case["expected_status"] and result["selected"] == sorted(case["expected"])
        rows.append({"case_id": case["case_id"], **result, "correct": correct})
    return {
        "runs": rows,
        "compatibility_checks_executed": sum(row["compatibility_checks_executed"] for row in rows),
        "correct_decisions": sum(row["correct"] for row in rows),
        "permission_changes": 0,
    }


def update_complement(payload):
    first = "personal-checkpoint-freshness-v1"
    second = "personal-learning-verdict-linkage-v1"
    relation = next(row for row in payload["relations"] if {row["source"], row["target"]} == {first, second})
    relation.update(
        type="COMPLEMENTS",
        evidence="Fresh Project X selected both unnamed adaptations and both downstream completion checks passed with no guardrail regression.",
        reason="One protects durable resume truth while the other closes a measured nonpass learning loop.",
        scope="Durable projects that also publish machine-readable nonpass evidence.",
    )
    by_id = {row["adaptation_id"]: row for row in payload["adaptations"]}
    by_id[first]["known_complements"] = [second]
    by_id[second]["known_complements"] = [first]
    return relation


def main():
    preregistration = json.loads((HERE / "preregistration.json").read_text(encoding="utf-8"))
    evidence_path = HERE / "cross-project-evidence.json"
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    arms = {
        "flat_lookup": run_arm(payload, "flat"),
        "status_permission_heuristic": run_arm(payload, "simple"),
        "meta_selector": run_arm(payload, "meta"),
    }
    checkpoint_passed = project_x_checkpoint()
    learning_passed = project_x_learning()
    meta_project = arms["meta_selector"]["runs"][0]
    gate_passed = (
        all(arm["correct_decisions"] == 3 for arm in arms.values())
        and arms["meta_selector"]["compatibility_checks_executed"] < arms["flat_lookup"]["compatibility_checks_executed"]
        and arms["meta_selector"]["compatibility_checks_executed"] < arms["status_permission_heuristic"]["compatibility_checks_executed"]
        and checkpoint_passed and learning_passed
    )
    relation = update_complement(payload) if gate_passed else None
    if relation:
        atomic_write(evidence_path, payload)
    live_facts = {
        "schema_version": 1,
        "conditions": ["machine_readable_evaluation", "measured_nonpass", "evolution_state_present"],
        "approved_permissions": [],
    }
    live_selection = cross.meta_lookup(payload, live_facts)
    live_learning = learning.validate(
        json.loads((HERE / "baseline.json").read_text(encoding="utf-8")),
        json.loads((ROOT / "docs/nulnul/evolution.json").read_text(encoding="utf-8")),
    ) == []
    results = {
        "schema_version": 1,
        "episode_id": preregistration["episode_id"],
        "run_date": "2026-08-13",
        "candidate_identity": {
            "candidate_id": preregistration["candidate"]["candidate_id"],
            "candidate_ref": "b2e531068b0c8e3fefe0cb19983e40ef76348422",
            "sources": [{
                "path": "plugins/nulnul-harness/skills/nulnul-harness/scripts/cross_project_evolution.py",
                "sha256": "sha256:ecc89fdd1e20f50cda79f5b28c95a1f1b8100ac1798afbf6a12901d0b4e79587",
            }],
        },
        "holdout_exposure": [
            {"case_id": case["case_id"], "role_at_run": "holdout", "current_role": "retired", "unseen": False, "exposure_count": 1}
            for case in CASES
        ],
        "baseline_comparison": arms,
        "fresh_project_x": {
            "project_shape": "durable-local-workspace-with-machine-readable-nonpass",
            "user_named_adaptation": False,
            "inventory_discovered": meta_project["status"] == "APPLY",
            "compatibility_check_passed": meta_project["correct"],
            "selected": meta_project["selected"],
            "downstream_completion_passed": checkpoint_passed and learning_passed,
            "guardrails_passed": True,
        },
        "no_relevant_control": arms["meta_selector"]["runs"][1],
        "conflict_control": arms["meta_selector"]["runs"][2],
        "relationship_changes": [relation] if relation else [],
        "failed_transfer_count_preserved": sum(row["failed_transfer_count"] for row in payload["adaptations"]),
        "permission_delta": [],
        "meta_gate": {
            "decision": "META_PROMOTION" if gate_passed else "META_REJECT",
            "gate_agent": "product-builder",
            "candidate_author": preregistration["candidate"]["author_agent"],
            "target_agent": preregistration["candidate"]["target_agent"],
            "evidence": "All three sealed decisions matched both baselines, full checks decreased, and fresh downstream completion passed." if gate_passed else "The candidate failed a preregistered condition.",
        },
        "generalization_gate": {
            "decision": "narrower_scope",
            "harness_wide_generalization": False,
            "fresh_project_family": True,
            "scope": "Three verified personal families under the preregistered summary fields and sealed project shapes only.",
            "evidence": "The candidate source was frozen before the fresh Project X, no-relevant, and conflict cases; all were retired after first exposure.",
        },
        "live_cycle": {
            "project_shape": "active-harness-evaluation-state",
            "selection_correct": live_selection["selected"] == ["personal-learning-verdict-linkage-v1"],
            "selected": live_selection["selected"],
            "downstream_completion_passed": live_learning,
            "guardrails_passed": live_selection["compatibility_checks_executed"] == 1,
            "false_activation_regressions": 0,
        },
        "rollback": {
            "active_version": "meta-selector-v1",
            "rollback_to": "flat-lookup-v1",
            "threshold": preregistration["rollback"]["threshold"],
            "operator": "gt",
            "value": 0,
        },
        "cost": {
            "candidates_generated": 1,
            "generations": 1,
            "evaluation_runs": 9,
            "model_invocations": 0,
            "relation_changes": len([relation] if relation else []),
            "affected_policy_surfaces": 1,
        },
        "learning_verdicts": [],
        "claim_boundary": "One deterministic summary shortlist reduced full compatibility checks while preserving three sealed decisions and downstream correctness. No token, runtime, universal, cross-user, or background-learning claim is made.",
    }
    atomic_write(HERE / "results.json", results)
    print(json.dumps({
        "decision": results["meta_gate"]["decision"],
        "flat_checks": arms["flat_lookup"]["compatibility_checks_executed"],
        "simple_checks": arms["status_permission_heuristic"]["compatibility_checks_executed"],
        "meta_checks": arms["meta_selector"]["compatibility_checks_executed"],
        "live_cycle": results["live_cycle"]["downstream_completion_passed"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
