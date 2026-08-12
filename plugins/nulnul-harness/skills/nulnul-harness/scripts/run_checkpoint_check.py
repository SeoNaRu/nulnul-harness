#!/usr/bin/env python3
"""Run the exact completion command recorded by a concise checkpoint."""

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path

import validate_checkpoint


def atomic_write(path, payload):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        temporary = Path(handle.name)
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def record_verification(checkpoint_path, payload, root, status):
    if payload.get("schema_version") != 3:
        return []
    payload["verification_status"] = status
    evidence = {
        "schema_version": 1,
        "verification_status": status,
        "verification_files": payload["verification_files"],
        "verification_fingerprint": "",
    }
    if status == "verified":
        try:
            evidence["verification_fingerprint"] = validate_checkpoint.verification_fingerprint(
                root, payload["verification_files"]
            )
        except (OSError, UnicodeError, ValueError) as error:
            payload["verification_status"] = "unknown"
            evidence["verification_status"] = "unknown"
            atomic_write(checkpoint_path.with_name("checkpoint.verification.json"), evidence)
            atomic_write(checkpoint_path, payload)
            return [str(error)]
    atomic_write(checkpoint_path.with_name("checkpoint.verification.json"), evidence)
    atomic_write(checkpoint_path, payload)
    return []


def run(checkpoint_path, root, timeout):
    payload = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    errors = validate_checkpoint.validate(payload)
    if errors:
        return {"passed": False, "exit_code": None, "errors": errors}
    command = payload["completion_check"]
    try:
        result = subprocess.run(command, cwd=root, shell=True, timeout=timeout)
        passed = result.returncode == 0
        errors = record_verification(
            checkpoint_path, payload, root, "verified" if passed else "failed"
        )
        try:
            evidence = json.loads(
                checkpoint_path.with_name("checkpoint.verification.json").read_text(encoding="utf-8")
            )
        except (OSError, UnicodeError, json.JSONDecodeError):
            evidence = None
        return {
            "passed": passed and not errors,
            "exit_code": result.returncode,
            "verification_status": payload.get("verification_status", "unknown"),
            "fast_path_ready": passed and not errors and validate_checkpoint.fast_path_ready(payload, root, evidence),
            "errors": errors,
        }
    except subprocess.TimeoutExpired:
        errors = record_verification(checkpoint_path, payload, root, "failed")
        return {
            "passed": False,
            "exit_code": None,
            "verification_status": payload.get("verification_status", "unknown"),
            "fast_path_ready": False,
            "errors": ["completion_check timed out", *errors],
        }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("checkpoint", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()
    try:
        result = run(args.checkpoint, args.root, args.timeout)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        result = {"passed": False, "exit_code": None, "errors": [str(error)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(not result["passed"])


if __name__ == "__main__":
    main()
