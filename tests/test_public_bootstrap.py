import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/nulnul-harness"


class PublicBootstrapTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.plugin = self.root / "cache/nulnul-harness/installed-version"
        shutil.copytree(PLUGIN, self.plugin, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        self.scripts = self.plugin / "skills/nulnul-harness/scripts"

    def project(self, name):
        root = self.root / name
        root.mkdir()
        (root / "verify.py").write_text("assert 2 + 2 == 4\n", encoding="utf-8")
        for entry in ("AGENTS.md", "CLAUDE.md"):
            (root / entry).write_text(f"# Existing {entry}\n", encoding="utf-8")
        return root

    def govern(self, root, host="claude", passed=True):
        result = subprocess.run(
            [sys.executable, str(self.scripts / "activation_boundary.py"), "govern",
             "new-setup", "--host", host, "--root", str(root)],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0 if passed else 1, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def execute(self, root, receipt, host="claude", passed=True):
        plan = {
            "schema_version": 2, "mode": "new-setup", "host": host,
            "goal": "Preserve a verified local utility.",
            "milestone": "Create a resumable checkpoint.",
            "completion_check": f"{sys.executable} verify.py",
            "verification_files": ["verify.py"],
            "constraints": ["No external writes or protected host configuration changes."],
            "roster": {"skills": ["nulnul-harness: inspected public plugin"],
                       "plugins": ["nulnul-harness"], "agents": ["reviewer: reuse"]},
            "agent_topology": "One owner; existing reviewer is kept for bounded verification.",
            "accepted_capabilities": [],
        }
        path = self.root / "setup-plan.json"
        path.write_text(json.dumps(plan), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(self.scripts / "setup_transaction.py"), str(path),
             "--root", str(root), "--governed-receipt", receipt],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0 if passed else 1, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        if not passed:
            self.assertEqual(payload["failed_phase"], "governed-authority")
            self.assertFalse((root / "docs/nulnul/checkpoint.json").exists())
        return payload

    def test_public_package_bootstraps_both_hosts_without_shadow_skills(self):
        for host in ("codex", "claude"):
            with self.subTest(host=host):
                root = self.project(host)
                inactive = root / ("CLAUDE.md" if host == "codex" else "AGENTS.md")
                before = inactive.read_bytes()
                governed = self.govern(root, host)
                self.assertEqual(governed["contract_source"], "executing-plugin")
                self.assertEqual(Path(governed["load_target"]), self.scripts.parent / "SKILL.md")
                result = self.execute(root, governed["activation_receipt"], host)
                self.assertEqual(result["status"], "SETUP_TRANSACTION_PASS")
                self.assertEqual(inactive.read_bytes(), before)
                self.assertFalse((root / ".claude").exists())
                self.assertFalse((root / ".agents").exists())
                self.assertFalse((root / ".codex").exists())
                self.assertTrue(result["completion_check"]["fast_path_ready"])

    def test_public_package_rejects_stale_foreign_and_unsafe_contracts(self):
        root = self.project("original")
        receipt = self.govern(root)["activation_receipt"]
        self.execute(self.project("different-project"), receipt, passed=False)
        self.execute(root, self.govern(root, "codex")["activation_receipt"], passed=False)
        for path in (
            self.scripts.parent / "SKILL.md", self.scripts / "setup_transaction.py",
            self.scripts / "activation_boundary.py", self.plugin / ".claude-plugin/plugin.json",
        ):
            with self.subTest(stale=path.name):
                original = path.read_bytes()
                path.write_bytes(original + b"\n")
                self.execute(root, receipt, passed=False)
                path.write_bytes(original)
        manifest = self.plugin / ".claude-plugin/plugin.json"
        original_manifest = manifest.read_bytes()
        foreign_metadata = json.loads(original_manifest)
        foreign_metadata["name"] = "foreign"
        manifest.write_text(json.dumps(foreign_metadata), encoding="utf-8")
        self.govern(root, passed=False)
        manifest.unlink()
        self.govern(root, passed=False)
        manifest.write_bytes(original_manifest)
        skill = self.scripts.parent / "SKILL.md"
        original_skill = skill.read_bytes()
        skill.unlink()
        self.govern(root, passed=False)
        foreign = self.root / "foreign.md"
        foreign.write_bytes(original_skill)
        skill.symlink_to(foreign)
        self.govern(root, passed=False)
        skill.unlink()
        skill.write_bytes(original_skill)
        local = root / ".claude/skills/nulnul-harness/SKILL.md"
        local.parent.mkdir(parents=True)
        local.symlink_to(foreign)
        self.govern(root, passed=False)
        local.unlink()
        foreign_script = self.root / "activation_boundary.py"
        foreign_script.write_text("# not the executing package\n", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "-c",
             "import sys; from pathlib import Path; sys.path.insert(0, sys.argv[1]); "
             "import activation_boundary as guard; "
             "guard.governed_stage(Path(sys.argv[2]), Path(sys.argv[3]), 'new-setup', 'claude')",
             str(self.scripts), str(foreign_script), str(root)],
            capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("executing package is unsafe", result.stderr)
