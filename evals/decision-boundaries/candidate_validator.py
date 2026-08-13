#!/usr/bin/env python3
"""Archived validator for the rejected scoped-decision candidate."""

import argparse
import json
from pathlib import Path


LAYERS = {
    "design.component_shape",
    "design.visual_tone",
    "frontend.architecture",
    "backend.architecture",
}
STATUSES = {"absent", "undecided", "accepted", "working", "insufficient", "invalid"}
SOURCES = {"none", "current_user", "project", "approved_personal", "external_capability", "outcome_fit"}
BASIS_KINDS = {
    "accepted_contract",
    "approved_preference",
    "observed_failure",
    "explicit_user_request",
    "required_dependency",
    "measurable_incompatibility",
    "migration_benefit",
    "outcome_fit",
}
ROOT_FIELDS = {
    "schema_version", "decision_id", "target", "required_layers", "decisions",
    "capabilities_used", "personal_sources_read", "unrelated_personal_reads",
    "permission_delta",
}
DECISION_FIELDS = {"layer", "current", "action", "proposed", "basis"}
CURRENT_FIELDS = {"status", "source", "value"}
BASIS_FIELDS = {"kind", "source", "evidence", "depends_on"}
EXISTING_CHANGE_KINDS = {
    "observed_failure", "explicit_user_request", "required_dependency",
    "measurable_incompatibility", "migration_benefit",
}


def validate(payload, required_layers=()):
    errors = []

    def exact_fields(value, fields, label):
        if not isinstance(value, dict):
            errors.append(f"{label} must be an object")
            return False
        missing = sorted(fields - value.keys())
        extra = sorted(value.keys() - fields)
        if missing:
            errors.append(f"{label} missing: {', '.join(missing)}")
        if extra:
            errors.append(f"{label} fields are not allowed: {', '.join(extra)}")
        return not missing and not extra

    if not exact_fields(payload, ROOT_FIELDS, "root"):
        return errors
    if payload["schema_version"] != 1:
        errors.append("schema_version must be 1")
    for field in ("decision_id", "target"):
        if not isinstance(payload[field], str) or not payload[field].strip():
            errors.append(f"{field} must be non-empty")

    declared = payload["required_layers"]
    if not isinstance(declared, list) or not declared:
        errors.append("required_layers must be a non-empty array")
        declared = []
    elif len(declared) != len(set(declared)):
        errors.append("required_layers must be unique")
    unsupported = sorted(set(declared) - LAYERS)
    if unsupported:
        errors.append("unsupported required layer: " + ", ".join(unsupported))
    missing_required = sorted(set(required_layers) - set(declared))
    if missing_required:
        errors.append("required layer missing: " + ", ".join(missing_required))

    decisions = payload["decisions"]
    if not isinstance(decisions, list):
        errors.append("decisions must be an array")
        decisions = []
    by_layer = {}
    for index, decision in enumerate(decisions):
        label = f"decisions[{index}]"
        if not exact_fields(decision, DECISION_FIELDS, label):
            continue
        layer = decision["layer"]
        if layer not in LAYERS:
            errors.append(f"{label}.layer is unsupported")
            continue
        if layer in by_layer:
            errors.append(f"decision layer is duplicated: {layer}")
        by_layer[layer] = decision
        current = decision["current"]
        basis = decision["basis"]
        if not exact_fields(current, CURRENT_FIELDS, f"{label}.current"):
            continue
        if not exact_fields(basis, BASIS_FIELDS, f"{label}.basis"):
            continue
        status = current["status"]
        source = current["source"]
        value = current["value"]
        kind = basis["kind"]
        basis_source = basis["source"]
        evidence = basis["evidence"]
        dependency = basis["depends_on"]
        action = decision["action"]
        proposed = decision["proposed"]

        if status not in STATUSES:
            errors.append(f"{label}.current.status is invalid")
        if source not in SOURCES:
            errors.append(f"{label}.current.source is invalid")
        if kind not in BASIS_KINDS:
            errors.append(f"{label}.basis.kind is invalid")
        if basis_source not in SOURCES:
            errors.append(f"{label}.basis.source is invalid")
        if not isinstance(evidence, str) or not evidence.strip():
            errors.append(f"{label}.basis.evidence must be non-empty")
        if dependency is not None and dependency not in LAYERS:
            errors.append(f"{label}.basis.depends_on is unsupported")
        if status in {"accepted", "working", "insufficient", "invalid"} and (
            not isinstance(value, str) or not value.strip()
        ):
            errors.append(f"{label}.current.value must describe the existing decision")

        if action == "preserve":
            if status not in {"accepted", "working"}:
                errors.append(f"{label} cannot preserve a non-established layer")
            if proposed != value:
                errors.append(f"{label} preserve must keep the current value")
            if kind != "accepted_contract" or basis_source != source:
                errors.append(f"{label} preserve must cite the current accepted contract")
            if dependency is not None:
                errors.append(f"{label} preserve cannot depend on another changed layer")
        elif action == "change":
            if not isinstance(proposed, str) or not proposed.strip() or proposed == value:
                errors.append(f"{label} change needs a different non-empty proposed value")
            if status in {"accepted", "working"} and kind not in EXISTING_CHANGE_KINDS:
                errors.append(f"{label} changes an established layer without independent justification")
            if status == "accepted" and source == "project" and basis_source in {
                "approved_personal", "external_capability"
            }:
                errors.append(f"{label} lets lower-scope guidance override an accepted project decision")
            if kind == "approved_preference" and not (
                layer.startswith("design.")
                and status in {"absent", "undecided"}
                and basis_source == "approved_personal"
            ):
                errors.append(f"{label} applies a personal preference outside undecided design scope")
            if kind == "required_dependency":
                if dependency is None or dependency == layer:
                    errors.append(f"{label} required dependency must name another layer")
            elif dependency is not None:
                errors.append(f"{label} dependency is allowed only for required_dependency")
        else:
            errors.append(f"{label}.action must be preserve or change")

    if set(by_layer) != set(declared):
        errors.append("decisions must match required_layers exactly")
    for layer, decision in by_layer.items():
        dependency = decision.get("basis", {}).get("depends_on")
        if dependency is not None and (
            dependency not in by_layer or by_layer[dependency].get("action") != "change"
        ):
            errors.append(f"{layer} depends on a layer that is not changing")

    capabilities = payload["capabilities_used"]
    if not isinstance(capabilities, list) or any(
        not isinstance(item, str) or not item for item in capabilities
    ):
        errors.append("capabilities_used must contain non-empty strings")
    for field in ("personal_sources_read", "unrelated_personal_reads"):
        if isinstance(payload[field], bool) or not isinstance(payload[field], int) or payload[field] < 0:
            errors.append(f"{field} must be an integer >= 0")
    if payload["permission_delta"] != []:
        errors.append("permission_delta must remain empty")
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--require-layer", action="append", default=[])
    args = parser.parse_args()
    try:
        payload = json.loads(args.artifact.read_text(encoding="utf-8"))
        errors = validate(payload, args.require_layer)
    except (OSError, json.JSONDecodeError) as error:
        errors = [f"cannot read decision artifact: {error}"]
    print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()
