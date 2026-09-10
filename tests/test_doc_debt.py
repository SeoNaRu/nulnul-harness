import importlib.util
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
DETECTOR = ROOT / "plugins/nulnul-harness/skills/nulnul-harness/scripts/check_doc_debt.py"

spec = importlib.util.spec_from_file_location("check_doc_debt", DETECTOR)
detector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(detector)


class DocDebtTests(unittest.TestCase):
    """The workspace has no git history, so these cover the modification-time path."""

    def setUp(self):
        self.workspace = Path(tempfile.mkdtemp())
        self.document = self.workspace / "AGENTS.md"
        self.source = self.workspace / "app.py"
        self.document.write_text("guidance", encoding="utf-8")
        self.source.write_text("print('hi')\n", encoding="utf-8")

    def touch(self, path, when):
        os.utime(path, (when, when))

    def test_source_newer_than_the_document_is_reported(self):
        self.touch(self.document, 1_000)
        self.touch(self.source, 2_000)
        stale = detector.check(self.workspace, ("AGENTS.md",))
        self.assertEqual([entry["document"] for entry in stale], ["AGENTS.md"])
        self.assertEqual(stale[0]["newest_source"], "app.py")

    def test_updated_document_clears_the_debt(self):
        self.touch(self.source, 2_000)
        self.touch(self.document, 3_000)
        self.assertEqual(detector.check(self.workspace, ("AGENTS.md",)), [])

    def test_missing_document_is_not_reported(self):
        self.touch(self.source, 2_000)
        self.document.unlink()
        self.assertEqual(detector.check(self.workspace, ("AGENTS.md",)), [])

    def test_non_source_files_do_not_create_debt(self):
        self.source.unlink()
        (self.workspace / "notes.txt").write_text("scratch", encoding="utf-8")
        self.touch(self.document, 1_000)
        self.touch(self.workspace / "notes.txt", 5_000)
        self.assertEqual(detector.check(self.workspace, ("AGENTS.md",)), [])

    def test_empty_source_result_is_reused_across_documents(self):
        self.source.unlink()
        (self.workspace / "README.md").write_text("readme", encoding="utf-8")
        with mock.patch.object(detector, "newest_source_by_mtime", wraps=detector.newest_source_by_mtime) as scan:
            self.assertEqual(detector.check(self.workspace, ("AGENTS.md", "README.md")), [])
        self.assertEqual(scan.call_count, 1)

    def test_fallback_scans_once_and_preserves_source_scope(self):
        nested = self.workspace / "nested"
        nested.mkdir()
        (nested / ".sql").write_text("select 1", encoding="utf-8")
        (nested / "app.tsx").write_text("source", encoding="utf-8")
        (nested / "notes.txt").write_text("not source", encoding="utf-8")
        ignored = self.workspace / ".git"
        ignored.mkdir()
        (ignored / "hook.py").write_text("not source", encoding="utf-8")
        self.touch(self.source, 1000)
        self.touch(nested / "app.tsx", 1500)
        self.touch(nested / ".sql", 2000)
        with mock.patch.object(os, "scandir", wraps=os.scandir) as scan:
            self.assertEqual(detector.newest_source_by_mtime(self.workspace), nested / ".sql")
        self.assertEqual(scan.call_count, 2)


class DocDebtGitTests(unittest.TestCase):
    """Commit times decide, so a document fixed in the same commit is not flagged."""

    def setUp(self):
        self.workspace = Path(tempfile.mkdtemp())
        self.git("git", "init", "-q")
        self.git("git", "config", "user.email", "test@example.com")
        self.git("git", "config", "user.name", "test")

    def git(self, *command):
        subprocess.run(command, cwd=self.workspace, check=True, capture_output=True)

    def commit(self, message, **files):
        for name, content in files.items():
            path = self.workspace / name.replace("__", ".")
            path.write_text(content, encoding="utf-8")
        self.git("git", "add", "-A")
        self.git("git", "commit", "-qm", message)

    def test_document_committed_with_its_code_is_not_reported(self):
        self.commit("first", AGENTS__md="guidance", app__py="print('hi')\n")
        with mock.patch.object(
            detector, "newest_source_by_mtime", side_effect=AssertionError("unneeded scan")
        ):
            self.assertEqual(detector.check(self.workspace, ("AGENTS.md",)), [])

    def test_code_committed_after_the_document_is_reported(self):
        self.commit("first", AGENTS__md="guidance")
        self.commit("second", app__py="print('hi')\n")
        stale = detector.check(self.workspace, ("AGENTS.md",))
        self.assertEqual([entry["document"] for entry in stale], ["AGENTS.md"])
        self.assertEqual(stale[0]["newest_source"], "app.py")

    def test_uncommitted_document_edit_clears_the_debt(self):
        self.commit("first", AGENTS__md="guidance")
        self.commit("second", app__py="print('hi')\n")
        (self.workspace / "AGENTS.md").write_text("touched but not committed", encoding="utf-8")
        self.assertEqual(detector.check(self.workspace, ("AGENTS.md",)), [])

    def test_uncommitted_source_with_clean_document_is_reported(self):
        self.commit("first", AGENTS__md="guidance", app__py="print('hi')\n")
        (self.workspace / "app.py").write_text("print('changed')\n", encoding="utf-8")
        stale = detector.check(self.workspace, ("AGENTS.md",))
        self.assertEqual(stale, [{"document": "AGENTS.md", "newest_source": "app.py"}])

    def test_active_host_excludes_the_inactive_root_entry(self):
        self.commit("roots", AGENTS__md="codex", CLAUDE__md="claude")
        self.commit("source", app__py="print('hi')\n")
        self.commit("codex docs", AGENTS__md="codex updated")
        self.assertEqual(detector.check(self.workspace, host="codex"), [])
        self.assertEqual(
            [entry["document"] for entry in detector.check(self.workspace, host="claude")],
            ["CLAUDE.md"],
        )


if __name__ == "__main__":
    unittest.main()
