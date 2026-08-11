import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("release_gate", ROOT / "scripts/release_gate.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ReleaseGateTests(unittest.TestCase):
    def setUp(self):
        self.cases = json.loads((ROOT / "evals/cases.json").read_text(encoding="utf-8"))
        self.results = json.loads((ROOT / "evals/results.json").read_text(encoding="utf-8"))

    def test_current_score_uses_only_passed_evidence(self):
        score = MODULE.calculate(self.cases, self.results)
        expected = sum(
            case["release_gate_weight"]
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
        altered["cases"][0]["release_gate_weight"] += 1
        with self.assertRaises(ValueError):
            MODULE.calculate(altered, self.results)

    def test_missing_learning_verdict_inventory_fails_release(self):
        learning = json.loads(
            (ROOT / "evals/benchmarks/setup-baseline/results.json").read_text(encoding="utf-8")
        )
        evolution = json.loads((ROOT / "docs/nulnul/evolution.json").read_text(encoding="utf-8"))
        learning.pop("learning_verdicts")
        with self.assertRaisesRegex(ValueError, "learning_verdicts must be an array"):
            MODULE.validate_learning_gate(learning, evolution)


if __name__ == "__main__":
    unittest.main()
