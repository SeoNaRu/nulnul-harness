import importlib.util
import json
import unittest
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples/youtube-sheets"
SPEC = importlib.util.spec_from_file_location(
    "build_youtube_sheets_example", ROOT / "scripts/build_youtube_sheets_example.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class YoutubeSheetsPublicExampleTests(unittest.TestCase):
    def setUp(self):
        self.payload = json.loads((EXAMPLE / "input.json").read_text(encoding="utf-8"))
        self.output = MODULE.build(self.payload)

    def test_output_matches_public_contract(self):
        expected = json.loads((EXAMPLE / "expected.json").read_text(encoding="utf-8"))
        self.assertEqual(self.output, expected)

    def test_duplicate_and_exclusion_never_reach_action_queues(self):
        actionable = self.output["leads"] + self.output["needs_second_review"]
        ids = [row["channel_id"] for row in actionable]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertNotIn("demo-contacted", ids)
        self.assertEqual(ids.count("demo-crypto"), 1)

    def test_contact_quality_routes_to_distinct_queues(self):
        self.assertEqual(
            {row["channel_id"] for row in self.output["leads"]},
            {"demo-crypto", "demo-stock"},
        )
        self.assertEqual(
            {row["contact_grade"] for row in self.output["needs_second_review"]},
            {"channel-only", "indirect", "none"},
        )

    def test_formula_like_public_text_is_escaped(self):
        row = next(row for row in self.output["research_log"] if row["channel_id"] == "demo-irrelevant")
        self.assertTrue(row["name"].startswith("'="))

    def test_fixture_uses_only_synthetic_reserved_domains(self):
        for row in self.payload["candidates"]:
            self.assertTrue(row["channel_id"].startswith("demo-"))
            self.assertEqual(urlparse(row["channel_url"]).hostname, "youtube.invalid")
            contact = row["contact"]["value"]
            if "@" in contact:
                self.assertTrue(contact.endswith("@example.invalid"))
            elif contact:
                self.assertEqual(urlparse(contact).hostname, "example.invalid")


if __name__ == "__main__":
    unittest.main()
