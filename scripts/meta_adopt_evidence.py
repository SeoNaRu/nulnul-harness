#!/usr/bin/env python3
"""Validate sanitized exact-version public Meta Evolution adoption evidence."""

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


def validate(payload, preregistration, expected_version):
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
        return ["public meta adoption evidence must use schema version 1"]
    if not isinstance(preregistration, dict) or preregistration.get("schema_version") != 1:
        return ["public meta adoption preregistration must use schema version 1"]
    reject_private(payload)
    if payload.get("episode_id") != preregistration.get("episode_id"):
        errors.append("public meta adoption episode identity mismatch")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", payload.get("run_date", "")):
        errors.append("public meta adoption run date is invalid")

    installed = payload.get("installed_plugin", {})
    if installed.get("version") != expected_version:
        errors.append("public meta adoption plugin version is stale")
    if installed.get("distribution_source") != "github-tag" or installed.get("marketplace_ref") != f"v{expected_version}":
        errors.append("public meta adoption did not use the exact GitHub tag")
    if installed.get("local_override") is not False or installed.get("symlink") is not False:
        errors.append("public meta adoption reused local source")

    release = payload.get("distribution", {})
    if release.get("release_tag") != f"v{expected_version}":
        errors.append("public meta adoption release tag is stale")
    if not re.fullmatch(r"[0-9a-f]{40}", release.get("release_commit", "")):
        errors.append("public meta adoption release commit is invalid")
    if release.get("asset") != f"nulnul-harness-{expected_version}.zip" or not re.fullmatch(
        r"[0-9a-f]{64}", release.get("asset_sha256", "")
    ):
        errors.append("public meta adoption asset identity is invalid")
    if release.get("local_public_byte_identity") is not True or release.get("manifest_identity") is not True:
        errors.append("public meta adoption artifact identity failed")

    frozen = preregistration.get("frozen_candidate", {})
    candidate = payload.get("meta_candidate", {})
    for field in ("selector_version", "candidate_id", "candidate_ref", "source_sha256"):
        if candidate.get(field) != frozen.get(field):
            errors.append(f"public meta candidate identity mismatch: {field}")

    expected_families = preregistration.get("adaptation_inventory", {}).get("families", [])
    available = payload.get("available_adaptation_families", [])
    if available != expected_families or len(set(available)) < 3:
        errors.append("public Personal registry does not contain the frozen three-family inventory")
    home = payload.get("personal_home", {})
    if any(home.get(field) is not True for field in (
        "configured", "existing_directory", "not_symlink", "registry_valid", "privacy_passed",
    )) or home.get("path_stored") is not False:
        errors.append("public meta Personal Home validation failed")

    project = payload.get("project_m", {})
    flat = project.get("flat_lookup", {})
    meta = project.get("meta_selector", {})
    if project.get("user_named_adaptation") is not False or project.get("available") != available:
        errors.append("fresh Project M did not discover the unnamed frozen inventory")
    if meta.get("status") != flat.get("status") or meta.get("selected") != flat.get("selected"):
        errors.append("fresh Project M meta decision differs from flat lookup")
    flat_checks = flat.get("compatibility_checks_executed")
    meta_checks = meta.get("compatibility_checks_executed")
    if not isinstance(flat_checks, int) or not isinstance(meta_checks, int) or meta_checks >= flat_checks:
        errors.append("fresh Project M did not reduce full compatibility checks")
    if meta.get("shortlisted") != meta.get("selected") or not isinstance(meta.get("excluded"), list):
        errors.append("fresh Project M shortlist evidence is incomplete")
    if project.get("false_activations") != 0 or project.get("relevant_omissions") != 0:
        errors.append("fresh Project M selected incorrectly")
    checks = project.get("downstream_completion_checks")
    if not isinstance(checks, list) or not checks or any(item.get("exit_code") != 0 for item in checks):
        errors.append("fresh Project M downstream completion failed")
    if project.get("permission_delta") != [] or project.get("privacy_result") != "passed":
        errors.append("fresh Project M permission or privacy boundary failed")

    no_match = payload.get("no_relevant_control", {})
    if (
        no_match.get("status") != "NO_RELEVANT_ADAPTATION"
        or no_match.get("selected") != []
        or no_match.get("forced_apply_count") != 0
        or no_match.get("project_local_flow_continued") is not True
    ):
        errors.append("public no-relevant control failed")
    conflict = payload.get("conflict_control", {})
    if (
        conflict.get("status") != "META_CONFLICT"
        or conflict.get("selected") != []
        or conflict.get("auto_apply") is not False
        or conflict.get("arbitrary_winner") is not None
        or conflict.get("permission_delta") != []
    ):
        errors.append("public conflict control did not fail closed")

    live = payload.get("live_cycle", {})
    if live.get("downstream_completion_passed") is not True or any(
        live.get(field) != 0 for field in (
            "false_activations", "relevant_omissions", "unsupported_conflict_resolutions", "permission_expansions",
        )
    ):
        errors.append("public meta live cycle failed")
    rollback = payload.get("rollback_control", {})
    if (
        rollback.get("isolated") is not True
        or rollback.get("threshold_breached") is not True
        or rollback.get("rolled_back_to") != "flat-lookup-v1"
        or rollback.get("unrelated_state_corruption") is not False
    ):
        errors.append("public meta rollback control failed")
    exposure = payload.get("exposure", {})
    if (
        exposure.get("classification") != "release_adoption"
        or exposure.get("candidate_tuning") is not False
        or exposure.get("retired_local_holdouts_reused") is not False
    ):
        errors.append("public meta adoption violated exposure discipline")
    gate = payload.get("meta_gate", {})
    if gate.get("decision") != "META_PROMOTION" or gate.get("gate_agent") in {
        gate.get("candidate_author"), gate.get("target_agent"),
    }:
        errors.append("public Meta Gate failed or self-approved")
    generalization = payload.get("generalization", {})
    if generalization.get("decision") != "narrower_scope" or generalization.get("harness_wide") is not False:
        errors.append("public meta adoption widened the Generalization claim")
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence", type=Path)
    parser.add_argument("preregistration", type=Path)
    parser.add_argument("--version", required=True)
    args = parser.parse_args()
    try:
        payload = json.loads(args.evidence.read_text(encoding="utf-8"))
        preregistration = json.loads(args.preregistration.read_text(encoding="utf-8"))
        errors = validate(payload, preregistration, args.version)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        errors = [f"cannot read public meta adoption evidence: {error}"]
    print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()
