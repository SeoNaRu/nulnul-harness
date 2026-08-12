#!/usr/bin/env python3
"""Validate a concise NULNUL resume checkpoint."""

import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath


TEXT_FIELDS = ("goal", "milestone", "completion_check", "last_verified", "next_action")
LEGACY_LIST_FIELDS = ("approved_permissions", "blockers")
V2_LIST_FIELDS = ("permission_constraints",) + LEGACY_LIST_FIELDS
V3_LIST_FIELDS = V2_LIST_FIELDS + ("verification_files",)
VERIFICATION_STATUSES = {"verified", "failed", "unknown"}
RESULT_DESCRIPTION = re.compile(r"(?:,\s*and\b|\bpasses?\b|\breports?\s+(?:ok|valid)\b)", re.IGNORECASE)
FINGERPRINT = re.compile(r"sha256:[0-9a-f]{64}")


def validate(payload):
    if not isinstance(payload, dict):
        return ["checkpoint must be an object"]
    errors = []
    version = payload.get("schema_version")
    if version not in {1, 2, 3}:
        errors.append("schema_version must be 1, 2, or 3")
        return errors
    if version >= 2 and payload.get("verification_status") not in VERIFICATION_STATUSES:
        errors.append("verification_status must be verified, failed, or unknown")
    for field in TEXT_FIELDS:
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{field} must be a non-empty string")
    completion = payload.get("completion_check")
    if version >= 2 and isinstance(completion, str) and RESULT_DESCRIPTION.search(completion):
        errors.append("completion_check must be an exact command, not a result description")
    list_fields = V3_LIST_FIELDS if version == 3 else V2_LIST_FIELDS if version == 2 else LEGACY_LIST_FIELDS
    for field in list_fields:
        value = payload.get(field)
        if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
            errors.append(f"{field} must be an array of non-empty strings")
    if version == 3:
        files = payload.get("verification_files")
        if isinstance(files, list):
            invalid = [item for item in files if isinstance(item, str) and not valid_relative_path(item)]
            if invalid:
                errors.append("verification_files must contain normalized relative file paths")
            if len(files) != len(set(files)):
                errors.append("verification_files must not contain duplicates")
            if payload.get("verification_status") == "verified" and not files:
                errors.append("verified checkpoints require verification_files")
    prohibited = {"secret", "secrets", "credential", "credentials", "api_key", "token"}
    for key in payload:
        if key.lower() in prohibited:
            errors.append(f"prohibited sensitive field: {key}")
    return errors


def valid_relative_path(value):
    path = PurePosixPath(value)
    return (
        value == path.as_posix()
        and not path.is_absolute()
        and "\\" not in value
        and value not in {".", "docs/nulnul/checkpoint.json"}
        and ".." not in path.parts
    )


def verification_fingerprint(root, files):
    # ponytail: hash only declared check inputs; expand verification_files when check scope grows.
    root = root.resolve()
    digest = hashlib.sha256()
    for name in sorted(files):
        path = root / name
        try:
            path.resolve().relative_to(root)
        except (OSError, ValueError):
            raise ValueError(f"verification file escapes repository root: {name}")
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"verification file is missing or not a regular file: {name}")
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return "sha256:" + digest.hexdigest()


def freshness_errors(payload, root, evidence):
    if payload.get("schema_version") != 3 or payload.get("verification_status") != "verified":
        return ["checkpoint is not a schema-version-3 verified state"]
    if not isinstance(evidence, dict):
        return ["verification evidence is missing"]
    if evidence.get("schema_version") != 1 or evidence.get("verification_status") != "verified":
        return ["verification evidence is not verified"]
    if evidence.get("verification_files") != payload.get("verification_files"):
        return ["verification evidence does not match checkpoint files"]
    if not isinstance(evidence.get("verification_fingerprint"), str) or not FINGERPRINT.fullmatch(
        evidence["verification_fingerprint"]
    ):
        return ["verification evidence fingerprint is invalid"]
    try:
        actual = verification_fingerprint(root, payload.get("verification_files", []))
    except (OSError, UnicodeError, ValueError) as error:
        return [str(error)]
    return [] if actual == evidence["verification_fingerprint"] else ["verification fingerprint is stale"]


def fast_path_ready(payload, root=None, evidence=None):
    return (
        not validate(payload)
        and payload["schema_version"] == 3
        and payload["verification_status"] == "verified"
        and root is not None
        and not freshness_errors(payload, root, evidence)
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("checkpoint", type=Path)
    parser.add_argument("--root", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.checkpoint.read_text(encoding="utf-8"))
        errors = validate(payload)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        errors = [f"cannot read checkpoint: {error}"]
    root = args.root or args.checkpoint.parent.parent.parent
    try:
        evidence = json.loads(
            args.checkpoint.with_name("checkpoint.verification.json").read_text(encoding="utf-8")
        )
    except (OSError, UnicodeError, json.JSONDecodeError):
        evidence = None
    ready = not errors and fast_path_ready(payload, root, evidence)
    print(json.dumps({
        "valid": not errors,
        "fast_path_ready": ready,
        "fresh": ready,
        "errors": errors,
    }, ensure_ascii=False, indent=2))
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()
