import sys
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "plugins/nulnul-harness/skills/nulnul-harness/scripts"
sys.path.insert(0, str(SCRIPTS))
from capability_pack import scientific_tree_digest


class ProductTreeDigestTests(unittest.TestCase):
    def test_git_inputs_ignore_generated_files_but_include_tracked_ignored_and_untracked_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            (root / ".gitignore").write_text("node_modules/\ndist/\n")
            (root / "source.py").write_text("before")
            original = scientific_tree_digest(root)
            (root / "node_modules").mkdir()
            (root / "node_modules/dep.js").write_text("dependency")
            (root / "dist").mkdir()
            (root / "dist/output.js").write_text("generated")
            self.assertEqual(original, scientific_tree_digest(root))
            subprocess.run(["git", "-C", str(root), "add", "-f", "dist/output.js"], check=True)
            tracked = scientific_tree_digest(root)
            (root / "dist/output.js").write_text("tracked change")
            self.assertNotEqual(tracked, scientific_tree_digest(root))
            before = scientific_tree_digest(root)
            (root / "source.py").write_text("after")
            self.assertNotEqual(before, scientific_tree_digest(root))
            before = scientific_tree_digest(root)
            (root / "new.py").write_text("new source")
            self.assertNotEqual(before, scientific_tree_digest(root))
            before = scientific_tree_digest(root)
            (root / "source.py").unlink()
            self.assertNotEqual(before, scientific_tree_digest(root))

    def test_non_git_project_preserves_source_and_ignores_runtime(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "source.py").write_text("before")
            original = scientific_tree_digest(root)
            (root / ".runtime").mkdir()
            (root / ".runtime/event.json").write_text("event")
            self.assertEqual(original, scientific_tree_digest(root))
            (root / "source.py").write_text("after")
            self.assertNotEqual(original, scientific_tree_digest(root))
