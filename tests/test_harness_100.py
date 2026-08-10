import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("harness_100", ROOT / "scripts/harness_100.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Harness100Tests(unittest.TestCase):
    def setUp(self):
        self.cases = json.loads((ROOT / "evals/cases.json").read_text(encoding="utf-8"))
        self.results = json.loads((ROOT / "evals/results.json").read_text(encoding="utf-8"))

    def test_current_score_uses_only_passed_evidence(self):
        score = MODULE.calculate(self.cases, self.results)
        expected = sum(
            case["harness_100_weight"]
            for case in self.cases["cases"]
            if next(result for result in self.results["results"] if result["case_id"] == case["id"])["status"]
            == "passed"
        )
        self.assertEqual(score["score"], expected)
        self.assertEqual(score["possible"], 100)
        self.assertEqual(score["release_ready"], expected == 100)

    def test_all_passed_is_release_ready(self):
        passed = {
            "results": [
                {"case_id": case["id"], "status": "passed"}
                for case in self.cases["cases"]
            ]
        }
        score = MODULE.calculate(self.cases, passed)
        self.assertEqual(score["score"], 100)
        self.assertTrue(score["release_ready"])

    def test_invalid_weights_fail_closed(self):
        altered = json.loads(json.dumps(self.cases))
        altered["cases"][0]["harness_100_weight"] += 1
        with self.assertRaises(ValueError):
            MODULE.calculate(altered, self.results)


if __name__ == "__main__":
    unittest.main()
