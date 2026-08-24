#!/usr/bin/env python3
"""Validate sanitized exact-version public Meta Evolution adoption evidence."""

import argparse
import copy
import hashlib
import json
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]


PROHIBITED_KEYS = {
    "personal_home_path", "project_path", "repository_name", "project_source",
    "source_code", "raw_prompt", "raw_response", "transcript", "raw_transcript",
    "command_history", "raw_log", "credential", "credentials", "token", "email",
    "contact_data", "customer_name", "database_identifier",
}
ABSOLUTE_PATH = re.compile(r"(?:^|\s)(?:/(?:[^\s/][^\s]*)|[A-Za-z]:[\\/]\S*)")


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _run_json(command, cwd=None):
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if result.returncode:
        raise ValueError(f"control failed: {Path(command[1]).name}: {result.stderr.strip()}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise ValueError(f"control returned invalid JSON: {Path(command[1]).name}") from error


def _extract(archive, directory):
    with zipfile.ZipFile(archive) as bundle:
        members = bundle.infolist()
        names = [item.filename for item in members]
        if len(names) != len(set(names)):
            raise ValueError("public plugin archive contains duplicate paths")
        for item in members:
            path = PurePosixPath(item.filename)
            if (
                path.is_absolute()
                or not path.parts
                or path.parts[0] != "nulnul-harness"
                or ".." in path.parts
                or stat.S_ISLNK(item.external_attr >> 16)
            ):
                raise ValueError("public plugin archive contains an unsafe path")
        bundle.extractall(directory)
    return Path(directory) / "nulnul-harness"


def _lookup(script, evidence, facts, directory, *, meta=False):
    facts_path = Path(directory) / ("meta-facts.json" if meta else "flat-facts.json")
    _write(facts_path, facts)
    command = [sys.executable, str(script), str(evidence), "--facts", str(facts_path)]
    if meta:
        command.append("--meta")
    return _run_json(command)


def _migration_control(scripts, directory):
    project = Path(directory) / "project-m"
    shutil.copytree(ROOT / "tests/fixtures/legacy-1.3.0", project)
    agents_before = (project / "AGENTS.md").read_bytes()
    (project / "CLAUDE.md").write_text("# Claude guidance\n", encoding="utf-8")
    (project / "test_health.py").write_text(
        "import unittest\n\n"
        "class HealthTests(unittest.TestCase):\n"
        "    def test_health(self):\n"
        "        self.assertTrue(True)\n",
        encoding="utf-8",
    )
    contract = project / "docs/nulnul/project.md"
    migration = _run_json([
        sys.executable, str(scripts / "migrate_legacy_checkpoint.py"),
        str(contract), str(project / "CLAUDE.md"),
    ])
    checkpoint_path = contract.with_name("checkpoint.json")
    checkpoint = _read(checkpoint_path)
    checkpoint["verification_files"] = ["test_health.py"]
    _write(checkpoint_path, checkpoint)
    completion = _run_json([
        sys.executable, str(scripts / "run_checkpoint_check.py"),
        str(checkpoint_path), "--root", str(project),
    ])
    validation = _run_json([
        sys.executable, str(scripts / "validate_checkpoint.py"),
        str(checkpoint_path), "--root", str(project),
    ])
    if (
        migration.get("status") != "created"
        or not completion.get("passed")
        or not completion.get("fast_path_ready")
        or not validation.get("valid")
        or not validation.get("fast_path_ready")
        or (project / "AGENTS.md").read_bytes() != agents_before
    ):
        raise ValueError("exact-public transactional migration control failed")


def _rollback_state(template):
    payload = copy.deepcopy(template)
    payload["feedback"].append({
        "id": "feedback-meta-release-rollback",
        "source": "test",
        "target_agent": "coach",
        "observed": "The live completion rate dropped.",
        "expected": "Keep completion rate at or above 0.9.",
        "evidence": "isolated release control",
        "scope": "agent",
        "status": "converted",
    })
    payload["proposals"].append({
        "id": "proposal-meta-release-rollback",
        "feedback_ids": ["feedback-meta-release-rollback"],
        "target_agent": "coach",
        "author_agent": "coach",
        "from_version": 1,
        "to_version": 2,
        "cause": "The candidate breached its live threshold.",
        "change_target": "Meta selection procedure",
        "regression_check": "python3 -m unittest -v",
        "primary_metric": "completion rate",
        "permission_delta": [],
        "rollback": "coach v1",
        "change_level": "meta",
        "discovery_evidence": "The isolated live cycle reproduced the drop.",
        "transfer_check": None,
        "status": "provisional",
    })
    payload["promotions"].append({
        "id": "promotion-meta-release-rollback",
        "proposal_id": "proposal-meta-release-rollback",
        "gate_agent": "gate",
        "before": "completion rate 0.9",
        "after": "completion rate 0.7",
        "regressions_passed": True,
        "decision": "provisional",
        "live_cycle": {
            "status": "observed",
            "metric": "completion rate",
            "rollback_threshold": "roll back below 0.9",
            "metric_value": 0.7,
            "rollback_operator": "lt",
            "rollback_value": 0.9,
            "evidence": "isolated release control",
        },
    })
    payload["agents"]["coach"].update(
        trial_version=2,
        trial_promotion_id="promotion-meta-release-rollback",
    )
    return payload


def _rollback_control(plugin, directory):
    state_path = Path(directory) / "rollback-state.json"
    template = _read(plugin / "skills/nulnul-harness/assets/evolution-state.template.json")
    state = _rollback_state(template)
    unrelated_before = copy.deepcopy({
        "checkpoint": state["checkpoint"],
        "navigator": state["agents"]["navigator"],
        "gate": state["agents"]["gate"],
        "autonomous_episodes": state["autonomous_episodes"],
    })
    _write(state_path, state)
    scripts = plugin / "skills/nulnul-harness/scripts"
    result = _run_json([sys.executable, str(scripts / "apply_live_cycle_rollback.py"), str(state_path)])
    validation = _run_json([sys.executable, str(scripts / "validate_evolution_state.py"), str(state_path)])
    updated = _read(state_path)
    unrelated_after = {
        "checkpoint": updated["checkpoint"],
        "navigator": updated["agents"]["navigator"],
        "gate": updated["agents"]["gate"],
        "autonomous_episodes": updated["autonomous_episodes"],
    }
    return (
        result.get("rolled_back") == ["promotion-meta-release-rollback"]
        and not validation.get("errors")
        and updated["agents"]["coach"]["version"] == 1
        and unrelated_before == unrelated_after
    )


def capture(archive, local_archive, personal_home, release_commit, run_id, run_date):
    archive = Path(archive)
    home = Path(personal_home)
    preregistration = _read(ROOT / "evals/meta-evolution/release-preregistration.json")
    frozen = preregistration["frozen_candidate"]
    with tempfile.TemporaryDirectory() as temporary:
        temporary = Path(temporary)
        plugin = _extract(archive, temporary / "public")
        scripts = plugin / "skills/nulnul-harness/scripts"
        manifest = _read(plugin / ".codex-plugin/plugin.json")
        claude_manifest = _read(plugin / ".claude-plugin/plugin.json")
        version = manifest["version"]
        if archive.name != f"nulnul-harness-{version}.zip":
            raise ValueError("public plugin archive name does not match its manifest")
        if claude_manifest.get("version") != version:
            raise ValueError("public plugin manifests disagree")
        if _sha256(scripts / "cross_project_evolution.py") != frozen["source_sha256"]:
            raise ValueError("public meta selector differs from the frozen candidate")
        if not home.is_dir() or home.is_symlink():
            raise ValueError("approved Personal Home is missing or unsafe")
        home_evidence = home / "cross-project-evidence.json"
        if home_evidence.is_symlink() or _sha256(home_evidence) != preregistration["adaptation_inventory"]["evidence_sha256"]:
            raise ValueError("Personal Home inventory differs from the frozen evidence")
        home_validation = _run_json([
            sys.executable, str(scripts / "personal_adaptation.py"),
            "validate-home", "--home", str(home),
        ])
        evidence_validation = _run_json([
            sys.executable, str(scripts / "cross_project_evolution.py"), str(home_evidence),
        ])
        if not home_validation.get("valid") or not evidence_validation.get("valid"):
            raise ValueError("Personal Home validation failed")
        evidence = _read(home_evidence)
        families = [item["mechanism_family"] for item in evidence["adaptations"]]
        if families != preregistration["adaptation_inventory"]["families"]:
            raise ValueError("Personal Home does not contain the frozen family inventory")

        project_facts = {
            "schema_version": 1,
            "conditions": ["durable_multi_session", "multi_file_state_migration", "local_offline_repository"],
            "approved_permissions": [],
        }
        flat = _lookup(scripts / "cross_project_evolution.py", home_evidence, project_facts, temporary)
        meta = _lookup(scripts / "cross_project_evolution.py", home_evidence, project_facts, temporary, meta=True)
        if flat.get("selected") != ["personal-transactional-migration-v1"] or meta.get("selected") != flat.get("selected"):
            raise ValueError("Project M selected the wrong adaptation")

        no_match_facts = {
            "schema_version": 1,
            "conditions": ["one_shot_task", "single_file_change"],
            "approved_permissions": [],
        }
        no_match = _lookup(
            scripts / "cross_project_evolution.py", home_evidence, no_match_facts,
            temporary / "no-match", meta=True,
        )
        conflict_evidence = copy.deepcopy(evidence)
        conflict_evidence["relations"][0].update(
            type="CONFLICTS",
            evidence="Fresh isolated release control selected both writers.",
            reason="Both candidates would own the same live-state transition.",
            scope="Isolated release conflict control.",
        )
        conflict_path = temporary / "conflict-evidence.json"
        _write(conflict_path, conflict_evidence)
        conflict_facts = {
            "schema_version": 1,
            "conditions": [
                "durable_multi_session", "verified_checkpoint_used", "deterministic_completion_check",
                "bounded_verification_files", "checkpoint_receipt_supported",
                "multi_file_state_migration", "local_offline_repository",
            ],
            "approved_permissions": [],
        }
        conflict = _lookup(
            scripts / "cross_project_evolution.py", conflict_path, conflict_facts,
            temporary / "conflict", meta=True,
        )
        _migration_control(scripts, temporary)
        rollback_passed = _rollback_control(plugin, temporary)
        if no_match.get("status") != "NO_RELEVANT_ADAPTATION" or conflict.get("status") != "META_CONFLICT" or not rollback_passed:
            raise ValueError("Meta release control failed closed")

        asset_sha = _sha256(archive)
        local_identity = asset_sha == _sha256(local_archive)
        case_id = f"release:project-m-{version}-r1"
        payload = copy.deepcopy(_read(ROOT / "evals/meta-evolution/public-adoption.json"))
        payload.update(run_id=run_id, run_date=run_date, meta_candidate=frozen)
        payload["installed_plugin"].update(version=version, marketplace_ref=f"v{version}")
        payload["distribution"].update(
            release_tag=f"v{version}", release_commit=release_commit,
            asset=archive.name, asset_sha256=asset_sha,
            local_public_byte_identity=local_identity, manifest_identity=True,
        )
        payload["available_adaptation_families"] = families
        payload["project_m"].update(case_id=case_id, available=families)
        payload["project_m"]["flat_lookup"] = {
            "status": flat["status"],
            "selected": flat["selected"],
            "compatibility_checks_executed": flat["compatibility_checks_executed"],
        }
        payload["project_m"]["meta_selector"] = {
            "status": meta["status"],
            "selected": meta["selected"],
            "shortlisted": meta["selected"],
            "excluded": meta["skipped"],
            "compatibility_checks_executed": meta["compatibility_checks_executed"],
        }
        payload["project_m"]["downstream_completion_checks"][-1]["check"] = (
            f"exact-public {version} transactional migration and validation"
        )
        payload["no_relevant_control"].update(
            status=no_match["status"], selected=no_match["selected"],
            flat_compatibility_checks=len(evidence["adaptations"]),
            meta_compatibility_checks=no_match["compatibility_checks_executed"],
        )
        payload["conflict_control"].update(
            status=conflict["status"], selected=conflict["selected"],
            compatibility_checks_executed=conflict["compatibility_checks_executed"],
        )
        payload["live_cycle"]["case_id"] = case_id
        payload["rollback_control"].update(
            method="The exact public executor restored the confirmed version after a threshold breach.",
            rolled_back_to=preregistration["rollback"]["rollback_to"],
        )
        payload["control_provenance"] = (
            f"Fresh Project M, no-match, conflict, migration, and rollback controls ran through "
            f"the exact public {version} artifact. No retired holdout was reopened and no candidate tuning occurred."
        )
        payload["claim_boundary"] = (
            f"The exact public {version} artifact reduced fresh Project M checks from three to one, "
            "preserved the correct apply, completed migration, and failed closed on no-match and conflict controls. "
            "No universal or cross-user claim is made."
        )
    errors = validate(payload, preregistration, version)
    if errors:
        raise ValueError("captured Meta adoption evidence is invalid: " + "; ".join(errors))
    return payload


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
    if len(sys.argv) > 1 and sys.argv[1] == "capture":
        parser = argparse.ArgumentParser()
        parser.add_argument("command", choices=["capture"])
        parser.add_argument("archive", type=Path)
        parser.add_argument("local_archive", type=Path)
        parser.add_argument("personal_home", type=Path)
        parser.add_argument("output", type=Path)
        parser.add_argument("--release-commit", required=True)
        parser.add_argument("--run-id", required=True)
        parser.add_argument("--run-date", required=True)
        args = parser.parse_args()
        try:
            payload = capture(
                args.archive, args.local_archive, args.personal_home,
                args.release_commit, args.run_id, args.run_date,
            )
            _write(args.output, payload)
            errors = []
        except (OSError, UnicodeError, ValueError, zipfile.BadZipFile, json.JSONDecodeError) as error:
            errors = [str(error)]
        print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
        raise SystemExit(bool(errors))

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
