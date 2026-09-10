"""Privacy-bounded projection of existing runtime events, not a second event writer."""

import hashlib
import re
from functools import lru_cache
from pathlib import Path

IDENTITY = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,159}")
DIGEST = re.compile(r"[a-f0-9]{64}")
KINDS = {
    "SESSION_STARTED", "TASK_STARTED", "CONTEXT_ASSEMBLED", "CAPABILITY_SELECTED",
    "CAPABILITY_PACK_CREATED", "CAPABILITY_BODY_INCLUDED", "WORK_SESSION_STARTED",
    "CHECK_STARTED", "CHECK_COMPLETED", "CAPABILITY_EXPERIENCE_ATTRIBUTED",
    "TASK_COMPLETED", "TASK_FAILED", "SESSION_FINALIZED",
}
IDS = {"pack_id", "capability_id", "experience_id", "recovered_from"}
HASHES = {"pack_digest", "check_id"}
COUNTS = {"item_count", "byte_count"}
ENUMS = {
    "result": {"pass", "fail"},
    "status": {"COMPLETED", "PARTIAL", "BLOCKED", "ABORTED", "RECOVERED"},
    "method": {
        "explicit", "explicit-selection", "semantic", "semantic-selection",
        "deterministic-unique", "deterministic-no-match", "deterministic-no-candidates",
        "deterministic-strong-match", "unique-strong-match", "no-capability",
    },
}


def identity(value):
    if not isinstance(value, str) or re.match(r"^(?:sk-|ghp_|github_pat_|xox[baprs]-|AKIA|ASIA)", value):
        return None
    return value if IDENTITY.fullmatch(value) else None


@lru_cache(maxsize=1)
def producer_digest():
    digest = hashlib.sha256()
    root = Path(__file__).resolve().parent
    for name in ("foundation_runtime.py", "capability_pack.py", "run_checkpoint_check.py",
                 "validate_checkpoint.py", "trace_evidence.py"):
        digest.update(name.encode("utf-8") + b"\0")
        digest.update((root / name).read_bytes() + b"\0")
    return digest.hexdigest()


def revision(value):
    if isinstance(value, str) and re.fullmatch(r"(?:[a-f0-9]{7,64}|v?\d+\.\d+\.\d+(?:[-.][A-Za-z0-9]+)*)", value):
        return value
    return "unknown"


def project_event(event, active):
    """Whitelist only IDs, hashes, counters and enums. Never copy goals or raw details."""
    if event.get("kind") not in KINDS:
        return None
    session_id = identity(event.get("session_id"))
    task_id = event.get("task_id")
    if not session_id or (task_id is not None and not identity(task_id)):
        return None
    if not isinstance(active, dict) or active.get("session_id") != session_id:
        return None
    sequence = event.get("event_id")
    if type(sequence) is not int or not 0 < sequence < 2**53:
        return None
    details = {}
    source_details = event.get("details", {})
    if not isinstance(source_details, dict):
        return None
    for key, value in source_details.items():
        if key in IDS and identity(value):
            details[key] = value
        elif key in HASHES and isinstance(value, str) and DIGEST.fullmatch(value):
            details[key] = value
        elif key in COUNTS and type(value) is int and 0 <= value < 2**53:
            details[key] = value
        elif key == "exit_code" and type(value) is int and -(2**31) <= value < 2**31:
            details[key] = value
        elif key == "capability_ids" and isinstance(value, list) and len(value) <= 16:
            if all(identity(item) for item in value):
                details[key] = value
        elif key in ENUMS and isinstance(value, str) and value in ENUMS[key]:
            details[key] = value
    fingerprint = active.get("host_fingerprint", {})
    if not isinstance(fingerprint, dict):
        return None
    host = fingerprint.get("host", "unknown")
    return {
        "schema_version": 1,
        "producer": "nulnul-harness",
        "producer_digest": producer_digest(),
        "session_id": session_id,
        "task_id": task_id,
        "event_id": sequence,
        "kind": event["kind"],
        "created_at": event["created_at"],
        "host": host if host in {"codex", "claude"} else "unknown",
        "host_session_key": identity(active.get("trace_host_session_key")),
        "project_revision": revision(active.get("project_revision")),
        "harness_revision": revision(active.get("nulnul_revision")),
        "details": details,
    }
