import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "plugins/nulnul-harness/skills/nulnul-harness/scripts/validate_meta_evolution.py"
PREREGISTRATION = ROOT / "evals/meta-evolution/preregistration.json"
RESULTS = ROOT / "evals/meta-evolution/results.json"
EVIDENCE = ROOT / "evals/meta-evolution/cross-project-evidence.json"
SPEC = importlib.util.spec_from_file_location("validate_meta_evolution", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class MetaEvolutionTests(unittest.TestCase):
    def setUp(self):
        self.preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
        self.results = json.loads(RESULTS.read_text(encoding="utf-8"))
        self.evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))

    def errors(self, preregistration=None, results=None, evidence=None):
        return MODULE.validate(
            preregistration or self.preregistration,
            results or self.results,
            evidence or self.evidence,
            ROOT,
        )

    def test_current_meta_episode_is_valid(self):
        self.assertEqual(self.errors(), [])
        self.assertEqual(self.results["meta_gate"]["decision"], "META_PROMOTION")

    def test_meta_proposer_or_target_cannot_self_approve(self):
        altered = copy.deepcopy(self.results)
        altered["meta_gate"]["gate_agent"] = "coach"
        self.assertIn("Meta proposer or target self-approved", self.errors(results=altered))

    def test_permission_expansion_is_rejected(self):
        altered = copy.deepcopy(self.results)
        altered["permission_delta"] = ["publish"]
        self.assertIn("meta policy expanded permissions", self.errors(results=altered))

    def test_holdout_leakage_and_reuse_are_rejected(self):
        preregistration = copy.deepcopy(self.preregistration)
        preregistration["holdout"]["material_path"] = "tests/test_cross_project_evolution.py"
        self.assertIn("HOLDOUT leaked into candidate snapshot", self.errors(preregistration=preregistration))
        altered = copy.deepcopy(self.results)
        altered["holdout_exposure"][0]["current_role"] = "holdout"
        self.assertIn("used HOLDOUT remains reusable", self.errors(results=altered))

    def test_unbounded_generation_is_rejected(self):
        altered = copy.deepcopy(self.results)
        altered["cost"]["generations"] = 2
        errors = self.errors(results=altered)
        self.assertIn("meta episode exceeded max_generations", errors)
        self.assertIn("meta episode must remain one-generation", errors)

    def test_rejected_replay_needs_new_evidence(self):
        preregistration = copy.deepcopy(self.preregistration)
        preregistration["archive_lookup"]["matching_rejected_meta_proposals"] = ["proposal-old"]
        self.assertIn("rejected meta proposal replay lacks new evidence", self.errors(preregistration=preregistration))

    def test_cloned_project_shape_is_rejected(self):
        evidence = copy.deepcopy(self.evidence)
        evidence["adaptations"][0]["tested_project_shapes"].append(evidence["adaptations"][0]["tested_project_shapes"][0])
        self.assertTrue(any("cloned project shape counted twice" in error for error in self.errors(evidence=evidence)))

    def test_failed_transfer_cannot_be_hidden(self):
        altered = copy.deepcopy(self.results)
        altered["failed_transfer_count_preserved"] = 0
        self.assertIn("failed transfer evidence was hidden", self.errors(results=altered))

    def test_no_match_and_conflict_controls_fail_closed(self):
        altered = copy.deepcopy(self.results)
        altered["no_relevant_control"]["status"] = "APPLY"
        self.assertIn("no-relevant-adaptation control forced an apply", self.errors(results=altered))
        altered = copy.deepcopy(self.results)
        altered["conflict_control"].update(status="APPLY", conflicts=[])
        self.assertIn("conflict control was auto-resolved", self.errors(results=altered))

    def test_relation_change_needs_evidence_and_current_identity(self):
        altered = copy.deepcopy(self.results)
        altered["relationship_changes"][0]["evidence"] = ""
        self.assertIn("relationship changes lack bounded evidence", self.errors(results=altered))

    def test_no_advantage_is_a_valid_gate_decision(self):
        altered = copy.deepcopy(self.results)
        flat = altered["baseline_comparison"]["flat_lookup"]
        meta = altered["baseline_comparison"]["meta_selector"]
        for target, source in zip(meta["runs"], flat["runs"]):
            target["compatibility_checks_executed"] = source["compatibility_checks_executed"]
        meta["compatibility_checks_executed"] = flat["compatibility_checks_executed"]
        altered["meta_gate"]["decision"] = "META_NO_ADVANTAGE"
        altered["relationship_changes"] = []
        altered["cost"]["relation_changes"] = 0
        self.assertEqual(self.errors(results=altered), [])

    def test_missing_rollback_and_unsupported_schema_fail_closed(self):
        altered = copy.deepcopy(self.results)
        altered["rollback"].pop("threshold")
        self.assertIn("meta rollback threshold is missing or not executable", self.errors(results=altered))
        preregistration = copy.deepcopy(self.preregistration)
        preregistration["schema_version"] = 99
        self.assertIn("meta preregistration must be a schema-version-1 object", self.errors(preregistration=preregistration))


if __name__ == "__main__":
    unittest.main()
