#!/usr/bin/env python3
"""Validate and use a user-selected local NULNUL personal adaptation home."""

import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path


REGISTRY_NAME = "personal-adaptations.json"
VALID_DECISIONS = {
    "PERSONAL_PROMOTION", "NARROWER_PERSONAL_SCOPE", "PERSONAL_REJECT",
    "INSUFFICIENT_TRANSFER_EVIDENCE", "PRIVACY_BLOCKED", "PERMISSION_BLOCKED",
}
ACTIVE_STATUSES = {"active", "narrowed"}
ALL_STATUSES = ACTIVE_STATUSES | {"revoked", "stale"}
ALLOWED_CONDITIONS = {
    "durable_multi_session", "verified_checkpoint_used",
    "deterministic_completion_check", "bounded_verification_files",
    "checkpoint_receipt_supported", "one_shot_task",
    "completion_check_unavailable", "mutable_file_identity_unavailable",
    "local_offline_repository", "multi_file_state_migration",
    "single_file_change", "external_state_migration",
    "machine_readable_evaluation", "measured_nonpass",
    "evolution_state_present", "passing_only_run", "evolution_state_absent",
}
PROHIBITED_KEYS = {
    "project_source", "source_code", "repository_name", "customer_name",
    "database_identifier", "raw_prompt", "raw_response", "raw_transcript",
    "transcript", "command_history", "raw_log", "private_issue", "secret",
    "secrets", "credential", "credentials", "api_key", "token", "email",
    "contact_data", "absolute_path", "machine_path",
}
ABSOLUTE_PATH = re.compile(r"(?:^|\s)(?:/(?:[^\s/][^\s]*)|[A-Za-z]:[\\/]\S*)")
EMAIL = re.compile(r"\b[^\s@]+@[^\s@]+\.[^\s@]+\b")
CREDENTIAL = re.compile(r"\b(?:sk-|ghp_|github_pat_|AKIA)[A-Za-z0-9_-]{8,}\b")


class PersonalEvolutionError(ValueError):
    pass


def _require(value, fields, label, errors):
    if not isinstance(value, dict):
        errors.append(f"{label} must be an object")
        return False
    missing = sorted(fields - value.keys())
    if missing:
        errors.append(f"{label} missing: {', '.join(missing)}")
        return False
    return True


def _nonempty(value, label, errors):
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} must be non-empty")


def _reject_private(value, errors, label="root"):
    if isinstance(value, dict):
        for key, item in value.items():
            if key.lower() in PROHIBITED_KEYS:
                errors.append(f"{label}.{key} is prohibited")
            _reject_private(item, errors, f"{label}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_private(item, errors, f"{label}[{index}]")
    elif isinstance(value, str) and (ABSOLUTE_PATH.search(value) or EMAIL.search(value) or CREDENTIAL.search(value)):
        errors.append(f"{label} contains private or machine-specific data")


def adaptation_identity(adaptation):
    return (
        adaptation.get("mechanism_id"), adaptation.get("target_job"),
        tuple(sorted(adaptation.get("activation_conditions", []))),
        tuple(sorted(adaptation.get("contraindications", []))),
    )


def validate_adaptation(adaptation, label="adaptation"):
    errors = []
    fields = {
        "adaptation_id", "title", "target_job", "mechanism_id", "mechanism",
        "source_scope", "current_scope", "source_evidence", "activation_conditions",
        "contraindications", "tested_project_shapes", "transfer_results",
        "primary_metric", "guardrails", "required_permissions", "privacy_class",
        "provenance", "status", "promoted_by", "promoted_at", "disable_condition",
        "conflicts_with",
    }
    if not _require(adaptation, fields, label, errors):
        return errors
    _reject_private(adaptation, errors, label)
    for field in (
        "adaptation_id", "title", "target_job", "mechanism_id", "mechanism",
        "primary_metric", "promoted_by", "promoted_at", "disable_condition",
    ):
        _nonempty(adaptation[field], f"{label}.{field}", errors)
    if adaptation["source_scope"] not in {"project", "core"}:
        errors.append(f"{label}.source_scope must be project or core")
    if adaptation["current_scope"] != "personal":
        errors.append(f"{label}.current_scope must be personal")
    if adaptation["status"] not in ALL_STATUSES:
        errors.append(f"{label}.status is invalid")
    if adaptation["status"] == "revoked" and (
        not isinstance(adaptation.get("revocation_reason"), str)
        or not adaptation["revocation_reason"].strip()
        or not isinstance(adaptation.get("revoked_at"), str)
        or not adaptation["revoked_at"].strip()
    ):
        errors.append(f"{label} revoked status needs reason and timestamp")
    if adaptation["privacy_class"] != "generalized_bounded_evidence":
        errors.append(f"{label}.privacy_class is invalid")
    for field in ("activation_conditions", "contraindications"):
        values = adaptation[field]
        if not isinstance(values, list) or not values or any(item not in ALLOWED_CONDITIONS for item in values):
            errors.append(f"{label}.{field} contains unsupported conditions")
        elif len(values) != len(set(values)):
            errors.append(f"{label}.{field} contains duplicates")
    if set(adaptation["activation_conditions"]) & set(adaptation["contraindications"]):
        errors.append(f"{label} activation and contraindication conditions overlap")
    for field in ("tested_project_shapes", "guardrails", "conflicts_with"):
        values = adaptation[field]
        if not isinstance(values, list) or any(not isinstance(item, str) or not item for item in values):
            errors.append(f"{label}.{field} must contain non-empty strings")
    if not adaptation["tested_project_shapes"]:
        errors.append(f"{label}.tested_project_shapes must not be empty")
    if not adaptation["guardrails"]:
        errors.append(f"{label}.guardrails must not be empty")
    permissions = adaptation["required_permissions"]
    if not isinstance(permissions, list) or any(not isinstance(item, str) or not item for item in permissions):
        errors.append(f"{label}.required_permissions must contain strings")
    source = adaptation["source_evidence"]
    if _require(source, {"original_failure", "before", "after", "gate_decision", "live_cycle", "known_limitation"}, f"{label}.source_evidence", errors):
        for field, value in source.items():
            _nonempty(value, f"{label}.source_evidence.{field}", errors)
    provenance = adaptation["provenance"]
    if _require(provenance, {"source_proposal_id", "candidate_ref", "source_gate_id"}, f"{label}.provenance", errors):
        for field, value in provenance.items():
            _nonempty(value, f"{label}.provenance.{field}", errors)
    transfers = adaptation["transfer_results"]
    if not isinstance(transfers, list) or not transfers:
        errors.append(f"{label}.transfer_results must not be empty")
    else:
        seen_cases = set()
        for index, row in enumerate(transfers):
            row_label = f"{label}.transfer_results[{index}]"
            required = {
                "case_id", "mechanism_id", "candidate_ref", "project_shape",
                "activation_decision", "application_status", "completion_check_passed",
                "guardrails", "evidence",
            }
            if not _require(row, required, row_label, errors):
                continue
            case_id = row["case_id"]
            if case_id in seen_cases:
                errors.append(f"{row_label}.case_id is duplicated")
            seen_cases.add(case_id)
            if row["mechanism_id"] != adaptation["mechanism_id"] or row["candidate_ref"] != provenance.get("candidate_ref"):
                errors.append(f"{row_label} identity mismatch")
            expected = {
                "APPLY": ("applied", True),
                "SKIP": ("skipped", None),
            }.get(row["activation_decision"])
            if expected is None or (row["application_status"], row["completion_check_passed"]) != expected:
                errors.append(f"{row_label} has an invalid outcome")
            if not isinstance(row["guardrails"], dict) or not row["guardrails"] or any(
                value != "passed" for value in row["guardrails"].values()
            ):
                errors.append(f"{row_label} has failed guardrails")
    return errors


def _git_file(root, ref, path):
    result = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=root, capture_output=True)
    return result.stdout if result.returncode == 0 else None


def validate_evidence(preregistration, results, root=None, require_fresh_adoption=True):
    errors = []
    _reject_private(preregistration, errors, "preregistration")
    _reject_private(results, errors, "results")
    if not isinstance(preregistration, dict) or preregistration.get("schema_version") != 1:
        return ["preregistration must be a schema-version-1 object", *errors]
    if not isinstance(results, dict) or results.get("schema_version") != 1:
        return [*errors, "results must be a schema-version-1 object"]
    candidate = preregistration.get("personal_candidate", {})
    candidate_fields = {
        "adaptation_id", "title", "target_job", "mechanism_id", "mechanism",
        "source_scope", "source_evidence", "activation_conditions", "contraindications",
        "primary_metric", "guardrails", "required_permissions", "privacy_class",
        "provenance", "disable_condition", "conflicts_with", "candidate_author",
    }
    if not _require(candidate, candidate_fields, "personal_candidate", errors):
        return errors
    if not candidate.get("activation_conditions"):
        errors.append("personal_candidate.activation_conditions must not be empty")
    if candidate.get("privacy_class") != "generalized_bounded_evidence":
        errors.append("personal_candidate.privacy_class is invalid")
    if not isinstance(candidate.get("required_permissions"), list):
        errors.append("personal_candidate.required_permissions must be an array")
    approved = preregistration.get("approved_permissions")
    if not isinstance(approved, list):
        errors.append("approved_permissions must be an array")
        approved = []
    if isinstance(candidate.get("required_permissions"), list) and any(
        item not in approved for item in candidate["required_permissions"]
    ):
        errors.append("personal candidate expands permission without approval")
    claim = preregistration.get("transfer_preregistration", {})
    claim_fields = {
        "claim", "activation_conditions", "contraindications", "primary_metric",
        "guardrails", "falsification_condition", "candidate_ref", "candidate_sources",
        "holdout_case_ids",
    }
    if _require(claim, claim_fields, "transfer_preregistration", errors):
        for field in ("claim", "primary_metric", "falsification_condition", "candidate_ref"):
            _nonempty(claim[field], f"transfer_preregistration.{field}", errors)
        for field in ("activation_conditions", "contraindications", "guardrails", "holdout_case_ids"):
            if not isinstance(claim[field], list) or not claim[field]:
                errors.append(f"transfer_preregistration.{field} must not be empty")
        if claim.get("activation_conditions") != candidate.get("activation_conditions"):
            errors.append("transfer activation conditions do not match the candidate")
        if claim.get("contraindications") != candidate.get("contraindications"):
            errors.append("transfer contraindications do not match the candidate")
        if claim.get("candidate_ref") != candidate.get("provenance", {}).get("candidate_ref"):
            errors.append("candidate reference identity mismatch")
        if root is not None:
            for source in claim.get("candidate_sources", []):
                content = _git_file(root, claim["candidate_ref"], source.get("path"))
                digest = "sha256:" + hashlib.sha256(content).hexdigest() if content is not None else None
                if digest != source.get("sha256"):
                    errors.append(f"candidate source identity mismatch: {source.get('path')}")
            for case in preregistration.get("holdout_cases", []):
                if _git_file(root, claim["candidate_ref"], case.get("material_path")) is not None:
                    errors.append(f"holdout leakage at candidate snapshot: {case.get('case_id')}")
    prereg_cases = preregistration.get("holdout_cases")
    if not isinstance(prereg_cases, list) or len(prereg_cases) < 3:
        errors.append("representative transfer needs at least two positive shapes and one negative shape")
        prereg_cases = []
    prereg_by_id = {}
    for case in prereg_cases:
        case_id = case.get("case_id") if isinstance(case, dict) else None
        if not case_id or case_id in prereg_by_id:
            errors.append(f"holdout case id is missing or duplicated: {case_id}")
            continue
        prereg_by_id[case_id] = case
        if case.get("current_role") != "holdout" or case.get("unseen") is not True or case.get("exposure_count") != 0:
            errors.append(f"holdout case is already exposed: {case_id}")
        if case.get("role_at_run") != "holdout" or not isinstance(case.get("expected_activation"), bool):
            errors.append(f"holdout case contract is invalid: {case_id}")
    if claim and set(claim.get("holdout_case_ids", [])) != set(prereg_by_id):
        errors.append("preregistered holdout identity mismatch")
    result_rows = results.get("transfer_results")
    if not isinstance(result_rows, list):
        errors.append("transfer_results must be an array")
        result_rows = []
    result_by_id = {}
    all_transfer_passed = True
    for row in result_rows:
        case_id = row.get("case_id") if isinstance(row, dict) else None
        if not case_id or case_id in result_by_id:
            errors.append(f"transfer result is missing or duplicated: {case_id}")
            continue
        result_by_id[case_id] = row
        case = prereg_by_id.get(case_id, {})
        if (
            not case
            or row.get("role_at_run") != "holdout"
            or row.get("mechanism_id") != candidate.get("mechanism_id")
            or row.get("candidate_ref") != claim.get("candidate_ref")
        ):
            errors.append(f"transfer result identity mismatch: {case_id}")
            all_transfer_passed = False
            continue
        expected = "APPLY" if case.get("expected_activation") else "SKIP"
        if row.get("activation_decision") != expected:
            errors.append(f"transfer activation decision failed: {case_id}")
            all_transfer_passed = False
        if expected == "APPLY" and (
            row.get("application_status") != "applied"
            or row.get("completion_check_passed") is not True
        ):
            errors.append(f"positive transfer failed: {case_id}")
            all_transfer_passed = False
        if expected == "SKIP" and (
            row.get("application_status") != "skipped"
            or row.get("completion_check_passed") is not None
        ):
            errors.append(f"negative transfer did not skip: {case_id}")
            all_transfer_passed = False
        guardrails = row.get("guardrails")
        if not isinstance(guardrails, dict) or not guardrails or any(value != "passed" for value in guardrails.values()):
            errors.append(f"transfer guardrail failed: {case_id}")
            all_transfer_passed = False
    if set(result_by_id) != set(prereg_by_id):
        errors.append("failed or missing transfer result was hidden")
        all_transfer_passed = False
    exposure = results.get("exposure_updates")
    if not isinstance(exposure, list) or {row.get("case_id") for row in exposure if isinstance(row, dict)} != set(prereg_by_id):
        errors.append("used holdout exposure inventory is incomplete")
    else:
        for row in exposure:
            if row.get("current_role") != "retired" or row.get("unseen") is not False or row.get("exposure_count") != 1:
                errors.append(f"used holdout remains reusable: {row.get('case_id')}")
    gate = results.get("personal_gate", {})
    if not _require(gate, {"decision", "gate_agent", "candidate_author", "evidence", "established_scope"}, "personal_gate", errors):
        return errors
    if gate["decision"] not in VALID_DECISIONS:
        errors.append("personal gate decision is invalid")
    if gate["gate_agent"] == gate["candidate_author"] or gate["candidate_author"] != candidate.get("candidate_author"):
        errors.append("Personal Gate self-approval or author identity mismatch")
    if gate["decision"] in {"PERSONAL_PROMOTION", "NARROWER_PERSONAL_SCOPE"} and not all_transfer_passed:
        errors.append("Personal Gate promoted without complete transfer evidence")
    if gate["decision"] == "NARROWER_PERSONAL_SCOPE" and "universal" in str(gate["established_scope"]).lower():
        errors.append("narrower scope cannot be recorded as a universal personal rule")
    rejected = results.get("rejected_personal_candidates")
    if not isinstance(rejected, list) or not rejected:
        errors.append("rejected personal candidate inventory must not be empty")
    else:
        for index, row in enumerate(rejected):
            label = f"rejected_personal_candidates[{index}]"
            if _require(row, {"candidate_id", "mechanism_id", "source_claim_id", "decision", "reason"}, label, errors):
                if row["decision"] != "PERSONAL_REJECT":
                    errors.append(f"{label}.decision must be PERSONAL_REJECT")
                for field, value in row.items():
                    _nonempty(value, f"{label}.{field}", errors)
    adaptation = results.get("personal_adaptation")
    if gate["decision"] in {"PERSONAL_PROMOTION", "NARROWER_PERSONAL_SCOPE"}:
        errors.extend(validate_adaptation(adaptation, "personal_adaptation"))
        if isinstance(adaptation, dict):
            for field in candidate_fields - {
                "candidate_author", "activation_conditions", "contraindications",
            }:
                if field in {"source_evidence", "provenance"}:
                    continue
                if adaptation.get(field) != candidate.get(field):
                    errors.append(f"personal adaptation changed preregistered field: {field}")
            candidate_activation = set(candidate.get("activation_conditions", []))
            candidate_contraindications = set(candidate.get("contraindications", []))
            final_activation = set(adaptation.get("activation_conditions", []))
            final_contraindications = set(adaptation.get("contraindications", []))
            if gate["decision"] == "PERSONAL_PROMOTION" and (
                final_activation != candidate_activation
                or final_contraindications != candidate_contraindications
            ):
                errors.append("personal promotion changed preregistered activation boundary")
            if gate["decision"] == "NARROWER_PERSONAL_SCOPE" and (
                not candidate_activation <= final_activation
                or not candidate_contraindications <= final_contraindications
                or (candidate_activation == final_activation and candidate_contraindications == final_contraindications)
            ):
                errors.append("narrower personal scope must strictly narrow activation")
            if adaptation.get("source_evidence") != candidate.get("source_evidence") or adaptation.get("provenance") != candidate.get("provenance"):
                errors.append("personal adaptation source identity mismatch")
            if adaptation.get("promoted_by") != gate["gate_agent"]:
                errors.append("personal adaptation promotion owner mismatch")
            if adaptation.get("transfer_results") != result_rows:
                errors.append("personal adaptation transfer evidence mismatch")
            expected_status = "narrowed" if gate["decision"] == "NARROWER_PERSONAL_SCOPE" else "active"
            if adaptation.get("status") != expected_status:
                errors.append("personal adaptation status does not match Gate decision")
    elif adaptation is not None:
        errors.append("rejected personal candidate cannot create an adaptation")
    adoption = results.get("fresh_project_adoption", {})
    if require_fresh_adoption and gate["decision"] in {"PERSONAL_PROMOTION", "NARROWER_PERSONAL_SCOPE"}:
        required = {"project_shape", "adaptation_id", "inventory_discovered", "compatibility_check_passed", "applied", "completion_check_passed", "guardrails", "evidence"}
        if _require(adoption, required, "fresh_project_adoption", errors):
            if adoption.get("adaptation_id") != candidate.get("adaptation_id") or not all(
                adoption.get(field) is True for field in (
                    "inventory_discovered", "compatibility_check_passed", "applied", "completion_check_passed"
                )
            ):
                errors.append("fresh Project D did not verify personal reuse")
            if not isinstance(adoption.get("guardrails"), dict) or any(value != "passed" for value in adoption["guardrails"].values()):
                errors.append("fresh Project D guardrail failed")
    return errors


def validate_registry(payload):
    errors = []
    _reject_private(payload, errors)
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        return ["personal registry must be a schema-version-1 object", *errors]
    adaptations = payload.get("adaptations")
    if not isinstance(adaptations, list):
        return [*errors, "adaptations must be an array"]
    seen_ids = set()
    seen_identity = {}
    for index, adaptation in enumerate(adaptations):
        label = f"adaptations[{index}]"
        errors.extend(validate_adaptation(adaptation, label))
        adaptation_id = adaptation.get("adaptation_id") if isinstance(adaptation, dict) else None
        if adaptation_id in seen_ids:
            errors.append(f"duplicate adaptation id: {adaptation_id}")
        seen_ids.add(adaptation_id)
        identity = adaptation_identity(adaptation) if isinstance(adaptation, dict) else None
        if identity in seen_identity:
            errors.append(f"duplicate adaptation identity: {adaptation_id}")
        seen_identity[identity] = adaptation_id
    return errors


def _registry_path(home):
    if home is None:
        raise PersonalEvolutionError("PERSONAL_HOME_REQUIRED")
    root = Path(home)
    if root.is_symlink() or not root.is_dir():
        raise PersonalEvolutionError("PERSONAL_HOME_REQUIRED: select and create the directory with user approval")
    target = root / REGISTRY_NAME
    if target.is_symlink():
        raise PersonalEvolutionError("personal registry must not be a symlink")
    return target


def load_registry(home):
    path = _registry_path(home)
    if not path.exists():
        return {"schema_version": 1, "adaptations": []}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise PersonalEvolutionError(f"cannot read personal registry: {error}") from error
    errors = validate_registry(payload)
    if errors:
        raise PersonalEvolutionError("; ".join(errors))
    return payload


def _atomic_write(path, payload):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        temporary = Path(handle.name)
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def promote(home, preregistration, results, root=None):
    errors = validate_evidence(preregistration, results, root, require_fresh_adoption=False)
    if errors:
        raise PersonalEvolutionError("; ".join(errors))
    gate = results["personal_gate"]
    if gate["decision"] not in {"PERSONAL_PROMOTION", "NARROWER_PERSONAL_SCOPE"}:
        raise PersonalEvolutionError(f"personal candidate is not promotable: {gate['decision']}")
    path = _registry_path(home)
    registry = load_registry(home)
    adaptation = results["personal_adaptation"]
    identity = adaptation_identity(adaptation)
    existing = next((item for item in registry["adaptations"] if adaptation_identity(item) == identity), None)
    if existing is None:
        registry["adaptations"].append(adaptation)
        action = "promoted"
    else:
        if existing["adaptation_id"] != adaptation["adaptation_id"]:
            raise PersonalEvolutionError("duplicate adaptation identity uses a different id")
        by_case = {row["case_id"]: row for row in existing["transfer_results"]}
        by_case.update({row["case_id"]: row for row in adaptation["transfer_results"]})
        existing["transfer_results"] = list(by_case.values())
        existing["tested_project_shapes"] = sorted(set(existing["tested_project_shapes"] + adaptation["tested_project_shapes"]))
        action = "merged"
    errors = validate_registry(registry)
    if errors:
        raise PersonalEvolutionError("; ".join(errors))
    _atomic_write(path, registry)
    return {"status": action, "adaptation_id": adaptation["adaptation_id"], "registry": str(path.name)}


def discover(home, facts):
    registry = load_registry(home)
    if not isinstance(facts, dict) or facts.get("schema_version") != 1:
        raise PersonalEvolutionError("project facts must be a schema-version-1 object")
    conditions = facts.get("conditions")
    approved = facts.get("approved_permissions")
    if not isinstance(conditions, list) or any(item not in ALLOWED_CONDITIONS for item in conditions):
        raise PersonalEvolutionError("project facts contain unsupported conditions")
    if not isinstance(approved, list):
        raise PersonalEvolutionError("project facts approved_permissions must be an array")
    condition_set = set(conditions)
    applicable = []
    skipped = []
    for adaptation in registry["adaptations"]:
        if adaptation["status"] not in ACTIVE_STATUSES:
            skipped.append({"adaptation_id": adaptation["adaptation_id"], "reason": adaptation["status"]})
            continue
        if not set(adaptation["activation_conditions"]) <= condition_set or set(adaptation["contraindications"]) & condition_set:
            skipped.append({"adaptation_id": adaptation["adaptation_id"], "reason": "conditions_not_met"})
            continue
        if any(permission not in approved for permission in adaptation["required_permissions"]):
            skipped.append({"adaptation_id": adaptation["adaptation_id"], "reason": "permission_blocked"})
            continue
        applicable.append(adaptation)
    ids = {item["adaptation_id"] for item in applicable}
    conflicts = sorted({
        tuple(sorted((item["adaptation_id"], conflict)))
        for item in applicable for conflict in item["conflicts_with"] if conflict in ids
    })
    if conflicts:
        return {"status": "CONFLICT_REQUIRES_RESOLUTION", "applicable": [], "skipped": skipped, "conflicts": conflicts}
    return {"status": "APPLY" if applicable else "SKIP", "applicable": [item["adaptation_id"] for item in applicable], "skipped": skipped, "conflicts": []}


def revoke(home, adaptation_id, reason, revoked_at):
    path = _registry_path(home)
    registry = load_registry(home)
    adaptation = next((item for item in registry["adaptations"] if item["adaptation_id"] == adaptation_id), None)
    if adaptation is None:
        raise PersonalEvolutionError("adaptation not found")
    adaptation.update(status="revoked", revocation_reason=reason, revoked_at=revoked_at)
    _atomic_write(path, registry)
    return {"status": "revoked", "adaptation_id": adaptation_id}


def _read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate_parser = subparsers.add_parser("validate-evidence")
    validate_parser.add_argument("preregistration", type=Path)
    validate_parser.add_argument("results", type=Path)
    validate_parser.add_argument("--root", type=Path, default=Path.cwd())
    registry_parser = subparsers.add_parser("validate-home")
    registry_parser.add_argument("--home", type=Path)
    promote_parser = subparsers.add_parser("promote")
    promote_parser.add_argument("preregistration", type=Path)
    promote_parser.add_argument("results", type=Path)
    promote_parser.add_argument("--home", type=Path)
    promote_parser.add_argument("--root", type=Path, default=Path.cwd())
    discover_parser = subparsers.add_parser("discover")
    discover_parser.add_argument("facts", type=Path)
    discover_parser.add_argument("--home", type=Path)
    revoke_parser = subparsers.add_parser("revoke")
    revoke_parser.add_argument("adaptation_id")
    revoke_parser.add_argument("--reason", required=True)
    revoke_parser.add_argument("--revoked-at", required=True)
    revoke_parser.add_argument("--home", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "validate-evidence":
            errors = validate_evidence(_read(args.preregistration), _read(args.results), args.root)
            output = {"valid": not errors, "errors": errors}
        elif args.command == "validate-home":
            errors = validate_registry(load_registry(args.home))
            output = {"valid": not errors, "errors": errors}
        elif args.command == "promote":
            output = promote(args.home, _read(args.preregistration), _read(args.results), args.root)
        elif args.command == "discover":
            output = discover(args.home, _read(args.facts))
        else:
            output = revoke(args.home, args.adaptation_id, args.reason, args.revoked_at)
        failed = bool(output.get("errors"))
    except (OSError, UnicodeError, json.JSONDecodeError, PersonalEvolutionError) as error:
        output = {"valid": False, "errors": [str(error)]}
        failed = True
    print(json.dumps(output, ensure_ascii=False, indent=2))
    raise SystemExit(failed)


if __name__ == "__main__":
    main()
