import importlib.util
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


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
        self.assertEqual(detector.check(self.workspace, ("AGENTS.md",)), [])

    def test_code_committed_after_the_document_is_reported(self):
        self.commit("first", AGENTS__md="guidance")
        self.commit("second", app__py="print('hi')\n")
        stale = detector.check(self.workspace, ("AGENTS.md",))
        self.assertEqual([entry["document"] for entry in stale], ["AGENTS.md"])
        self.assertEqual(stale[0]["newest_source"], "app.py")

    def test_uncommitted_document_edit_does_not_clear_the_debt(self):
        self.commit("first", AGENTS__md="guidance")
        self.commit("second", app__py="print('hi')\n")
        (self.workspace / "AGENTS.md").write_text("touched but not committed", encoding="utf-8")
        self.assertEqual(len(detector.check(self.workspace, ("AGENTS.md",))), 1)


if __name__ == "__main__":
    unittest.main()
