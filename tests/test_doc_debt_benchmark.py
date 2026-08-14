import json
import statistics
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "evals/benchmarks/doc-debt/results.json"


class DocDebtBenchmarkTests(unittest.TestCase):
    def test_published_ab_preserves_behavior_and_improves_median(self):
        payload = json.loads(RESULTS.read_text(encoding="utf-8"))
        self.assertEqual(payload["champion_ref"], "v2.1.0")
        self.assertTrue(payload["behavior_equal"])
        self.assertEqual(payload["decision"], "accepted")
        self.assertGreaterEqual(len(payload["runs"]), 8)
        for arm in ("champion", "candidate"):
            measured = statistics.median(
                row["elapsed_seconds"] for row in payload["runs"] if row["arm"] == arm
            )
            self.assertEqual(payload["medians"][arm], measured)
        self.assertLess(payload["medians"]["candidate"], payload["medians"]["champion"])
        self.assertGreater(payload["improvement_percent"], 0)


if __name__ == "__main__":
    unittest.main()
