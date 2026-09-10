#!/usr/bin/env python3
"""Bounded session, experience, memory, context, and evolution operating layer."""

import argparse
import contextlib
import datetime as dt
import hashlib
import json
import os
import platform
import re
import sys
import uuid
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))
import capability_contract
import trace_evidence
from sync_host_entry import atomic_batch_write, atomic_write


SCHEMA_VERSION = 1
MAX_CONTEXT_ITEMS = 8
MAX_CONTEXT_BYTES = 4096
MAX_SEARCH_ITEMS_PER_TYPE = 128
SESSION_STATES = {"STARTED", "ACTIVE", "COMPLETED", "PARTIAL", "BLOCKED", "ABORTED", "RECOVERED"}
EXPERIENCE_TYPES = {"TASK_EXPERIENCE", "CAPABILITY_EXPERIENCE", "GOVERNED_EXPERIENCE", "RECOVERY_EXPERIENCE"}
QUALITY_STATES = {"VERIFIED", "PARTIAL", "UNATTRIBUTED", "INVALID"}
MEMORY_STATES = {"ACTIVE", "SUPERSEDED", "RETIRED", "COMPACTED"}
EVENT_TYPES = {
    "SESSION_STARTED", "TASK_STARTED", "CONTEXT_ASSEMBLED", "CAPABILITY_OPPORTUNITY",
    "CAPABILITY_SELECTION_REQUIRED", "CAPABILITY_SELECTED", "CAPABILITY_PACK_CREATED",
    "CAPABILITY_BODY_INCLUDED", "WORK_SESSION_STARTED", "CAPABILITY_EXPERIENCE_ATTRIBUTED",
    "GOVERNED_ACTIVATED", "TOOL_EXECUTION", "FILE_READ", "FILE_WRITE", "CHECK_STARTED",
    "CHECK_COMPLETED", "DECISION", "ERROR", "TASK_COMPLETED", "TASK_FAILED", "SESSION_FINALIZED",
    "SETUP_PLAN_CREATED", "SETUP_TRANSACTION_STARTED", "PROJECT_CONTRACT_WRITTEN",
    "CAPABILITY_CONTRACT_VALIDATED", "HOST_ENTRY_WRITTEN",
    "CHECKPOINT_WRITTEN", "SETUP_VALIDATED", "SETUP_ROLLED_BACK", "SETUP_COMPLETED",
    "AGENT_TOPOLOGY_SELECTED", "AGENT_TASK_BOUND", "AGENT_HANDOFF_RECORDED",
    "AGENT_EXPERIENCE_ATTRIBUTED", "TOPOLOGY_EXPERIENCE_ATTRIBUTED",
}
COMPLETENESS = {"COMPLETE", "PARTIAL", "MINIMAL"}
HARNESS_ATTRIBUTION_CLASSES = {
    "HARNESS_SELECTION_POLICY", "HARNESS_CONTEXT_POLICY", "HARNESS_AGENT_POLICY",
    "HARNESS_VERIFICATION_POLICY", "HARNESS_MEMORY_POLICY",
}
SECRET_KEYS = re.compile(
    r"(?:api[_-]?key|(?:^|[_-])(?:auth|authorization|token|password|passwd|secret|credential)(?:$|[_-]))",
    re.I,
)
TERMS = re.compile(r"[a-z0-9][a-z0-9._/-]*", re.I)
ID_PREFIXES = {
    "session": "ses", "task": "tsk", "experience": "exp", "decision": "dec", "lesson": "les",
}
LAYER_FIELDS = {
    "id", "purpose", "input", "output", "durable_state_owned", "mutation_authority",
    "observability_produced", "provenance_produced", "next_layer", "must_not_own",
}


def utc_now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def make_id(kind):
    return f"{ID_PREFIXES[kind]}-{dt.datetime.now(dt.timezone.utc):%Y%m%dT%H%M%SZ}-{uuid.uuid4().hex[:12]}"


def encoded(payload):
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def digest(payload):
    data = payload if isinstance(payload, bytes) else json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(data).hexdigest()


def redact(value):
    if isinstance(value, dict):
        return {key: "[REDACTED]" if SECRET_KEYS.search(str(key)) else redact(item) for key, item in value.items()}
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


def harness_policy(root, control_id, defaults):
    current = Path(root).resolve() / "docs/nulnul/harness-controls.json"
    if not current.exists():
        return dict(defaults), False
    import harness_control
    return harness_control.project_policy(root, control_id, defaults)


def tokens(*values):
    return sorted({term.lower() for value in values for term in TERMS.findall(str(value)) if len(term) > 1})


def read_json(path, default=None):
    if not path.exists():
        return default
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"state path must be one regular file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path):
    if not path.exists():
        return []
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"state path must be one regular file: {path}")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path, payload):
    atomic_write(path, encoded(redact(payload)))


def write_jsonl(path, rows):
    atomic_write(path, "".join(json.dumps(redact(row), ensure_ascii=False, sort_keys=True) + "\n" for row in rows))


class Store:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.nulnul = self.root / "docs/nulnul"
        self.memory = self.nulnul / "memory"
        self.sessions = self.memory / "sessions"
        self.experiences = self.memory / "experiences"
        self.index = self.memory / "index.json"
        self.decisions = self.memory / "decisions.jsonl"
        self.lessons = self.memory / "lessons.jsonl"
        self.open_threads = self.memory / "open-threads.json"
        self.handoff = self.memory / "handoff.json"
        self.local = self.nulnul / ".runtime"
        self.raw = self.local / "raw"
        self.active = self.local / "active-session.json"
        self.lock = self.local / "writer.lock"
        self.retention = self.local / "retention.json"

    def initialize(self):
        if not self.root.is_dir():
            raise ValueError("project root must be one existing directory")
        self.sessions.mkdir(parents=True, exist_ok=True)
        self.experiences.mkdir(parents=True, exist_ok=True)
        self.local.mkdir(parents=True, exist_ok=True)
        ignore = self.nulnul / ".gitignore"
        start, end = "# nulnul:local-runtime:start", "# nulnul:local-runtime:end"
        block = f"{start}\n.runtime/\n{end}"
        current = ignore.read_text(encoding="utf-8") if ignore.exists() else ""
        if start not in current:
            atomic_write(ignore, (current.rstrip() + "\n\n" if current.strip() else "") + block + "\n")
        if not self.index.exists():
            write_json(self.index, empty_index())
        if not self.open_threads.exists():
            write_json(self.open_threads, {"schema_version": SCHEMA_VERSION, "threads": []})
        if not self.retention.exists():
            write_json(self.retention, {
                "schema_version": SCHEMA_VERSION,
                "raw_evidence": {"mode": "keep", "days": None},
            })


def empty_index():
    return {
        "schema_version": SCHEMA_VERSION,
        "active_session_id": None,
        "sessions": [],
        "experiences": [],
        "search": [],
        "updated_at": utc_now(),
    }


def process_alive(pid):
    try:
        os.kill(pid, 0)
    except (OSError, TypeError, ValueError):
        return False
    return True


@contextlib.contextmanager
def writer(store):
    store.local.mkdir(parents=True, exist_ok=True)
    token = uuid.uuid4().hex
    payload = {"pid": os.getpid(), "token": token, "created_at": utc_now()}
    # ponytail: one project-wide lock is enough until concurrent writers become supported.
    for attempt in range(2):
        try:
            descriptor = os.open(store.lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                handle.write(encoded(payload))
            break
        except FileExistsError:
            owner = read_json(store.lock, {})
            if attempt == 0 and not process_alive(owner.get("pid")):
                store.lock.unlink(missing_ok=True)
                continue
            raise RuntimeError("another NULNUL session writer owns this project")
    try:
        yield
    finally:
        current = read_json(store.lock, {})
        if current.get("token") == token:
            store.lock.unlink(missing_ok=True)


def load_index(store):
    payload = read_json(store.index, empty_index())
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported memory index schema")
    return payload


def save_index(store, index):
    index["updated_at"] = utc_now()
    by_type = {}
    for item in index.get("search", []):
        by_type.setdefault(item["type"], []).append(item)
    index["search"] = [
        item
        for kind in sorted(by_type)
        for item in sorted(by_type[kind], key=lambda row: row.get("created_at", ""), reverse=True)[:MAX_SEARCH_ITEMS_PER_TYPE]
    ]
    write_json(store.index, index)


def host_fingerprint(
    host="unknown", host_version=None, model=None, configuration=None, nulnul_revision=None,
    project_revision=None, host_trust=None, admission_state=None, capability_digests=None,
    platform_name=None, project_root=None,
):
    payload = redact({
        "host": host or "unknown",
        "host_version": host_version or "unknown",
        "model": model or "unknown",
        "configuration": configuration or {},
        "nulnul_revision": nulnul_revision or "unknown",
        "project_revision": project_revision or "unknown",
        "project_root_identity": digest(str(Path(project_root).resolve()).encode()) if project_root else "unknown",
        "platform": platform_name or platform.platform(),
        "host_trust": host_trust or "unknown",
        "admission_state": admission_state or "unknown",
        "active_capability_digests": sorted(capability_digests or []),
    })
    payload["fingerprint_id"] = digest(payload)
    return payload


def append_event(store, session_id, task_id, kind, details=None):
    if kind not in EVENT_TYPES:
        raise ValueError(f"unknown runtime event: {kind}")
    path = store.local / "events" / f"{session_id}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = read_jsonl(path)
    event = {
        "event_id": len(rows) + 1,
        "kind": kind,
        "session_id": session_id,
        "task_id": task_id,
        "created_at": utc_now(),
        "details": redact(details or {}),
    }
    # Keep the transport projection out of CLI/model output. The same writer owns it.
    projection = trace_evidence.project_event(event, read_json(store.active, {}) or {})
    rows.append(event | {"trace": projection} if projection is not None else event)
    write_jsonl(path, rows)
    return event


def _finalize_active(store, active, status, next_handoff=None, completeness="PARTIAL"):
    if status not in SESSION_STATES - {"STARTED", "ACTIVE", "RECOVERED"}:
        raise ValueError("invalid final session status")
    if completeness not in COMPLETENESS:
        raise ValueError("invalid observability completeness")
    if status == "COMPLETED" and any(task.get("status") != "COMPLETED" for task in active.get("tasks", [])):
        raise ValueError("a session with unfinished tasks cannot be marked COMPLETED")
    active["status"] = status
    active["ended_at"] = utc_now()
    active["observability_completeness"] = completeness
    active["next_handoff"] = next_handoff or active.get("next_handoff") or ""
    record = {
        key: active.get(key)
        for key in (
            "schema_version", "session_id", "host_fingerprint", "started_at", "ended_at", "status",
            "user_goal", "task_ids", "important_changes", "verification_results", "capability_activations",
            "capability_packs", "governed_activations", "decision_ids", "experience_ids", "failures", "open_threads",
            "next_handoff", "observability_completeness", "project_revision", "nulnul_revision",
            "recovered_from", "source_refs", "provenance",
        )
    }
    handoff = {
        "schema_version": SCHEMA_VERSION,
        "session_id": active["session_id"],
        "done": [task["goal"] for task in active["tasks"] if task.get("status") == "COMPLETED"],
        "failed": [task["goal"] for task in active["tasks"] if task.get("status") in {"FAILED", "ABORTED"}],
        "open": active.get("open_threads", []),
        "next": active["next_handoff"],
        "important_decisions": active.get("decision_ids", []),
        "relevant_memory_ids": active.get("experience_ids", []) + active.get("decision_ids", []),
        "current_checkpoint": active.get("current_checkpoint"),
        "created_at": utc_now(),
        "derived_from": [f"session:{active['session_id']}"],
    }
    append_event(store, active["session_id"], None, "SESSION_FINALIZED", {"status": status})
    atomic_batch_write({
        store.sessions / f"{active['session_id']}.json": encoded(redact(record)),
        store.handoff: encoded(redact(handoff)),
    })
    index = load_index(store)
    index["active_session_id"] = None
    if active["session_id"] not in index["sessions"]:
        index["sessions"].append(active["session_id"])
    save_index(store, index)
    store.active.unlink(missing_ok=True)
    return record


def start_session(root, goal, fingerprint, current_checkpoint=None, session_id=None):
    store = Store(root)
    store.initialize()
    with writer(store):
        previous = read_json(store.active)
        recovered_from = None
        recovery_experience = None
        if previous:
            recovered_from = previous["session_id"]
            previous.setdefault("failures", []).append("session ended before finalization")
            previous.setdefault("open_threads", []).append({"thread": "Recover interrupted session", "status": "ACTIVE"})
            recovery_task = next(
                (task for task in reversed(previous.get("tasks", [])) if task.get("status") == "ACTIVE"),
                None,
            )
            if recovery_task is None:
                recovery_task = {
                    "task_id": make_id("task"),
                    "goal": "Recover interrupted session",
                    "job": "Interrupted session recovery",
                    "tags": ["recovery"],
                    "modules": [],
                    "status": "BLOCKED",
                    "started_at": previous["started_at"],
                }
                previous.setdefault("task_ids", []).append(recovery_task["task_id"])
                previous.setdefault("tasks", []).append(recovery_task)
            recovery_task["status"] = "BLOCKED"
            recovery_task["ended_at"] = utc_now()
            recovery_experience = normalize_experience(store, previous, recovery_task, {
                "experience_type": "RECOVERY_EXPERIENCE",
                "quality": "PARTIAL",
                "result": "BLOCKED",
                "product_outcome": "Recovered only the evidence available from an interrupted session",
                "verified_failure_reason": "session ended before finalization",
            })
            write_json(store.experiences / f"{recovery_experience['experience_id']}.json", recovery_experience)
            previous.setdefault("experience_ids", []).append(recovery_experience["experience_id"])
            _finalize_active(store, previous, "PARTIAL", "Recover available evidence", "PARTIAL")
        prior_handoff = read_json(store.handoff)
        identity = session_id or make_id("session")
        initial_context = context_pack(store.root, goal)
        fingerprint = redact(dict(fingerprint))
        fingerprint["project_root_identity"] = digest(str(store.root).encode())
        fingerprint["fingerprint_id"] = digest({
            key: value for key, value in fingerprint.items() if key != "fingerprint_id"
        })
        if current_checkpoint is None:
            states = [
                path.relative_to(store.root).as_posix()
                for path in (store.nulnul / "checkpoint.json", store.nulnul / "evolution.json")
                if path.is_file() and not path.is_symlink()
            ]
            current_checkpoint = states[0] if len(states) == 1 else None
        record = {
            "schema_version": SCHEMA_VERSION,
            "session_id": identity,
            "host_fingerprint": redact(fingerprint),
            # Explicit host identity only. Never infer a session from cwd or recency.
            "trace_host_session_key": trace_evidence.identity(
                os.environ.get("NULNUL_TRACE_SESSION")
                or (os.environ.get("CODEX_THREAD_ID") if fingerprint.get("host") == "codex" else None)
            ),
            "started_at": utc_now(),
            "ended_at": None,
            "status": "RECOVERED" if recovered_from else "STARTED",
            "user_goal": goal,
            "task_ids": [],
            "tasks": [],
            "important_changes": [],
            "verification_results": [],
            "capability_activations": [],
            "capability_packs": [],
            "agent_topologies": [],
            "governed_activations": [],
            "decision_ids": [],
            "experience_ids": [],
            "failures": [],
            "open_threads": [],
            "next_handoff": "",
            "current_checkpoint": current_checkpoint,
            "observability_completeness": "MINIMAL",
            "project_revision": fingerprint.get("project_revision", "unknown"),
            "nulnul_revision": fingerprint.get("nulnul_revision", "unknown"),
            "recovered_from": recovered_from,
            "source_refs": [f"session:{recovered_from}"] if recovered_from else [],
            "provenance": {"created_by": "foundation_runtime", "schema_version": SCHEMA_VERSION},
            "previous_handoff": prior_handoff,
            "initial_context_pack": initial_context,
        }
        write_json(store.active, record)
        index = load_index(store)
        if recovery_experience:
            index["experiences"].append(recovery_experience["experience_id"])
            _add_search(index, "experience", recovery_experience)
        index["active_session_id"] = identity
        save_index(store, index)
        append_event(store, identity, None, "SESSION_STARTED", {"recovered_from": recovered_from})
        append_event(store, identity, None, "CONTEXT_ASSEMBLED", {
            "item_count": initial_context["item_count"], "byte_count": initial_context["byte_count"],
        })
        return record


def start_task(root, goal, job=None, tags=None, modules=None, task_id=None, agent_context=None):
    store = Store(root)
    store.initialize()
    with writer(store):
        active = read_json(store.active)
        if not active:
            raise ValueError("no active NULNUL session")
        identity = task_id or make_id("task")
        if identity in active["task_ids"]:
            raise ValueError("duplicate task id")
        pack = context_pack(store.root, goal, modules=modules or [])
        task = {
            "task_id": identity,
            "goal": goal,
            "job": job or goal,
            "tags": sorted(set(tags or [])),
            "modules": sorted(set(modules or [])),
            "status": "ACTIVE",
            "started_at": utc_now(),
            "context_pack": pack,
        }
        if agent_context is not None:
            required = (
                "agent_topology_id", "agent_topology_digest", "agent_id",
                "agent_contract_digest", "agent_role", "work_scope",
                "verification_owner_agent_id",
            )
            if not isinstance(agent_context, dict) or any(
                not isinstance(agent_context.get(field), str) or not agent_context[field].strip()
                for field in required
            ):
                raise ValueError("agent task context is incomplete")
            task["agent_context"] = redact(agent_context)
        active["task_ids"].append(identity)
        active["tasks"].append(task)
        active["status"] = "ACTIVE"
        write_json(store.active, active)
        append_event(store, active["session_id"], identity, "TASK_STARTED", {"job": task["job"]})
        append_event(store, active["session_id"], identity, "CONTEXT_ASSEMBLED", {
            "item_count": pack["item_count"], "byte_count": pack["byte_count"],
        })
        if agent_context is not None:
            selected = append_event(store, active["session_id"], identity, "AGENT_TOPOLOGY_SELECTED", {
                "agent_topology_id": agent_context["agent_topology_id"],
                "agent_topology_digest": agent_context["agent_topology_digest"],
            })
            bound = append_event(store, active["session_id"], identity, "AGENT_TASK_BOUND", {
                "agent_id": agent_context["agent_id"], "work_scope": agent_context["work_scope"],
            })
            task["agent_context"].update({
                "topology_selected_event_id": selected["event_id"],
                "topology_bound_event_id": bound["event_id"],
            })
            write_json(store.active, active)
        # The host injects only this compact envelope; the user goal already exists in the
        # conversation and the full Task record remains local for inspection.
        return task | {
            "model_context": {
                "session_id": active["session_id"],
                "task_id": identity,
                "items": pack["items"],
            }
        }


def agent_experience_eligibility(record):
    """Validate bounded Agent/Topology attribution without changing Capability credit."""
    reasons = []
    if record.get("agent_attribution_scope") not in {"AGENT", "TOPOLOGY"}:
        return False, ["not an Agent or Topology attributed experience"]
    if record.get("quality") != "VERIFIED":
        reasons.append("quality is not VERIFIED")
    if record.get("observability_completeness") != "COMPLETE":
        reasons.append("Agent observability is not COMPLETE")
    required = (
        "agent_topology_id", "agent_topology_digest", "verification_owner_agent_id",
        "work_scope", "agent_ordering",
    )
    reasons.extend(
        f"missing {field}" for field in required
        if record.get(field) is None or record.get(field) == ""
    )
    for field in ("agent_topology_digest", "agent_contract_digest"):
        if field in record and not re.fullmatch(r"[a-f0-9]{64}", str(record.get(field, ""))):
            reasons.append(f"invalid {field}")
    if record.get("topology_active_before_work") is not True:
        reasons.append("topology was not active before work")
    checks = record.get("check_ids", [])
    if not isinstance(checks, list) or not checks or any(
        not re.fullmatch(r"[a-f0-9]{64}", str(identity)) for identity in checks
    ):
        reasons.append("authoritative Check IDs are missing or invalid")
    ordering = record.get("agent_ordering", {})
    orders = [ordering.get(name) for name in ("topology_bound", "work_started", "check", "attribution")]
    if (
        not all(isinstance(value, int) and value > 0 for value in orders)
        or orders != sorted(orders)
        or len(set(orders)) != len(orders)
    ):
        reasons.append("Agent causal ordering is incomplete or invalid")
    if record.get("agent_attribution_scope") == "AGENT":
        for field in ("agent_id", "agent_contract_digest", "agent_role"):
            if not isinstance(record.get(field), str) or not record[field]:
                reasons.append(f"missing {field}")
        if record.get("responsibility_observed") is not True:
            reasons.append("Agent responsibility was not independently observed")
    else:
        children = record.get("child_agent_experience_ids", [])
        if not isinstance(children, list) or not children:
            reasons.append("Topology Experience has no child Agent Experiences")
    return not reasons, reasons


def harness_experience_eligibility(record):
    """Accept only observable control-attributed evidence; capability/model failures stay separate."""
    attribution = record.get("harness_attribution_class")
    if attribution not in HARNESS_ATTRIBUTION_CLASSES:
        return False, ["not a Harness-attributed experience"]
    reasons = []
    if record.get("quality") != "VERIFIED":
        reasons.append("quality is not VERIFIED")
    if record.get("observability_completeness") != "COMPLETE":
        reasons.append("Harness observability is not COMPLETE")
    if not re.fullmatch(r"control-[a-z0-9][a-z0-9-]{1,63}", str(record.get("control_id", ""))):
        reasons.append("invalid Harness CONTROL_ID")
    if not re.fullmatch(r"[a-f0-9]{64}", str(record.get("control_digest", ""))):
        reasons.append("invalid Harness control digest")
    for field in ("observed_decision", "expected_effect", "actual_effect"):
        if not isinstance(record.get(field), str) or not record[field].strip():
            reasons.append(f"missing {field}")
    cost = record.get("harness_cost")
    if not isinstance(cost, dict) or not cost or any(
        not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0
        for value in cost.values()
    ):
        reasons.append("Harness cost evidence is incomplete")
    checks = record.get("check_ids") or ([record.get("check_id")] if record.get("check_id") else [])
    if not checks or any(not re.fullmatch(r"[a-f0-9]{64}", str(identity)) for identity in checks):
        reasons.append("authoritative Check IDs are missing or invalid")
    refs = set(record.get("source_refs", []))
    if checks and not all(f"check:{identity}" in refs for identity in checks):
        reasons.append("authoritative Check source refs are missing")
    if f"control:{record.get('control_id')}@{record.get('control_digest')}" not in refs:
        reasons.append("Harness control source ref is missing")
    return not reasons, reasons


def experience_eligibility(record, project_path, *, require_current=True):
    reasons = []
    if record.get("experience_type") != "CAPABILITY_EXPERIENCE":
        return False, ["not a capability experience"]
    if record.get("quality") != "VERIFIED":
        reasons.append("quality is not VERIFIED")
    if record.get("observability_completeness") != "COMPLETE":
        reasons.append("causal observability is not COMPLETE")
    capability_id = record.get("capability_id")
    try:
        matches = [
            row for row in capability_contract.load(project_path, require_canonical=True)
            if row["capability_id"] == capability_id
        ]
        accepted = matches[0] if len(matches) == 1 else None
        if accepted is None or require_current and not accepted["accepted_current"]:
            raise ValueError("capability is not accepted/current")
    except (OSError, UnicodeError, ValueError):
        accepted = None
        reasons.append("capability is unknown" if not require_current else "capability is not accepted/current")
    required = (
        "pack_id", "pack_digest", "check_id", "body_digest", "selection_evidence",
        "product_outcome", "check_result", "success",
    )
    reasons.extend(f"missing {field}" for field in required if record.get(field) in {None, ""})
    if record.get("attribution_scope") != "CAPABILITY":
        reasons.append("individual capability attribution is unavailable")
    if record.get("body_active_before_work") is not True:
        reasons.append("capability body was not active before work")
    ordering = record.get("ordering", {})
    names = ("selection", "pack_created", "body_included", "work_session", "check", "attribution")
    orders = [ordering.get(name) for name in names]
    if (
        not all(isinstance(value, int) and value > 0 for value in orders)
        or orders != sorted(orders)
        or len(set(orders)) != len(orders)
    ):
        reasons.append("causal ordering is incomplete or invalid")
    pack = record.get("pack_receipt", {})
    work = record.get("work_start_receipt", {})
    check = record.get("check_receipt", {})
    attribution = record.get("attribution_receipt", {})
    if pack.get("pack_id") != record.get("pack_id") or pack.get("pack_digest") != record.get("pack_digest"):
        reasons.append("capability pack receipt does not match")
    refs = [row for row in pack.get("capability_refs", []) if row.get("capability_id") == capability_id]
    if len(refs) != 1:
        reasons.append("capability pack does not contain one exact capability ref")
        reference = {}
    else:
        reference = refs[0]
    if reference.get("body_digest") != record.get("body_digest"):
        reasons.append("body digest does not match capability pack")
    if accepted and record.get("logical_load_target") != accepted.get("logical_load_target"):
        reasons.append("canonical capability target does not match")
    if accepted and reference.get("logical_load_target") != accepted.get("logical_load_target"):
        reasons.append("pack capability target does not match canonical target")
    if work.get("pack_id") != record.get("pack_id") or work.get("pack_digest") != record.get("pack_digest"):
        reasons.append("work-session receipt does not link to the pack")
    if work.get("body_digests", {}).get(capability_id) != record.get("body_digest"):
        reasons.append("work-session body digest does not match")
    if check.get("check_id") != record.get("check_id") or check.get("pack_id") != record.get("pack_id"):
        reasons.append("check receipt does not link to the capability pack")
    if check.get("capability_id") != capability_id:
        reasons.append("check receipt does not link to the capability")
    if (
        attribution.get("pack_id") != record.get("pack_id")
        or attribution.get("check_id") != record.get("check_id")
        or attribution.get("capability_id") != capability_id
    ):
        reasons.append("attribution receipt does not link to pack, capability, and check")
    if check.get("result") != record.get("check_result"):
        reasons.append("check result does not match receipt")
    expected_success = str(check.get("result", "")).lower() in {"pass", "passed", "success"}
    if not isinstance(record.get("success"), bool) or record.get("success") is not expected_success:
        reasons.append("success does not match check receipt")
    if record.get("result") != ("SUCCESS" if expected_success else "FAILURE"):
        reasons.append("experience result does not match check receipt")
    receipt_orders = {
        "selection": work.get("selection_event_id"),
        "pack_created": work.get("pack_created_event_id"),
        "body_included": work.get("body_included_event_id"),
        "work_session": work.get("work_session_event_id"),
        "check": check.get("completed_event_id"),
        "attribution": attribution.get("event_id"),
    }
    for name, value in receipt_orders.items():
        if value != ordering.get(name):
            reasons.append(f"{name} order does not match its receipt")
    source_refs = set(record.get("source_refs", []))
    if f"pack:{record.get('pack_id')}" not in source_refs:
        reasons.append("capability pack source reference is missing")
    if f"check:{record.get('check_id')}" not in source_refs:
        reasons.append("check source reference is missing")
    if not any(reference.startswith("raw:") for reference in source_refs):
        reasons.append("ordered raw evidence reference is missing")
    for field in ("command_hash", "product_state_id", "output_digest"):
        if not re.fullmatch(r"[a-f0-9]{64}", str(check.get(field, ""))):
            reasons.append(f"check receipt is missing {field}")
    if not isinstance(check.get("exit_code"), int):
        reasons.append("check receipt is missing exit_code")
    if require_current and accepted and accepted.get("version_or_digest") and record.get("capability_version") not in {
        accepted["version_or_digest"], None,
    }:
        reasons.append("capability version or digest is stale")
    return not reasons, reasons


def normalize_experience(store, active, task, outcome):
    experience_type = outcome.get("experience_type", "TASK_EXPERIENCE")
    if experience_type not in EXPERIENCE_TYPES:
        raise ValueError("invalid experience type")
    quality = outcome.get("quality", "PARTIAL")
    if quality not in QUALITY_STATES:
        raise ValueError("invalid experience quality")
    result = outcome.get("result", "BLOCKED")
    if result not in {"SUCCESS", "FAILURE", "BLOCKED"}:
        raise ValueError("invalid experience result")
    checks = outcome.get("checks", [])
    observability = outcome.get("observability_completeness", active.get("observability_completeness", "MINIMAL"))
    if observability not in COMPLETENESS:
        raise ValueError("invalid experience observability completeness")
    check_results = [str(check.get("result", "")).lower() for check in checks]
    passed = {"pass", "passed", "success"}
    failed = {"fail", "failed", "failure"}
    if quality == "VERIFIED":
        if not check_results or any(value not in passed | failed for value in check_results):
            quality = "PARTIAL"
        elif result == "SUCCESS" and not all(value in passed for value in check_results):
            quality = "PARTIAL"
        elif result == "FAILURE" and (
            not any(value in failed for value in check_results) or not outcome.get("verified_failure_reason")
        ):
            quality = "PARTIAL"
        elif result == "BLOCKED":
            quality = "PARTIAL"
    control_candidate = outcome.get("control_candidate")
    if control_candidate is not None:
        refs = control_candidate.get("evidence_refs", []) if isinstance(control_candidate, dict) else []
        if (
            quality != "VERIFIED"
            or not isinstance(control_candidate, dict)
            or not str(control_candidate.get("suggestion", "")).strip()
            or not refs
            or any(not validate_source_ref(reference) for reference in refs)
        ):
            raise ValueError("CONTROL_CANDIDATE requires verified evidence, a suggestion, and valid evidence refs")
        control_candidate = {
            "class": "CONTROL_CANDIDATE",
            "suggestion": control_candidate["suggestion"].strip(),
            "evidence_refs": sorted(set(refs)),
        }
    identity = outcome.get("experience_id") or make_id("experience")
    if (store.experiences / f"{identity}.json").exists():
        raise ValueError("duplicate experience id")
    record = {
        "schema_version": SCHEMA_VERSION,
        "experience_id": identity,
        "experience_type": experience_type,
        "session_id": active["session_id"],
        "task_id": task["task_id"],
        "task_job": task["job"],
        "project_revision_before": outcome.get("project_revision_before", active.get("project_revision")),
        "project_revision_after": outcome.get("project_revision_after", active.get("project_revision")),
        "changes": outcome.get("changes", []),
        "checks": checks,
        "product_outcome": outcome.get("product_outcome", "unknown"),
        "result": result,
        "verified_failure_reason": outcome.get("verified_failure_reason"),
        "host_fingerprint": active["host_fingerprint"].get("fingerprint_id"),
        "quality": quality,
        "observability_completeness": observability,
        "status": "ACTIVE",
        "created_at": utc_now(),
        "derived_from": [f"session:{active['session_id']}", f"task:{task['task_id']}"],
        "source_refs": outcome.get("source_refs", []),
        "supersedes": None,
        "superseded_by": None,
        "project_revision": outcome.get("project_revision_after", active.get("project_revision")),
        "nulnul_revision": active.get("nulnul_revision"),
        "tags": sorted(set(task.get("tags", []) + outcome.get("tags", []))),
        "modules": sorted(set(task.get("modules", []) + outcome.get("modules", []))),
        "control_candidate": control_candidate,
    }
    for field in (
        "pack_id", "pack_digest", "active_capability_ids", "attribution_scope",
        "capability_id", "capability_version", "match_evidence", "selection_evidence",
        "logical_load_target", "body_digest", "body_active_before_work", "check_id",
        "check_result", "success", "ordering", "pack_receipt", "work_start_receipt",
        "check_receipt", "attribution_receipt", "governed_stage", "governed_host", "authority",
        "setup_transaction_id", "authorized_write_set", "validation_result", "restart_required",
        "rollback_result", "failure_phase",
        "agent_topology_id", "agent_topology_digest", "agent_id", "agent_contract_digest",
        "agent_role", "parent_agent_id", "work_scope", "handoff_id", "handoff_status",
        "verification_owner_agent_id", "agent_attribution_scope", "responsibility_observed",
        "topology_active_before_work", "check_ids", "agent_ordering",
        "child_agent_experience_ids", "agent_pack_binding_id",
        "control_id", "control_digest", "observed_decision", "expected_effect",
        "actual_effect", "harness_cost", "harness_attribution_class",
    ):
        if field in outcome:
            record[field] = outcome[field]
    if experience_type == "CAPABILITY_EXPERIENCE" and record.get("capability_id"):
        try:
            accepted = capability_contract.selected(
                store.nulnul / "project.md", record["capability_id"]
            )
            record["logical_load_target"] = accepted["logical_load_target"]
        except (OSError, UnicodeError, ValueError):
            pass
    eligible, reasons = experience_eligibility(record, store.nulnul / "project.md")
    record["evolution_eligible"] = eligible
    record["eligibility_reasons"] = reasons
    agent_eligible, agent_reasons = agent_experience_eligibility(record)
    record["agent_evolution_eligible"] = agent_eligible
    record["agent_eligibility_reasons"] = agent_reasons
    harness_eligible, harness_reasons = harness_experience_eligibility(record)
    record["harness_evolution_eligible"] = harness_eligible
    record["harness_eligibility_reasons"] = harness_reasons
    if experience_type == "CAPABILITY_EXPERIENCE" and any("does not match" in reason or "not accepted" in reason for reason in reasons):
        record["quality"] = "INVALID"
    return redact(record)


def search_item(kind, record):
    if kind == "experience":
        item_id = record["experience_id"]
        summary = f"{record['task_job']}: {record.get('product_outcome', 'unknown')} ({record.get('result')})"
    elif kind == "decision":
        item_id = record["decision_id"]
        summary = f"{record['decision']} — {record['why']}"
    elif kind == "lesson":
        item_id = record["lesson_id"]
        summary = record["lesson"]
    else:
        item_id = record["thread_id"]
        summary = record["thread"]
    return {
        "item_id": item_id,
        "type": kind,
        "status": record.get("status", "ACTIVE"),
        "created_at": record.get("created_at"),
        "summary": summary[:800],
        "terms": tokens(summary, record.get("scope", ""), record.get("task_job", ""), record.get("tags", []), record.get("modules", [])),
        "capability_id": record.get("capability_id"),
        "modules": record.get("modules", []),
        "quality": record.get("quality"),
        "evolution_eligible": record.get("evolution_eligible", False),
        "provenance": record.get("derived_from", []) + record.get("source_refs", []),
    }


def _add_search(index, kind, record):
    item = search_item(kind, record)
    index["search"] = [row for row in index.get("search", []) if row["item_id"] != item["item_id"]]
    index["search"].append(item)


def _promote(store, active, task, experience, candidates):
    decision_rows = read_jsonl(store.decisions)
    lesson_rows = read_jsonl(store.lessons)
    threads = read_json(store.open_threads, {"schema_version": SCHEMA_VERSION, "threads": []})
    promoted = {"decisions": [], "lessons": [], "threads": []}
    if experience["quality"] != "VERIFIED":
        return promoted
    policy, _ = harness_policy(store.root, "control-memory-promotion", {
        "minimum_repeat_count": 1, "require_verified": True,
    })
    minimum = policy["minimum_repeat_count"]
    def repeated(value, existing, field):
        return 1 + sum(row.get("status") == "ACTIVE" and row.get(field) == value for row in existing) >= minimum
    for candidate in candidates.get("decisions", []):
        if (
            not candidate.get("decision") or not candidate.get("why")
            or not repeated(candidate["decision"], decision_rows, "decision")
        ):
            continue
        row = {
            "schema_version": SCHEMA_VERSION,
            "decision_id": make_id("decision"),
            "decision": candidate["decision"],
            "why": candidate["why"],
            "session_id": active["session_id"],
            "task_id": task["task_id"],
            "derived_from": [f"experience:{experience['experience_id']}"],
            "evidence": candidate.get("evidence", []),
            "source_refs": candidate.get("source_refs", []),
            "created_at": utc_now(),
            "status": "ACTIVE",
            "supersedes": None,
            "superseded_by": None,
            "project_revision": experience.get("project_revision_after"),
            "host_fingerprint": experience.get("host_fingerprint"),
            "nulnul_revision": experience.get("nulnul_revision"),
            "scope": candidate.get("scope", "project"),
        }
        decision_rows.append(row)
        promoted["decisions"].append(row)
    for candidate in candidates.get("lessons", []):
        if (
            not candidate.get("lesson") or not candidate.get("scope")
            or not repeated(candidate["lesson"], lesson_rows, "lesson")
        ):
            continue
        row = {
            "schema_version": SCHEMA_VERSION,
            "lesson_id": make_id("lesson"),
            "lesson": candidate["lesson"],
            "scope": candidate["scope"],
            "session_id": active["session_id"],
            "task_id": task["task_id"],
            "derived_from": [f"experience:{experience['experience_id']}"],
            "evidence": candidate.get("evidence", []),
            "source_refs": candidate.get("source_refs", []),
            "created_at": utc_now(),
            "status": "ACTIVE",
            "supersedes": None,
            "superseded_by": None,
            "project_revision": experience.get("project_revision_after"),
            "host_fingerprint": experience.get("host_fingerprint"),
            "nulnul_revision": experience.get("nulnul_revision"),
        }
        lesson_rows.append(row)
        promoted["lessons"].append(row)
    for candidate in candidates.get("open_threads", []):
        if (
            not candidate.get("thread")
            or not repeated(candidate["thread"], threads["threads"], "thread")
        ):
            continue
        row = {
            "thread_id": f"thr-{uuid.uuid4().hex[:12]}",
            "thread": candidate["thread"],
            "next": candidate.get("next", ""),
            "status": "ACTIVE",
            "created_at": utc_now(),
            "derived_from": [f"experience:{experience['experience_id']}"],
            "source_refs": candidate.get("source_refs", []),
            "tags": candidate.get("tags", []),
            "modules": candidate.get("modules", []),
        }
        threads["threads"].append(row)
        promoted["threads"].append(row)
    write_jsonl(store.decisions, decision_rows)
    write_jsonl(store.lessons, lesson_rows)
    write_json(store.open_threads, threads)
    return promoted


def finish_task(root, task_id, outcome, promotions=None):
    store = Store(root)
    store.initialize()
    with writer(store):
        active = read_json(store.active)
        if not active:
            raise ValueError("no active NULNUL session")
        task = next((row for row in active["tasks"] if row["task_id"] == task_id), None)
        if not task or task.get("status") != "ACTIVE":
            raise ValueError("task is not active")
        outcome = dict(outcome)
        result = outcome.get("result", "BLOCKED")
        task["status"] = {"SUCCESS": "COMPLETED", "FAILURE": "FAILED", "BLOCKED": "BLOCKED"}.get(result, result)
        task["ended_at"] = utc_now()
        if outcome.get("pack_id"):
            # Local import keeps the host-independent state layer free of adapter imports.
            import capability_pack
            facts = capability_pack.experience_facts(
                store.root, task_id, outcome["pack_id"], outcome.get("check_id"),
                outcome.get("capability_id"),
            )
            source_refs = sorted(set(outcome.get("source_refs", []) + facts.pop("source_refs", [])))
            outcome.update(facts)
            outcome["source_refs"] = source_refs
            if outcome.get("attribution_scope") == "CAPABILITY":
                outcome["experience_type"] = "CAPABILITY_EXPERIENCE"
                if outcome.get("check_id"):
                    attributed = append_event(store, active["session_id"], task_id, "CAPABILITY_EXPERIENCE_ATTRIBUTED", {
                        "pack_id": outcome["pack_id"],
                        "capability_id": outcome["capability_id"],
                        "check_id": outcome["check_id"],
                    })
                    outcome.setdefault("ordering", {})["attribution"] = attributed["event_id"]
                    outcome["attribution_receipt"] = {
                        "pack_id": outcome["pack_id"],
                        "capability_id": outcome["capability_id"],
                        "check_id": outcome["check_id"],
                        "event_id": attributed["event_id"],
                    }
            else:
                outcome["experience_type"] = "TASK_EXPERIENCE"
        agent_context = task.get("agent_context")
        if agent_context:
            for field, value in agent_context.items():
                outcome.setdefault(field, value)
            outcome["source_refs"] = sorted(set(outcome.get("source_refs", []) + [
                f"agent:{agent_context['agent_id']}",
                f"topology:{agent_context['agent_topology_id']}@{agent_context['agent_topology_digest']}",
            ]))
            scope = outcome.get("agent_attribution_scope", "AGENT")
            event = append_event(
                store, active["session_id"], task_id,
                "AGENT_EXPERIENCE_ATTRIBUTED" if scope == "AGENT" else "TOPOLOGY_EXPERIENCE_ATTRIBUTED",
                {
                    "agent_topology_id": outcome.get("agent_topology_id"),
                    "agent_id": outcome.get("agent_id"),
                    "check_ids": outcome.get("check_ids") or ([outcome["check_id"]] if outcome.get("check_id") else []),
                },
            )
            ordering = dict(outcome.get("agent_ordering", {}))
            work = outcome.get("work_start_receipt", {})
            check = outcome.get("check_receipt", {})
            ordering.setdefault("topology_bound", agent_context.get("topology_bound_event_id"))
            ordering.setdefault("work_started", work.get("work_session_event_id"))
            ordering.setdefault("check", check.get("completed_event_id"))
            ordering["attribution"] = event["event_id"]
            outcome["agent_ordering"] = ordering
            outcome.setdefault("check_ids", [outcome["check_id"]] if outcome.get("check_id") else [])
            outcome.setdefault("topology_active_before_work", bool(
                isinstance(ordering.get("topology_bound"), int)
                and isinstance(ordering.get("work_started"), int)
                and ordering["topology_bound"] < ordering["work_started"]
            ))
            outcome.setdefault("responsibility_observed", scope == "AGENT")
        experience = normalize_experience(store, active, task, outcome)
        write_json(store.experiences / f"{experience['experience_id']}.json", experience)
        promoted = _promote(store, active, task, experience, promotions or {})
        active["experience_ids"].append(experience["experience_id"])
        active["decision_ids"].extend(row["decision_id"] for row in promoted["decisions"])
        active["important_changes"].extend(outcome.get("changes", []))
        active["verification_results"].extend(outcome.get("checks", []))
        active["observability_completeness"] = outcome.get(
            "observability_completeness", active.get("observability_completeness", "MINIMAL")
        )
        active["open_threads"].extend(promoted["threads"])
        if experience.get("pack_id") and experience["pack_id"] not in active["capability_packs"]:
            active["capability_packs"].append(experience["pack_id"])
        if experience.get("agent_topology_digest"):
            topology = {
                "agent_topology_id": experience.get("agent_topology_id"),
                "agent_topology_digest": experience["agent_topology_digest"],
            }
            if topology not in active.setdefault("agent_topologies", []):
                active["agent_topologies"].append(topology)
        if experience.get("governed_stage"):
            active["governed_activations"].append(experience["governed_stage"])
        if result == "FAILURE":
            active["failures"].append(outcome.get("verified_failure_reason") or "task failed")
        write_json(store.active, active)
        index = load_index(store)
        if experience["experience_id"] not in index["experiences"]:
            index["experiences"].append(experience["experience_id"])
        _add_search(index, "experience", experience)
        for kind, rows in promoted.items():
            singular = {"decisions": "decision", "lessons": "lesson", "threads": "thread"}[kind]
            for row in rows:
                _add_search(index, singular, row)
        save_index(store, index)
        event = "TASK_COMPLETED" if result == "SUCCESS" else "TASK_FAILED"
        append_event(store, active["session_id"], task_id, event, {"experience_id": experience["experience_id"]})
        return experience


def finalize_session(root, status="COMPLETED", next_handoff=None, completeness="PARTIAL"):
    store = Store(root)
    store.initialize()
    with writer(store):
        active = read_json(store.active)
        if not active:
            raise ValueError("no active NULNUL session")
        return _finalize_active(store, active, status, next_handoff, completeness)


def record_event(root, kind, task_id=None, details=None):
    store = Store(root)
    store.initialize()
    with writer(store):
        active = read_json(store.active)
        if not active:
            raise ValueError("no active NULNUL session")
        if kind == "CAPABILITY_PACK_CREATED":
            pack_id = (details or {}).get("pack_id")
            if not re.fullmatch(r"pack-[a-f0-9]{32}", str(pack_id or "")):
                raise ValueError("CAPABILITY_PACK_CREATED requires a valid pack identity")
        event = append_event(store, active["session_id"], task_id, kind, details)
        if kind == "CAPABILITY_PACK_CREATED":
            active.setdefault("capability_packs", [])
            if pack_id not in active["capability_packs"]:
                active["capability_packs"].append(pack_id)
        active["observability_completeness"] = "PARTIAL"
        write_json(store.active, active)
        return event


def lifecycle_update(root, kind, identity, status, supersedes=None):
    if kind not in {"decision", "lesson", "experience", "thread"} or status not in MEMORY_STATES:
        raise ValueError("invalid memory lifecycle transition")
    store = Store(root)
    store.initialize()
    with writer(store):
        if kind == "experience":
            paths = sorted(store.experiences.glob("*.json"))
            records = [read_json(path) for path in paths]
            record = next((row for row in records if row["experience_id"] == identity), None)
            if not record:
                raise ValueError("unknown experience")
        elif kind in {"decision", "lesson"}:
            path = store.decisions if kind == "decision" else store.lessons
            records = read_jsonl(path)
            id_field = f"{kind}_id"
            record = next((row for row in records if row[id_field] == identity), None)
            if not record:
                raise ValueError(f"unknown {kind}")
        else:
            path = store.open_threads
            records = read_json(path, {"threads": []})["threads"]
            record = next((row for row in records if row["thread_id"] == identity), None)
            if not record:
                raise ValueError("unknown thread")
        id_field = "thread_id" if kind == "thread" else f"{kind}_id"
        if supersedes == identity:
            raise ValueError("record cannot supersede itself")
        if supersedes:
            previous = next((row for row in records if row[id_field] == supersedes), None)
            if not previous:
                raise ValueError("superseded record is unknown")
            previous["status"] = "SUPERSEDED"
            previous["superseded_by"] = identity
            record["supersedes"] = supersedes
        record["status"] = status
        if kind == "experience":
            updates = {store.experiences / f"{row['experience_id']}.json": encoded(redact(row)) for row in records}
            atomic_batch_write(updates)
        elif kind == "thread":
            write_json(path, {"schema_version": SCHEMA_VERSION, "threads": records})
        else:
            write_jsonl(path, records)
        rebuild_search_index(store)
        return record


def compact_lessons(root):
    store = Store(root)
    store.initialize()
    with writer(store):
        rows = read_jsonl(store.lessons)
        groups = {}
        for row in rows:
            if row.get("status") == "ACTIVE":
                key = (" ".join(row["lesson"].lower().split()), row["scope"].lower())
                groups.setdefault(key, []).append(row)
        compacted = 0
        for matches in groups.values():
            if len(matches) < 2:
                continue
            survivor = sorted(matches, key=lambda row: row["created_at"])[-1]
            for old in matches:
                if old is survivor:
                    continue
                old["status"] = "COMPACTED"
                old["superseded_by"] = survivor["lesson_id"]
                survivor["derived_from"] = sorted(set(survivor.get("derived_from", []) + [f"lesson:{old['lesson_id']}"]))
                survivor["source_refs"] = sorted(set(survivor.get("source_refs", []) + old.get("source_refs", [])))
                compacted += 1
        write_jsonl(store.lessons, rows)
        rebuild_search_index(store)
        return {"status": "compacted" if compacted else "unchanged", "compacted": compacted}


def rebuild_search_index(store):
    index = load_index(store)
    index["search"] = []
    for row in read_jsonl(store.decisions):
        _add_search(index, "decision", row)
    for row in read_jsonl(store.lessons):
        _add_search(index, "lesson", row)
    for row in read_json(store.open_threads, {"threads": []})["threads"]:
        _add_search(index, "thread", row)
    for identity in index.get("experiences", [])[-MAX_SEARCH_ITEMS_PER_TYPE:]:
        row = read_json(store.experiences / f"{identity}.json")
        if row:
            _add_search(index, "experience", row)
    save_index(store, index)


def context_pack(root, task, capability_id=None, modules=None, max_items=MAX_CONTEXT_ITEMS, max_bytes=MAX_CONTEXT_BYTES):
    if max_items < 1 or max_items > MAX_CONTEXT_ITEMS or max_bytes < 256 or max_bytes > MAX_CONTEXT_BYTES:
        raise ValueError("context budget exceeds the product limit")
    store = Store(root)
    if not store.root.is_dir():
        raise ValueError("project root must be one existing directory")
    index = load_index(store)
    policy, _ = harness_policy(store.root, "control-context-ranking", {
        "module_weight": 6, "overlap_weight": 1, "same_capability_weight": 10,
    })
    query = set(tokens(task, modules or [], capability_id or ""))
    candidates = []
    for item in index.get("search", []):
        if item.get("status") != "ACTIVE" or item["type"] == "session":
            continue
        if item["type"] == "experience" and item.get("quality") != "VERIFIED":
            continue
        overlap = query.intersection(item.get("terms", []))
        same_capability = capability_id and item.get("capability_id") == capability_id
        same_module = bool(set(modules or []).intersection(item.get("modules", [])))
        if not (overlap or same_capability or same_module or item["type"] == "thread" and overlap):
            continue
        score = (
            len(overlap) * policy["overlap_weight"]
            + (policy["same_capability_weight"] if same_capability else 0)
            + (policy["module_weight"] if same_module else 0)
        )
        reason = "same capability" if same_capability else "same module" if same_module else {
            "decision": "active decision", "lesson": "active lesson", "thread": "open thread", "experience": "relevant verified experience",
        }[item["type"]]
        candidates.append((score, item.get("created_at", ""), item, reason))
    output = []
    used = 0
    seen = set()
    for _, _, item, reason in sorted(candidates, key=lambda row: (row[0], row[1]), reverse=True):
        content = item["summary"][:800]
        key = digest(content.encode())
        if key in seen:
            continue
        candidate = {
            "item_id": item["item_id"],
            "type": item["type"],
            "why_included": reason,
            "bounded_content": content,
            "provenance": item.get("provenance", []),
            "status": item["status"],
            "recency": item.get("created_at"),
        }
        size = len(json.dumps(candidate, ensure_ascii=False, separators=(",", ":")).encode())
        if len(output) >= max_items or used + size > max_bytes:
            continue
        output.append(candidate)
        used += size
        seen.add(key)
    return {
        "schema_version": SCHEMA_VERSION,
        "task": task,
        "items": output,
        "item_count": len(output),
        "byte_count": used,
        "max_items": max_items,
        "max_bytes": max_bytes,
        "raw_transcripts_included": False,
    }


def all_records(store):
    sessions = [read_json(path) for path in sorted(store.sessions.glob("*.json"))]
    active = read_json(store.active)
    if active:
        sessions.append(active)
    experiences = [read_json(path) for path in sorted(store.experiences.glob("*.json"))]
    return {
        "session": sessions,
        "experience": experiences,
        "decision": read_jsonl(store.decisions),
        "lesson": read_jsonl(store.lessons),
        "thread": read_json(store.open_threads, {"threads": []})["threads"],
    }


def validate_source_ref(reference):
    if not isinstance(reference, str) or not reference or "\x00" in reference:
        return False
    if reference.startswith("pack:"):
        return bool(re.fullmatch(r"pack:pack-[a-f0-9]{32}", reference))
    if reference.startswith(("activation:", "check:")):
        # activation: remains valid only as historical imported provenance.
        return bool(re.fullmatch(r"(?:activation|check):[a-f0-9]{64}", reference))
    if reference.startswith("git:"):
        return bool(re.fullmatch(r"git:[a-f0-9]{7,64}", reference))
    if reference.startswith(("raw:", "file:")):
        value = reference.split(":", 1)[1]
        path = Path(value.split("#", 1)[0])
        return bool(value) and not path.is_absolute() and ".." not in path.parts
    if reference.startswith("agent:"):
        return bool(re.fullmatch(r"agent:agent-[a-z0-9][a-z0-9-]{0,63}", reference))
    if reference.startswith("topology:"):
        return bool(re.fullmatch(r"topology:topology-[a-z0-9][a-z0-9-]{1,63}@[a-f0-9]{64}", reference))
    if reference.startswith("handoff:"):
        return bool(re.fullmatch(r"handoff:hnd-[a-f0-9]{32}", reference))
    if reference.startswith("control:"):
        return bool(re.fullmatch(r"control:control-[a-z0-9][a-z0-9-]{1,63}@[a-f0-9]{64}", reference))
    if reference.startswith("generalization:"):
        # Cross-project priors remain non-authoritative; this ref preserves only
        # target-local validation lineage to the approved local knowledge store.
        return bool(re.fullmatch(r"generalization:gen-[a-f0-9]{16}", reference))
    return reference.startswith(tuple(f"{kind}:" for kind in ("session", "task", "experience", "decision", "lesson", "thread")))


def validate_lineage(root):
    store = Store(root)
    if not store.root.is_dir():
        raise ValueError("project root must be one existing directory")
    records = all_records(store)
    identifiers = {
        "session": {row["session_id"] for row in records["session"]},
        "task": {identity for row in records["session"] for identity in row.get("task_ids", [])},
        "experience": {row["experience_id"] for row in records["experience"]},
        "decision": {row["decision_id"] for row in records["decision"]},
        "lesson": {row["lesson_id"] for row in records["lesson"]},
        "thread": {row["thread_id"] for row in records["thread"]},
    }
    errors = []
    for row in records["session"]:
        identity = row["session_id"]
        for reference in row.get("source_refs", []):
            if not validate_source_ref(reference):
                errors.append(f"{identity}: invalid source_ref {reference}")
                continue
            prefix, _, target = reference.partition(":")
            if prefix in identifiers and target not in identifiers[prefix]:
                errors.append(f"{identity}: dangling source_ref {reference}")
    for kind in ("experience", "decision", "lesson", "thread"):
        id_field = "thread_id" if kind == "thread" else f"{kind}_id"
        by_id = {row[id_field]: row for row in records[kind]}
        for row in records[kind]:
            identity = row[id_field]
            for reference in row.get("derived_from", []):
                prefix, _, target = reference.partition(":")
                if prefix not in identifiers or target not in identifiers[prefix]:
                    errors.append(f"{identity}: dangling derived_from {reference}")
            for reference in row.get("source_refs", []):
                if not validate_source_ref(reference):
                    errors.append(f"{identity}: invalid source_ref {reference}")
                else:
                    prefix, _, target = reference.partition(":")
                    if prefix in identifiers and target not in identifiers[prefix]:
                        errors.append(f"{identity}: dangling source_ref {reference}")
            supersedes = row.get("supersedes")
            superseded_by = row.get("superseded_by")
            if supersedes == identity or superseded_by == identity:
                errors.append(f"{identity}: self-supersession")
            if supersedes and (supersedes not in by_id or by_id[supersedes].get("superseded_by") != identity):
                errors.append(f"{identity}: broken supersedes link")
            if superseded_by and (superseded_by not in by_id or by_id[superseded_by].get("supersedes") != identity and row.get("status") != "COMPACTED"):
                errors.append(f"{identity}: broken superseded_by link")
        for identity in by_id:
            seen = set()
            current = identity
            while current and current in by_id:
                if current in seen:
                    errors.append(f"{identity}: supersession cycle")
                    break
                seen.add(current)
                current = by_id[current].get("supersedes")
    project = store.nulnul / "project.md"
    for row in records["experience"]:
        if row.get("capability_id"):
            try:
                matches = [
                    capability for capability in capability_contract.load(project, require_canonical=True)
                    if capability["capability_id"] == row["capability_id"]
                ]
                if len(matches) != 1:
                    raise ValueError("unknown historical capability")
            except (OSError, UnicodeError, ValueError):
                errors.append(f"{row['experience_id']}: invalid capability ref")
        if row.get("evolution_eligible"):
            eligible, reasons = experience_eligibility(row, project, require_current=False)
            if not eligible:
                errors.append(f"{row['experience_id']}: invalid evolution eligibility ({'; '.join(reasons)})")
        if row.get("agent_evolution_eligible"):
            eligible, reasons = agent_experience_eligibility(row)
            if not eligible:
                errors.append(f"{row['experience_id']}: invalid Agent evolution eligibility ({'; '.join(reasons)})")
            for child in row.get("child_agent_experience_ids", []):
                if child not in identifiers["experience"]:
                    errors.append(f"{row['experience_id']}: dangling child Agent Experience {child}")
        if row.get("harness_evolution_eligible"):
            eligible, reasons = harness_experience_eligibility(row)
            if not eligible:
                errors.append(f"{row['experience_id']}: invalid Harness evolution eligibility ({'; '.join(reasons)})")
    return sorted(set(errors))


def evolution_query(root, capability_id=None, job=None, since=None, limit=20):
    if limit < 1 or limit > 50:
        raise ValueError("evolution query limit must be between 1 and 50")
    store = Store(root)
    if not store.root.is_dir():
        raise ValueError("project root must be one existing directory")
    index = load_index(store)
    rows = []
    for item in index.get("search", []):
        if item["type"] != "experience" or item.get("status") != "ACTIVE":
            continue
        record = read_json(store.experiences / f"{item['item_id']}.json")
        if not record or record.get("quality") != "VERIFIED" or not record.get("evolution_eligible"):
            continue
        if capability_id and record.get("capability_id") != capability_id:
            continue
        if job and job.lower() not in record.get("task_job", "").lower():
            continue
        rows.append(record)
    rows.sort(key=lambda row: row["created_at"])
    if since:
        boundaries = [row["created_at"] for row in rows if since in {row.get("capability_version"), row.get("body_digest")}]
        rows = [row for row in rows if row["created_at"] > max(boundaries)] if boundaries else []
    rows = rows[-limit:]
    return {
        "schema_version": SCHEMA_VERSION,
        "filters": {"capability_id": capability_id, "job": job, "since": since, "limit": limit},
        "count": len(rows),
        "experiences": rows,
    }


def validate_layer_registry(path=None):
    path = path or Path(__file__).resolve().parent.parent / "assets/layer-contracts.json"
    payload = read_json(path)
    errors = []
    if not payload or payload.get("schema_version") != 1 or payload.get("cross_cutting") != "identity_and_provenance":
        errors.append("invalid layer registry header")
        return errors
    layers = payload.get("layers", [])
    ids = [row.get("id") for row in layers]
    if len(layers) != 12 or len(ids) != len(set(ids)):
        errors.append("layer registry must contain 12 unique layers")
    for row in layers:
        missing = sorted(LAYER_FIELDS - set(row))
        if missing:
            errors.append(f"{row.get('id', '<unknown>')}: missing {', '.join(missing)}")
        if row.get("next_layer") not in ids:
            errors.append(f"{row.get('id', '<unknown>')}: unknown next layer")
    return errors


def structured_file_reads(arguments):
    """Return positive path operands from structured argv; glob exclusions are never reads."""
    ignored_next = False
    option_values = {"-g", "--glob", "-t", "--type", "--type-add", "-e", "--regexp", "-f", "--file"}
    result = []
    for index, value in enumerate(arguments):
        if ignored_next:
            ignored_next = False
            continue
        if value in option_values:
            ignored_next = True
            continue
        if value.startswith("!") or value.startswith("-") or index == 0:
            continue
        if "/" in value or Path(value).suffix in {".json", ".md", ".py", ".toml", ".yaml", ".yml"}:
            result.append(value)
    return result


def classify_failure(evidence_interpretable, stage):
    if not evidence_interpretable:
        return "INFRASTRUCTURE_FAILURE"
    if stage == "product-prerequisite":
        return "PRODUCT_CONTRACT_FAILURE"
    return "PRODUCT_FAILURE"


def configure_raw_retention(root, days=None):
    """Set the local raw-evidence policy; deletion remains opt-in."""
    if days is not None and (not isinstance(days, int) or days < 1 or days > 3650):
        raise ValueError("raw retention days must be between 1 and 3650")
    store = Store(root)
    store.initialize()
    with writer(store):
        policy = {
            "schema_version": SCHEMA_VERSION,
            "raw_evidence": {"mode": "expire" if days else "keep", "days": days},
        }
        write_json(store.retention, policy)
        return policy


def inspect(store, kind, limit=10, identity=None):
    if not store.root.is_dir():
        raise ValueError("project root must be one existing directory")
    if kind == "current-session":
        return read_json(store.active, {"status": "none"})
    if kind == "sessions":
        paths = sorted(store.sessions.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True)[:limit]
        return {"sessions": [read_json(path) for path in paths]}
    if kind == "experiences":
        index = load_index(store)
        ids = index.get("experiences", [])[-limit:]
        return {"experiences": [read_json(store.experiences / f"{identity}.json") for identity in reversed(ids)]}
    if kind == "decisions":
        return {"decisions": [row for row in read_jsonl(store.decisions) if row.get("status") == "ACTIVE"][-limit:]}
    if kind == "lessons":
        return {"lessons": [row for row in read_jsonl(store.lessons) if row.get("status") == "ACTIVE"][-limit:]}
    if kind == "open-threads":
        return {"open_threads": [row for row in read_json(store.open_threads, {"threads": []})["threads"] if row.get("status") == "ACTIVE"][:limit]}
    if kind == "stats":
        records = all_records(store)
        return {
            "sessions": len(records["session"]),
            "experiences": len(records["experience"]),
            "active_decisions": sum(row.get("status") == "ACTIVE" for row in records["decision"]),
            "active_lessons": sum(row.get("status") == "ACTIVE" for row in records["lesson"]),
            "open_threads": sum(row.get("status") == "ACTIVE" for row in records["thread"]),
            "index_bytes": store.index.stat().st_size if store.index.exists() else 0,
            "raw_evidence_location": "local-only: docs/nulnul/.runtime/",
            "raw_evidence_retention": read_json(
                store.retention,
                {"schema_version": SCHEMA_VERSION, "raw_evidence": {"mode": "keep", "days": None}},
            )["raw_evidence"],
        }
    if kind == "lineage":
        if not identity:
            raise ValueError("lineage inspection requires an Experience ID")
        experience = read_json(store.experiences / f"{identity}.json")
        if not experience:
            raise ValueError("unknown experience")
        return {
            "experience": experience,
            "derived_records": [
                row
                for row in read_jsonl(store.decisions) + read_jsonl(store.lessons)
                if f"experience:{identity}" in row.get("derived_from", [])
            ],
            "lineage_errors": validate_lineage(store.root),
        }
    raise ValueError("unknown inspection surface")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    sub = parser.add_subparsers(dest="command", required=True)
    start = sub.add_parser("session-start")
    start.add_argument("--goal", required=True)
    start.add_argument("--fingerprint", type=Path)
    start.add_argument("--host", default="unknown")
    start.add_argument("--host-version")
    start.add_argument("--model")
    start.add_argument("--nulnul-revision")
    start.add_argument("--project-revision")
    start.add_argument("--host-trust")
    start.add_argument("--admission-state")
    task = sub.add_parser("task-start")
    task.add_argument("--goal", required=True)
    task.add_argument("--job")
    finish = sub.add_parser("task-finish")
    finish.add_argument("--task-id", required=True)
    finish.add_argument("--outcome", type=Path, required=True)
    finish.add_argument("--promotions", type=Path)
    final = sub.add_parser("session-finalize")
    final.add_argument("--status", choices=sorted(SESSION_STATES - {"STARTED", "ACTIVE", "RECOVERED"}), default="COMPLETED")
    final.add_argument("--next")
    final.add_argument("--completeness", choices=sorted(COMPLETENESS), default="PARTIAL")
    event = sub.add_parser("event")
    event.add_argument("kind", choices=sorted(EVENT_TYPES))
    event.add_argument("--task-id")
    event.add_argument("--details", type=Path)
    context = sub.add_parser("context")
    context.add_argument("--task", required=True)
    context.add_argument("--capability")
    context.add_argument("--module", action="append", default=[])
    query = sub.add_parser("evolution-query")
    query.add_argument("--capability")
    query.add_argument("--job")
    query.add_argument("--since")
    query.add_argument("--limit", type=int, default=20)
    view = sub.add_parser("inspect")
    view.add_argument("kind", choices=("current-session", "sessions", "experiences", "decisions", "lessons", "open-threads", "lineage", "stats"))
    view.add_argument("--limit", type=int, default=10)
    view.add_argument("--id")
    life = sub.add_parser("lifecycle")
    life.add_argument("kind", choices=("decision", "lesson", "experience", "thread"))
    life.add_argument("identity")
    life.add_argument("status", choices=sorted(MEMORY_STATES))
    life.add_argument("--supersedes")
    retention = sub.add_parser("raw-retention")
    retention.add_argument("--days", type=int)
    sub.add_parser("compact-lessons")
    sub.add_parser("validate-lineage")
    sub.add_parser("validate-layers")
    args = parser.parse_args()
    try:
        if args.command == "session-start":
            fingerprint = read_json(args.fingerprint) if args.fingerprint else host_fingerprint(
                args.host,
                args.host_version,
                args.model,
                nulnul_revision=args.nulnul_revision,
                project_revision=args.project_revision,
                host_trust=args.host_trust,
                admission_state=args.admission_state,
                project_root=args.root,
            )
            payload = start_session(args.root, args.goal, fingerprint)
        elif args.command == "task-start":
            payload = start_task(args.root, args.goal, args.job)
        elif args.command == "task-finish":
            payload = finish_task(
                args.root,
                args.task_id,
                read_json(args.outcome),
                read_json(args.promotions, {}) if args.promotions else {},
            )
        elif args.command == "session-finalize":
            payload = finalize_session(args.root, args.status, args.next, args.completeness)
        elif args.command == "event":
            payload = record_event(args.root, args.kind, args.task_id, read_json(args.details, {}) if args.details else {})
        elif args.command == "context":
            payload = context_pack(args.root, args.task, args.capability, args.module)
        elif args.command == "evolution-query":
            payload = evolution_query(args.root, args.capability, args.job, args.since, args.limit)
        elif args.command == "inspect":
            payload = inspect(Store(args.root), args.kind, args.limit, args.id)
        elif args.command == "lifecycle":
            payload = lifecycle_update(args.root, args.kind, args.identity, args.status, args.supersedes)
        elif args.command == "raw-retention":
            payload = configure_raw_retention(args.root, args.days)
        elif args.command == "compact-lessons":
            payload = compact_lessons(args.root)
        elif args.command == "validate-lineage":
            errors = validate_lineage(args.root)
            payload = {"valid": not errors, "errors": errors}
        else:
            errors = validate_layer_registry()
            payload = {"valid": not errors, "errors": errors}
        failed = payload.get("valid") is False
    except (OSError, UnicodeError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        payload = {"status": "failed", "error": str(error)}
        failed = True
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    raise SystemExit(failed)


if __name__ == "__main__":
    main()
