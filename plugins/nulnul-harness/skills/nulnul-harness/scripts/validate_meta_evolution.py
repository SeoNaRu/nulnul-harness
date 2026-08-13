#!/usr/bin/env python3
"""Validate one bounded cross-project Meta Evolution episode."""

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cross_project_evolution
import personal_adaptation


DECISIONS = {
    "META_PROMOTION", "META_REJECT", "META_NARROWER_SCOPE", "META_NO_ADVANTAGE",
    "META_INSUFFICIENT_EVIDENCE", "META_CONFLICT", "META_PERMISSION_BLOCKED", "META_ROLLBACK",
}


def git_file(root, ref, path):
    result = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=root, capture_output=True)
    return result.stdout if result.returncode == 0 else None


def validate(preregistration, results, evidence, root=None):
    errors = []
    personal_adaptation._reject_private(preregistration, errors, "meta_preregistration")
    personal_adaptation._reject_private(results, errors, "meta_results")
    errors.extend(cross_project_evolution.validate_evidence(evidence))
    if not isinstance(preregistration, dict) or preregistration.get("schema_version") != 1:
        return ["meta preregistration must be a schema-version-1 object", *errors]
    if not isinstance(results, dict) or results.get("schema_version") != 1:
        return [*errors, "meta results must be a schema-version-1 object"]
    entry = preregistration.get("entry_gate", {})
    if entry.get("decision") != "PASS" or entry.get("verified_independent_families", 0) < 3:
        errors.append("Meta Evolution started without three independent verified families")
    for row in evidence.get("adaptations", []):
        shapes = row.get("tested_project_shapes", [])
        if len(shapes) != len(set(shapes)):
            errors.append(f"cloned project shape counted twice: {row.get('adaptation_id')}")
    archive = preregistration.get("archive_lookup", {})
    if archive.get("matching_rejected_meta_proposals") and results.get("new_evidence_for_replay") is not True:
        errors.append("rejected meta proposal replay lacks new evidence")
    budget = preregistration.get("budget", {})
    cost = results.get("cost", {})
    limits = {
        "candidates_generated": "max_candidates",
        "generations": "max_generations",
        "evaluation_runs": "max_evaluation_runs",
        "model_invocations": "max_model_invocations",
        "relation_changes": "max_relation_changes",
        "affected_policy_surfaces": "max_affected_policy_surfaces",
    }
    for used, limit in limits.items():
        if not isinstance(cost.get(used), int) or not isinstance(budget.get(limit), int) or cost[used] > budget[limit]:
            errors.append(f"meta episode exceeded {limit}")
    if budget.get("max_generations") != 1 or cost.get("generations") != 1:
        errors.append("meta episode must remain one-generation")
    candidate = preregistration.get("candidate", {})
    identity = results.get("candidate_identity", {})
    if identity.get("candidate_id") != candidate.get("candidate_id") or identity.get("candidate_ref") != "b2e531068b0c8e3fefe0cb19983e40ef76348422":
        errors.append("meta candidate identity mismatch")
    if root is not None:
        for source in identity.get("sources", []):
            content = git_file(root, identity.get("candidate_ref"), source.get("path"))
            digest = "sha256:" + hashlib.sha256(content).hexdigest() if content is not None else None
            if digest != source.get("sha256"):
                errors.append(f"meta candidate source mismatch: {source.get('path')}")
        holdout_path = preregistration.get("holdout", {}).get("material_path")
        if not holdout_path or git_file(root, identity.get("candidate_ref"), holdout_path) is not None:
            errors.append("HOLDOUT leaked into candidate snapshot")
    expected_cases = set(preregistration.get("evaluation_split", {}).get("HOLDOUT", []))
    exposure = results.get("holdout_exposure", [])
    if {row.get("case_id") for row in exposure if isinstance(row, dict)} != expected_cases:
        errors.append("holdout exposure inventory is incomplete")
    elif any(
        row.get("role_at_run") != "holdout" or row.get("current_role") != "retired"
        or row.get("unseen") is not False or row.get("exposure_count") != 1
        for row in exposure
    ):
        errors.append("used HOLDOUT remains reusable")
    arms = results.get("baseline_comparison", {})
    flat = arms.get("flat_lookup", {})
    simple = arms.get("status_permission_heuristic", {})
    meta = arms.get("meta_selector", {})
    for label, arm in (("flat", flat), ("simple", simple), ("meta", meta)):
        runs = arm.get("runs", [])
        if {row.get("case_id") for row in runs if isinstance(row, dict)} != expected_cases or not all(row.get("correct") is True for row in runs):
            errors.append(f"{label} arm lacks complete correct holdout results")
        if arm.get("compatibility_checks_executed") != sum(row.get("compatibility_checks_executed", -1) for row in runs):
            errors.append(f"{label} arm compatibility total is invalid")
    improved = isinstance(meta.get("compatibility_checks_executed"), int) and all(
        meta.get("compatibility_checks_executed", 10**9) < arm.get("compatibility_checks_executed", -1)
        for arm in (flat, simple)
    )
    no_relevant = results.get("no_relevant_control", {})
    if no_relevant.get("status") != "NO_RELEVANT_ADAPTATION" or no_relevant.get("selected") != []:
        errors.append("no-relevant-adaptation control forced an apply")
    conflict = results.get("conflict_control", {})
    if conflict.get("status") != "META_CONFLICT" or conflict.get("selected") != [] or not conflict.get("conflicts"):
        errors.append("conflict control was auto-resolved")
    project = results.get("fresh_project_x", {})
    if project.get("user_named_adaptation") is not False or not all(
        project.get(field) is True for field in ("inventory_discovered", "compatibility_check_passed", "downstream_completion_passed", "guardrails_passed")
    ):
        errors.append("fresh Project X did not verify unnamed downstream reuse")
    gate = results.get("meta_gate", {})
    if gate.get("decision") not in DECISIONS:
        errors.append("Meta Gate decision is invalid")
    if gate.get("candidate_author") != candidate.get("author_agent") or gate.get("target_agent") != candidate.get("target_agent"):
        errors.append("Meta Gate candidate ownership mismatch")
    if gate.get("gate_agent") in {gate.get("candidate_author"), gate.get("target_agent")}:
        errors.append("Meta proposer or target self-approved")
    if gate.get("decision") == "META_PROMOTION" and not improved:
        errors.append("meta selector did not beat both fair baselines")
    if gate.get("decision") == "META_PROMOTION" and (
        errors or meta.get("correct_decisions") != len(expected_cases)
        or meta.get("permission_changes") != 0
    ):
        errors.append("Meta Gate promoted without complete independent evidence")
    generalization = results.get("generalization_gate", {})
    if (
        generalization.get("decision") != "narrower_scope"
        or generalization.get("harness_wide_generalization") is not False
        or generalization.get("fresh_project_family") is not True
        or not isinstance(generalization.get("scope"), str)
        or not generalization["scope"]
    ):
        errors.append("Meta Generalization Gate did not preserve narrower scope")
    if preregistration.get("candidate", {}).get("permission_delta") != [] or results.get("permission_delta") != []:
        errors.append("meta policy expanded permissions")
    if results.get("failed_transfer_count_preserved") != sum(row["failed_transfer_count"] for row in evidence.get("adaptations", [])):
        errors.append("failed transfer evidence was hidden")
    relation_changes = results.get("relationship_changes", [])
    if len(relation_changes) != cost.get("relation_changes") or any(
        row.get("type") not in cross_project_evolution.RELATIONS
        or not all(isinstance(row.get(field), str) and row[field] for field in ("evidence", "reason", "scope"))
        for row in relation_changes
    ):
        errors.append("relationship changes lack bounded evidence")
    for relation in relation_changes:
        if relation not in evidence.get("relations", []):
            errors.append("relationship change is missing from current evidence")
    live = results.get("live_cycle", {})
    if gate.get("decision") == "META_PROMOTION" and not all(
        live.get(field) is True for field in ("selection_correct", "downstream_completion_passed", "guardrails_passed")
    ):
        errors.append("promoted meta selector lacks a passing live cycle")
    rollback = results.get("rollback", {})
    if not isinstance(rollback.get("threshold"), str) or not rollback["threshold"] or rollback.get("operator") != "gt" or rollback.get("value") != 0:
        errors.append("meta rollback threshold is missing or not executable")
    if results.get("learning_verdicts") != []:
        errors.append("passing meta episode must have an empty learning verdict inventory")
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("preregistration", type=Path)
    parser.add_argument("results", type=Path)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        preregistration = json.loads(args.preregistration.read_text(encoding="utf-8"))
        results = json.loads(args.results.read_text(encoding="utf-8"))
        evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
        errors = validate(preregistration, results, evidence, args.root)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        errors = [f"cannot read Meta Evolution evidence: {error}"]
    print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()
