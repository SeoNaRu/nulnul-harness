import json
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "claude_adopt_evidence", ROOT / "scripts/claude_adopt_evidence.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ClaudeAdoptEvidenceTests(unittest.TestCase):
    def test_git_marketplace_with_exact_github_url_is_public_source(self):
        outputs = [
            '[{"id":"nulnul-harness@nulnul-harness","version":"2.0.0-rc.2"}]',
            '[{"name":"nulnul-harness","source":"git","url":"https://github.com/SeoNaRu/nulnul-harness.git"}]',
        ]
        with patch.object(MODULE.subprocess, "run") as run:
            run.side_effect = [type("Result", (), {"stdout": output}) for output in outputs]
            self.assertEqual(MODULE.installed_plugin(), ("2.0.0-rc.2", "github"))

    def test_bounded_shell_roster_read_counts(self):
        calls = [{
            "name": "Bash",
            "input": {"command": 'for f in .claude/agents/*; do cat "$f"; done'},
        }]
        self.assertTrue(MODULE.roster_was_read(calls, {"collector": {}, "reviewer": {}}))

    def test_explicit_bounded_agent_reads_count(self):
        calls = [{
            "name": "Bash",
            "input": {
                "command": (
                    "cat .claude/agents/collector.md; "
                    "cat .claude/agents/reviewer.md"
                )
            },
        }]
        self.assertTrue(MODULE.roster_was_read(calls, {"collector": {}, "reviewer": {}}))

    def test_printed_agent_paths_do_not_count_as_reads(self):
        calls = [{
            "name": "Bash",
            "input": {
                "command": (
                    "echo cat .claude/agents/collector.md; "
                    "echo cat .claude/agents/reviewer.md"
                )
            },
        }]
        self.assertFalse(MODULE.roster_was_read(calls, {"collector": {}, "reviewer": {}}))

    def test_release_identity_and_positioning_are_required(self):
        evidence = json.loads(
            (ROOT / "evals/benchmarks/claude-adopt/evidence.json").read_text(encoding="utf-8")
        )
        evidence.pop("distribution")
        evidence["public_positioning_violations"] = 1
        errors = MODULE.validate(evidence, "1.7.0")
        self.assertIn("Claude adopt evidence release tag is stale", errors)
        self.assertIn("Claude adopt evidence public positioning regressed", errors)
