#!/usr/bin/env python3
"""Validate sanitized public Personal Evolution adoption evidence."""

import argparse
import json
import re
from pathlib import Path


PROHIBITED_KEYS = {
    "personal_home_path", "project_path", "repository_name", "project_source",
    "source_code", "raw_prompt", "raw_response", "transcript", "raw_transcript",
    "command_history", "raw_log", "credential", "credentials", "token", "email",
    "contact_data", "customer_name", "database_identifier",
}
ABSOLUTE_PATH = re.compile(r"(?:^|\s)(?:/(?:[^\s/][^\s]*)|[A-Za-z]:[\\/]\S*)")


def validate(payload, expected_version):
    errors = []

    def reject_private(value, label="root"):
        if isinstance(value, dict):
            for key, item in value.items():
                if key.lower() in PROHIBITED_KEYS:
                    errors.append(f"{label}.{key} is prohibited")
                reject_private(item, f"{label}.{key}")
        elif isinstance(value, list):
            for index, item in enumerate(value):
                reject_private(item, f"{label}[{index}]")
        elif isinstance(value, str) and ABSOLUTE_PATH.search(value):
            errors.append(f"{label} contains a machine path")

    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        return ["public personal adoption evidence must use schema version 1"]
    reject_private(payload)
    if payload.get("case_id") != "public-personal-adoption-1":
        errors.append("public personal adoption case identity is invalid")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", payload.get("run_date", "")):
        errors.append("public personal adoption run date is invalid")
    installed = payload.get("installed_plugin", {})
    if installed.get("version") != expected_version:
        errors.append("public personal adoption plugin version is stale")
    if installed.get("distribution_source") != "github-tag" or installed.get("marketplace_ref") != f"v{expected_version}":
        errors.append("public personal adoption did not use the exact GitHub tag")
    if installed.get("local_override") is not False or installed.get("symlink") is not False:
        errors.append("public personal adoption reused local source")
    release = payload.get("distribution", {})
    if release.get("release_tag") != f"v{expected_version}":
        errors.append("public personal adoption release tag is stale")
    if not re.fullmatch(r"[0-9a-f]{40}", release.get("release_commit", "")):
        errors.append("public personal adoption release commit is invalid")
    if release.get("asset") != f"nulnul-harness-{expected_version}.zip" or not re.fullmatch(
        r"[0-9a-f]{64}", release.get("asset_sha256", "")
    ):
        errors.append("public personal adoption asset identity is invalid")
    home = payload.get("personal_home", {})
    if any(home.get(field) is not True for field in ("configured", "existing_directory", "not_symlink", "registry_valid", "privacy_passed")):
        errors.append("public personal home validation failed")
    if home.get("path_stored") is not False:
        errors.append("public evidence stores the personal home path")
    adaptation = payload.get("adaptation", {})
    if adaptation.get("adaptation_id") != "personal-checkpoint-freshness-v1" or adaptation.get("status") != "active":
        errors.append("public personal adaptation identity is invalid")
    positive = payload.get("fresh_project", {})
    if positive.get("shape") != "ruby-library" or positive.get("discovery") != "APPLY":
        errors.append("fresh Project E did not discover the adaptation")
    if any(positive.get(field) is not True for field in (
        "activation_match", "contraindication_clear", "compatibility_passed",
        "application_passed", "completion_check_passed", "verified_resume",
    )):
        errors.append("fresh Project E personal reuse failed")
    if positive.get("permission_delta") != [] or positive.get("protected_writes") != []:
        errors.append("fresh Project E expanded authority")
    negative = payload.get("negative_project", {})
    if negative.get("registry_checked") is not True or negative.get("decision") != "SKIP" or negative.get("reason") != "conditions_not_met":
        errors.append("fresh negative project did not skip")
    revoked = payload.get("revocation_control", {})
    if revoked.get("isolated_copy") is not True or revoked.get("decision") != "SKIP" or revoked.get("reason") != "revoked":
        errors.append("revoked adaptation remained applicable")
    baseline = payload.get("baseline", {})
    if baseline.get("adaptation_discovered") is not False or baseline.get("completion_check_passed") is not True:
        errors.append("public personal adoption baseline is invalid")
    gate = payload.get("personal_gate", {})
    if gate.get("status") != "passed" or gate.get("gate_agent") == gate.get("candidate_author"):
        errors.append("public Personal Gate failed or self-approved")
    if payload.get("privacy_result") != "passed" or payload.get("public_positioning_violations") != 0:
        errors.append("public personal adoption privacy or positioning failed")
    attempts = payload.get("attempts", [])
    if not isinstance(attempts, list) or any(item.get("raw_transcript_retained") is not False for item in attempts):
        errors.append("public personal adoption attempt hygiene is invalid")
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--version", required=True)
    args = parser.parse_args()
    try:
        payload = json.loads(args.evidence.read_text(encoding="utf-8"))
        errors = validate(payload, args.version)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        errors = [f"cannot read public personal adoption evidence: {error}"]
    print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()
