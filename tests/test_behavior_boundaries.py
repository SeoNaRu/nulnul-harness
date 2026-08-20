import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "evals/behavior-boundaries"
SPEC = importlib.util.spec_from_file_location("behavior_boundaries", HERE / "run_ab.py")
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


class BehaviorBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.cases = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))
        self.preregistration = json.loads(
            (HERE / "preregistration.json").read_text(encoding="utf-8")
        )

    def test_preregistered_inventory_and_budget_are_bounded(self):
        expected = set(self.preregistration["primary_cases"]) | set(
            self.preregistration["candidate_controls"]
        )
        self.assertEqual(set(self.cases), expected)
        budget = self.preregistration["budget"]
        self.assertEqual((budget["max_candidates"], budget["max_generations"]), (1, 1))
        self.assertEqual(budget["permission_delta"], [])
        self.assertEqual((budget["external_writes"], budget["new_dependencies"], budget["new_services"]), (0, 0, 0))
        self.assertFalse(budget["holdout_access"])

    def test_primary_product_case_does_not_disclose_the_expected_route(self):
        prompt = self.cases["ordinary-multisession-tuning-v2"]["prompt"]
        for leaked_answer in ("agent version", "Coach", "evolution", "checkpoint"):
            self.assertNotIn(leaked_answer, prompt)

    def test_score_fails_one_wrong_boundary(self):
        case_id = "gameplay-capability-selection-v2"
        decision = {
            key: value
            for key, value in self.cases[case_id]["expected"].items()
            if key not in {"options_count_min", "options_count_max", "actual_optional_skills"}
        }
        decision.update(options_count=2, permission_delta=[])
        self.assertTrue(all(RUNNER.score(case_id, decision).values()))
        decision["frontend_design_offered"] = True
        self.assertFalse(all(RUNNER.score(case_id, decision).values()))


if __name__ == "__main__":
    unittest.main()
