#!/usr/bin/env python3
"""Build immutable pre-work capability packs without privileged host access."""

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
import uuid
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))
import capability_contract


SCHEMA_VERSION = 1
MAX_CANDIDATES = 3
STRONG_MATCH_TERMS = 2
HOST_BODY_ROOTS = {"codex": ".agents/skills", "claude": ".claude/skills"}
GENERIC_TERMS = {
    "accepted", "behavior", "capability", "change", "changes", "current", "job",
    "only", "preserve", "project", "task", "the", "when", "with", "work",
}
PACK_ID = re.compile(r"pack-[a-f0-9]{32}")
HEX64 = re.compile(r"[a-f0-9]{64}")
COMPLETION_CHECK = re.compile(
    r"^Observable completion check:\s*(?:`([^`\r\n]+)`|([^`\r\n]+))\s*$",
    re.MULTILINE,
)


def runtime():
    import foundation_runtime
    return foundation_runtime


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def canonical_digest(payload):
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def stores(root):
    store = runtime().Store(root)
    return store, store.local / "capability-packs", store.local / "work-starts", store.local / "pack-checks"


def active_task(root, task_id):
    rt = runtime()
    store = rt.Store(root)
    active = rt.read_json(store.active)
    if not active:
        raise ValueError("no active NULNUL session")
    task = next((row for row in active.get("tasks", []) if row.get("task_id") == task_id), None)
    if not task or task.get("status") != "ACTIVE":
        raise ValueError("capability pack requires one active matching task")
    return store, active, task


def selection_terms(*values):
    return set(runtime().tokens(*values)) - GENERIC_TERMS


def selection_policy(root):
    defaults = {
        "candidate_limit": MAX_CANDIDATES,
        "semantic_fallback": True,
        "strategy": "hybrid_p3",
        "strong_match_terms": STRONG_MATCH_TERMS,
    }
    current = Path(root).resolve() / "docs/nulnul/harness-controls.json"
    if not current.exists():
        return defaults, False
    # Project policy is maintenance-only state. The common Direct path never imports or
    # reads the control registry when no promoted policy exists.
    import harness_control
    return harness_control.project_policy(root, "control-capability-selection", defaults)


def candidates(project, task, limit=None):
    project = Path(project).resolve()
    policy, _ = selection_policy(project.parents[2])
    limit = policy["candidate_limit"] if limit is None else limit
    if limit < 1 or limit > MAX_CANDIDATES:
        raise ValueError("candidate limit exceeds the product bound")
    query = selection_terms(
        task.get("goal", ""), task.get("job", ""), task.get("tags", []),
        task.get("modules", []),
        [item.get("bounded_content", "") for item in task.get("context_pack", {}).get("items", [])],
    )
    ranked = []
    for row in capability_contract.bounded_view(project):
        metadata = selection_terms(
            row["capability_id"], row["job"], row["activation_trigger"],
            row["project_check_identity"],
        )
        overlap = sorted(query & metadata)
        if not overlap:
            continue
        ranked.append((len(overlap), row["capability_id"], row, overlap))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    return [
        {
            "capability_id": row["capability_id"],
            "job": row["job"],
            "activation_trigger": row["activation_trigger"],
            "project_check_identity": row["project_check_identity"],
            "status": row["status"],
            "version_or_digest": row["version_or_digest"],
            "logical_load_target": row["logical_load_target"],
            "matched_terms": overlap,
            "score": score,
        }
        for score, _, row, overlap in ranked[:limit]
    ]


def body_source(root, host, capability_id):
    if host not in HOST_BODY_ROOTS:
        raise ValueError("unsupported capability-pack host")
    root = Path(root).resolve()
    relative = Path(HOST_BODY_ROOTS[host]) / capability_id / "SKILL.md"
    target = root / relative
    if (
        target.is_symlink()
        or not target.is_file()
        or not target.resolve().is_relative_to(root)
        or any(parent.is_symlink() for parent in target.parents if parent != root)
    ):
        raise ValueError(f"selected capability body is unavailable: {capability_id}")
    return target, relative.as_posix()


def configured_check(project):
    project = Path(project)
    if project.is_symlink() or not project.is_file():
        raise ValueError("canonical project check is unavailable")
    matches = COMPLETION_CHECK.findall(project.read_text(encoding="utf-8"))
    command = next((value for value in matches[0] if value), "").strip() if len(matches) == 1 else ""
    if not command or len(command.encode()) > 2048:
        raise ValueError("canonical project check must be one bounded exact command")
    return command


def canonical_ref(root, host, row, evidence, check_command):
    target, relative = body_source(root, host, row["capability_id"])
    body = target.read_bytes()
    body_digest = hashlib.sha256(body).hexdigest()
    accepted_digest = row.get("version_or_digest") or ""
    if HEX64.fullmatch(accepted_digest) and accepted_digest != body_digest:
        raise ValueError("selected capability body does not match its accepted digest")
    return {
        "capability_id": row["capability_id"],
        "version_or_digest": row.get("version_or_digest"),
        "logical_load_target": row["logical_load_target"],
        "project_check_identity": row["project_check_identity"],
        "project_check_command": check_command,
        "body_source": relative,
        "body_digest": body_digest,
        "selection_evidence": evidence,
    }


def pack_file(root, pack_id):
    if not PACK_ID.fullmatch(str(pack_id)):
        raise ValueError("invalid capability pack identity")
    return stores(root)[1] / f"{pack_id}.json"


def load_pack(root, pack_id, task_id=None):
    rt = runtime()
    path = pack_file(root, pack_id)
    payload = rt.read_json(path)
    if not payload or payload.get("pack_id") != pack_id or payload.get("status") != "READY":
        raise ValueError("capability pack is unavailable")
    digest = payload.get("pack_digest")
    unsigned = {key: value for key, value in payload.items() if key != "pack_digest"}
    if digest != canonical_digest(unsigned):
        raise ValueError("capability pack digest is invalid")
    if task_id is not None and payload.get("task_id") != task_id:
        raise ValueError("capability pack belongs to a different task")
    return payload


def event_for(root, session_id, kind, pack_id):
    rt = runtime()
    path = rt.Store(root).local / "events" / f"{session_id}.jsonl"
    matches = [
        event for event in rt.read_jsonl(path)
        if event.get("kind") == kind and event.get("details", {}).get("pack_id") == pack_id
    ]
    if len(matches) != 1:
        raise ValueError(f"capability pack is missing one {kind} event")
    return matches[0]


def prepare(root, project, task_id, host, selected=None, evidence=None, no_capability=False):
    root = Path(root).resolve()
    project = Path(project)
    if not project.is_absolute():
        project = root / project
    if project.resolve() != (root / "docs/nulnul/project.md").resolve():
        raise ValueError("capability pack requires the canonical project contract")
    store, active, task = active_task(root, task_id)
    _, packs, _, _ = stores(root)
    if any(runtime().read_json(path, {}).get("task_id") == task_id for path in packs.glob("*.json")):
        raise ValueError("one immutable capability pack already exists for this task")
    policy, policy_loaded = selection_policy(root)
    bounded = candidates(project, task, policy["candidate_limit"])
    runtime().record_event(root, "CAPABILITY_OPPORTUNITY", task_id, {
        "candidate_ids": [row["capability_id"] for row in bounded],
        "body_content_included": False,
    })
    candidate_ids = {row["capability_id"] for row in bounded}
    selected = list(dict.fromkeys(selected or []))
    if selected and no_capability:
        raise ValueError("selection cannot contain capability IDs and NO_CAPABILITY")
    if selected:
        if not evidence or not evidence.strip() or len(evidence.encode()) > 1024:
            raise ValueError("bounded semantic selection evidence is required")
        if not set(selected) <= candidate_ids:
            raise ValueError("selector may choose only bounded accepted/current candidates")
        selection_method = "bounded-semantic"
        selection_evidence = evidence.strip()
    elif no_capability:
        if len((evidence or "").encode()) > 1024:
            raise ValueError("bounded semantic selection evidence is too large")
        selection_method = "bounded-semantic"
        selection_evidence = (evidence or "bounded selector returned NO_CAPABILITY").strip()
    elif not bounded:
        selection_method = "deterministic-zero"
        selection_evidence = "no accepted capability metadata overlapped the bounded task context"
    elif len(bounded) == 1 and bounded[0]["score"] >= policy["strong_match_terms"]:
        selected = [bounded[0]["capability_id"]]
        selection_method = "deterministic-single"
        selection_evidence = "unique strong metadata match: " + ", ".join(bounded[0]["matched_terms"])
    elif policy["semantic_fallback"] and policy["strategy"] == "hybrid_p3":
        event = runtime().record_event(root, "CAPABILITY_SELECTION_REQUIRED", task_id, {
            "candidate_ids": [row["capability_id"] for row in bounded],
        })
        return {
            "schema_version": SCHEMA_VERSION,
            "status": "SELECTION_REQUIRED",
            "task_id": task_id,
            "candidates": bounded,
            "candidate_limit": policy["candidate_limit"],
            "body_content_included": False,
            "event": event,
            "next": "select only a materially fitting listed ID, or choose NO_CAPABILITY, then prepare once",
        }
    else:
        selected = []
        selection_method = "deterministic-no-match"
        selection_evidence = "current deterministic policy did not admit an ambiguous candidate"
    if no_capability:
        selected = []
    rows = {row["capability_id"]: row for row in capability_contract.bounded_view(project)}
    check_command = configured_check(project) if selected else None
    refs = [
        canonical_ref(root, host, rows[identity], selection_evidence, check_command)
        for identity in selected
    ]
    pack_id = f"pack-{uuid.uuid4().hex}"
    selection_event = runtime().record_event(root, "CAPABILITY_SELECTED", task_id, {
        "pack_id": pack_id,
        "capability_ids": selected,
        "method": selection_method,
    })
    payload = {
        "schema_version": SCHEMA_VERSION,
        "pack_id": pack_id,
        "task_id": task_id,
        "host": host,
        "project_revision": active.get("project_revision", "unknown"),
        "capability_refs": refs,
        "selection_evidence": selection_evidence,
        "selection_method": selection_method,
        "selection_control_loaded": policy_loaded,
        "memory_refs": [item["item_id"] for item in task.get("context_pack", {}).get("items", [])],
        "created_at": now(),
        "status": "READY",
    }
    payload["pack_digest"] = canonical_digest(payload)
    packs.mkdir(parents=True, exist_ok=True)
    path = packs / f"{pack_id}.json"
    runtime().write_json(path, payload)
    path.chmod(0o444)
    try:
        created = runtime().record_event(root, "CAPABILITY_PACK_CREATED", task_id, {
            "pack_id": pack_id,
            "pack_digest": payload["pack_digest"],
            "capability_ids": selected,
        })
    except Exception:
        path.chmod(0o600)
        path.unlink(missing_ok=True)
        raise
    return payload | {
        "selection_event": selection_event,
        "created_event": created,
        "body_content_included": False,
        "next": "the Foundation host binds this Pack before starting the work model",
    }


def work_start(root, pack_id):
    root = Path(root).resolve()
    pack = load_pack(root, pack_id)
    _, active, task = active_task(root, pack["task_id"])
    _, _, starts, _ = stores(root)
    receipt_path = starts / f"{pack_id}.json"
    if receipt_path.exists():
        raise ValueError("work session already started for this capability pack")
    bodies = []
    for reference in pack["capability_refs"]:
        accepted = capability_contract.selected(
            root / "docs/nulnul/project.md", reference["capability_id"]
        )
        for field in ("version_or_digest", "logical_load_target", "project_check_identity"):
            if accepted.get(field) != reference.get(field):
                raise ValueError("selected capability contract changed after pack creation")
        target, relative = body_source(root, pack["host"], reference["capability_id"])
        if relative != reference["body_source"]:
            raise ValueError("selected capability body source changed after pack creation")
        if hashlib.sha256(target.read_bytes()).hexdigest() != reference["body_digest"]:
            raise ValueError("selected capability body changed after pack creation")
        bodies.append({
            "capability_id": reference["capability_id"],
            "body_digest": reference["body_digest"],
            "content": target.read_text(encoding="utf-8"),
        })
    created = event_for(root, active["session_id"], "CAPABILITY_PACK_CREATED", pack_id)
    selected = event_for(root, active["session_id"], "CAPABILITY_SELECTED", pack_id)
    body_event = None
    if bodies:
        body_event = runtime().record_event(root, "CAPABILITY_BODY_INCLUDED", task["task_id"], {
            "pack_id": pack_id,
            "capability_ids": [row["capability_id"] for row in bodies],
        })
    work_event = runtime().record_event(root, "WORK_SESSION_STARTED", task["task_id"], {
        "pack_id": pack_id,
    })
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "pack_id": pack_id,
        "pack_digest": pack["pack_digest"],
        "task_id": task["task_id"],
        "selection_event_id": selected["event_id"],
        "pack_created_event_id": created["event_id"],
        "body_included_event_id": body_event["event_id"] if body_event else None,
        "work_session_event_id": work_event["event_id"],
        "body_digests": {row["capability_id"]: row["body_digest"] for row in bodies},
        "product_state_before_work": scientific_tree_digest(root),
        "started_at": now(),
        "status": "WORK_SESSION_READY",
    }
    starts.mkdir(parents=True, exist_ok=True)
    runtime().write_json(receipt_path, receipt)
    return receipt | {
        "model_context": {
            "session_id": active["session_id"],
            "task_id": task["task_id"],
            "pack_id": pack_id,
            "memory_items": task.get("context_pack", {}).get("items", []),
            "capabilities": bodies,
        }
    }


def bootstrap(root, project, task_id, host, selected=None, evidence=None, no_capability=False):
    """Construct and bind one Pack before the main work model starts."""
    pack = prepare(root, project, task_id, host, selected, evidence, no_capability)
    if pack.get("status") == "SELECTION_REQUIRED":
        return pack
    started = work_start(root, pack["pack_id"])
    capabilities = started["model_context"]["capabilities"]
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "WORK_SESSION_READY",
        "pack_id": pack["pack_id"],
        "pack_digest": pack["pack_digest"],
        "selection_method": pack["selection_method"],
        "selection_evidence": pack["selection_evidence"],
        "capability_ids": [row["capability_id"] for row in pack["capability_refs"]],
        "model_context": ({"pack_id": pack["pack_id"], "capabilities": capabilities} if capabilities else {}),
    }


def scientific_tree_digest(root):
    entries = []
    for path in sorted(Path(root).rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root)
        if {".git", "__pycache__", ".pytest_cache", ".runtime"}.intersection(relative.parts):
            continue
        if path.is_symlink():
            entries.append([relative.as_posix(), "symlink", os.readlink(path)])
        elif path.is_file() and path.suffix != ".pyc":
            entries.append([relative.as_posix(), "file", hashlib.sha256(path.read_bytes()).hexdigest()])
    return canonical_digest(entries)


def run_check(root, pack_id, capability_id=None):
    root = Path(root).resolve()
    pack = load_pack(root, pack_id)
    _, active, task = active_task(root, pack["task_id"])
    _, _, starts, checks = stores(root)
    work = runtime().read_json(starts / f"{pack_id}.json")
    if not work or work.get("status") != "WORK_SESSION_READY":
        raise ValueError("work session has not started from this capability pack")
    refs = pack["capability_refs"]
    if len(refs) != 1 and not capability_id:
        raise ValueError("a multi-capability pack requires an exact check capability ID")
    capability_id = capability_id or refs[0]["capability_id"]
    reference = next((row for row in refs if row["capability_id"] == capability_id), None)
    if not reference:
        raise ValueError("configured project check does not match the selected capability")
    check_identity = reference["project_check_identity"]
    command = reference.get("project_check_command")
    if command != configured_check(root / "docs/nulnul/project.md"):
        raise ValueError("configured project check changed after Pack construction")
    if checks.exists() and any(
        runtime().read_json(path, {}).get("pack_id") == pack_id
        and runtime().read_json(path, {}).get("capability_id") == capability_id
        for path in checks.glob("*.json")
    ):
        raise ValueError("project check already ran for this pack capability")
    started = runtime().record_event(root, "CHECK_STARTED", task["task_id"], {
        "pack_id": pack_id, "capability_id": capability_id,
    })
    before = scientific_tree_digest(root)
    completed = subprocess.run(
        command, cwd=root, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        check=False,
    )
    after = scientific_tree_digest(root)
    result = "pass" if completed.returncode == 0 else "fail"
    finished = runtime().record_event(root, "CHECK_COMPLETED", task["task_id"], {
        "pack_id": pack_id, "capability_id": capability_id,
        "exit_code": completed.returncode, "result": result,
    })
    created_at = now()
    source = {
        "session_id": active["session_id"],
        "task_id": task["task_id"],
        "pack_id": pack_id,
        "pack_digest": pack["pack_digest"],
        "capability_id": capability_id,
        "capability_digest": reference["body_digest"],
        "project_check_identity": check_identity,
        "command_hash": hashlib.sha256(command.encode()).hexdigest(),
        "product_state_id": after,
        "exit_code": completed.returncode,
        "result": result,
        "output_digest": hashlib.sha256(completed.stdout).hexdigest(),
        "completed_event_id": finished["event_id"],
        "created_at": created_at,
    }
    check_id = canonical_digest(source)
    receipt = source | {
        "schema_version": SCHEMA_VERSION,
        "check_id": check_id,
        "command": command,
        "product_state_before_check": before,
        "started_event_id": started["event_id"],
        "status": "CHECKED",
    }
    checks.mkdir(parents=True, exist_ok=True)
    runtime().write_json(checks / f"{check_id}.json", receipt)
    return receipt


def finalize_pack_task(root, pack_id, harness_evidence=None):
    """Own the authoritative check and Capability Experience finalization."""
    root = Path(root).resolve()
    pack = load_pack(root, pack_id)
    _, _, task = active_task(root, pack["task_id"])
    refs = pack["capability_refs"]
    if len(refs) != 1:
        raise ValueError("authoritative capability finalization requires one selected capability")
    _, _, starts, _ = stores(root)
    work = runtime().read_json(starts / f"{pack_id}.json")
    if not work or work.get("status") != "WORK_SESSION_READY":
        raise ValueError("work session has not started from this capability pack")
    if work.get("product_state_before_work") == scientific_tree_digest(root):
        raise ValueError("Pack task finalization requires observable product work")
    reference = refs[0]
    check = run_check(root, pack_id, reference["capability_id"])
    passed = check["result"] == "pass"
    outcome = {
        "pack_id": pack_id,
        "check_id": check["check_id"],
        "capability_id": reference["capability_id"],
        "quality": "VERIFIED",
        "observability_completeness": "COMPLETE",
        "result": "SUCCESS" if passed else "FAILURE",
        "product_outcome": "canonical project check passed" if passed else "canonical project check failed",
        "checks": [{"id": reference["project_check_identity"], "result": check["result"]}],
    }
    if harness_evidence is not None:
        if not isinstance(harness_evidence, dict):
            raise ValueError("Harness evidence must be one bounded object")
        import harness_control
        control = harness_control.current_control(root, str(harness_evidence.get("control_id", "")))
        required = ("observed_decision", "expected_effect", "actual_effect")
        if any(not isinstance(harness_evidence.get(field), str) or not harness_evidence[field].strip() for field in required):
            raise ValueError("Harness evidence is incomplete")
        cost = harness_evidence.get("harness_cost")
        if not isinstance(cost, dict) or not cost or any(
            not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0
            for value in cost.values()
        ):
            raise ValueError("Harness cost evidence is incomplete")
        outcome.update({
            "control_id": control["control_id"],
            "control_digest": control["current_digest"],
            "observed_decision": harness_evidence["observed_decision"].strip(),
            "expected_effect": harness_evidence["expected_effect"].strip(),
            "actual_effect": harness_evidence["actual_effect"].strip(),
            "harness_cost": cost,
            "harness_attribution_class": control["attribution_class"],
            "check_ids": [check["check_id"]],
            "source_refs": [f"control:{control['control_id']}@{control['current_digest']}"],
        })
    if not passed:
        outcome["verified_failure_reason"] = "the canonical Pack-owned project check failed"
    experience = runtime().finish_task(root, task["task_id"], outcome)
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "PACK_TASK_FINALIZED",
        "check": check,
        "experience": experience,
    }


def experience_facts(root, task_id, pack_id, check_id=None, capability_id=None):
    rt = runtime()
    pack = load_pack(root, pack_id, task_id)
    _, _, starts, checks = stores(root)
    work = rt.read_json(starts / f"{pack_id}.json")
    if not work or work.get("task_id") != task_id:
        raise ValueError("work-session receipt does not match the task")
    refs = pack["capability_refs"]
    facts = {
        "pack_id": pack_id,
        "pack_digest": pack["pack_digest"],
        "active_capability_ids": [row["capability_id"] for row in refs],
        "attribution_scope": "PACK" if len(refs) != 1 else "CAPABILITY",
        "pack_receipt": {
            "pack_id": pack_id,
            "pack_digest": pack["pack_digest"],
            "task_id": task_id,
            "project_revision": pack["project_revision"],
            "host": pack["host"],
            "selection_method": pack["selection_method"],
            "capability_refs": pack["capability_refs"],
        },
        "work_start_receipt": work,
        "source_refs": [f"pack:{pack_id}"],
    }
    # A multi-capability Pack is attributable only as a Pack until a future
    # contract can prove per-capability work and checks independently.
    if len(refs) != 1:
        return facts
    capability_id = capability_id or refs[0]["capability_id"]
    reference = next((row for row in refs if row["capability_id"] == capability_id), None)
    if not reference:
        raise ValueError("capability experience is not a member of its pack")
    facts.update({
        "attribution_scope": "CAPABILITY",
        "capability_id": capability_id,
        "capability_version": reference.get("version_or_digest"),
        "logical_load_target": reference["logical_load_target"],
        "body_digest": reference["body_digest"],
        "selection_evidence": reference["selection_evidence"],
        "match_evidence": reference["selection_evidence"],
        "body_active_before_work": True,
    })
    if not check_id:
        return facts
    check = rt.read_json(checks / f"{check_id}.json")
    if not check or check.get("pack_id") != pack_id or check.get("capability_id") != capability_id:
        raise ValueError("project check receipt does not match the pack capability")
    facts.update({
        "check_id": check_id,
        "check_result": check["result"],
        "success": check["result"] == "pass",
        "check_receipt": check,
        "ordering": {
            "selection": work["selection_event_id"],
            "pack_created": work["pack_created_event_id"],
            "body_included": work["body_included_event_id"],
            "work_session": work["work_session_event_id"],
            "check": check["completed_event_id"],
        },
        "source_refs": [
            f"pack:{pack_id}", f"check:{check_id}",
            f"raw:docs/nulnul/.runtime/events/{rt.read_json(rt.Store(root).active)['session_id']}.jsonl",
        ],
    })
    return facts


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("prepare")
    create.add_argument("project", type=Path)
    create.add_argument("--task-id", required=True)
    create.add_argument("--host", choices=sorted(HOST_BODY_ROOTS), required=True)
    create.add_argument("--select", action="append", default=[])
    create.add_argument("--no-capability", action="store_true")
    create.add_argument("--evidence")
    create.add_argument("--root", type=Path, default=Path("."))
    boot = sub.add_parser("bootstrap")
    boot.add_argument("project", type=Path)
    boot.add_argument("--task-id", required=True)
    boot.add_argument("--host", choices=sorted(HOST_BODY_ROOTS), required=True)
    boot.add_argument("--select", action="append", default=[])
    boot.add_argument("--no-capability", action="store_true")
    boot.add_argument("--evidence")
    boot.add_argument("--root", type=Path, default=Path("."))
    start = sub.add_parser("work-start")
    start.add_argument("--pack-id", required=True)
    start.add_argument("--root", type=Path, default=Path("."))
    final = sub.add_parser("finalize")
    final.add_argument("--pack-id", required=True)
    final.add_argument("--root", type=Path, default=Path("."))
    final.add_argument("--harness-evidence", type=Path)
    inspect = sub.add_parser("inspect")
    inspect.add_argument("--pack-id", required=True)
    inspect.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            payload = prepare(
                args.root, args.project, args.task_id, args.host, args.select,
                args.evidence, args.no_capability,
            )
        elif args.command == "bootstrap":
            payload = bootstrap(
                args.root, args.project, args.task_id, args.host, args.select,
                args.evidence, args.no_capability,
            )
        elif args.command == "work-start":
            payload = work_start(args.root, args.pack_id)
        elif args.command == "finalize":
            payload = finalize_pack_task(
                args.root, args.pack_id,
                runtime().read_json(args.harness_evidence) if args.harness_evidence else None,
            )
        else:
            payload = load_pack(args.root, args.pack_id)
        failed = False
    except (OSError, UnicodeError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        payload = {"status": "failed", "error": str(error)}
        failed = True
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    raise SystemExit(failed)


if __name__ == "__main__":
    main()
