import json
import re
import unittest
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/nulnul-harness"
SKILL = PLUGIN / "skills/nulnul-harness"


class ProductPluginTests(unittest.TestCase):
    def test_marketplace_points_to_standalone_plugin(self):
        marketplace = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
        entry = next(item for item in marketplace["plugins"] if item["name"] == "nulnul-harness")
        self.assertEqual(entry["source"]["path"], "./plugins/nulnul-harness")
        self.assertEqual(entry["policy"]["installation"], "AVAILABLE")
        self.assertEqual(marketplace["name"], "nulnul-harness")

    def test_plugin_contains_only_the_product_skill(self):
        manifest = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], PLUGIN.name)
        self.assertEqual(manifest["version"], "1.2.1")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertEqual([path.name for path in (PLUGIN / "skills").iterdir()], ["nulnul-harness"])
        self.assertLessEqual(len(manifest["interface"]["shortDescription"]), 30)
        self.assertLessEqual(len(manifest["interface"]["defaultPrompt"]), 3)
        self.assertEqual(manifest["repository"], "https://github.com/SeoNaRu/nulnul-harness")
        self.assertEqual(manifest["interface"]["displayName"], "nulnul harness")
        for field in ("websiteURL", "privacyPolicyURL", "termsOfServiceURL"):
            self.assertTrue(manifest["interface"][field].startswith("https://"), field)
        for field in ("composerIcon", "logo"):
            asset = PLUGIN / manifest["interface"][field].removeprefix("./")
            self.assertTrue(asset.is_file(), field)
            root = ET.parse(asset).getroot()
            self.assertIn("viewBox", root.attrib)

    def test_skill_is_portable_and_complete(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        for heading in ("## Product decision gate", "## Required inputs", "## Workflow", "## Outputs", "## Failure handling", "## Validation"):
            self.assertIn(heading, text)
        self.assertIn("Search installed and trusted existing capabilities before creating anything", text)
        self.assertIn("Before activating, inspect any user-named local task contract such as TASK.md", text)
        self.assertIn("Treat installed availability as discovery evidence, not verification", text)
        self.assertIn("Popularity is a signal, not proof", text)
        self.assertIn("keep it only when the primary metric improves", text)
        self.assertIn("Never let an agent approve its own upgrade", text)
        self.assertIn("resume from the last verified checkpoint", text)
        self.assertIn("take the fast path", text)
        self.assertIn("Before activating, inspect any user-named local task contract such as TASK.md", text)
        self.assertIn("do not activate when it already provides explicit local inputs, outputs, constraints, and a runnable completion check", text)
        self.assertIn("external-write planning, multi-session checkpointing, or evidence-gated agent evolution", text)
        self.assertIn("stop when every uncovered job has one adequate verified candidate", text)
        for path in (
            "references/discovery-and-questions.md",
            "references/capability-discovery.md",
            "references/data-workflow-safety.md",
            "references/agent-assembly.md",
            "references/project-files.md",
            "references/evolution.md",
            "references/personal-evolution.md",
            "assets/AGENTS.template.md",
            "assets/evolution-state.template.json",
            "assets/project-contract.template.md",
            "agents/openai.yaml",
            "scripts/validate_evolution_state.py",
        ):
            self.assertTrue((SKILL / path).is_file(), path)
        for forbidden in ("AI Capability Lab", "curate-capabilities", "validate_lab.py", "sandbox/runs", "[TODO:", "Project Harness"):
            self.assertNotIn(forbidden, text)
        self.assertIn("stable identity, deterministic deduplication, exclusion precedence", text)

    def test_submission_scenario_inventory(self):
        payload = json.loads((ROOT / "evals/cases.json").read_text(encoding="utf-8"))
        cases = payload["cases"]
        self.assertEqual(len({case["id"] for case in cases}), 9)
        self.assertEqual(sum(case["kind"] == "positive" for case in cases), 6)
        self.assertEqual(sum(case["kind"] == "negative" for case in cases), 3)
        for case in cases:
            for field in ("prompt", "fixture", "expected_behavior", "expected_result"):
                self.assertTrue(case[field], f"{case['id']}: {field}")
            if case["kind"] == "negative":
                self.assertTrue(case["why_not_complete"], case["id"])

        results = json.loads((ROOT / "evals/results.json").read_text(encoding="utf-8"))["results"]
        self.assertEqual(len(results), len(cases))
        self.assertEqual({result["case_id"] for result in results}, {case["id"] for case in cases})
        self.assertTrue(all(result["status"] in {"passed", "requires-rerun"} for result in results))

    def test_release_metadata_and_archive_are_consistent(self):
        version = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))["version"]
        self.assertIn(f"Version: `{version}`", (ROOT / "submission/listing.md").read_text(encoding="utf-8"))
        self.assertIn(f"# nulnul harness {version}", (ROOT / "submission/release-notes.md").read_text(encoding="utf-8"))
        self.assertIn(f"version-{version}", (ROOT / "README.md").read_text(encoding="utf-8"))

        archive = ROOT / "dist" / f"nulnul-harness-{version}.zip"
        self.assertTrue(archive.is_file())
        with zipfile.ZipFile(archive) as bundle:
            bundled = {
                Path(name).relative_to("nulnul-harness").as_posix(): bundle.read(name)
                for name in bundle.namelist()
                if not name.endswith("/")
            }
        product = {
            path.relative_to(PLUGIN).as_posix(): path.read_bytes()
            for path in PLUGIN.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
        }
        self.assertEqual(bundled, product)

    def test_readme_locales_are_consistent_and_links_resolve(self):
        manifest = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        readmes = {
            "README.md": ("README.ko.md", "35 passed"),
            "README.ko.md": ("README.md", "35개 통과"),
        }
        for name, (other_locale, test_claim) in readmes.items():
            text = (ROOT / name).read_text(encoding="utf-8")
            self.assertIn(other_locale, text)
            self.assertIn(f"version-{manifest['version']}", text)
            self.assertIn("Harness_100-100%2F100", text)
            self.assertIn("codex plugin add nulnul-harness@nulnul-harness", text)
            self.assertIn(test_claim, text)
            for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", text):
                if target.startswith(("https://", "http://", "#")):
                    continue
                self.assertTrue((ROOT / target.split("#", 1)[0]).exists(), f"{name}: {target}")

    def test_legacy_lab_is_not_part_of_the_product(self):
        for path in ("plugins/project-harness", "catalog", "docs/research", "sandbox", "scripts/validate_lab.py", "skills-lock.json"):
            self.assertFalse((ROOT / path).exists(), path)


if __name__ == "__main__":
    unittest.main()
