import copy
import importlib.util
import json
import statistics
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = ROOT / "examples/youtube-sheets/expected.json"
SCORER = ROOT / "scripts/score_workbook_task.py"
RESULTS = ROOT / "evals/benchmarks/youtube-sheets/ab-results.json"

spec = importlib.util.spec_from_file_location("score_workbook_task", SCORER)
scorer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scorer)


class WorkbookTaskBenchmarkTests(unittest.TestCase):
    def test_exact_structure_passes_and_regression_fails(self):
        expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
        self.assertTrue(scorer.score(expected, expected)["passed"])
        broken = copy.deepcopy(expected)
        broken["research_log"][0]["verdict"] = "X"
        result = scorer.score(expected, broken)
        self.assertFalse(result["passed"])
        self.assertFalse(result["section_matches"]["research_log"])

    def test_published_ab_medians_match_runs(self):
        payload = json.loads(RESULTS.read_text(encoding="utf-8"))
        for arm in ("baseline", "harness", "navigator_v3_candidate"):
            runs = payload["runs"][arm]
            self.assertEqual(len(runs), 3)
            self.assertTrue(all(run["passed"] for run in runs))
            self.assertTrue(all(run["human_interventions"] == 0 for run in runs))
            for metric in (
                "elapsed_seconds",
                "input_tokens",
                "cached_input_tokens",
                "output_tokens",
                "reasoning_output_tokens",
            ):
                self.assertEqual(
                    payload["medians"][arm][metric],
                    statistics.median(run[metric] for run in runs),
                )

        baseline = payload["medians"]["baseline"]
        harness = payload["medians"]["harness"]
        for metric, delta in payload["medians"]["harness_delta_percent"].items():
            if metric == "success_rate":
                continue
            self.assertEqual(delta, round((harness[metric] - baseline[metric]) / baseline[metric] * 100, 2))

        candidate = payload["medians"]["navigator_v3_candidate"]
        for metric, delta in payload["medians"]["candidate_delta_vs_harness_percent"].items():
            if metric == "success_rate":
                continue
            self.assertEqual(delta, round((candidate[metric] - harness[metric]) / harness[metric] * 100, 2))


if __name__ == "__main__":
    unittest.main()
