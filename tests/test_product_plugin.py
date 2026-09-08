import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from scripts.pack_plugin import pack


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/nulnul-harness"
SKILL = PLUGIN / "skills/nulnul-harness"


class ProductPluginTests(unittest.TestCase):
    def test_public_metadata_is_product_first(self):
        codex = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        claude = json.loads((PLUGIN / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        marketplace = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        listing = (ROOT / "submission/listing.md").read_text(encoding="utf-8")
        openai = (SKILL / "agents/openai.yaml").read_text(encoding="utf-8")
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
            "openai short": re.search(r'^\s*short_description: "(.+)"$', openai, re.M).group(1),
            "openai default": re.search(r'^\s*default_prompt: "(.+)"$', openai, re.M).group(1),
            **{
                f"codex default prompt {index}": prompt
                for index, prompt in enumerate(codex["interface"]["defaultPrompt"], 1)
            },
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
        self.assertRegex(manifest["version"], r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$")
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
        self.assertIn("Treat installed availability as discovery evidence, not selection or verification", text)
        self.assertIn("Popularity is a signal, not proof", text)
        self.assertIn("Keep it only when primary outcome quality improves", text)
        self.assertIn("Never let an agent approve its own upgrade", text)
        self.assertIn("a better method the user had to surface", text)
        self.assertIn("Harness change is first-order and declarative", text)
        self.assertIn("reuse now, add now, needs approval, and skip", text)
        self.assertIn("resume from the last verified checkpoint", text)
        self.assertIn("**Fast path**", text)
        self.assertIn("**Adopt and upgrade**", text)
        self.assertIn("Never recreate a role that already exists", text)
        self.assertIn("Context is a quality-adjusted budget", text)
        self.assertIn("Never make an unattended session edit host-protected configuration paths", text)
        self.assertIn("a denied write attempt is still a failed setup", text)
        self.assertIn("made no write tool call targeting `.claude/**`", text)
        self.assertIn("Before activating, inspect any user-named local task contract such as TASK.md", text)
        self.assertIn("do not activate when it already provides explicit local inputs, outputs, constraints, and a runnable completion check", text)
        self.assertIn("external-write planning, multi-session checkpointing, or evidence-gated agent evolution", text)
        self.assertIn("Stop when every job has a proven outcome-competitive candidate", text)
        self.assertIn("first run the bounded `claude plugin list --json` command", text)
        self.assertIn("A Codex run may create or update only `AGENTS.md`", text)
        self.assertIn("a Claude Code run may create or update only `CLAUDE.md`", text)
        self.assertIn("scripts/sync_host_entry.py", text)
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
            "references/foundation.md",
            "references/workflow-delivery.md",
            "references/workflow-recipes.md",
            "references/skill-acceptance.md",
            "references/external-candidate-preparation.md",
            "assets/workflow-example.json",
            "assets/skill-cases.template.json",
            "scripts/workflow_delivery.py",
            "assets/AGENTS.template.md",
            "assets/evolution-state.template.json",
            "assets/layer-contracts.json",
            "assets/harness-controls.json",
            "assets/project-contract.template.md",
            "assets/setup-plan.template.json",
            "agents/openai.yaml",
            "scripts/validate_evolution_state.py",
            "scripts/validate_project_setup.py",
            "scripts/validate_checkpoint.py",
            "scripts/run_checkpoint_check.py",
            "scripts/validate_learning_loop.py",
            "scripts/migrate_legacy_checkpoint.py",
            "scripts/sync_host_entry.py",
            "scripts/capability_contract.py",
            "scripts/capability_pack.py",
            "scripts/activation_boundary.py",
            "scripts/foundation_runtime.py",
            "scripts/setup_transaction.py",
            "scripts/natural_selection.py",
            "scripts/external_competition.py",
            "scripts/agent_evolution.py",
            "scripts/harness_control.py",
            "scripts/harness_evolution.py",
            "scripts/cross_project_evolution.py",
            "scripts/generalization_core.py",
            "scripts/apply_live_cycle_rollback.py",
            "scripts/validate_experience_digest.py",
            "scripts/validate_generalization_gate.py",
            "scripts/validate_autonomous_evolution.py",
            "scripts/compact_evolution_state.py",
            "scripts/personal_adaptation.py",
        ):
            self.assertTrue((SKILL / path).is_file(), path)
        manifest = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertIn("capability-natural-selection", manifest["interface"]["capabilities"])
        self.assertIn("external-capability-competition", manifest["interface"]["capabilities"])
        self.assertIn("agent-evolution-core", manifest["interface"]["capabilities"])
        self.assertIn("harness-evolution-core", manifest["interface"]["capabilities"])
        self.assertIn("cross-project-generalization-core", manifest["interface"]["capabilities"])
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
        self.assertIn("compacted `docs/nulnul/evolution.json`", text)
        self.assertIn("do not load the archive into ordinary resume context", text)
        discovery = (SKILL / "references/capability-discovery.md").read_text(encoding="utf-8")
        self.assertIn("Never recursively scan a home directory", discovery)
        self.assertIn("Do not treat cached marketplace entries as installed", discovery)
        meta = (SKILL / "references/meta-evolution.md").read_text(encoding="utf-8")
        self.assertIn("Close every measured learning loop in the same run", meta)
        self.assertIn("append one `pending` proposal", meta)
        generalization = (SKILL / "references/generalization.md").read_text(encoding="utf-8")
        self.assertIn("Evaluation exposure is state", generalization)
        self.assertIn("After the first result, retire the holdout", generalization)
        self.assertIn("Project Memory never becomes global Memory", generalization)
        self.assertIn("zero Generalization lookup", generalization)
        personal = (SKILL / "references/personal-evolution.md").read_text(encoding="utf-8")
        self.assertIn("Run one bounded autonomous episode", personal)
        self.assertIn("NO_PROMOTION", personal)
        self.assertIn("Reuse a verified adaptation personally", personal)
        self.assertIn("PERSONAL_HOME_REQUIRED", personal)
        self.assertIn("Move a candidate to `provisional`", personal)

    def test_outcome_first_decision_contract(self):
        payload = json.loads((ROOT / "evals/outcome-first/cases.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["evaluation_kind"], "deterministic-decision-contract")
        self.assertIn("do not measure model task performance", payload["claim_boundary"])
        self.assertEqual(
            payload["decision_order"],
            [
                "maximize_expected_verified_outcome_quality",
                "respect_user_safety_permission_cost_compatibility_and_reproducibility_constraints",
                "break_materially_equivalent_ties_by_lower_waste",
            ],
        )

        cases = {case["id"]: case for case in payload["cases"]}
        self.assertEqual(len(cases), 15)
        expected = {
            "more-capability-clearly-wins": ("specialized-reviewed", "SELECT", "PASS"),
            "same-quality-less-complexity-wins": ("focused-two", "SELECT", "PASS"),
            "installed-capability-materially-weaker": ("external-verified", "REQUEST_APPROVAL", "PASS"),
            "tiny-improvement-huge-complexity-loses": ("existing-strong", "KEEP", "PASS"),
            "zero-additions-is-correct": ("current-zero", "KEEP", "PASS"),
            "under-building-is-failure": ("justified-specialist", "REJECT_OBSERVED", "FAIL_UNDER_BUILDING"),
            "beginner-states-outcome-not-topology": ("infer-project-fit-path", "INFER_TOPOLOGY", "PASS"),
            "no-ai-fomo-with-strong-project-fit-capability": ("keep-current", "KEEP", "PASS"),
            "local-skill-evolves-without-external-replacement": ("reservation-review-v3", "UPGRADE", "PASS"),
            "project-skill-beats-famous-external": ("project-reviewer", "KEEP", "PASS"),
            "merge-overlap-instead-of-accumulate": ("merged-survivor", "MERGE_AND_RETIRE", "PASS"),
            "agent-evolves-from-repeated-project-failure": ("backend-reviewer-v2", "UPGRADE", "PASS"),
            "routing-evolves-without-rewriting-good-skills": ("routing-candidate", "UPGRADE_ROUTING", "PASS"),
            "verified-state-enables-bounded-continuity": ("verified-bounded-resume", "RESUME", "PASS"),
            "plain-language-evidence-without-private-reasoning": ("progressive-evidence", "EXPLAIN", "PASS"),
        }
        self.assertEqual(
            {
                case_id: (case["expected_path"], case["expected_action"], case["expected_validation"])
                for case_id, case in cases.items()
            },
            expected,
        )
        self.assertTrue(cases["installed-capability-materially-weaker"]["paths"]["external-verified"]["requires_approval"])
        self.assertEqual(
            cases["installed-capability-materially-weaker"]["after_approval"]["lifecycle"],
            ["REPLACE", "RETIRE"],
        )
        self.assertEqual(cases["zero-additions-is-correct"]["paths"]["current-zero"]["added_capabilities"], 0)
        self.assertEqual(cases["under-building-is-failure"]["observed_path"], "minimal-only")
        self.assertEqual(
            cases["beginner-states-outcome-not-topology"]["paths"]["infer-project-fit-path"]["user_harness_decisions"],
            0,
        )
        self.assertEqual(
            cases["routing-evolves-without-rewriting-good-skills"]["paths"]["routing-candidate"]["capability_files_changed"],
            0,
        )
        self.assertEqual(
            cases["verified-state-enables-bounded-continuity"]["paths"]["verified-bounded-resume"]["reexplanation_questions"],
            0,
        )
        inspectable = cases["plain-language-evidence-without-private-reasoning"]["paths"]["progressive-evidence"]
        self.assertEqual(
            inspectable["fields"],
            ["USED", "UPGRADED", "REPLACED", "RETIRED", "SKIPPED", "WHY", "VERIFY", "EVOLUTION", "NEXT_STATE"],
        )
        self.assertFalse(inspectable["private_reasoning_exposed"])

        skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        discovery = (SKILL / "references/capability-discovery.md").read_text(encoding="utf-8")
        assembly = (SKILL / "references/agent-assembly.md").read_text(encoding="utf-8")
        evolution = (SKILL / "references/evolution.md").read_text(encoding="utf-8")
        self.assertIn("Simplicity is a tie-breaker, not the objective", skill)
        self.assertIn("under-building, premature reuse, verification underinvestment, or agent under-allocation", skill)
        self.assertIn("outcome-first, project-fit, evidence-driven, waste-aware", skill)
        self.assertIn("`KEEP`, `UPGRADE`, `REPLACE`, `MERGE`, `RETIRE`, or `CREATE`", skill)
        self.assertIn("user never has to design the agent team or capability stack", skill)
        self.assertIn("`RESULT`, `VERIFY`, and `RESUME`", skill)
        self.assertIn("Do not equate installed with selected", discovery)
        self.assertIn("project fit is determined by evidence", discovery)
        self.assertIn("user-facing AI FOMO", discovery)
        self.assertIn("Treat an external capability as a candidate, not a permanent addition", discovery)
        self.assertIn("Agent count is neither a target nor a primary metric", assembly)
        self.assertIn("fewer agents is not one either", assembly)
        self.assertIn("new version of that same role even when no external replacement exists", assembly)
        self.assertIn("A cost reduction that lowers quality is a regression", evolution)
        self.assertIn("## Evolve capabilities and routing", evolution)
        self.assertIn("Capability accumulation is not evolution", evolution)
        for decision in ("KEEP", "UPGRADE", "REPLACE", "MERGE", "RETIRE", "CREATE"):
            self.assertIn(f"`{decision}`", evolution)

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

    def test_ci_packs_current_version_before_archive_checks(self):
        workflow = (ROOT / ".github/workflows/test.yml").read_text(encoding="utf-8")
        self.assertLess(workflow.index("scripts/pack_plugin.py"), workflow.index("unittest discover"))

    def test_plugin_archive_is_reproducible(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plugin = root / "nulnul-harness"
            plugin.mkdir()
            source = plugin / "payload.txt"
            source.write_text("same bytes", encoding="utf-8")
            first, second = root / "first.zip", root / "second.zip"

            source.chmod(0o600)
            os.utime(source, (1_700_000_000, 1_700_000_000))
            pack(plugin, first)
            source.chmod(0o777)
            os.utime(source, (1_800_000_000, 1_800_000_000))
            pack(plugin, second)

            self.assertEqual(first.read_bytes(), second.read_bytes())
            with zipfile.ZipFile(first) as bundle:
                info = bundle.infolist()[0]
            self.assertEqual(info.date_time, (1980, 1, 1, 0, 0, 0))
            self.assertEqual(info.create_system, 3)
            self.assertEqual(info.external_attr >> 16, 0o100644)

    def test_readme_locales_are_consistent_and_links_resolve(self):
        manifest = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        readmes = {
            "README.md": ("README.ko.md", "446 checks"),
            "README.ko.md": ("README.md", "446개 검사"),
        }
        for name, (other_locale, test_claim) in readmes.items():
            text = (ROOT / name).read_text(encoding="utf-8")
            self.assertIn(other_locale, text)
            self.assertIn(f"version-{manifest['version'].replace('-', '--')}", text)
            self.assertNotIn("Release_Gate-100%2F100", text)
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
