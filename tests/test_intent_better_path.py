import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "evals/intent-better-path"
PREREG = json.loads((EVAL / "preregistration.json").read_text(encoding="utf-8"))
AMENDMENT = json.loads((EVAL / "amendment.json").read_text(encoding="utf-8"))
BASELINE = json.loads((EVAL / "baseline-natural.json").read_text(encoding="utf-8"))
CANDIDATE = json.loads((EVAL / "candidate-results.json").read_text(encoding="utf-8"))
RESULTS = json.loads((EVAL / "results.json").read_text(encoding="utf-8"))
CASES = json.loads((EVAL / "natural-cases.json").read_text(encoding="utf-8"))
SPEC = importlib.util.spec_from_file_location("intent_eval", EVAL / "run_eval.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
SKILL = (ROOT / "plugins/nulnul-harness/skills/nulnul-harness/SKILL.md").read_text(encoding="utf-8")


class IntentBetterPathTests(unittest.TestCase):
    def rescored(self, payload):
        return [
            MODULE.score(row["decision"], CASES[row["case_id"]]["expected"])
            for row in payload["runs"]
        ]

    def test_budget_and_invalid_preflight_are_preserved(self):
        self.assertTrue(AMENDMENT["recorded_before_candidate_generation"])
        self.assertEqual(RESULTS["evaluation"]["total_model_invocations"], 16)
        self.assertLessEqual(
            RESULTS["evaluation"]["total_model_invocations"],
            PREREG["budget"]["max_model_invocations"],
        )
        self.assertEqual(RESULTS["evaluation"]["invalid_preflight_invocations"], 6)

    def test_natural_baseline_reproduces_both_failures(self):
        passed = [all(checks.values()) for checks in self.rescored(BASELINE)]
        self.assertEqual(passed, [False, False, False, True])
        self.assertEqual(RESULTS["reproduced_failures"]["design"]["authority_override_violations"], 1)
        self.assertEqual(RESULTS["reproduced_failures"]["technology"]["unnecessary_switches"], 2)

    def test_candidate_is_rejected_and_removed(self):
        passed = [all(checks.values()) for checks in self.rescored(CANDIDATE)]
        self.assertEqual(passed, [False, False, True, True, False, False])
        self.assertEqual(RESULTS["gate"]["decision"], "NO_PROMOTION")
        self.assertFalse(RESULTS["gate"]["candidate_promoted"])
        self.assertNotIn("## Intent and means gate", SKILL)

    def test_privacy_permissions_and_skill_guardrail(self):
        for payload in (BASELINE, CANDIDATE):
            for row in payload["runs"]:
                decision = row["decision"]
                self.assertNotIn("brief_reason", decision)
                self.assertEqual(decision["unrelated_personal_reads"], 0)
                self.assertEqual(decision["permission_delta"], [])
        design = [row for row in CANDIDATE["runs"] if row["case_id"] == "design-natural"]
        self.assertTrue(all(row["decision"]["skill_used"] for row in design))

    def test_negative_control_inventory_is_complete(self):
        controls = {row["id"] for row in RESULTS["controls"]}
        self.assertEqual(len(controls), 15)
        self.assertIn("explicit-python-constraint", controls)
        self.assertIn("suitable-existing-python", controls)
        self.assertIn("permission-expansion", controls)


if __name__ == "__main__":
    unittest.main()
