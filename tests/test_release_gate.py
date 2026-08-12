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
        self.setup = json.loads(
            (ROOT / "evals/benchmarks/setup-baseline/results.json").read_text(encoding="utf-8")
        )
        self.performance = json.loads(
            (ROOT / "evals/benchmarks/performance.json").read_text(encoding="utf-8")
        )
        self.activation = json.loads(
            (ROOT / "evals/benchmarks/activation/results.json").read_text(encoding="utf-8")
        )
        self.evolution = json.loads((ROOT / "docs/nulnul/evolution.json").read_text(encoding="utf-8"))
        self.generalization_manifest = json.loads(
            (ROOT / "evals/generalization/manifest.json").read_text(encoding="utf-8")
        )
        self.generalization_results = json.loads(
            (ROOT / "evals/generalization/results.json").read_text(encoding="utf-8")
        )

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
        learning = json.loads(json.dumps(self.setup))
        evolution = json.loads((ROOT / "docs/nulnul/evolution.json").read_text(encoding="utf-8"))
        learning.pop("learning_verdicts")
        with self.assertRaisesRegex(ValueError, "learning_verdicts must be an array"):
            MODULE.validate_learning_gate(learning, evolution)

    def test_current_performance_and_activation_gates_pass(self):
        performance = MODULE.validate_performance_gate(self.performance)
        activation = MODULE.validate_activation_gate()
        live = MODULE.validate_activation_results(self.activation, self.evolution)
        self.assertEqual(performance["status"], "passed")
        self.assertLess(performance["comparisons"]["fast-resume"]["input_tokens"], 0)
        self.assertGreaterEqual(activation["case_count"], 10)
        self.assertGreaterEqual(activation["minimum_rounds"], 3)
        self.assertEqual(live["exact_runs"], 3)
        self.assertGreaterEqual(live["comparable_pairs"], 3)
        self.assertLessEqual(live["paired_input_change_percent"], 20)
        generalization = MODULE.validate_generalization_gate(
            self.generalization_manifest, self.generalization_results
        )
        self.assertEqual(generalization["decision"], "narrower_scope")
        self.assertFalse(generalization["harness_wide_generalization"])
        autonomous = MODULE.validate_autonomous_gate(self.evolution)
        self.assertEqual(autonomous["episodes"][0]["decision"], "AUTONOMOUS_EVOLUTION_WIN")

    def test_autonomous_gate_rejects_self_credit(self):
        altered = json.loads(json.dumps(self.evolution))
        altered["autonomous_episodes"][0]["candidates"][1]["evaluation"][
            "owner_agent"
        ] = "coach"
        with self.assertRaisesRegex(ValueError, "self-credited"):
            MODULE.validate_autonomous_gate(altered)

    def test_autonomous_gate_rejects_completion_check_budget_bypass(self):
        altered = json.loads(json.dumps(self.evolution))
        episode = altered["autonomous_episodes"][1]
        retry = next(arm for arm in episode["baseline"]["arms"] if arm["id"] == "retry")
        retry["completion_checks"] = 0
        with self.assertRaisesRegex(ValueError, "retry comparison"):
            MODULE.validate_autonomous_gate(altered)

    def test_generalization_gate_rejects_leakage_and_reuse(self):
        leaked = json.loads(json.dumps(self.generalization_manifest))
        perl = next(case for case in leaked["holdout_cases"] if "perl" in case["case_id"])
        perl["material_path"] = (
            "plugins/nulnul-harness/skills/nulnul-harness/scripts/validate_checkpoint.py"
        )
        with self.assertRaisesRegex(ValueError, "holdout leakage"):
            MODULE.validate_generalization_gate(leaked, self.generalization_results)

        reused = json.loads(json.dumps(self.generalization_manifest))
        perl = next(case for case in reused["holdout_cases"] if "perl" in case["case_id"])
        perl["exposure_count"] = 2
        with self.assertRaisesRegex(ValueError, "reuse is prohibited"):
            MODULE.validate_generalization_gate(reused, self.generalization_results)

    def test_generalization_gate_rejects_failure_identity_and_budget_claims(self):
        failed = json.loads(json.dumps(self.generalization_results))
        failed["case_results"][0]["primary"]["heldout_task_success"] = False
        with self.assertRaisesRegex(ValueError, "primary metric failed"):
            MODULE.validate_generalization_gate(self.generalization_manifest, failed)

        wrong_identity = json.loads(json.dumps(self.generalization_results))
        wrong_identity["mechanism_id"] = "different-mechanism"
        with self.assertRaisesRegex(ValueError, "identity does not match"):
            MODULE.validate_generalization_gate(self.generalization_manifest, wrong_identity)

        incomparable = json.loads(json.dumps(self.generalization_results))
        incomparable["budget_comparison"]["comparable"] = False
        with self.assertRaisesRegex(ValueError, "fair comparison"):
            MODULE.validate_generalization_gate(self.generalization_manifest, incomparable)

        not_established_manifest = json.loads(json.dumps(self.generalization_manifest))
        claim = next(
            item for item in not_established_manifest["claims"]
            if item["claim_id"] == incomparable["claim_id"]
        )
        claim["status"] = "not_established"
        incomparable["decision"] = "not_established"
        MODULE.validate_generalization_gate(not_established_manifest, incomparable)

        sensitive = json.loads(json.dumps(self.generalization_results))
        sensitive["raw_transcript"] = "private"
        with self.assertRaisesRegex(ValueError, "raw_transcript is prohibited"):
            MODULE.validate_generalization_gate(self.generalization_manifest, sensitive)

    def test_exposed_validation_case_cannot_be_renamed_holdout(self):
        recycled = json.loads(json.dumps(self.generalization_manifest))
        suite = recycled["suites"][0]
        suite.update(
            current_role="holdout", development_use=False, candidate_selection=False,
            release_validation=False, unseen=True,
        )
        with self.assertRaisesRegex(ValueError, "already exposed"):
            MODULE.validate_generalization_gate(recycled, self.generalization_results)

    def test_performance_gate_rejects_token_or_read_scope_regression(self):
        slower = json.loads(json.dumps(self.performance))
        comparison = next(item for item in slower["comparisons"] if item["id"] == "fast-resume")
        for run in comparison["candidate"]["runs"]:
            run["input_tokens"] = 999999
        with self.assertRaisesRegex(ValueError, "fast-resume regressed"):
            MODULE.validate_performance_gate(slower)

        slower_workflow = json.loads(json.dumps(self.performance))
        comparison = next(item for item in slower_workflow["comparisons"] if item["id"] == "bounded-workflow")
        for run in comparison["candidate"]["runs"]:
            run["elapsed_seconds"] = 999999
        with self.assertRaisesRegex(ValueError, "bounded-workflow regressed"):
            MODULE.validate_performance_gate(slower_workflow)

        broad = json.loads(json.dumps(self.performance))
        broad["controls"][0]["passed"] = False
        with self.assertRaisesRegex(ValueError, "control failed"):
            MODULE.validate_performance_gate(broad)

    def test_performance_gate_rejects_mismatched_pairs(self):
        paired = json.loads(json.dumps(self.performance))
        comparison = next(item for item in paired["comparisons"] if item["mode"] == "paired")
        comparison["candidate"]["runs"][0]["pair"] = "wrong"
        with self.assertRaisesRegex(ValueError, "mismatched pair"):
            MODULE.validate_performance_gate(paired)

    def test_activation_gate_rejects_small_or_single_run_matrix(self):
        tiny = {"positive": {"expect_activation": True}}
        with self.assertRaisesRegex(ValueError, "at least 10 cases"):
            MODULE.validate_activation_gate(tiny, 3)
        with self.assertRaisesRegex(ValueError, "at least 3 times"):
            MODULE.validate_activation_gate(
                {f"p{i}": {"expect_activation": True} for i in range(5)}
                | {f"n{i}": {"expect_activation": False} for i in range(5)},
                1,
            )

    def test_activation_results_reject_read_or_token_regressions(self):
        broad = json.loads(json.dumps(self.activation))
        accepted = next(arm for arm in broad["arms"] if arm["decision"] == "accepted")
        accepted["runs"][0]["correct"] = False
        accepted["runs"][0]["forbidden_reads"] = ["docs/nulnul/project.md"]
        with self.assertRaisesRegex(ValueError, "not exact and bounded"):
            MODULE.validate_activation_results(broad, self.evolution)

        expensive = json.loads(json.dumps(self.activation))
        expensive["paired_comparison"]["maximum_input_change_percent"] = -100
        with self.assertRaisesRegex(ValueError, "paired input-token budget"):
            MODULE.validate_activation_results(expensive, self.evolution)

    def test_observable_evolution_rejects_invalid_or_sensitive_digests(self):
        result = MODULE.validate_observable_evolution(self.activation)
        self.assertEqual(result["owners"], {"navigator": 0, "gate": 1})

        bad_stage = json.loads(json.dumps(self.activation))
        bad_stage["observable_evolution"]["champion"]["runs"][0]["stages"][0]["stage"] = "thinking"
        with self.assertRaisesRegex(ValueError, "stage is invalid"):
            MODULE.validate_observable_evolution(bad_stage)

        sensitive = json.loads(json.dumps(self.activation))
        sensitive["observable_evolution"]["champion"]["runs"][0]["raw_transcript"] = "private"
        with self.assertRaisesRegex(ValueError, "raw_transcript is prohibited"):
            MODULE.validate_observable_evolution(sensitive)

        wrong_order = json.loads(json.dumps(self.activation))
        wrong_order["observable_evolution"]["causal_attribution_1_4_1"]["measurements"][
            "resolvable_wrapper"
        ]["verification_stage_entered"][0] = True
        with self.assertRaisesRegex(ValueError, "incomplete or misaligned"):
            MODULE.validate_observable_evolution(wrong_order)

        stale_truth = json.loads(json.dumps(self.activation))
        stale_truth["observable_evolution"]["checkpoint_truth_1_4_2"][
            "candidate_measurements"
        ]["unverified_mutated_repository_state_accepted_for_fast_resume"][0] = True
        with self.assertRaisesRegex(ValueError, "checkpoint-truth evidence is incomplete or unsafe"):
            MODULE.validate_observable_evolution(stale_truth)

    def test_claude_evidence_fails_on_unverified_protected_write(self):
        version = json.loads((ROOT / "plugins/nulnul-harness/.codex-plugin/plugin.json").read_text(encoding="utf-8"))["version"]
        evidence = {
            "schema_version": 1,
            "case_id": "positive-adopt-existing-harness",
            "plugin_version": version,
            "plugin_source": "github",
            "protected_write_calls": [],
            "existing_agents": {
                "collector": {"before_sha256": "a", "after_sha256": "a"},
                "reviewer": {"before_sha256": "b", "after_sha256": "b"},
            },
            "roster_enumerated": True,
            "agents_classified": True,
            "session_entry_present": True,
            "checkpoint_fast_path_ready": True,
            "checks": {name: {"exit_code": 0} for name in ("repository", "project_setup", "checkpoint", "completion", "documentation_debt")},
        }
        MODULE.validate_claude_gate(evidence, version)
        evidence["protected_write_calls"] = [{"tool": "Write", "target": ".claude/**"}]
        with self.assertRaisesRegex(ValueError, "protected-path write"):
            MODULE.validate_claude_gate(evidence, version)


if __name__ == "__main__":
    unittest.main()
