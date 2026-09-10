import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "plugins/nulnul-harness/skills/nulnul-harness/scripts/sync_host_entry.py"
SPEC = importlib.util.spec_from_file_location("sync_host_entry", SCRIPT)
host_entry = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(host_entry)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class HostEntryOwnershipTests(unittest.TestCase):
    def project(self, directory, state="evolution.json"):
        root = Path(directory)
        shared = root / "docs/nulnul"
        shared.mkdir(parents=True)
        (shared / "project.md").write_text("# shared setup\n", encoding="utf-8")
        (shared / state).write_text("{}\n", encoding="utf-8")
        return root

    def test_codex_first_creates_only_agents(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.project(directory)
            result = host_entry.sync(root, "codex")
            self.assertEqual(result["entry"], "AGENTS.md")
            self.assertTrue((root / "AGENTS.md").is_file())
            self.assertFalse((root / "CLAUDE.md").exists())

    def test_claude_first_creates_only_claude(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.project(directory)
            result = host_entry.sync(root, "claude")
            self.assertEqual(result["entry"], "CLAUDE.md")
            self.assertTrue((root / "CLAUDE.md").is_file())
            self.assertFalse((root / "AGENTS.md").exists())

    def test_codex_then_claude_preserves_agents_byte_for_byte(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.project(directory)
            host_entry.sync(root, "codex")
            agents = root / "AGENTS.md"
            agents.write_text("user-owned codex guidance\n\n" + agents.read_text(encoding="utf-8"), encoding="utf-8")
            before = digest(agents)
            host_entry.sync(root, "claude")
            self.assertEqual(digest(agents), before)
            self.assertIn("docs/nulnul/evolution.json", (root / "CLAUDE.md").read_text(encoding="utf-8"))

    def test_claude_then_codex_preserves_claude_byte_for_byte(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.project(directory)
            host_entry.sync(root, "claude")
            claude = root / "CLAUDE.md"
            claude.write_text("user-owned claude guidance\n\n" + claude.read_text(encoding="utf-8"), encoding="utf-8")
            before = digest(claude)
            host_entry.sync(root, "codex")
            self.assertEqual(digest(claude), before)
            self.assertIn("docs/nulnul/evolution.json", (root / "AGENTS.md").read_text(encoding="utf-8"))

    def test_existing_guidance_is_preserved_and_sync_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.project(directory, "checkpoint.json")
            protected = root / ".claude/settings.json"
            protected.parent.mkdir()
            protected.write_text('{"permissions": []}\n', encoding="utf-8")
            protected_before = digest(protected)
            target = root / "AGENTS.md"
            target.write_text("# Existing rules\n\nKeep this.\n", encoding="utf-8")
            host_entry.sync(root, "codex")
            once = target.read_text(encoding="utf-8")
            self.assertTrue(all(line == line.rstrip() for line in once.splitlines()))
            result = host_entry.sync(root, "codex")
            self.assertEqual(result["status"], "unchanged")
            self.assertEqual(target.read_text(encoding="utf-8"), once)
            self.assertIn("Keep this.", once)
            self.assertEqual(once.count(host_entry.START), 1)
            self.assertEqual(digest(protected), protected_before)

    def test_invalid_or_ambiguous_inputs_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(ValueError, "exactly one shared"):
                host_entry.sync(root, "codex")
            root = self.project(directory)
            (root / "docs/nulnul/checkpoint.json").write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "exactly one shared"):
                host_entry.sync(root, "claude")
            with self.assertRaisesRegex(ValueError, "unsupported host"):
                host_entry.sync(root, "other")

    def test_generated_commands_execute_from_project_and_reject_stale_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.project(directory, "checkpoint.json")
            scripts = root / "installed 'plugin' $literal\\copy" / "scripts"
            scripts.mkdir(parents=True)
            for name in ("validate_checkpoint.py", "run_checkpoint_check.py"):
                shutil.copy2(SCRIPT.with_name(name), scripts / name)
            (root / "input.txt").write_text("original")
            (root / "check.py").write_text(
                "from pathlib import Path\n"
                "with Path('runs.txt').open('a') as handle: handle.write('run\\n')\n"
            )
            checkpoint = root / "docs/nulnul/checkpoint.json"
            checkpoint.write_text(json.dumps({
                "schema_version": 3, "goal": "local task", "milestone": "local check",
                "completion_check": "python3 check.py", "verification_status": "unknown",
                "verification_files": ["input.txt", "check.py"], "last_verified": "none",
                "next_action": "run check", "permission_constraints": ["local only"],
                "approved_permissions": ["local check"], "blockers": [],
            }))
            inactive = root / "CLAUDE.md"
            inactive.write_text("preserve me\n")
            with patch.object(host_entry, "__file__", str(scripts / "sync_host_entry.py")):
                host_entry.sync(root, "codex")
                # Replacement must preserve shell quoting and literal backslashes too.
                host_entry.sync(root, "codex")
            commands = re.findall(r"```sh\n(.*?)\n```", (root / "AGENTS.md").read_text(), re.S)
            self.assertEqual(len(commands), 2)

            def run(command):
                result = subprocess.run(command, shell=True, cwd=root, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                return json.loads(result.stdout)

            self.assertFalse(run(commands[0])["fast_path_ready"])
            self.assertTrue(run(commands[1])["fast_path_ready"])
            self.assertTrue(run(commands[0])["fast_path_ready"])
            (root / "input.txt").write_text("changed")
            self.assertFalse(run(commands[0])["fast_path_ready"])
            self.assertEqual((root / "runs.txt").read_text(), "run\n")
            self.assertEqual(inactive.read_text(), "preserve me\n")


if __name__ == "__main__":
    unittest.main()
