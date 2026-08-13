import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "evals/decision-boundaries"
PREREG = json.loads((EVAL / "preregistration.json").read_text(encoding="utf-8"))
RUNS = json.loads((EVAL / "candidate-results.json").read_text(encoding="utf-8"))
RESULTS = json.loads((EVAL / "results.json").read_text(encoding="utf-8"))
SKILL = (ROOT / "plugins/nulnul-harness/skills/nulnul-harness/SKILL.md").read_text(encoding="utf-8")


class DecisionBoundaryEvidenceTests(unittest.TestCase):
    def test_previous_no_promotion_and_budget_are_preserved(self):
        self.assertTrue(RESULTS["previous_no_promotion"]["preserved"])
        self.assertEqual(RUNS["model_invocations"], 9)
        self.assertLess(RUNS["model_invocations"], PREREG["budget"]["max_model_invocations"])
        self.assertEqual(RESULTS["live_dogfooding"]["unused_reserved_model_invocations"], 1)

    def test_candidate_failed_every_repeated_primary_case(self):
        primary = [row for row in RUNS["runs"] if row["case_id"] in {"design-scope", "web-layer-spillover"}]
        self.assertEqual(len(primary), 4)
        self.assertFalse(any(row["passed"] for row in primary))
        self.assertEqual(RESULTS["candidate"]["design_primary"], "0/2")
        self.assertEqual(RESULTS["candidate"]["web_primary"], "0/2")

    def test_gate_rejected_and_shipped_candidate_was_removed(self):
        self.assertEqual(RESULTS["gate"]["decision"], "NO_PROMOTION")
        self.assertFalse(RESULTS["gate"]["candidate_promoted"])
        self.assertNotIn("## Scoped decision boundary", SKILL)
        self.assertFalse((ROOT / "plugins/nulnul-harness/skills/nulnul-harness/scripts/validate_decision_boundaries.py").exists())
        self.assertFalse((ROOT / "plugins/nulnul-harness/skills/nulnul-harness/assets/decision-boundaries.template.json").exists())

    def test_evidence_is_structural_and_permission_safe(self):
        serialized = json.dumps(RUNS)
        self.assertNotIn("basis.evidence", serialized)
        for row in RUNS["runs"]:
            self.assertEqual(row["observed"]["unrelated_personal_reads"], 0)
            self.assertEqual(row["observed"]["permission_delta"], [])
        self.assertEqual(RESULTS["structural_controls"]["passed"], 14)
        self.assertEqual(RESULTS["structural_controls"]["total"], 14)


if __name__ == "__main__":
    unittest.main()
