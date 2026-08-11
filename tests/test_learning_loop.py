import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "plugins/nulnul-harness/skills/nulnul-harness/scripts/validate_learning_loop.py"
SPEC = importlib.util.spec_from_file_location("validate_learning_loop", SCRIPT)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class LearningLoopTests(unittest.TestCase):
    def setUp(self):
        self.results = json.loads(
            (ROOT / "evals/benchmarks/setup-baseline/results.json").read_text(encoding="utf-8")
        )
        self.evolution = json.loads(
            (ROOT / "docs/nulnul/evolution.json").read_text(encoding="utf-8")
        )

    def test_all_published_nonpass_verdicts_entered_the_coach_loop(self):
        self.assertEqual(validator.validate(self.results, self.evolution), [])

    def test_unlinked_nonpass_verdict_fails_closed(self):
        broken = copy.deepcopy(self.results)
        broken["learning_verdicts"][0].pop("feedback_id")
        self.assertIn(
            "verdict continuation-context-cost has no linked feedback",
            validator.validate(broken, self.evolution),
        )
        broken["learning_verdicts"][0]["proposal_ids"] = [[]]
        self.assertIn(
            "verdict continuation-context-cost has an invalid proposal id",
            validator.validate(broken, self.evolution),
        )
        broken.pop("learning_verdicts")
        self.assertEqual(
            validator.validate(broken, self.evolution),
            ["learning_verdicts must be an array"],
        )


if __name__ == "__main__":
    unittest.main()
