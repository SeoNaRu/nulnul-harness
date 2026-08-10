import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "evals/benchmarks/youtube-sheets/fixture.json"
EXAMPLE = ROOT / "evals/benchmarks/youtube-sheets/example-output.json"
SPEC = importlib.util.spec_from_file_location(
    "score_youtube_sheets", ROOT / "scripts/score_youtube_sheets.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class YoutubeSheetsBenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_reference_output_passes(self):
        candidate = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        result = MODULE.score(self.fixture, candidate)
        self.assertTrue(result["passed"])
        self.assertEqual(result["f1"], 1.0)
        self.assertEqual(result["duplicate_rate"], 0.0)

    def test_irrelevant_duplicate_output_fails(self):
        candidate = {
            "records": [
                {"channel_id": "UC-daily-kitchen", "category": "crypto"},
                {"channel_id": "UC-daily-kitchen", "category": "crypto"},
            ]
        }
        result = MODULE.score(self.fixture, candidate)
        self.assertFalse(result["passed"])
        self.assertEqual(result["precision"], 0.0)
        self.assertGreater(result["duplicate_rate"], 0.0)


if __name__ == "__main__":
    unittest.main()
