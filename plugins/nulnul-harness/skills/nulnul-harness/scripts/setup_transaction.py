#!/usr/bin/env python3
"""Apply one bounded, rollback-safe Governed Setup plan."""

import argparse
import json
import os
import stat
import sys
import uuid
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))
import activation_boundary
import capability_contract
import foundation_runtime
import run_checkpoint_check
import sync_host_entry
import validate_checkpoint


SCHEMA_VERSION = 2
SETUP_MODES = {"new-setup", "adopt-upgrade"}
HOSTS = {"codex", "claude"}
COMMON_PLAN_FIELDS = {
    "schema_version", "mode", "host", "goal", "milestone", "completion_check",
    "verification_files", "constraints", "roster", "agent_topology",
}
PLAN_FIELDS = COMMON_PLAN_FIELDS | {"accepted_capabilities"}
LEGACY_PLAN_FIELDS = COMMON_PLAN_FIELDS | {"capabilities"}
SEMANTIC_CAPABILITY_FIELDS = {
    "capability_id", "job", "activation_trigger", "project_check_identity",
    "version_or_digest",
}
ROSTER_FIELDS = {"skills", "plugins", "agents"}
TRANSACTION_EVENTS = {
    "SETUP_PLAN_CREATED",
    "SETUP_TRANSACTION_STARTED",
    "PROJECT_CONTRACT_WRITTEN",
    "CAPABILITY_CONTRACT_VALIDATED",
    "HOST_ENTRY_WRITTEN",
    "CHECKPOINT_WRITTEN",
    "SETUP_VALIDATED",
    "SETUP_ROLLED_BACK",
    "SETUP_COMPLETED",
}


def one_line(value, field, limit=2048):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be one non-empty string")
    value = value.strip()
    if "\n" in value or "\r" in value or len(value.encode()) > limit:
        raise ValueError(f"{field} must be one bounded line")
    return value


def string_list(value, field, *, required=False):
    if not isinstance(value, list) or (required and not value):
        raise ValueError(f"{field} must be an array of bounded strings")
    rows = [one_line(item, field) for item in value]
    if len(rows) != len(set(rows)):
        raise ValueError(f"{field} must not contain duplicates")
    return rows


def validate_plan(payload):
    if not isinstance(payload, dict) or payload.get("schema_version") not in {1, SCHEMA_VERSION}:
        raise ValueError("unsupported setup plan schema")
    version = payload["schema_version"]
    expected_fields = PLAN_FIELDS if version == SCHEMA_VERSION else LEGACY_PLAN_FIELDS
    if set(payload) != expected_fields:
        raise ValueError(f"setup plan fields do not match schema version {version}")
    if payload.get("mode") not in SETUP_MODES:
        raise ValueError("setup mode must be new-setup or adopt-upgrade")
    if payload.get("host") not in HOSTS:
        raise ValueError("setup host must be codex or claude")
    roster = payload.get("roster")
    if not isinstance(roster, dict) or set(roster) != ROSTER_FIELDS:
        raise ValueError("setup roster must contain skills, plugins, and agents")
    rows = payload.get("accepted_capabilities" if version == SCHEMA_VERSION else "capabilities")
    if not isinstance(rows, list):
        raise ValueError("accepted capabilities must be one array")
    if version == SCHEMA_VERSION:
        if any(not isinstance(row, dict) or set(row) != SEMANTIC_CAPABILITY_FIELDS for row in rows):
            raise ValueError(
                "accepted capability entries must contain only capability_id, job, "
                "activation_trigger, project_check_identity, and version_or_digest"
            )
        canonical_rows = [capability_contract.accepted_record(row) for row in rows]
    else:
        # Schema-v1 compatibility is assertion-only: stale targets are never normalized.
        canonical_rows = capability_contract.parse(
            capability_contract.render(rows), require_canonical=True
        )
    plan = {
        "schema_version": SCHEMA_VERSION,
        "mode": payload["mode"],
        "host": payload["host"],
        "goal": one_line(payload.get("goal"), "goal"),
        "milestone": one_line(payload.get("milestone"), "milestone"),
        "completion_check": one_line(payload.get("completion_check"), "completion_check"),
        "verification_files": sorted(string_list(
            payload.get("verification_files"), "verification_files", required=True
        )),
        "constraints": string_list(payload.get("constraints"), "constraints", required=True),
        "roster": {
            name: string_list(roster.get(name), f"roster.{name}")
            for name in sorted(ROSTER_FIELDS)
        },
        "agent_topology": one_line(payload.get("agent_topology"), "agent_topology"),
        "capabilities": canonical_rows,
    }
    classified_agents = []
    agent_names = set()
    for entry in plan["roster"]["agents"]:
        name, separator, action = entry.rpartition(":")
        name, action = name.strip(), action.strip()
        if (
            not separator or not name or ":" in name
            or action not in {"reuse", "kept", "upgraded", "merged", "removed"}
            or name.casefold() in agent_names
        ):
            raise ValueError(
                "roster.agents needs one unique 'name: disposition' per existing role; "
                "disposition is reuse, kept, upgraded, merged, or removed"
            )
        agent_names.add(name.casefold())
        classified_agents.append(f"{name}: {'reuse' if action == 'kept' else action}")
    plan["roster"]["agents"] = classified_agents
    checkpoint = checkpoint_payload(plan)
    errors = validate_checkpoint.validate(checkpoint)
    if errors:
        raise ValueError("setup plan cannot produce a valid checkpoint: " + "; ".join(errors))
    return plan


def display(values):
    return ", ".join(values) if values else "none"


def project_contract(plan):
    capabilities = plan["capabilities"]
    agent_rows = "\n".join(f"- {entry}" for entry in plan["roster"]["agents"])
    if not agent_rows:
        agent_rows = "- No existing project roles were reported by the inspected roster."
    requirement_rows = "\n".join(
        f"- `{row['capability_id']}`: {row['job']}; activate when {row['activation_trigger']}; "
        f"check `{row['project_check_identity']}`."
        for row in capabilities
    ) or "- No project-local capability is currently accepted."
    evidence_rows = "\n".join(
        f"- `{row['capability_id']}`: `{row['status']}` at "
        f"`{row['logical_load_target']}`; runtime admission uses this canonical row."
        for row in capabilities
    ) or "- The bounded setup plan selected no project-local capability."
    routing_rows = "\n".join(
        f"- `{row['capability_id']}` handles {row['job']} only when "
        f"{row['activation_trigger']}; verify with `{row['project_check_identity']}`."
        for row in capabilities if row["accepted_current"]
    ) or "- Ordinary work continues directly because no capability is accepted/current."
    constraints = "\n".join(f"- {item}" for item in plan["constraints"])
    accepted = display([row["capability_id"] for row in capabilities if row["accepted_current"]])
    host_label = "Codex" if plan["host"] == "codex" else "Claude Code"
    return f"""# nulnul project setup

Status: active; generated by one deterministic Governed Setup transaction.

## Goal

{plan['goal']}

## Current milestone

{plan['milestone']}

Observable completion check: {plan['completion_check']}

## Constraints and permissions

{constraints}
- External services, credentials, deployment, public writes, and global configuration require explicit user approval.

## Inspected roster

- Host surface: {host_label}
- Skills: {display(plan['roster']['skills'])}
- Plugins: {display(plan['roster']['plugins'])}
- Agents: {display(plan['roster']['agents'])}

## Capability requirements

{requirement_rows}

## Candidate evidence

{evidence_rows}

{capability_contract.render(capabilities)}
## Capability routing

{routing_rows}

Available capabilities and capabilities active for the current task are separate sets.

## Setup decisions

- Reuse now: {accepted}
- Add now: only the transaction-owned project contract, host entry, checkpoint, receipt, and narrow host rule
- Needs approval: external or global changes; Codex project trust remains user/host owned
- Skip: unaccepted capabilities and unrelated infrastructure

## Agent topology

{plan['agent_topology']}

## Agent classifications

{agent_rows}

## Evolution baseline

- Representative run: {plan['milestone']}
- Primary metric: the exact completion command exits zero.
- Guardrails: transaction validation, host ownership, bounded authority, and rollback.
- Rollback: restore every transaction-owned setup surface byte-for-byte.

## Assumptions and accepted evolution

- Assumption: the bounded Setup Plan contains the current project facts required by this contract.
- Revisit when: repository evidence or a user decision changes those facts.
- Accepted change: none; capability evolution remains outside Setup.

## Continuity

- Active checkpoint: `docs/nulnul/checkpoint.json`
- Resume rule: validate the checkpoint and its verification receipt before fast resume.
- Personal promotion scope: project-local unless a private home is explicitly approved.
"""


def checkpoint_payload(plan):
    return {
        "schema_version": 3,
        "goal": plan["goal"],
        "milestone": plan["milestone"],
        "completion_check": plan["completion_check"],
        "verification_status": "unknown",
        "verification_files": plan["verification_files"],
        "last_verified": "Verification is owned by the adjacent deterministic receipt.",
        "next_action": "Continue the current milestone.",
        "permission_constraints": plan["constraints"],
        "approved_permissions": [],
        "blockers": [],
    }


def owned_paths(root, host):
    return [
        root / "docs/nulnul/project.md",
        root / "docs/nulnul/checkpoint.json",
        root / "docs/nulnul/checkpoint.verification.json",
        root / sync_host_entry.HOST_ENTRIES[host],
    ]


def snapshot(paths):
    result = {}
    for path in paths:
        if path.is_symlink() or (path.exists() and not path.is_file()):
            raise ValueError(f"transaction-owned path is unsafe: {path}")
        result[path] = (
            (path.read_bytes(), stat.S_IMODE(path.stat().st_mode)) if path.exists() else None
        )
    return result


def restore(originals, directory_state):
    errors = []
    for path, original in reversed(list(originals.items())):
        try:
            if original is None:
                path.unlink(missing_ok=True)
            else:
                sync_host_entry.atomic_write(path, original[0].decode("utf-8"))
                path.chmod(original[1])
        except (OSError, UnicodeError) as error:
            errors.append(f"{path}: {error}")
    for directory, existed in reversed(directory_state):
        if not existed:
            try:
                directory.rmdir()
            except FileNotFoundError:
                pass
            except OSError:
                if directory.exists() and not any(directory.iterdir()):
                    errors.append(f"could not remove transaction directory: {directory}")
    return errors


def active_task_id(root):
    store = foundation_runtime.Store(root)
    active = foundation_runtime.read_json(store.active)
    if not active:
        return None
    task = next((item for item in reversed(active.get("tasks", [])) if item.get("status") == "ACTIVE"), None)
    return task.get("task_id") if task else None


def emit(root, kind, details=None):
    if kind not in TRANSACTION_EVENTS:
        raise ValueError("invalid setup transaction event")
    store = foundation_runtime.Store(root)
    if store.active.is_file() and not store.active.is_symlink():
        foundation_runtime.record_event(root, kind, active_task_id(root), details or {})


def receipt_path(root, transaction_id):
    store = foundation_runtime.Store(root)
    if not store.active.is_file() and not store.local.is_dir():
        return None
    return store.local / "setup-transactions" / f"{transaction_id}.json"


def experience_outcome(result, authority, receipt=None):
    passed = result["status"] == "SETUP_TRANSACTION_PASS"
    source_refs = []
    if receipt is not None:
        source_refs.append("raw:" + receipt.relative_to(Path(result["project_root"])).as_posix())
    return {
        "experience_type": "GOVERNED_EXPERIENCE",
        "quality": "VERIFIED" if passed or result.get("rollback_result") == "PASS" else "PARTIAL",
        "observability_completeness": "COMPLETE",
        "result": "SUCCESS" if passed else "FAILURE",
        "product_outcome": (
            "Governed setup transaction completed"
            if passed else "Governed setup transaction failed and rolled back"
        ),
        "verified_failure_reason": None if passed else result.get("reason"),
        "checks": [{"id": "setup-transaction", "result": "pass" if passed else "fail"}],
        "changes": result.get("files_written", []) if passed else [],
        "governed_stage": result.get("mode"),
        "governed_host": result.get("host"),
        "authority": authority,
        "setup_transaction_id": result["setup_transaction_id"],
        "authorized_write_set": result.get("authorized_write_set", []),
        "validation_result": result.get("validation_result"),
        "restart_required": result.get("restart_required", False),
        "rollback_result": result.get("rollback_result"),
        "failure_phase": result.get("failed_phase"),
        "source_refs": source_refs,
    }


def execute(root, payload, governed_receipt, timeout=300):
    root = Path(root).resolve()
    transaction_id = f"stx-{uuid.uuid4().hex[:16]}"
    result = {
        "schema_version": SCHEMA_VERSION,
        "setup_transaction_id": transaction_id,
        "project_root": str(root),
        "status": "SETUP_TRANSACTION_FAIL",
        "mode": payload.get("mode") if isinstance(payload, dict) else None,
        "host": payload.get("host") if isinstance(payload, dict) else None,
        "validation_result": "FAIL",
        "rollback_result": "NOT_REQUIRED",
        "restart_required": False,
        "files_written": [],
        "authorized_write_set": [],
        "phases": [],
        "validators": [],
        "model_semantic_inputs": [
            "mode", "host", "goal", "milestone_and_check", "constraints", "roster",
            "agent_topology", "accepted_capabilities",
        ],
    }
    authority = []
    originals = None
    directories = []
    inactive_before = None
    phase = "plan-validation"
    try:
        if not root.is_dir():
            raise ValueError("project root must be one existing directory")
        plan = validate_plan(payload)
        result.update(mode=plan["mode"], host=plan["host"])
        emit(root, "SETUP_PLAN_CREATED", {"transaction_id": transaction_id, "mode": plan["mode"]})
        phase = "governed-authority"
        governed = activation_boundary.governed_stage(
            Path(__file__), root, plan["mode"], plan["host"]
        )
        if governed_receipt != governed["activation_receipt"]:
            raise ValueError("setup transaction requires the exact Governed activation receipt")
        authority = governed["authority"]
        result["authorized_write_set"] = authority
        if (root / "docs/nulnul/evolution.json").exists():
            raise ValueError("deterministic Setup does not replace the existing evolution writer")
        paths = owned_paths(root, plan["host"])
        expected = set(authority)
        if expected != {path.relative_to(root).as_posix() for path in paths}:
            raise ValueError("Governed authority does not match the Setup transaction write set")
        originals = snapshot(paths)
        prior_checkpoint = prior_verification = None
        if plan["mode"] == "adopt-upgrade":
            try:
                prior_checkpoint = json.loads(originals[root / "docs/nulnul/checkpoint.json"][0])
                prior_verification = json.loads(
                    originals[root / "docs/nulnul/checkpoint.verification.json"][0]
                )
                if not (
                    validate_checkpoint.fast_path_ready(prior_checkpoint, root, prior_verification)
                    and prior_verification.get("completion_check_digest") is not None
                    and prior_checkpoint["completion_check"] == plan["completion_check"]
                    and prior_checkpoint["verification_files"] == plan["verification_files"]
                ):
                    prior_checkpoint = None
            except (TypeError, UnicodeError, ValueError):
                prior_checkpoint = None
        inactive = root / sync_host_entry.HOST_ENTRIES[
            "claude" if plan["host"] == "codex" else "codex"
        ]
        if inactive.is_symlink() or (inactive.exists() and not inactive.is_file()):
            raise ValueError("inactive host entry is unsafe")
        inactive_before = inactive.read_bytes() if inactive.exists() else None
        directory_candidates = [root / "docs", root / "docs/nulnul"]
        directories = [(path, path.exists()) for path in directory_candidates]
        emit(root, "SETUP_TRANSACTION_STARTED", {"transaction_id": transaction_id})

        phase = "project-and-checkpoint-write"
        project = root / "docs/nulnul/project.md"
        checkpoint = root / "docs/nulnul/checkpoint.json"
        expected_project = project_contract(plan)
        expected_checkpoint = checkpoint_payload(plan)
        sync_host_entry.atomic_batch_write({
            project: expected_project,
            checkpoint: json.dumps(expected_checkpoint, ensure_ascii=False, indent=2) + "\n",
        })
        result["phases"].append("project-and-checkpoint-write")
        emit(root, "PROJECT_CONTRACT_WRITTEN", {"transaction_id": transaction_id})
        emit(root, "CHECKPOINT_WRITTEN", {"transaction_id": transaction_id})

        phase = "capability-validation"
        setup_rows = capability_contract.load(project, require_canonical=True, current_only=True)
        expected_rows = [row for row in plan["capabilities"] if row["accepted_current"]]
        if setup_rows != expected_rows:
            raise ValueError("Setup and runtime capability rows differ")
        pack_rows = [
            capability_contract.selected(project, row["capability_id"])
            for row in expected_rows
        ]
        if pack_rows != expected_rows:
            raise ValueError("Setup and Capability Pack rows differ")
        sync_host_entry.validate_setup_for_runtime(root)
        result["canonical_capabilities"] = setup_rows
        result["validators"].extend([
            "project-contract", "canonical-capability", "runtime-bounded-view",
            "pack-resolution",
        ])
        result["phases"].append("capability-validation")
        emit(root, "CAPABILITY_CONTRACT_VALIDATED", {
            "transaction_id": transaction_id,
            "accepted_capabilities": [row["capability_id"] for row in setup_rows],
        })

        phase = "host-write"
        sync_result = sync_host_entry.sync(root, plan["host"])
        if sync_result.get("status") == "failed":
            raise ValueError(json.dumps(sync_result, sort_keys=True))
        entry = root / sync_host_entry.HOST_ENTRIES[plan["host"]]
        expected_entry = entry.read_bytes()
        result["phases"].append("host-write")
        result["validators"].append("host-ownership")
        emit(root, "HOST_ENTRY_WRITTEN", {"transaction_id": transaction_id})

        phase = "checkpoint-verification"
        if prior_checkpoint is not None and validate_checkpoint.fast_path_ready(
            prior_checkpoint, root, prior_verification
        ):
            expected_checkpoint["verification_status"] = "verified"
            sync_host_entry.atomic_write(
                checkpoint, json.dumps(expected_checkpoint, ensure_ascii=False, indent=2) + "\n"
            )
            check = {
                "passed": True, "exit_code": None, "verification_status": "verified",
                "fast_path_ready": True, "errors": [], "reused": True,
            }
        else:
            check = {**run_checkpoint_check.run(checkpoint, root, timeout), "reused": False}
        result["completion_check"] = check
        if not check.get("passed"):
            raise ValueError("completion check failed: " + "; ".join(check.get("errors", [])))
        result["phases"].append("checkpoint-verification")
        result["validators"].append("checkpoint-verification")

        phase = "final-validation"
        checkpoint_record = json.loads(checkpoint.read_text(encoding="utf-8"))
        verification = json.loads(
            checkpoint.with_name("checkpoint.verification.json").read_text(encoding="utf-8")
        )
        if not validate_checkpoint.fast_path_ready(checkpoint_record, root, verification):
            raise ValueError("verified Setup checkpoint is not runtime-ready")
        if project.read_text(encoding="utf-8") != expected_project:
            raise ValueError("completion check changed the generated project contract")
        for name, value in expected_checkpoint.items():
            if name != "verification_status" and checkpoint_record.get(name) != value:
                raise ValueError(f"completion check changed checkpoint field: {name}")
        sync_host_entry.validate_setup_for_runtime(root)
        if entry.read_bytes() != expected_entry:
            raise ValueError("completion check changed the active host entry")
        if entry.read_text(encoding="utf-8").count(sync_host_entry.START) != 1:
            raise ValueError("active host entry is invalid")
        if inactive_before is not None and inactive.read_bytes() != inactive_before:
            raise ValueError("inactive host entry changed")
        if inactive_before is None and inactive.exists():
            raise ValueError("inactive host entry was created")
        result["validators"].extend(["checkpoint", "active-host-entry"])
        result["phases"].append("final-validation")
        result["validation_result"] = "PASS"
        result["status"] = "SETUP_TRANSACTION_PASS"
        result["files_written"] = [
            path.relative_to(root).as_posix()
            for path, before in originals.items()
            if path.exists() and (before is None or path.read_bytes() != before[0])
        ]
        result["generated_bytes"] = {
            path.relative_to(root).as_posix(): path.stat().st_size
            for path in paths if path.is_file()
        }
        result["rollback_result"] = "NOT_REQUIRED"
        emit(root, "SETUP_VALIDATED", {"transaction_id": transaction_id})
        emit(root, "SETUP_COMPLETED", {
            "transaction_id": transaction_id, "status": result["status"]
        })
    except (OSError, UnicodeError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        result["failed_phase"] = phase
        result["reason"] = str(error)
        interpretable = not isinstance(error, OSError) and "timed out" not in str(error)
        result["failure_classification"] = foundation_runtime.classify_failure(
            interpretable,
            "product-prerequisite"
            if phase in {"plan-validation", "governed-authority", "capability-validation", "final-validation"}
            else "product-execution",
        )
        if originals is not None:
            rollback_errors = restore(originals, directories)
            result["rollback_result"] = "FAIL" if rollback_errors else "PASS"
            if rollback_errors:
                result["rollback_errors"] = rollback_errors
            try:
                emit(root, "SETUP_ROLLED_BACK", {
                    "transaction_id": transaction_id,
                    "failed_phase": phase,
                    "rollback_result": result["rollback_result"],
                })
            except (OSError, UnicodeError, ValueError, RuntimeError):
                pass
    receipt = receipt_path(root, transaction_id)
    result["experience_outcome"] = experience_outcome(result, authority, receipt)
    if receipt is not None:
        result["transaction_receipt"] = receipt.relative_to(root).as_posix()
        foundation_runtime.write_json(receipt, result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("plan", type=Path)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--governed-receipt", required=True)
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()
    try:
        if args.plan.is_symlink() or not args.plan.is_file():
            raise ValueError("setup plan must be one regular JSON file")
        payload = json.loads(args.plan.read_text(encoding="utf-8"))
        result = execute(args.root, payload, args.governed_receipt, args.timeout)
    except (OSError, UnicodeError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        result = {"status": "SETUP_TRANSACTION_FAIL", "reason": str(error)}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    raise SystemExit(result.get("status") != "SETUP_TRANSACTION_PASS")


if __name__ == "__main__":
    main()
