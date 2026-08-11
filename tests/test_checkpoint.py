import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins/nulnul-harness/skills/nulnul-harness"
spec = importlib.util.spec_from_file_location(
    "validate_checkpoint", SKILL / "scripts/validate_checkpoint.py"
)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.checkpoint = json.loads(
            (SKILL / "assets/checkpoint.template.json").read_text(encoding="utf-8")
        )
        self.checkpoint.update(
            goal="Ship safely",
            milestone="Complete one route",
            completion_check="python3 -m unittest -v",
            verification_status="verified",
            last_verified="2 of 2 tests passed",
            next_action="Implement the next bounded request",
        )

    def test_complete_checkpoint_is_valid(self):
        self.assertEqual(validator.validate(self.checkpoint), [])
        self.assertTrue(validator.fast_path_ready(self.checkpoint))

    def test_only_verified_checkpoints_can_take_the_fast_path(self):
        for status in ("unknown", "failed"):
            self.checkpoint["verification_status"] = status
            self.assertEqual(validator.validate(self.checkpoint), [])
            self.assertFalse(validator.fast_path_ready(self.checkpoint))
        self.checkpoint["verification_status"] = "claimed"
        self.assertIn(
            "verification_status must be verified, failed, or unknown",
            validator.validate(self.checkpoint),
        )

    def test_missing_check_and_sensitive_field_are_rejected(self):
        self.checkpoint["completion_check"] = ""
        self.checkpoint["token"] = "do-not-store"
        errors = validator.validate(self.checkpoint)
        self.assertIn("completion_check must be a non-empty string", errors)
        self.assertIn("prohibited sensitive field: token", errors)

    def test_malformed_checkpoint_fails_closed_without_traceback(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "checkpoint.json"
            path.write_text("{", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SKILL / "scripts/validate_checkpoint.py"), str(path)],
                capture_output=True,
                text=True,
            )
        payload = json.loads(result.stdout)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(payload["valid"])
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
