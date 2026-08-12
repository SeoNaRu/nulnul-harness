#!/usr/bin/env python3
"""Validate NULNUL evaluation exposure and one-shot holdout evidence."""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


ROLES = {"DEV", "VALIDATION", "HOLDOUT"}
CURRENT_ROLES = {"dev", "validation", "holdout", "retired"}
DECISIONS = {"established", "not_established", "failed", "narrower_scope"}
PROHIBITED_KEYS = {
    "raw_prompt", "raw_response", "raw_transcript", "commands", "command",
    "absolute_path", "secret", "secrets", "credential", "credentials", "api_key", "token",
}
CLAIM_FIELDS = {
    "claim_id", "mechanism_id", "candidate_ref", "originating_development_failure",
    "causal_mechanism", "expected_transferable_behavior", "expected_domain",
    "expected_failure_boundary", "heldout_primary_metric", "guardrails",
    "falsification_condition", "holdout_case_ids", "candidate_sources", "status",
}


def git_file(root, ref, path):
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"], cwd=root, capture_output=True
    )
    return result.stdout if result.returncode == 0 else None


def validate(manifest, results=None, root=None):
    errors = []

    def reject_sensitive(value, label="root"):
        if isinstance(value, dict):
            for key, item in value.items():
                if key.lower() in PROHIBITED_KEYS:
                    errors.append(f"{label}.{key} is prohibited")
                reject_sensitive(item, f"{label}.{key}")
        elif isinstance(value, list):
            for index, item in enumerate(value):
                reject_sensitive(item, f"{label}[{index}]")

    reject_sensitive(manifest, "manifest")
    if results is not None:
        reject_sensitive(results, "results")
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 1:
        return ["manifest must be a schema-version-1 object", *errors]
    roles = manifest.get("roles")
    if not isinstance(roles, dict) or set(roles) != ROLES or not all(
        isinstance(value, str) and value for value in roles.values()
    ):
        errors.append("roles must define DEV, VALIDATION, and HOLDOUT")
    policy = manifest.get("gate_policy", {})
    if not all(isinstance(policy.get(field), list) and policy[field] for field in ("activate_for", "skip_for")):
        errors.append("gate_policy must define non-empty activate_for and skip_for lists")
    if policy.get("active") is not True or not isinstance(policy.get("active_reason"), str):
        errors.append("this generalization evidence must record an active gate reason")

    case_by_id = {}
    for suite in manifest.get("suites", []):
        common = {key: suite.get(key) for key in (
            "exposure_class", "current_role", "development_use", "candidate_selection",
            "release_validation", "unseen", "first_exposed", "mechanism_ids",
        )}
        for case_id in suite.get("case_ids", []):
            if case_id in case_by_id:
                errors.append(f"case id is duplicated: {case_id}")
            case_by_id[case_id] = common
    for case in manifest.get("holdout_cases", []):
        case_id = case.get("case_id")
        if not isinstance(case_id, str) or not case_id or case_id in case_by_id:
            errors.append(f"holdout case id is missing or duplicated: {case_id}")
            continue
        case_by_id[case_id] = case
    if not case_by_id:
        errors.append("evaluation exposure inventory is empty")
    for case_id, case in case_by_id.items():
        if case.get("exposure_class") not in ROLES or case.get("current_role") not in CURRENT_ROLES:
            errors.append(f"case {case_id} has an invalid exposure or current role")
        if not isinstance(case.get("first_exposed"), dict) or not all(
            isinstance(case["first_exposed"].get(field), str) and case["first_exposed"][field]
            for field in ("version", "run_id")
        ):
            errors.append(f"case {case_id} lacks first-exposure identity")
        for field in ("development_use", "candidate_selection", "release_validation", "unseen"):
            if not isinstance(case.get(field), bool):
                errors.append(f"case {case_id}.{field} must be boolean")
        if not isinstance(case.get("mechanism_ids"), list):
            errors.append(f"case {case_id}.mechanism_ids must be an array")
        if case.get("current_role") == "holdout" and (
            case.get("exposure_class") != "HOLDOUT"
            or case.get("development_use")
            or case.get("candidate_selection")
            or case.get("release_validation")
            or not case.get("unseen")
            or case.get("exposure_count", 0) != 0
        ):
            errors.append(f"case {case_id} is already exposed and cannot be a holdout")

    claims = manifest.get("claims")
    if not isinstance(claims, list) or not claims:
        errors.append("manifest must contain bounded generalization claims")
        claims = []
    claims_by_id = {}
    for claim in claims:
        missing = CLAIM_FIELDS - claim.keys()
        if missing:
            errors.append("generalization claim missing: " + ", ".join(sorted(missing)))
            continue
        if claim["claim_id"] in claims_by_id:
            errors.append(f"generalization claim id is duplicated: {claim['claim_id']}")
        claims_by_id[claim["claim_id"]] = claim
        if root is not None:
            for source in claim["candidate_sources"]:
                content = git_file(root, claim["candidate_ref"], source.get("path"))
                digest = "sha256:" + hashlib.sha256(content).hexdigest() if content is not None else None
                if digest != source.get("sha256"):
                    errors.append(f"candidate source identity mismatch: {source.get('path')}")
            for case_id in claim["holdout_case_ids"]:
                case = case_by_id.get(case_id, {})
                material = case.get("material_path")
                if not material or git_file(root, claim["candidate_ref"], material) is not None:
                    errors.append(f"holdout leakage at candidate snapshot: {case_id}")

    if results is None:
        if sum(claim.get("status") == "preregistered" for claim in claims) != 1:
            errors.append("exactly one unevaluated claim must remain preregistered")
        return errors
    if not isinstance(results, dict) or results.get("schema_version") != 1:
        return [*errors, "results must be a schema-version-1 object"]
    claim = claims_by_id.get(results.get("claim_id"), {})
    if results.get("decision") not in DECISIONS:
        errors.append("generalization decision is invalid")
    if claim.get("status") != results.get("decision"):
        errors.append("generalization claim status does not match its result")
    if results.get("claim_id") != claim.get("claim_id") or results.get("mechanism_id") != claim.get("mechanism_id"):
        errors.append("generalization result identity does not match the preregistered claim")
    rows = results.get("case_results")
    if not isinstance(rows, list) or len(rows) != len(claim.get("holdout_case_ids", [])):
        errors.append("results must contain every preregistered holdout exactly once")
        rows = []
    result_case_ids = set()
    for row in rows:
        case_id = row.get("case_id")
        if case_id in result_case_ids:
            errors.append(f"holdout result is duplicated: {case_id}")
        result_case_ids.add(case_id)
        case = case_by_id.get(case_id, {})
        if (
            case_id not in claim.get("holdout_case_ids", [])
            or row.get("run_id") != case.get("first_exposed", {}).get("run_id")
            or row.get("role_at_run") != "holdout"
            or row.get("mechanism_id") != claim.get("mechanism_id")
            or row.get("candidate_ref") != claim.get("candidate_ref")
        ):
            errors.append(f"holdout result identity is invalid: {case_id}")
        if case.get("current_role") not in {"retired", "dev", "validation"} or case.get("unseen") is not False:
            errors.append(f"used holdout remains reusable: {case_id}")
        if results.get("decision") in {"established", "narrower_scope"} and case.get("current_role") != "retired":
            errors.append(f"successful holdout was not retired: {case_id}")
        if case.get("exposure_count") != 1:
            errors.append(f"holdout reuse is prohibited: {case_id}")
        primary = row.get("primary", {})
        required_primary = (
            "heldout_task_success", "completion_check_passed",
            "stale_mutation_blocked", "post_check_fast_resume_ready",
        )
        primary_passed = all(primary.get(field) is True for field in required_primary)
        guardrails = row.get("guardrails", {})
        guardrails_passed = bool(guardrails) and all(
            isinstance(item, dict) and item.get("status") in {"passed", "not_applicable"}
            and isinstance(item.get("evidence"), str) and item["evidence"]
            for item in guardrails.values()
        )
        if results.get("decision") in {"established", "narrower_scope"} and not primary_passed:
            errors.append(f"heldout primary metric failed: {case_id}")
        if results.get("decision") in {"established", "narrower_scope"} and not guardrails_passed:
            errors.append(f"heldout guardrail failed: {case_id}")

    arms = results.get("baselines", {})
    single = arms.get("champion_single", {}).get("runs", [])
    retry = arms.get("retry_champion", {}).get("runs", [])
    candidate = arms.get("evolved_candidate", {}).get("runs", [])
    selection = arms.get("best_of_n_champion", {})
    fair = results.get("budget_comparison", {})
    if len(single) != 1 or len(retry) < 3 or len(candidate) != len(retry):
        errors.append("champion, retry, and evolved-candidate baseline runs are incomplete")
    if selection.get("source_arm") != "retry_champion" or selection.get("selected_safe_result") is not False:
        errors.append("best-of-N baseline is not derived from the repeated champion")
    if results.get("decision") in {"established", "narrower_scope"} and (
        not fair.get("comparable")
        or fair.get("fair_dimension") != "deterministic evaluation trials"
    ):
        errors.append("budget evidence does not support a fair comparison")
    if results.get("decision") in {"established", "narrower_scope"} and (
        not retry or any(run.get("stale_mutation_blocked") is not False for run in retry)
        or any(run.get("stale_mutation_blocked") is not True for run in candidate)
    ):
        errors.append("evolution safety win is not supported by retry and candidate evidence")
    if results.get("decision") == "established" and results.get("harness_wide_generalization") is not True:
        errors.append("an established decision must state its established scope")
    if results.get("decision") == "narrower_scope" and results.get("harness_wide_generalization") is not False:
        errors.append("a narrower-scope decision cannot claim harness-wide generalization")
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("results", type=Path, nargs="?")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        results = json.loads(args.results.read_text(encoding="utf-8")) if args.results else None
        errors = validate(manifest, results, args.root)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        errors = [f"cannot read generalization evidence: {error}"]
    print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()
