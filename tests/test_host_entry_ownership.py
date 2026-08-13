import hashlib
import importlib.util
import tempfile
import unittest
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


if __name__ == "__main__":
    unittest.main()
