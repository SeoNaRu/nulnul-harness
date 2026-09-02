#!/usr/bin/env python3
"""Validate and resolve bounded evolvable Harness control policies."""

import hashlib
import json
import re
from pathlib import Path


SCHEMA_VERSION = 1
STATUSES = {"CURRENT", "CHALLENGER", "SUPERSEDED", "RETIRED"}
CONTROL_FIELDS = {
    "control_id", "job", "current_version", "current_digest", "status",
    "attribution_class",
    "input_contract", "output_contract", "allowed_effects", "forbidden_effects",
    "evidence_signals", "verification_contract", "rollback_contract",
    "dependencies", "policy_schema", "policy",
}
ATTRIBUTION_CLASSES = {
    "HARNESS_SELECTION_POLICY", "HARNESS_CONTEXT_POLICY", "HARNESS_AGENT_POLICY",
    "HARNESS_VERIFICATION_POLICY", "HARNESS_MEMORY_POLICY",
}
REQUIRED_KERNEL = {
    "stable-identity", "provenance-integrity", "atomic-single-writer",
    "rollback", "evidence-integrity", "raw-transcript-privacy",
    "authority-separation", "lifecycle-history", "check-receipt-integrity",
    "champion-challenger-separation", "deterministic-promotion",
    "bounded-context-hard-limits",
}
KERNEL_FORBIDDEN_EFFECTS = {
    "forge_identity", "rewrite_provenance", "bypass_atomic_writer",
    "disable_rollback", "alter_source_evidence", "include_raw_transcript",
    "broaden_authority", "mutate_host_trust", "rewrite_lifecycle_history",
    "disable_authoritative_check", "self_promote", "raise_context_hard_limits",
}


def canonical_digest(payload):
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def paths(root):
    root = Path(root).resolve()
    nulnul = root / "docs/nulnul"
    return {
        "shipped": Path(__file__).resolve().parents[1] / "assets/harness-controls.json",
        "current": nulnul / "harness-controls.json",
        "history": nulnul / "memory/harness-controls",
    }


def _strings(value, field, *, required=True, maximum=32):
    if not isinstance(value, list) or len(value) > maximum or any(
        not isinstance(item, str) or not item.strip() or len(item.encode()) > 512
        for item in value
    ):
        raise ValueError(f"Harness control {field} must be a bounded string list")
    result = list(dict.fromkeys(item.strip() for item in value))
    if required and not result:
        raise ValueError(f"Harness control {field} cannot be empty")
    return result


def _text(value, field, maximum=2048):
    if not isinstance(value, str) or not value.strip() or len(value.encode()) > maximum:
        raise ValueError(f"Harness control {field} must be one bounded string")
    return value.strip()


def _validate_policy_value(name, value, contract):
    kind = contract.get("type")
    if kind == "integer":
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"Harness control policy {name} must be an integer")
        if value < contract.get("minimum", value) or value > contract.get("maximum", value):
            raise ValueError(f"Harness control policy {name} exceeds its guarded bounds")
    elif kind == "number":
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"Harness control policy {name} must be numeric")
        if value < contract.get("minimum", value) or value > contract.get("maximum", value):
            raise ValueError(f"Harness control policy {name} exceeds its guarded bounds")
    elif kind == "boolean":
        if not isinstance(value, bool):
            raise ValueError(f"Harness control policy {name} must be boolean")
    elif kind == "enum":
        if value not in contract.get("values", []):
            raise ValueError(f"Harness control policy {name} is outside its allowed values")
    else:
        raise ValueError(f"Harness control policy {name} has an unsupported schema")


def control_digest(record):
    return canonical_digest({
        key: record[key]
        for key in sorted(CONTROL_FIELDS - {"current_digest", "status"})
    })


def validate_control(record, *, statuses=STATUSES):
    if not isinstance(record, dict) or set(record) != CONTROL_FIELDS:
        raise ValueError("Harness control contract is incomplete")
    if not re.fullmatch(r"control-[a-z0-9][a-z0-9-]{1,63}", str(record.get("control_id", ""))):
        raise ValueError("invalid Harness CONTROL_ID")
    _text(record.get("job"), "job")
    version = record.get("current_version")
    if not isinstance(version, int) or version < 1:
        raise ValueError("Harness control version must be positive")
    if record.get("status") not in statuses:
        raise ValueError("invalid Harness control status")
    if record.get("attribution_class") not in ATTRIBUTION_CLASSES:
        raise ValueError("invalid Harness control attribution class")
    for field in (
        "input_contract", "output_contract", "allowed_effects", "forbidden_effects",
        "evidence_signals", "verification_contract", "rollback_contract",
    ):
        _strings(record.get(field), field)
    _strings(record.get("dependencies"), "dependencies", required=False)
    allowed = set(record["allowed_effects"])
    forbidden = set(record["forbidden_effects"])
    if allowed & forbidden or not KERNEL_FORBIDDEN_EFFECTS <= forbidden:
        raise ValueError("Harness control effects violate guarded Kernel boundaries")
    schema, policy = record.get("policy_schema"), record.get("policy")
    if not isinstance(schema, dict) or not schema or not isinstance(policy, dict) or set(schema) != set(policy):
        raise ValueError("Harness control policy must exactly match its bounded schema")
    for name, contract in schema.items():
        if not re.fullmatch(r"[a-z][a-z0-9_]{0,63}", str(name)) or not isinstance(contract, dict):
            raise ValueError("invalid Harness control policy field")
        _validate_policy_value(name, policy[name], contract)
    if record["control_id"] == "control-memory-promotion" and policy.get("require_verified") is not True:
        raise ValueError("Harness policy cannot promote unverified Memory")
    if record.get("current_digest") != control_digest(record):
        raise ValueError("Harness control digest is invalid")
    return record


def _registry_unsigned(registry):
    return {key: value for key, value in registry.items() if key != "registry_digest"}


def validate_registry(registry):
    if (
        not isinstance(registry, dict)
        or set(registry) != {"schema_version", "guarded_kernel", "kernel_digest", "controls", "registry_digest"}
        or registry.get("schema_version") != SCHEMA_VERSION
    ):
        raise ValueError("invalid Harness control registry schema")
    kernel = registry.get("guarded_kernel")
    if not isinstance(kernel, list) or len(kernel) != len(REQUIRED_KERNEL):
        raise ValueError("guarded Kernel inventory is incomplete")
    seen = set()
    for row in kernel:
        if not isinstance(row, dict) or set(row) != {
            "invariant_id", "behavior", "implementation_refs", "validator"
        }:
            raise ValueError("guarded Kernel invariant is incomplete")
        identity = row.get("invariant_id")
        if identity in seen:
            raise ValueError("duplicate guarded Kernel invariant")
        seen.add(identity)
        _text(row.get("behavior"), "Kernel behavior")
        _strings(row.get("implementation_refs"), "Kernel implementation refs")
        _text(row.get("validator"), "Kernel validator")
    if seen != REQUIRED_KERNEL:
        raise ValueError("guarded Kernel inventory does not match the required invariants")
    if registry.get("kernel_digest") != canonical_digest(kernel):
        raise ValueError("guarded Kernel digest is invalid")
    controls = registry.get("controls")
    if not isinstance(controls, list) or not controls:
        raise ValueError("Harness control registry is empty")
    by_id = {}
    for row in controls:
        validate_control(row)
        if row["control_id"] in by_id:
            raise ValueError("duplicate Harness CONTROL_ID")
        by_id[row["control_id"]] = row
    for row in controls:
        for dependency in row["dependencies"]:
            if dependency not in by_id or by_id[dependency]["status"] != "CURRENT":
                raise ValueError("Harness control has an unknown or noncurrent dependency")
    if registry.get("registry_digest") != canonical_digest(_registry_unsigned(registry)):
        raise ValueError("Harness control registry digest is invalid")
    return registry


def read_registry(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError("Harness control registry must be one regular file")
    return validate_registry(json.loads(path.read_text(encoding="utf-8")))


def validate_runtime_bindings(registry, baseline, *, allow_challenger=False):
    """Keep every shipped runtime slot resolvable under its compiled policy schema."""
    current = {
        row["control_id"]: row for row in registry["controls"]
        if row["status"] == "CURRENT" or (allow_challenger and row["status"] == "CHALLENGER")
    }
    for expected in baseline["controls"]:
        if expected["status"] != "CURRENT":
            continue
        actual = current.get(expected["control_id"])
        if not actual:
            raise ValueError("Harness registry retired a control still required by the runtime")
        if (
            actual["policy_schema"] != expected["policy_schema"]
            or actual["attribution_class"] != expected["attribution_class"]
        ):
            raise ValueError("Harness control changed its compiled runtime contract")
    return registry


def shipped_registry():
    registry = read_registry(paths(Path.cwd())["shipped"])
    return validate_runtime_bindings(registry, registry)


def current_registry(root):
    current = paths(root)["current"]
    if not current.exists():
        return shipped_registry()
    registry = read_registry(current)
    baseline = shipped_registry()
    if registry["kernel_digest"] != baseline["kernel_digest"]:
        raise ValueError("project Harness policy cannot change the guarded Kernel")
    return validate_runtime_bindings(registry, baseline)


def current_control(root, control_id):
    matches = [
        row for row in current_registry(root)["controls"]
        if row["control_id"] == control_id and row["status"] == "CURRENT"
    ]
    if len(matches) != 1:
        raise ValueError("Harness control is not uniquely current")
    return matches[0]


def project_policy(root, control_id, defaults):
    """Resolve a promoted policy; absence returns compiled defaults without reading the registry."""
    if not paths(root)["current"].exists():
        return dict(defaults), False
    return dict(current_control(root, control_id)["policy"]), True


def with_digests(registry):
    """Bind runtime-owned digests to a newly assembled registry."""
    registry = json.loads(json.dumps(registry))
    registry["kernel_digest"] = canonical_digest(registry["guarded_kernel"])
    for row in registry["controls"]:
        row["current_digest"] = control_digest(row)
    registry["registry_digest"] = canonical_digest(_registry_unsigned(registry))
    return validate_registry(registry)
