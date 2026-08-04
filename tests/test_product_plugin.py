import json
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/project-harness"
SKILL = PLUGIN / "skills/project-harness"


class ProductPluginTests(unittest.TestCase):
    def test_marketplace_points_to_standalone_plugin(self):
        marketplace = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
        entry = next(item for item in marketplace["plugins"] if item["name"] == "project-harness")
        self.assertEqual(entry["source"]["path"], "./plugins/project-harness")
        self.assertEqual(entry["policy"]["installation"], "AVAILABLE")
        self.assertEqual(marketplace["name"], "project-harness")

    def test_plugin_contains_only_the_product_skill(self):
        manifest = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], PLUGIN.name)
        self.assertEqual(manifest["version"], "1.0.0")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertEqual([path.name for path in (PLUGIN / "skills").iterdir()], ["project-harness"])
        self.assertLessEqual(len(manifest["interface"]["shortDescription"]), 30)
        self.assertLessEqual(len(manifest["interface"]["defaultPrompt"]), 3)
        self.assertEqual(manifest["repository"], "https://github.com/SeoNaRu/project-harness")
        for field in ("websiteURL", "privacyPolicyURL", "termsOfServiceURL"):
            self.assertTrue(manifest["interface"][field].startswith("https://"), field)
        for field in ("composerIcon", "logo"):
            asset = PLUGIN / manifest["interface"][field].removeprefix("./")
            self.assertTrue(asset.is_file(), field)
            root = ET.parse(asset).getroot()
            self.assertEqual(root.attrib["viewBox"].split()[2:], ["256", "256"])

    def test_skill_is_portable_and_complete(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        for heading in ("## Product decision gate", "## Required inputs", "## Workflow", "## Outputs", "## Failure handling", "## Validation"):
            self.assertIn(heading, text)
        self.assertIn("Do not invent a product", text)
        for path in (
            "references/discovery-and-questions.md",
            "references/project-files.md",
            "references/evolution.md",
            "assets/AGENTS.template.md",
            "assets/project-contract.template.md",
            "agents/openai.yaml",
        ):
            self.assertTrue((SKILL / path).is_file(), path)
        for forbidden in ("AI Capability Lab", "curate-capabilities", "validate_lab.py", "sandbox/runs", "[TODO:"):
            self.assertNotIn(forbidden, text)

    def test_submission_scenario_inventory(self):
        payload = json.loads((ROOT / "evals/cases.json").read_text(encoding="utf-8"))
        cases = payload["cases"]
        self.assertEqual(len({case["id"] for case in cases}), 8)
        self.assertEqual(sum(case["kind"] == "positive" for case in cases), 5)
        self.assertEqual(sum(case["kind"] == "negative" for case in cases), 3)
        for case in cases:
            for field in ("prompt", "fixture", "expected_behavior", "expected_result"):
                self.assertTrue(case[field], f"{case['id']}: {field}")
            if case["kind"] == "negative":
                self.assertTrue(case["why_not_complete"], case["id"])

        results = json.loads((ROOT / "evals/results.json").read_text(encoding="utf-8"))["results"]
        self.assertEqual(len(results), len(cases))
        self.assertEqual({result["case_id"] for result in results}, {case["id"] for case in cases})
        self.assertTrue(all(result["status"] == "passed" for result in results))

    def test_legacy_lab_is_not_part_of_the_product(self):
        for path in ("catalog", "docs/research", "sandbox", "scripts/validate_lab.py", "skills-lock.json"):
            self.assertFalse((ROOT / path).exists(), path)


if __name__ == "__main__":
    unittest.main()
