"""Setup must persist an explicit disposition for every reported role."""

import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "plugins/nulnul-harness/skills/nulnul-harness/scripts"
sys.path.insert(0, str(SCRIPTS))
import setup_transaction


class SetupRosterTests(unittest.TestCase):
    def plan(self, agents):
        return {
            "schema_version": setup_transaction.SCHEMA_VERSION,
            "mode": "adopt-upgrade",
            "host": "claude",
            "goal": "Keep a local utility correct.",
            "milestone": "Verify the requested behavior.",
            "completion_check": "node --test",
            "verification_files": ["src/label.js"],
            "constraints": ["No external or protected-path writes."],
            "roster": {"skills": [], "plugins": [], "agents": agents},
            "agent_topology": "One synthesis owner; preserve existing role boundaries.",
            "accepted_capabilities": [],
        }

    def test_explicit_dispositions_are_preserved_and_kept_normalizes_to_reuse(self):
        for action in ("reuse", "kept", "upgraded", "merged", "removed"):
            with self.subTest(action=action):
                plan = setup_transaction.validate_plan(self.plan([f"collector: {action}", "reviewer: reuse"]))
                contract = setup_transaction.project_contract(plan)
                expected = "reuse" if action == "kept" else action
                self.assertIn(f"- collector: {expected}\n", contract)
                self.assertIn("- reviewer: reuse\n", contract)
                self.assertIn("## Agent classifications", contract)
        self.assertEqual(setup_transaction.validate_plan(self.plan([]))["roster"]["agents"], [])

    def test_missing_ambiguous_duplicate_and_unknown_dispositions_are_rejected(self):
        cases = [
            ["collector"], ["collector: available"], [": reuse"],
            ["collector: reuse: reuse"],
            ["collector: reuse", "collector: removed"],
            ["Collector: reuse", "collector: removed"],
        ]
        for agents in cases:
            with self.subTest(agents=agents), self.assertRaisesRegex(ValueError, "roster.agents"):
                setup_transaction.validate_plan(self.plan(agents))


if __name__ == "__main__":
    unittest.main()
