#!/usr/bin/env python3
"""Move closed evolution history out of the default resume context."""

import argparse
import copy
import hashlib
import json
from pathlib import Path

import validate_autonomous_evolution
import validate_evolution_state
from sync_host_entry import atomic_batch_write


COLLECTIONS = ("feedback", "proposals", "promotions", "autonomous_episodes")
TERMINAL_PROPOSALS = {"accepted", "rejected", "rolled_back"}


def encoded(payload):
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def archive_path(state_path, state):
    manifest = state.get("archive")
    name = manifest.get("path") if isinstance(manifest, dict) else "evolution.archive.json"
    if not isinstance(name, str) or Path(name).name != name:
        raise ValueError("archive.path must be a file name beside evolution.json")
    return state_path.with_name(name)


def empty_archive(source_schema_version):
    return {
        "schema_version": 1,
        "source_schema_version": source_schema_version,
        "records": {name: [] for name in COLLECTIONS},
    }


def load_archive(state_path, state):
    manifest = state.get("archive")
    if manifest is None:
        return empty_archive(state.get("schema_version"))
    path = archive_path(state_path, state)
    if not path.is_file() or path.is_symlink():
        raise ValueError("evolution archive is missing or not a regular file")
    text = path.read_text(encoding="utf-8")
    if digest(text) != manifest.get("sha256"):
        raise ValueError("evolution archive digest does not match active state")
    archive = json.loads(text)
    if archive.get("schema_version") != 1 or not isinstance(archive.get("records"), dict):
        raise ValueError("evolution archive must be a schema-version-1 object")
    for name in COLLECTIONS:
        if not isinstance(archive["records"].get(name), list):
            raise ValueError(f"evolution archive records.{name} must be an array")
    counts = manifest.get("counts")
    if not isinstance(counts, dict) or any(
        counts.get(name) != len(archive["records"][name]) for name in COLLECTIONS
    ):
        raise ValueError("evolution archive counts do not match active state")
    return archive


def reconstruct(active, archive):
    full = copy.deepcopy(active)
    full.pop("archive", None)
    for name in COLLECTIONS:
        rows = archive["records"][name] + active.get(name, [])
        ids = [row.get("id") for row in rows if isinstance(row, dict)]
        if len(ids) != len(set(ids)):
            raise ValueError(f"evolution archive duplicates a {name} id")
        full[name] = rows
    return full


def read_full(state_path):
    active = json.loads(state_path.read_text(encoding="utf-8"))
    return reconstruct(active, load_archive(state_path, active))


def validate_full(payload):
    errors = validate_evolution_state.validate(payload)
    if payload.get("schema_version") == 4:
        errors.extend(validate_autonomous_evolution.validate(payload))
    if errors:
        raise ValueError("invalid reconstructed evolution state: " + "; ".join(errors))


def split(payload):
    proposals = payload["proposals"]
    promotions = payload["promotions"]
    keep_proposals = {
        row["id"] for row in proposals if row.get("status") not in TERMINAL_PROPOSALS
    }
    for agent_id in payload["agents"]:
        accepted = [
            row for row in proposals
            if row.get("target_agent") == agent_id and row.get("status") == "accepted"
        ]
        if accepted:
            keep_proposals.add(max(accepted, key=lambda row: row["to_version"])["id"])

    referenced_feedback = {
        feedback_id
        for row in proposals if row.get("id") in keep_proposals
        for feedback_id in row.get("feedback_ids", [])
    }
    active_feedback = [
        row for row in payload["feedback"]
        if row.get("status") in {"pending", "triaged"} or row.get("id") in referenced_feedback
    ]
    for row in active_feedback:
        keep_proposals.update(row.get("rejected_proposals", []))

    active = copy.deepcopy(payload)
    active.pop("archive", None)
    active["feedback"] = active_feedback
    active["proposals"] = [row for row in proposals if row.get("id") in keep_proposals]
    active["promotions"] = [
        row for row in promotions if row.get("proposal_id") in keep_proposals
    ]
    active["autonomous_episodes"] = []

    active_ids = {
        name: {row["id"] for row in active[name]}
        for name in COLLECTIONS
    }
    archived = {
        name: [row for row in payload.get(name, []) if row["id"] not in active_ids[name]]
        for name in COLLECTIONS
    }
    return active, archived


def check(state_path):
    active = json.loads(state_path.read_text(encoding="utf-8"))
    archive = load_archive(state_path, active)
    validate_full(reconstruct(active, archive))
    return {
        "valid": True,
        "active_bytes": state_path.stat().st_size,
        "archive_counts": {name: len(archive["records"][name]) for name in COLLECTIONS},
    }


def compact(state_path):
    before = state_path.stat().st_size
    current = json.loads(state_path.read_text(encoding="utf-8"))
    full = read_full(state_path)
    validate_full(full)
    active, records = split(full)
    if not any(records.values()) and "archive" not in current:
        return {"status": "unchanged", "active_bytes_before": before, "active_bytes_after": before}

    archive = {
        "schema_version": 1,
        "source_schema_version": full["schema_version"],
        "records": records,
    }
    archive_text = encoded(archive)
    active["archive"] = {
        "schema_version": 1,
        "path": "evolution.archive.json",
        "sha256": digest(archive_text),
        "counts": {name: len(records[name]) for name in COLLECTIONS},
    }
    active_text = encoded(active)
    errors = validate_evolution_state.validate(active)
    if errors:
        raise ValueError("invalid compacted evolution state: " + "; ".join(errors))
    validate_full(reconstruct(active, archive))
    atomic_batch_write({state_path: active_text, archive_path(state_path, active): archive_text})
    return {
        "status": "compacted",
        "active_bytes_before": before,
        "active_bytes_after": len(active_text.encode()),
        "archive_counts": active["archive"]["counts"],
    }


def rejected_for(state_path, agent):
    active = json.loads(state_path.read_text(encoding="utf-8"))
    full = reconstruct(active, load_archive(state_path, active))
    promotions = {row["proposal_id"]: row for row in full["promotions"]}
    return [
        {
            "id": row["id"],
            "status": row["status"],
            "mechanism_id": row.get("mechanism_id"),
            "pathology": row.get("pathology"),
            "cause": row["cause"],
            "gate_result": promotions.get(row["id"], {}).get("after"),
        }
        for row in full["proposals"]
        if row.get("target_agent") == agent and row.get("status") in {"rejected", "rolled_back"}
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("state", type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--rejected-for")
    args = parser.parse_args()
    try:
        if args.check:
            result = check(args.state)
        elif args.rejected_for:
            result = {"proposals": rejected_for(args.state, args.rejected_for)}
        else:
            result = compact(args.state)
        failed = False
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        result = {"status": "failed", "error": str(error)}
        failed = True
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(failed)


if __name__ == "__main__":
    main()
