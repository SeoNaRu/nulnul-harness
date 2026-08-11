#!/usr/bin/env python3
"""Validate a concise NULNUL resume checkpoint."""

import argparse
import json
from pathlib import Path


TEXT_FIELDS = ("goal", "milestone", "completion_check", "last_verified", "next_action")
LIST_FIELDS = ("approved_permissions", "blockers")


def validate(payload):
    if not isinstance(payload, dict):
        return ["checkpoint must be an object"]
    errors = []
    if payload.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    for field in TEXT_FIELDS:
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{field} must be a non-empty string")
    for field in LIST_FIELDS:
        value = payload.get(field)
        if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
            errors.append(f"{field} must be an array of non-empty strings")
    prohibited = {"secret", "secrets", "credential", "credentials", "api_key", "token"}
    for key in payload:
        if key.lower() in prohibited:
            errors.append(f"prohibited sensitive field: {key}")
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("checkpoint", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.checkpoint.read_text(encoding="utf-8"))
        errors = validate(payload)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        errors = [f"cannot read checkpoint: {error}"]
    print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()
