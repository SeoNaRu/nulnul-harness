#!/usr/bin/env python3
"""Validate bounded cross-project evidence and measure flat personal lookup."""

import argparse
import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))
import personal_adaptation


RELATIONS = {"COMPLEMENTS", "CONFLICTS", "SUPERSEDES", "REQUIRES", "ALTERNATIVE", "UNRELATED", "UNKNOWN"}
ACTIVE = {"active", "narrowed"}
ADAPTATION_FIELDS = {
    "adaptation_id", "mechanism_family", "target_job", "activation_conditions",
    "contraindications", "tested_project_shapes", "positive_transfer_count",
    "negative_skip_count", "failed_transfer_count", "narrowed_scope_count",
    "source_evidence_identity", "guardrails", "permission_requirements",
    "privacy_class", "compatibility_requirements", "known_conflicts",
    "known_complements", "cost_evaluation_summary", "freshness", "status",
}


def validate_evidence(payload):
    errors = []
    personal_adaptation._reject_private(payload, errors, "cross_project_evidence")
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        return ["cross-project evidence must be a schema-version-1 object", *errors]
    adaptations = payload.get("adaptations")
    if not isinstance(adaptations, list):
        return [*errors, "adaptations must be an array"]
    ids = set()
    families = set()
    for index, row in enumerate(adaptations):
        label = f"adaptations[{index}]"
        if not isinstance(row, dict) or not ADAPTATION_FIELDS <= row.keys():
            errors.append(f"{label} is incomplete")
            continue
        adaptation_id = row["adaptation_id"]
        family = row["mechanism_family"]
        if not isinstance(adaptation_id, str) or not adaptation_id or adaptation_id in ids:
            errors.append(f"{label}.adaptation_id is missing or duplicated")
        if not isinstance(family, str) or not family:
            errors.append(f"{label}.mechanism_family must be non-empty")
        ids.add(adaptation_id)
        families.add(family)
        for field in ("positive_transfer_count", "negative_skip_count", "failed_transfer_count", "narrowed_scope_count"):
            if isinstance(row[field], bool) or not isinstance(row[field], int) or row[field] < 0:
                errors.append(f"{label}.{field} must be a non-negative integer")
        if row["privacy_class"] != "generalized_bounded_evidence":
            errors.append(f"{label}.privacy_class is invalid")
        if row["status"] not in personal_adaptation.ALL_STATUSES:
            errors.append(f"{label}.status is invalid")
        for field in ("activation_conditions", "contraindications", "tested_project_shapes", "guardrails", "permission_requirements", "compatibility_requirements", "known_conflicts", "known_complements"):
            if not isinstance(row[field], list):
                errors.append(f"{label}.{field} must be an array")
        if not isinstance(row["source_evidence_identity"], dict) or not row["source_evidence_identity"]:
            errors.append(f"{label}.source_evidence_identity must be non-empty")
        freshness = row["freshness"]
        if not isinstance(freshness, dict) or freshness.get("evidence_status") not in {"current", "stale", "revoked"}:
            errors.append(f"{label}.freshness is invalid")
    relations = payload.get("relations")
    if not isinstance(relations, list):
        errors.append("relations must be an array")
        relations = []
    seen_relations = set()
    for index, row in enumerate(relations):
        label = f"relations[{index}]"
        required = {"source", "target", "type", "evidence", "reason", "scope"}
        if not isinstance(row, dict) or not required <= row.keys():
            errors.append(f"{label} is incomplete")
            continue
        identity = (row["source"], row["target"])
        if row["source"] not in ids or row["target"] not in ids or row["source"] == row["target"]:
            errors.append(f"{label} has invalid endpoints")
        if identity in seen_relations or tuple(reversed(identity)) in seen_relations:
            errors.append(f"{label} duplicates an adaptation pair")
        seen_relations.add(identity)
        if row["type"] not in RELATIONS:
            errors.append(f"{label}.type is invalid")
        for field in ("evidence", "reason", "scope"):
            if not isinstance(row[field], str) or not row[field].strip():
                errors.append(f"{label}.{field} must be non-empty")
    entry = payload.get("entry_gate", {})
    decision = "PASS" if len(families) >= 3 else "INSUFFICIENT_CROSS_PROJECT_EVIDENCE"
    if entry.get("decision") != decision or entry.get("independent_family_count") != len(families):
        errors.append("entry gate does not match independent mechanism families")
    if payload.get("raw_project_data_included") is not False:
        errors.append("raw project data must be explicitly absent")
    return errors


def _facts(facts):
    if not isinstance(facts, dict) or facts.get("schema_version") != 1:
        raise ValueError("project facts must be a schema-version-1 object")
    conditions = facts.get("conditions")
    permissions = facts.get("approved_permissions")
    if not isinstance(conditions, list) or any(item not in personal_adaptation.ALLOWED_CONDITIONS for item in conditions):
        raise ValueError("project facts contain unsupported conditions")
    if not isinstance(permissions, list):
        raise ValueError("approved_permissions must be an array")
    return set(conditions), set(permissions)


def _finish(payload, selected, considered, checks, skipped):
    selected_ids = {row["adaptation_id"] for row in selected}
    conflicts = sorted(
        sorted((row["source"], row["target"]))
        for row in payload["relations"]
        if row["type"] == "CONFLICTS" and {row["source"], row["target"]} <= selected_ids
    )
    if conflicts:
        status = "META_CONFLICT"
        selected_ids = set()
    else:
        status = "APPLY" if selected_ids else "NO_RELEVANT_ADAPTATION"
    return {
        "status": status,
        "selected": sorted(selected_ids),
        "adaptations_considered": considered,
        "compatibility_checks_executed": checks,
        "skipped": skipped,
        "conflicts": conflicts,
    }


def lookup(payload, facts, simple=False):
    errors = validate_evidence(payload)
    if errors:
        raise ValueError("; ".join(errors))
    conditions, permissions = _facts(facts)
    selected = []
    skipped = []
    checks = 0
    for row in payload["adaptations"]:
        if simple and row["status"] not in ACTIVE:
            skipped.append({"adaptation_id": row["adaptation_id"], "reason": row["status"]})
            continue
        if simple and any(permission not in permissions for permission in row["permission_requirements"]):
            skipped.append({"adaptation_id": row["adaptation_id"], "reason": "permission_blocked"})
            continue
        checks += 1
        if row["status"] not in ACTIVE:
            skipped.append({"adaptation_id": row["adaptation_id"], "reason": row["status"]})
        elif any(permission not in permissions for permission in row["permission_requirements"]):
            skipped.append({"adaptation_id": row["adaptation_id"], "reason": "permission_blocked"})
        elif not set(row["activation_conditions"]) <= conditions or set(row["contraindications"]) & conditions:
            skipped.append({"adaptation_id": row["adaptation_id"], "reason": "conditions_not_met"})
        else:
            selected.append(row)
    return _finish(payload, selected, len(payload["adaptations"]), checks, skipped)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--facts", type=Path)
    parser.add_argument("--simple", action="store_true")
    args = parser.parse_args()
    payload = json.loads(args.evidence.read_text(encoding="utf-8"))
    if args.facts:
        output = lookup(payload, json.loads(args.facts.read_text(encoding="utf-8")), args.simple)
    else:
        errors = validate_evidence(payload)
        output = {"valid": not errors, "errors": errors}
    print(json.dumps(output, ensure_ascii=False, indent=2))
    raise SystemExit(bool(output.get("errors")))


if __name__ == "__main__":
    main()
