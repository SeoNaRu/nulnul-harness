import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "evals/repository-receipts"
PREREG = json.loads((EVAL / "preregistration.json").read_text(encoding="utf-8"))
CANDIDATE = json.loads((EVAL / "candidate.json").read_text(encoding="utf-8"))
RUNS = json.loads((EVAL / "candidate-results.json").read_text(encoding="utf-8"))
RESULTS = json.loads((EVAL / "results.json").read_text(encoding="utf-8"))
SKILL = (ROOT / "plugins/nulnul-harness/skills/nulnul-harness/SKILL.md").read_text(encoding="utf-8")


class RepositoryReceiptEvidenceTests(unittest.TestCase):
    def test_previous_rejections_and_budget_are_preserved(self):
        self.assertEqual(len(RESULTS["previous_rejected_search_history"]), 2)
        self.assertTrue(all(row["decision"] == "NO_PROMOTION" for row in RESULTS["previous_rejected_search_history"]))
        self.assertEqual(PREREG["budget"]["max_generations"], 1)
        self.assertEqual(RUNS["model_invocations"], PREREG["budget"]["max_model_invocations"])
        self.assertEqual(RUNS["invalid_preflight_model_inferences"], 0)
        self.assertEqual(len(CANDIDATE["candidates"]), 1)

    def test_candidate_passed_repeated_primary_and_controls(self):
        primary = [row for row in RUNS["runs"] if row["case_id"] in {"design-primary", "web-primary"}]
        self.assertEqual(len(primary), 4)
        self.assertTrue(all(row["passed"] and row["receipt_valid"] for row in primary))
        self.assertEqual(RESULTS["design_result"]["project_truth_override_count"], 0)
        self.assertEqual(RESULTS["working_backend_preservation"]["unjustified_backend_changes"], 0)
        self.assertEqual(len(RESULTS["negative_controls"]), 16)
        self.assertTrue(all(row["status"] == "passed" for row in RESULTS["negative_controls"]))

    def test_personal_skill_override_and_challenge_remain_available(self):
        design = [row for row in RUNS["runs"] if row["case_id"] == "design-primary"]
        self.assertTrue(all(row["observed"]["visual_tone"] == "quiet" for row in design))
        self.assertTrue(all(row["observed"]["skill_used"] for row in design))
        override = next(row for row in RUNS["runs"] if row["case_id"] == "explicit-user-override")
        self.assertEqual(override["observed"]["override_scope"], "design.component_shape")
        challenge = next(row for row in RUNS["runs"] if row["case_id"] == "backend-challenge")
        self.assertEqual(challenge["observed"]["backend_action"], "change")
        self.assertEqual(challenge["observed"]["required_capability_check"], "failed")

    def test_context_privacy_permission_and_no_false_live_credit(self):
        context = RESULTS["context_privacy_permission"]
        self.assertEqual(context["unrelated_repository_reads"], 0)
        self.assertEqual(context["unrelated_personal_reads"], 0)
        self.assertEqual(context["permission_delta"], [])
        self.assertFalse(context["whole_repository_hash"])
        self.assertEqual(RESULTS["gate"]["decision"], "NO_PROMOTION")
        self.assertEqual(RESULTS["live_dogfooding"]["status"], "not_run")
        self.assertNotIn("## Repository-derived decision receipts", SKILL)


if __name__ == "__main__":
    unittest.main()
