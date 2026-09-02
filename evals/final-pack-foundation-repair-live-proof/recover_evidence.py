#!/usr/bin/env python3
"""Commit a manifest after the already-committed arm cleanup failed."""

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic_write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def write_json(path, value):
    atomic_write(path, (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode())
    if json.loads(Path(path).read_text(encoding="utf-8")) != value:
        raise ValueError(f"evidence readback failed: {path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence", type=Path)
    args = parser.parse_args()
    evidence = args.evidence.resolve()
    report_path = evidence / "final-report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    records = []
    for path in sorted((evidence / "arms").glob("*/record.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        transcript = evidence / record["raw_transcript"]
        patch = evidence / record["patch"]
        if not record.get("evidence_committed"):
            raise ValueError(f"arm was not evidence-committed: {record.get('arm_id')}")
        if sha(transcript) != record["raw_transcript_sha256"] or sha(patch) != record["patch_sha256"]:
            raise ValueError(f"arm artifact hash mismatch: {record.get('arm_id')}")
        if record["frozen_source_before"] != record["frozen_source_after"]:
            raise ValueError(f"frozen source mutation: {record.get('arm_id')}")
        records.append(record)
    if len(records) != 4 or report.get("primary_decision") != "V2.3_FOUNDATION_CORE_COMPLETE":
        raise ValueError("committed evidence does not contain the completed four-arm decision")
    atomic_write(evidence / "recover-evidence.py", Path(__file__).read_bytes())
    report["cleanup"] = {
        "workspaces": "CLEANUP_PASS",
        "codex-home": "POST_EVIDENCE_CLEANUP_FAILURE",
        "failure": "disposable auth.json symlink rejected by generic writable-copy cleanup",
        "scientific_result_affected": False,
    }
    report["evidence_recovery"] = {
        "arms_reexecuted": 0,
        "arm_records_revalidated": 4,
        "manifest_recovered_after_evidence_commit": True,
    }
    write_json(report_path, report)
    manifest = {
        path.relative_to(evidence).as_posix(): sha(path)
        for path in sorted(evidence.rglob("*"))
        if path.is_file() and path.name not in {"manifest.json", "manifest.receipt"}
    }
    write_json(evidence / "manifest.json", manifest)
    atomic_write(evidence / "manifest.receipt", (sha(evidence / "manifest.json") + "\n").encode())
    if (evidence / "manifest.receipt").read_text(encoding="utf-8").strip() != sha(evidence / "manifest.json"):
        raise ValueError("manifest receipt readback failure")
    print(json.dumps({
        "status": "pass",
        "primary_decision": report["primary_decision"],
        "arm_records": len(records),
        "manifest_sha256": sha(evidence / "manifest.json"),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
