import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "evals/constraint-lifecycle"
EVAL_V2 = ROOT / "evals/constraint-reconciliation-v2"


def load(name):
    return json.loads((EVAL / name).read_text(encoding="utf-8"))


def sha256(name):
    return hashlib.sha256((EVAL / name).read_bytes()).hexdigest()


def load_v2(name):
    return json.loads((EVAL_V2 / name).read_text(encoding="utf-8"))


def sha256_v2(name):
    return hashlib.sha256((EVAL_V2 / name).read_bytes()).hexdigest()


class ConstraintLifecycleEvidenceTests(unittest.TestCase):
    def test_rejected_candidate_is_bounded_and_removed(self):
        prereg = load("preregistration.json")
        attempts = load("execution-attempts.json")
        gate = load("gate-decision.json")
        first = load("results.json")
        refined = load("results-candidate-2.json")
        arms = {arm["id"]: arm for arm in first["arms"]}

        self.assertEqual(sha256("results.json"), gate["candidate_1"]["results_sha256"])
        self.assertEqual(sha256("results-candidate-2.json"), gate["candidate_2"]["results_sha256"])
        self.assertEqual(
            [arms["champion"]["exact_runs"], arms["candidate"]["exact_runs"], refined["arms"][0]["exact_runs"]],
            [0, 1, 2],
        )
        self.assertLessEqual(
            refined["paired_input_change_percent"],
            prereg["evaluation"]["maximum_paired_input_change_percent"],
        )
        self.assertEqual(
            [run["failed_checks"] for run in refined["arms"][0]["runs"] if not run["correct"]],
            2 * [{
                "permission-conflict": ["conflicts"],
                "ambiguous-project-conflict": ["conflicts"],
            }],
        )
        self.assertEqual(gate["decision"], gate["stop_reason"])
        self.assertEqual(gate["decision"], "NO_PROMOTION")
        self.assertEqual(gate["plugin_version_decision"], "keep 2.2.1")
        self.assertEqual(gate["guardrails"]["permission_delta"], [])
        self.assertFalse(gate["guardrails"]["raw_transcript_retained"])
        self.assertEqual(gate["guardrails"]["fixture_writes"], 0)
        budget = attempts["budget_after_attempts"]
        self.assertLessEqual(budget["model_invocations_used"], prereg["budget"]["max_model_invocations"])
        self.assertTrue(budget["budget_stop_triggered"])

        plugin = ROOT / "plugins/nulnul-harness"
        manifest = json.loads((plugin / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        skill = plugin / "skills/nulnul-harness/SKILL.md"
        self.assertEqual(manifest["version"], "2.2.1")
        self.assertEqual(hashlib.sha256(skill.read_bytes()).hexdigest(), prereg["champion"]["skill_sha256"])
        self.assertFalse((plugin / "skills/nulnul-harness/scripts/reconcile_constraints.py").exists())
        self.assertFalse((plugin / "skills/nulnul-harness/scripts/constraint_state.py").exists())
        self.assertFalse((plugin / "skills/nulnul-harness/scripts/record_constraint_review.py").exists())

    def test_second_candidate_is_recorded_and_removed(self):
        gate = load_v2("gate-decision.json")
        results = load_v2("results.json")
        arms = {arm["id"]: arm for arm in results["arms"]}

        self.assertEqual(sha256_v2("results.json"), gate["candidate"]["results_sha256"])
        self.assertEqual([arms["champion"]["exact_runs"], arms["candidate"]["exact_runs"]], [0, 0])
        self.assertEqual(gate["decision"], gate["stop_reason"])
        self.assertEqual(gate["decision"], "NO_PROMOTION")
        self.assertEqual(gate["plugin_version_decision"], "keep 2.2.1")
        self.assertEqual(gate["guardrails"]["permission_delta"], [])
        self.assertFalse(gate["guardrails"]["raw_transcript_retained"])

        plugin = ROOT / "plugins/nulnul-harness"
        manifest = json.loads((plugin / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], "2.2.1")
        self.assertFalse((plugin / "skills/nulnul-harness/scripts/reconcile_constraints.py").exists())


if __name__ == "__main__":
    unittest.main()
