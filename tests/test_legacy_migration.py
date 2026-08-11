import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins/nulnul-harness/skills/nulnul-harness"
SCRIPT = SKILL / "scripts/migrate_legacy_checkpoint.py"


class LegacyMigrationTests(unittest.TestCase):
    def copy_fixture(self, directory):
        target = Path(directory) / "project"
        shutil.copytree(ROOT / "tests/fixtures/legacy-1.3.0", target)
        return target

    def migrate(self, contract, guidance):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(contract), str(guidance)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_legacy_contract_migrates_without_claiming_verification(self):
        with tempfile.TemporaryDirectory() as directory:
            target = self.copy_fixture(directory)
            contract = target / "docs/nulnul/project.md"
            guidance = target / "AGENTS.md"
            guidance.chmod(0o640)
            result = self.migrate(contract, guidance)
            checkpoint = json.loads((contract.parent / "checkpoint.json").read_text(encoding="utf-8"))
            self.assertEqual(result["status"], "created")
            self.assertEqual(checkpoint["verification_status"], "unknown")
            self.assertEqual(checkpoint["goal"], "Ship the legacy project safely.")
            self.assertEqual(checkpoint["permission_constraints"], [
                "No external writes.",
                "Deployment requires explicit approval.",
            ])
            self.assertIn("Active checkpoint: `docs/nulnul/checkpoint.json`", contract.read_text(encoding="utf-8"))
            self.assertIn("docs/nulnul/checkpoint.json", guidance.read_text(encoding="utf-8"))
            self.assertEqual(guidance.stat().st_mode & 0o777, 0o640)

    def test_existing_evolution_state_prevents_a_second_writer(self):
        with tempfile.TemporaryDirectory() as directory:
            target = self.copy_fixture(directory)
            contract = target / "docs/nulnul/project.md"
            evolution = contract.with_name("evolution.json")
            evolution.write_text("{}\n", encoding="utf-8")
            before = contract.read_text(encoding="utf-8")
            result = self.migrate(contract, target / "AGENTS.md")
            self.assertEqual(result["status"], "skipped")
            self.assertFalse(contract.with_name("checkpoint.json").exists())
            self.assertEqual(contract.read_text(encoding="utf-8"), before)

    def test_host_protected_guidance_is_never_modified(self):
        with tempfile.TemporaryDirectory() as directory:
            target = self.copy_fixture(directory)
            contract = target / "docs/nulnul/project.md"
            protected = target / ".claude/AGENTS.md"
            protected.parent.mkdir()
            protected.write_text("protected\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(contract), str(protected)],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(contract.with_name("checkpoint.json").exists())
            self.assertEqual(protected.read_text(encoding="utf-8"), "protected\n")

    def test_1_3_1_checkpoint_keeps_values_but_requires_reverification(self):
        with tempfile.TemporaryDirectory() as directory:
            target = self.copy_fixture(directory)
            contract = target / "docs/nulnul/project.md"
            checkpoint_path = contract.with_name("checkpoint.json")
            checkpoint_path.write_text(json.dumps({
                "schema_version": 1,
                "goal": "Keep this value",
                "milestone": "And this milestone",
                "completion_check": "python3 -m unittest -v",
                "last_verified": "3 tests passed",
                "next_action": "Continue the old task",
                "approved_permissions": [],
                "blockers": [],
            }), encoding="utf-8")
            result = self.migrate(contract, target / "AGENTS.md")
            checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
            self.assertEqual(result["status"], "upgraded")
            self.assertEqual(checkpoint["goal"], "Keep this value")
            self.assertEqual(checkpoint["next_action"], "Continue the old task")
            self.assertEqual(checkpoint["verification_status"], "unknown")
            self.assertEqual(checkpoint["permission_constraints"], [
                "No external writes.",
                "Deployment requires explicit approval.",
            ])


if __name__ == "__main__":
    unittest.main()
