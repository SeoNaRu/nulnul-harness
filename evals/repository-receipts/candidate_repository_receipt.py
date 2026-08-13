#!/usr/bin/env python3
"""Candidate: derive and revalidate two bounded repository decisions."""

import argparse
import ast
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath


SCOPES = {"design.component_shape", "backend.architecture"}
ROOT_FIELDS = {
    "schema_version", "claim", "scope", "observed_value", "evidence",
    "current_check", "required_check", "derived_decision", "read_set",
    "permission_delta", "identity",
}
EVIDENCE_FIELDS = {"type", "path", "locator", "strength", "observed_value", "sha256"}
CHECK_FIELDS = {"script", "files", "status", "fingerprint"}
FINGERPRINT = re.compile(r"sha256:[0-9a-f]{64}")


class ReceiptError(ValueError):
    pass


def safe_file(root, name):
    path = PurePosixPath(name)
    if name != path.as_posix() or path.is_absolute() or ".." in path.parts or "\\" in name:
        raise ReceiptError(f"invalid repository path: {name}")
    candidate = root / name
    try:
        candidate.resolve().relative_to(root)
    except (OSError, ValueError) as error:
        raise ReceiptError(f"repository path escapes root: {name}") from error
    if candidate.is_symlink() or not candidate.is_file():
        raise ReceiptError(f"repository evidence is missing or not a regular file: {name}")
    return candidate


def digest_bytes(value):
    return "sha256:" + hashlib.sha256(value).hexdigest()


def file_digest(path):
    return digest_bytes(path.read_bytes())


def contract_anchor(root, name):
    path = safe_file(root, name)
    if path.suffix != ".json":
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ReceiptError(f"invalid JSON evidence: {name}") from error
    if not isinstance(payload, dict):
        return None
    locations = (
        ("/accepted/component_shape", payload.get("accepted", {}).get("component_shape")
         if isinstance(payload.get("accepted"), dict) else None),
        ("/accepted_design/surface_radius", payload.get("accepted_design", {}).get("surface_radius")
         if isinstance(payload.get("accepted_design"), dict) else None),
    )
    found = [(locator, value) for locator, value in locations if isinstance(value, str) and value]
    if not found:
        return None
    if len({value for _, value in found}) != 1:
        raise ReceiptError(f"conflicting accepted component-shape values: {name}")
    locator, value = found[0]
    return {
        "type": "accepted_design_contract",
        "path": name,
        "locator": locator,
        "strength": "authoritative",
        "observed_value": value,
        "sha256": file_digest(path),
    }


def design_receipt(root, names):
    anchors = [anchor for name in names if (anchor := contract_anchor(root, name))]
    values = {anchor["observed_value"] for anchor in anchors}
    if not anchors:
        raise ReceiptError("authoritative accepted design contract not found")
    if len(values) != 1:
        raise ReceiptError("authoritative design anchors conflict")
    return "project_component_shape", values.pop(), anchors, None, None, "preserve"


def python_identity(path):
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.name)
    except (UnicodeError, SyntaxError) as error:
        raise ReceiptError(f"invalid Python evidence: {path.name}") from error
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module.split(".", 1)[0])
    for module, identity in (
        ("flask", "python:flask"),
        ("fastapi", "python:fastapi"),
        ("django", "python:django"),
        ("wsgiref", "python:wsgi"),
    ):
        if module in modules:
            return identity
    return None


def entrypoint_anchor(root, name):
    path = safe_file(root, name)
    if path.suffix != ".py":
        return None
    identity = python_identity(path)
    if identity is None:
        return None
    return {
        "type": "python_entrypoint",
        "path": name,
        "locator": "python_import_graph",
        "strength": "authoritative",
        "observed_value": identity,
        "sha256": file_digest(path),
    }


def check_fingerprint(root, files):
    digest = hashlib.sha256()
    for name in sorted(files):
        path = safe_file(root, name)
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return "sha256:" + digest.hexdigest()


def run_check(root, script, files):
    path = safe_file(root, script)
    if path.suffix != ".py":
        raise ReceiptError("backend checks must be repository-local Python scripts")
    declared = sorted(set([script, *files]))
    result = subprocess.run(
        [sys.executable, script],
        cwd=root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=30,
        check=False,
    )
    return {
        "script": script,
        "files": declared,
        "status": "passed" if result.returncode == 0 else "failed",
        "fingerprint": check_fingerprint(root, declared),
    }


def backend_receipt(root, names, check_script, check_files, required_script, required_files):
    anchors = [anchor for name in names if (anchor := entrypoint_anchor(root, name))]
    values = {anchor["observed_value"] for anchor in anchors}
    if not anchors:
        raise ReceiptError("authoritative Python backend entrypoint not found")
    if len(values) != 1:
        raise ReceiptError("backend identity anchors conflict")
    if not check_script:
        raise ReceiptError("working backend requires an executable current check")
    current = run_check(root, check_script, check_files)
    if current["status"] != "passed":
        raise ReceiptError("current backend check failed")
    required = run_check(root, required_script, required_files) if required_script else None
    decision = "challenge" if required and required["status"] == "failed" else "preserve"
    return "current_backend_identity", values.pop(), anchors, current, required, decision


def identity(receipt):
    payload = {key: value for key, value in receipt.items() if key != "identity"}
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return digest_bytes(encoded)


def derive(root, scope, repository_files, check_script=None, check_files=(), required_script=None, required_files=()):
    # ponytail: two proven scopes only; add another adapter after a reproduced case needs it.
    root = root.resolve()
    if scope not in SCOPES:
        raise ReceiptError(f"unsupported receipt scope: {scope}")
    if not repository_files or len(repository_files) != len(set(repository_files)):
        raise ReceiptError("repository_files must be a non-empty unique list")
    for name in repository_files:
        safe_file(root, name)
    if scope == "design.component_shape":
        parts = design_receipt(root, repository_files)
    else:
        parts = backend_receipt(
            root, repository_files, check_script, check_files, required_script, required_files
        )
    claim, observed, evidence, current, required, decision = parts
    read_set = sorted(set(
        repository_files
        + ([check_script] if check_script else [])
        + list(check_files)
        + ([required_script] if required_script else [])
        + list(required_files)
    ))
    receipt = {
        "schema_version": 1,
        "claim": claim,
        "scope": scope,
        "observed_value": observed,
        "evidence": evidence,
        "current_check": current,
        "required_check": required,
        "derived_decision": decision,
        "read_set": read_set,
        "permission_delta": [],
        "identity": "",
    }
    receipt["identity"] = identity(receipt)
    return receipt


def validate(receipt, root):
    errors = []
    if not isinstance(receipt, dict):
        return ["receipt must be an object"]
    missing = sorted(ROOT_FIELDS - receipt.keys())
    extra = sorted(receipt.keys() - ROOT_FIELDS)
    if missing:
        errors.append("receipt missing: " + ", ".join(missing))
    if extra:
        errors.append("receipt fields are not allowed: " + ", ".join(extra))
    if missing or extra:
        return errors
    if receipt["schema_version"] != 1:
        errors.append("schema_version must be 1")
    if receipt["scope"] not in SCOPES:
        errors.append("receipt scope is unsupported")
    if receipt["permission_delta"] != []:
        errors.append("permission_delta must remain empty")
    if not isinstance(receipt["identity"], str) or not FINGERPRINT.fullmatch(receipt["identity"]):
        errors.append("identity must be a sha256 fingerprint")
    evidence = receipt["evidence"]
    if not isinstance(evidence, list) or not evidence:
        errors.append("evidence must be a non-empty array")
        return errors
    for index, anchor in enumerate(evidence):
        if not isinstance(anchor, dict) or set(anchor) != EVIDENCE_FIELDS:
            errors.append(f"evidence[{index}] has unsupported fields")
    for label in ("current_check", "required_check"):
        check = receipt[label]
        if check is not None and (not isinstance(check, dict) or set(check) != CHECK_FIELDS):
            errors.append(f"{label} has unsupported fields")
    if errors:
        return errors
    try:
        expected = derive(
            Path(root),
            receipt["scope"],
            [anchor["path"] for anchor in evidence],
            receipt["current_check"]["script"] if receipt["current_check"] else None,
            receipt["current_check"]["files"] if receipt["current_check"] else (),
            receipt["required_check"]["script"] if receipt["required_check"] else None,
            receipt["required_check"]["files"] if receipt["required_check"] else (),
        )
    except (OSError, UnicodeError, ReceiptError, subprocess.TimeoutExpired) as error:
        return [str(error)]
    if expected != receipt:
        errors.append("receipt does not match current repository evidence")
    return errors


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    derive_parser = subparsers.add_parser("derive")
    derive_parser.add_argument("scope", choices=sorted(SCOPES))
    derive_parser.add_argument("repository_files", nargs="+")
    derive_parser.add_argument("--root", type=Path, default=Path.cwd())
    derive_parser.add_argument("--check-script")
    derive_parser.add_argument("--check-file", action="append", default=[])
    derive_parser.add_argument("--required-check-script")
    derive_parser.add_argument("--required-check-file", action="append", default=[])
    derive_parser.add_argument("--output", type=Path)
    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("receipt", type=Path)
    validate_parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        if args.command == "derive":
            result = derive(
                args.root, args.scope, args.repository_files, args.check_script,
                args.check_file, args.required_check_script, args.required_check_file,
            )
            if args.output:
                args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        else:
            receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
            errors = validate(receipt, args.root)
            result = {"valid": not errors, "errors": errors}
            print(json.dumps(result, ensure_ascii=False, indent=2))
            raise SystemExit(bool(errors))
    except (OSError, UnicodeError, json.JSONDecodeError, ReceiptError, subprocess.TimeoutExpired) as error:
        result = {"valid": False, "errors": [str(error)]}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        raise SystemExit(1)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
