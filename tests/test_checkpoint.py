import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins/nulnul-harness/skills/nulnul-harness"
spec = importlib.util.spec_from_file_location(
    "validate_checkpoint", SKILL / "scripts/validate_checkpoint.py"
)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)
sys.path.insert(0, str(SKILL / "scripts"))
import run_checkpoint_check as runner


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "app.py").write_text("value = 1\n", encoding="utf-8")
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
            verification_files=["app.py"],
        )
        self.evidence = {
            "schema_version": 1,
            "verification_status": "verified",
            "verification_files": self.checkpoint["verification_files"],
            "verification_fingerprint": validator.verification_fingerprint(
                self.root, self.checkpoint["verification_files"]
            ),
        }

    def test_complete_checkpoint_is_valid(self):
        self.assertEqual(validator.validate(self.checkpoint), [])
        self.assertTrue(validator.fast_path_ready(self.checkpoint, self.root, self.evidence))

    def test_receipt_schema_version_requires_integer_one(self):
        for version in (True, False, 1.0, "1", None, [], {}, 0, 2):
            with self.subTest(version=version):
                evidence = {**self.evidence, "schema_version": version}
                self.assertFalse(validator.fast_path_ready(self.checkpoint, self.root, evidence))
        self.assertTrue(validator.fast_path_ready(self.checkpoint, self.root, self.evidence))

    def test_malformed_fields_are_rejected_before_running_a_check(self):
        path = self.root / "checkpoint.json"
        for field, value in (
            ("schema_version", []), ("schema_version", True), ("schema_version", 3.0),
            ("verification_status", {}), ("verification_status", []),
            ("verification_files", [{}]), ("verification_files", ["app.py", []]),
            ("verification_files", ["bad\0file.py"]),
        ):
            with self.subTest(field=field, value=value):
                payload = {**self.checkpoint, field: value}
                path.write_text(json.dumps(payload), encoding="utf-8")
                self.assertTrue(validator.validate(payload))
                self.assertFalse(validator.fast_path_ready(payload, self.root, self.evidence))
                with patch.object(runner.subprocess, "run") as command:
                    self.assertFalse(runner.run(path, self.root, 1)["passed"])
                command.assert_not_called()

    def test_interrupted_or_unstarted_recheck_invalidates_prior_success(self):
        path = self.root / "checkpoint.json"
        for failure in (KeyboardInterrupt(), OSError("cannot start check")):
            with self.subTest(failure=type(failure).__name__):
                runner.record_verification(path, self.checkpoint, self.root, "verified")
                with patch.object(runner.subprocess, "run", side_effect=failure):
                    with self.assertRaises(type(failure)):
                        runner.run(path, self.root, 1)
                payload = json.loads(path.read_text(encoding="utf-8"))
                evidence = json.loads(path.with_name("checkpoint.verification.json").read_text())
                self.assertEqual(payload["verification_status"], "unknown")
                self.assertFalse(validator.fast_path_ready(payload, self.root, evidence))

    def test_only_verified_checkpoints_can_take_the_fast_path(self):
        for status in ("unknown", "failed"):
            self.checkpoint["verification_status"] = status
            self.assertEqual(validator.validate(self.checkpoint), [])
            self.assertFalse(validator.fast_path_ready(self.checkpoint, self.root, self.evidence))
        self.checkpoint["verification_status"] = "claimed"
        self.assertIn(
            "verification_status must be verified, failed, or unknown",
            validator.validate(self.checkpoint),
        )
        legacy = {key: value for key, value in self.checkpoint.items() if key not in {
            "verification_files"
        }}
        legacy["schema_version"] = 2
        legacy["verification_status"] = "verified"
        self.assertEqual(validator.validate(legacy), [])
        self.assertFalse(validator.fast_path_ready(legacy, self.root, self.evidence))
        legacy["schema_version"] = 99
        self.assertEqual(validator.validate(legacy), ["schema_version must be 1, 2, or 3"])

    def test_product_mutation_makes_old_verified_evidence_stale(self):
        self.assertTrue(validator.fast_path_ready(self.checkpoint, self.root, self.evidence))
        (self.root / "app.py").write_text("value = 2\n", encoding="utf-8")
        self.assertFalse(validator.fast_path_ready(self.checkpoint, self.root, self.evidence))
        self.assertEqual(
            validator.freshness_errors(self.checkpoint, self.root, self.evidence),
            ["verification fingerprint is stale"],
        )

    def test_verification_files_are_bounded_relative_regular_files(self):
        for name in ("../app.py", "/tmp/app.py", "folder\\app.py"):
            self.checkpoint["verification_files"] = [name]
            self.assertIn(
                "verification_files must contain normalized relative file paths",
                validator.validate(self.checkpoint),
            )

    def test_nonempty_old_evidence_does_not_make_a_legacy_checkpoint_fresh(self):
        self.checkpoint["schema_version"] = 2
        self.checkpoint.pop("verification_files")
        self.checkpoint["last_verified"] = "old completion evidence still exists"
        self.assertEqual(validator.validate(self.checkpoint), [])
        self.assertFalse(validator.fast_path_ready(self.checkpoint, self.root, self.evidence))

    def test_missing_check_and_sensitive_field_are_rejected(self):
        self.checkpoint["completion_check"] = ""
        self.checkpoint["token"] = "do-not-store"
        errors = validator.validate(self.checkpoint)
        self.assertIn("completion_check must be a non-empty string", errors)
        self.assertIn("prohibited sensitive field: token", errors)

    def test_completion_check_must_be_an_executable_command(self):
        self.checkpoint["completion_check"] = "npm test passes (1/1), and validation reports ok"
        self.assertIn(
            "completion_check must be an exact command, not a result description",
            validator.validate(self.checkpoint),
        )
        path = self.root / "checkpoint.json"
        self.checkpoint.update(
            completion_check=f'"{sys.executable}" -c "raise SystemExit(0)"',
            verification_status="unknown",
        )
        path.write_text(json.dumps(self.checkpoint), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(SKILL / "scripts/run_checkpoint_check.py"), str(path), "--root", str(self.root)],
            capture_output=True,
            text=True,
        )
        updated = json.loads(path.read_text(encoding="utf-8"))
        evidence = json.loads(path.with_name("checkpoint.verification.json").read_text(encoding="utf-8"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(updated["verification_status"], "verified")
        self.assertEqual(evidence["verification_files"], ["app.py"])
        self.assertTrue(validator.fast_path_ready(updated, self.root, evidence))

    def test_failed_completion_check_blocks_fast_resume(self):
        path = self.root / "checkpoint.json"
        self.checkpoint["completion_check"] = f'"{sys.executable}" -c "raise SystemExit(1)"'
        path.write_text(json.dumps(self.checkpoint), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(SKILL / "scripts/run_checkpoint_check.py"), str(path), "--root", str(self.root)],
            capture_output=True,
            text=True,
        )
        updated = json.loads(path.read_text(encoding="utf-8"))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(updated["verification_status"], "failed")
        self.assertFalse(validator.fast_path_ready(updated, self.root, None))

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
