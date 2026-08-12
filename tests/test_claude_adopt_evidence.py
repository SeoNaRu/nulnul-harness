import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "claude_adopt_evidence", ROOT / "scripts/claude_adopt_evidence.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ClaudeAdoptEvidenceTests(unittest.TestCase):
    def test_bounded_shell_roster_read_counts(self):
        calls = [{
            "name": "Bash",
            "input": {"command": 'for f in .claude/agents/*; do cat "$f"; done'},
        }]
        self.assertTrue(MODULE.roster_was_read(calls, {"collector": {}, "reviewer": {}}))

    def test_printed_agent_paths_do_not_count_as_reads(self):
        calls = [{
            "name": "Bash",
            "input": {"command": "printf '.claude/agents/collector.md\\n.claude/agents/reviewer.md\\n'"},
        }]
        self.assertFalse(MODULE.roster_was_read(calls, {"collector": {}, "reviewer": {}}))
