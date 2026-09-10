"""One bounded check for projection privacy and command-bound checkpoint receipts."""

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "plugins/nulnul-harness/skills/nulnul-harness/scripts"
sys.path.insert(0, str(SCRIPTS))
import trace_evidence
import run_checkpoint_check
import validate_checkpoint


class TraceEvidenceTests(unittest.TestCase):
    def test_projection_and_receipt_negative_controls(self):
        active = {
            "session_id": "ses-example", "trace_host_session_key": "thread-example",
            "host_fingerprint": {"host": "codex", "configuration": {"token": "PRIVATE"}},
            "project_revision": "abcdef1234567", "nulnul_revision": "3.1.0",
            "user_goal": "PRIVATE",
        }
        event = {
            "event_id": 1, "session_id": "ses-example", "task_id": "tsk-example",
            "kind": "CAPABILITY_SELECTED", "created_at": "2026-09-09T00:00:00+00:00",
            "details": {"pack_id": "pack-example", "capability_ids": ["validation"],
                        "command": "PRIVATE", "stdout": "PRIVATE", "token": "PRIVATE"},
        }
        projected = trace_evidence.project_event(event, active)
        self.assertEqual(projected["host_session_key"], "thread-example")
        self.assertEqual(projected["details"]["capability_ids"], ["validation"])
        self.assertNotIn("PRIVATE", json.dumps(projected))
        self.assertIsNone(trace_evidence.project_event(event, {**active, "session_id": "other"}))
        self.assertIsNone(trace_evidence.project_event({**event, "event_id": True}, active))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "task.txt").write_text("same input", encoding="utf-8")
            checkpoint = root / "checkpoint.json"
            payload = {"schema_version": 3, "completion_check": "original check", "verification_files": ["task.txt"]}
            self.assertEqual(run_checkpoint_check.record_verification(checkpoint, payload, root, "verified"), [])
            receipt = json.loads((root / "checkpoint.verification.json").read_text())
            self.assertEqual(receipt["completion_check_digest"], hashlib.sha256(b"original check").hexdigest())
            self.assertEqual(validate_checkpoint.freshness_errors(payload, root, receipt), [])
            changed = {**payload, "completion_check": "different check"}
            self.assertTrue(validate_checkpoint.freshness_errors(changed, root, receipt))
            (root / "task.txt").write_text("changed input", encoding="utf-8")
            self.assertTrue(validate_checkpoint.freshness_errors(payload, root, receipt))


if __name__ == "__main__":
    unittest.main()
