#!/usr/bin/env python3
"""Validate a concise NULNUL resume checkpoint."""

import argparse
import json
import re
from pathlib import Path


TEXT_FIELDS = ("goal", "milestone", "completion_check", "last_verified", "next_action")
LEGACY_LIST_FIELDS = ("approved_permissions", "blockers")
V2_LIST_FIELDS = ("permission_constraints",) + LEGACY_LIST_FIELDS
VERIFICATION_STATUSES = {"verified", "failed", "unknown"}
RESULT_DESCRIPTION = re.compile(r"(?:,\s*and\b|\bpasses?\b|\breports?\s+(?:ok|valid)\b)", re.IGNORECASE)


def validate(payload):
    if not isinstance(payload, dict):
        return ["checkpoint must be an object"]
    errors = []
    version = payload.get("schema_version")
    if version not in {1, 2}:
        errors.append("schema_version must be 1 or 2")
        return errors
    if version == 2 and payload.get("verification_status") not in VERIFICATION_STATUSES:
        errors.append("verification_status must be verified, failed, or unknown")
    for field in TEXT_FIELDS:
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{field} must be a non-empty string")
    completion = payload.get("completion_check")
    if version == 2 and isinstance(completion, str) and RESULT_DESCRIPTION.search(completion):
        errors.append("completion_check must be an exact command, not a result description")
    for field in V2_LIST_FIELDS if version == 2 else LEGACY_LIST_FIELDS:
        value = payload.get(field)
        if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
            errors.append(f"{field} must be an array of non-empty strings")
    prohibited = {"secret", "secrets", "credential", "credentials", "api_key", "token"}
    for key in payload:
        if key.lower() in prohibited:
            errors.append(f"prohibited sensitive field: {key}")
    return errors


def fast_path_ready(payload):
    return (
        not validate(payload)
        and payload["schema_version"] == 2
        and payload["verification_status"] == "verified"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("checkpoint", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.checkpoint.read_text(encoding="utf-8"))
        errors = validate(payload)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        errors = [f"cannot read checkpoint: {error}"]
    print(json.dumps({
        "valid": not errors,
        "fast_path_ready": not errors and fast_path_ready(payload),
        "errors": errors,
    }, ensure_ascii=False, indent=2))
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()
