import json
import re
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/nulnul-harness"
SKILL = PLUGIN / "skills/nulnul-harness"


class ProductPluginTests(unittest.TestCase):
    def test_public_metadata_is_product_first(self):
        codex = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        claude = json.loads((PLUGIN / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        marketplace = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        listing = (ROOT / "submission/listing.md").read_text(encoding="utf-8")
        entry = next(item for item in marketplace["plugins"] if item["name"] == "nulnul-harness")
        descriptions = {
            "codex description": codex["description"],
            "codex short description": codex["interface"]["shortDescription"],
            "codex long description": codex["interface"]["longDescription"],
            "claude description": claude["description"],
            "marketplace description": marketplace["description"],
            "marketplace entry": entry["description"],
            "listing short": re.search(r"^- Short description: (.+)$", listing, re.M).group(1),
            "listing long": re.search(r"^- Long description: (.+)$", listing, re.M).group(1),
        }
        forbidden = (
            re.compile(r"\b(?:AI|agent)[ -]team\b", re.I),
            re.compile(r"\btask and meta[- ]agent(?: system|s)\b", re.I),
            re.compile(r"\bassembl\w* .{0,50}\bagent system\b", re.I),
        )
        violations = [
            label
            for label, text in descriptions.items()
            if any(pattern.search(text) for pattern in forbidden)
        ]
        self.assertEqual(violations, [])

    def test_marketplace_points_to_standalone_plugin(self):
        marketplace = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
        entry = next(item for item in marketplace["plugins"] if item["name"] == "nulnul-harness")
        self.assertEqual(entry["source"]["path"], "./plugins/nulnul-harness")
        self.assertEqual(entry["policy"]["installation"], "AVAILABLE")
        self.assertEqual(marketplace["name"], "nulnul-harness")

    def test_claude_code_marketplace_and_plugin_manifests_agree(self):
        marketplace = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        plugin = json.loads((PLUGIN / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        codex = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        entry = next(item for item in marketplace["plugins"] if item["name"] == "nulnul-harness")
        self.assertEqual(entry["source"], "./plugins/nulnul-harness")
        self.assertEqual(entry["version"], plugin["version"])
        self.assertTrue(marketplace["description"])
        for field in ("name", "version", "description", "homepage", "repository", "license"):
            self.assertEqual(plugin[field], codex[field], field)
        self.assertIn("claude-code-plugin", plugin["keywords"])
        self.assertTrue((PLUGIN / "skills/nulnul-harness/SKILL.md").is_file())

    def test_plugin_contains_only_the_product_skill(self):
        manifest = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], PLUGIN.name)
        self.assertEqual(manifest["version"], "2.0.0")
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
        self.assertIn("Enumerate the host's installed skills, plugins, and agents before judging coverage", text)
        self.assertIn("Before activating, inspect any user-named local task contract such as TASK.md", text)
        self.assertIn("Treat installed availability as discovery evidence, not verification", text)
        self.assertIn("Popularity is a signal, not proof", text)
        self.assertIn("keep it only when the primary metric improves", text)
        self.assertIn("Never let an agent approve its own upgrade", text)
        self.assertIn("a better method the user had to surface", text)
        self.assertIn("The meta side may modify its own discovery", text)
        self.assertIn("reuse now, add now, needs approval, and skip", text)
        self.assertIn("resume from the last verified checkpoint", text)
        self.assertIn("**Fast path**", text)
        self.assertIn("**Adopt and upgrade**", text)
        self.assertIn("Never recreate a role that already exists", text)
        self.assertIn("Context is a budget like any other", text)
        self.assertIn("Never make an unattended session edit host-protected configuration paths", text)
        self.assertIn("a denied write attempt is still a failed setup", text)
        self.assertIn("made no write tool call targeting `.claude/**`", text)
        self.assertIn("Before activating, inspect any user-named local task contract such as TASK.md", text)
        self.assertIn("do not activate when it already provides explicit local inputs, outputs, constraints, and a runnable completion check", text)
        self.assertIn("external-write planning, multi-session checkpointing, or evidence-gated agent evolution", text)
        self.assertIn("stop when every uncovered job has one adequate verified candidate", text)
        self.assertIn("first run the bounded `claude plugin list --json` command", text)
        for path in (
            "references/discovery-and-questions.md",
            "references/baseline-kernel.md",
            "references/capability-discovery.md",
            "references/capability-registry.md",
            "references/data-workflow-safety.md",
            "references/agent-assembly.md",
            "references/project-files.md",
            "references/evolution.md",
            "references/personal-evolution.md",
            "references/meta-evolution.md",
            "references/generalization.md",
            "assets/AGENTS.template.md",
            "assets/evolution-state.template.json",
            "assets/project-contract.template.md",
            "agents/openai.yaml",
            "scripts/validate_evolution_state.py",
            "scripts/validate_project_setup.py",
            "scripts/validate_checkpoint.py",
            "scripts/run_checkpoint_check.py",
            "scripts/validate_learning_loop.py",
            "scripts/migrate_legacy_checkpoint.py",
            "scripts/apply_live_cycle_rollback.py",
            "scripts/validate_experience_digest.py",
            "scripts/validate_generalization_gate.py",
            "scripts/validate_autonomous_evolution.py",
            "scripts/personal_adaptation.py",
        ):
            self.assertTrue((SKILL / path).is_file(), path)
        for forbidden in ("AI Capability Lab", "curate-capabilities", "validate_lab.py", "sandbox/runs", "[TODO:", "Project Harness"):
            self.assertNotIn(forbidden, text)
        self.assertIn("stable identity, deterministic deduplication, exclusion precedence", text)
        self.assertIn("Apply `references/baseline-kernel.md`", text)
        self.assertIn("Do not load it for a pure local function", text)
        self.assertIn("Run them without reading their source", text)
        self.assertIn("## Resume fast path", text)
        self.assertLess(text.index("## Resume fast path"), text.index("## Workflow"))
        self.assertIn("Do not load setup, discovery, assembly, or evolution references", text)
        self.assertIn("Read that checkpoint and the current task files, not the full setup contract", text)
        self.assertIn("validate that checkpoint before any repository-wide inspection", text)
        self.assertIn("entire allowed read set", text)
        self.assertIn("repeat an unchanged passing check", text)
        self.assertIn("when a legacy `project.md` has durable continuity", text)
        self.assertIn("existing root guidance alone does not preserve that evidence", text)
        self.assertIn("Never create `checkpoint.json` when `evolution.json` exists", text)
        discovery = (SKILL / "references/capability-discovery.md").read_text(encoding="utf-8")
        self.assertIn("Never recursively scan a home directory", discovery)
        self.assertIn("Do not treat cached marketplace entries as installed", discovery)
        meta = (SKILL / "references/meta-evolution.md").read_text(encoding="utf-8")
        self.assertIn("Close every measured learning loop in the same run", meta)
        self.assertIn("append one `pending` proposal", meta)
        generalization = (SKILL / "references/generalization.md").read_text(encoding="utf-8")
        self.assertIn("Evaluation exposure is state", generalization)
        self.assertIn("After the first result, retire the holdout", generalization)
        personal = (SKILL / "references/personal-evolution.md").read_text(encoding="utf-8")
        self.assertIn("Run one bounded autonomous episode", personal)
        self.assertIn("NO_PROMOTION", personal)
        self.assertIn("Reuse a verified adaptation personally", personal)
        self.assertIn("PERSONAL_HOME_REQUIRED", personal)

    def test_setup_trigger_is_multilingual(self):
        description = re.search(
            r"^description: (.*)$", (SKILL / "SKILL.md").read_text(encoding="utf-8"), re.M
        ).group(1)
        for phrase in (
            "set up the harness",
            "하네스 세팅해줘",
            "하네스 구성해줘",
            "配置一下 harness",
            "设置这个项目的 harness",
            "ハーネスをセットアップして",
            "ハーネスを構成して",
        ):
            self.assertIn(phrase, description, phrase)

    def test_submission_scenario_inventory(self):
        payload = json.loads((ROOT / "evals/cases.json").read_text(encoding="utf-8"))
        cases = payload["cases"]
        self.assertEqual(len({case["id"] for case in cases}), 12)
        self.assertEqual(sum(case["kind"] == "positive" for case in cases), 9)
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
        adopt = next(case for case in cases if case["id"] == "positive-adopt-existing-harness")
        self.assertIn("make no unattended write attempt within it", " ".join(adopt["expected_behavior"]))
        adopt_result = next(result for result in results if result["case_id"] == adopt["id"])
        self.assertEqual(adopt_result["status"], "passed")
        meta = next(case for case in cases if case["id"] == "positive-meta-evolution-from-discovery")
        self.assertIn("improvement procedure itself", " ".join(meta["expected_behavior"]))
        meta_result = next(result for result in results if result["case_id"] == meta["id"])
        self.assertEqual(meta_result["status"], "passed")

    def test_release_metadata_and_archive_are_consistent(self):
        version = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))["version"]
        self.assertIn(f"Version: `{version}`", (ROOT / "submission/listing.md").read_text(encoding="utf-8"))
        self.assertIn(f"# nulnul harness {version}", (ROOT / "submission/release-notes.md").read_text(encoding="utf-8"))
        badge_version = version.replace("-", "--")
        self.assertIn(f"version-{badge_version}", (ROOT / "README.md").read_text(encoding="utf-8"))

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
            "README.md": ("README.ko.md", "161 passed"),
            "README.ko.md": ("README.md", "161개 통과"),
        }
        for name, (other_locale, test_claim) in readmes.items():
            text = (ROOT / name).read_text(encoding="utf-8")
            self.assertIn(other_locale, text)
            self.assertIn(f"version-{manifest['version'].replace('-', '--')}", text)
            self.assertIn("Release_Gate-100%2F100", text)
            self.assertIn("codex plugin add nulnul-harness@nulnul-harness", text)
            self.assertIn("claude plugin install nulnul-harness@nulnul-harness", text)
            self.assertIn(test_claim, text)
            self.assertNotIn('<h1 align="center">NULNUL</h1>', text)
            self.assertIn("https://ai.meta.com/research/publications/hyperagents/", text)
            self.assertIn("https://news.hada.io/weekly/202615", text)
            for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", text):
                if target.startswith(("https://", "http://", "#")):
                    continue
                self.assertTrue((ROOT / target.split("#", 1)[0]).exists(), f"{name}: {target}")

    def test_setup_baseline_rejects_context_regressions(self):
        results = json.loads(
            (ROOT / "evals/benchmarks/setup-baseline/results.json").read_text(encoding="utf-8")
        )
        arms = {arm["id"]: arm for arm in results["setup_arms"]}
        baseline = arms["prior-1.2.1"]
        accepted = arms["accepted-1.3.0-candidate"]
        rejected = arms["initial-1.3.0-candidate"]
        change = 100 * (accepted["input_tokens"] / baseline["input_tokens"] - 1)
        self.assertTrue(accepted["exact_behavior"])
        self.assertLessEqual(change, results["setup_gate"]["maximum_input_increase_percent"])
        self.assertEqual(rejected["decision"], "rejected")
        self.assertGreater(
            rejected["input_change_percent"], results["setup_gate"]["maximum_input_increase_percent"]
        )
        self.assertTrue(results["continuation"]["exact_behavior"])
        self.assertIn("not-established", results["continuation"]["status"])
        resume = results["resume_gate"]
        self.assertEqual(resume["status"], "accepted-after-three-rejections")
        self.assertEqual(len(resume["rejected_candidates"]), 3)
        self.assertTrue(all(run["exact_behavior"] for run in resume["accepted_candidate"]["runs"]))
        self.assertLess(resume["accepted_candidate"]["input_change_percent"], 0)
        self.assertTrue(resume["transfer_live_cycle"]["exact_behavior"])
        self.assertFalse(resume["transfer_live_cycle"]["full_setup_contract_read"])
        learning = subprocess.run(
            [
                sys.executable,
                str(SKILL / "scripts/validate_learning_loop.py"),
                str(ROOT / "evals/benchmarks/setup-baseline/results.json"),
                str(ROOT / "docs/nulnul/evolution.json"),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(learning.returncode, 0, learning.stdout + learning.stderr)

    def test_meta_harness_is_a_product_capability(self):
        manifest = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertIn("meta-harness-evolution", manifest["interface"]["capabilities"])
        self.assertIn("bounded-autonomous-evolution", manifest["interface"]["capabilities"])
        reference = (SKILL / "references/meta-evolution.md").read_text(encoding="utf-8")
        for phrase in (
            "One editable project program",
            "Bootstrap the initial conditions",
            "Discover better ways, not only failures",
            "Change the improvement procedure",
            "Accumulate across runs",
        ):
            self.assertIn(phrase, reference)

    def test_root_agent_routes_only_approved_durable_wiki_lessons(self):
        agreement = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        ignored = (ROOT / ".gitignore").read_text(encoding="utf-8")
        for phrase in (
            ".nulnul.local.json",
            "obsidian_wiki_root",
            "00_위키-작업규칙.md",
            "read `index.md` first",
            "append one entry to `log.md`",
            "Skip routine passing runs",
            "never copy raw transcripts",
        ):
            self.assertIn(phrase, agreement)
        self.assertIn(".nulnul.local.json", ignored)
        self.assertNotIn("/mnt/c/Users/", agreement)

    def test_legacy_lab_is_not_part_of_the_product(self):
        for path in ("plugins/project-harness", "catalog", "docs/research", "sandbox", "scripts/validate_lab.py", "skills-lock.json"):
            self.assertFalse((ROOT / path).exists(), path)


if __name__ == "__main__":
    unittest.main()
