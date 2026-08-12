import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "plugins/nulnul-harness/skills/nulnul-harness/scripts/cross_project_evolution.py"
EVIDENCE = ROOT / "evals/meta-evolution/cross-project-evidence.json"
SPEC = importlib.util.spec_from_file_location("cross_project_evolution", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CrossProjectEvolutionTests(unittest.TestCase):
    def setUp(self):
        self.evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))

    def facts(self, conditions, permissions=None):
        return {"schema_version": 1, "conditions": conditions, "approved_permissions": permissions or []}

    def test_current_entry_evidence_is_valid(self):
        self.assertEqual(MODULE.validate_evidence(self.evidence), [])
        self.assertEqual(self.evidence["entry_gate"]["independent_family_count"], 3)

    def test_one_family_or_same_family_variants_fail_entry_gate(self):
        one = copy.deepcopy(self.evidence)
        one["adaptations"] = one["adaptations"][:1]
        one["relations"] = []
        self.assertIn("entry gate does not match independent mechanism families", MODULE.validate_evidence(one))
        variants = copy.deepcopy(self.evidence)
        for row in variants["adaptations"]:
            row["mechanism_family"] = "same-family"
        self.assertIn("entry gate does not match independent mechanism families", MODULE.validate_evidence(variants))

    def test_raw_or_private_project_data_is_rejected(self):
        raw = copy.deepcopy(self.evidence)
        raw["raw_project_data_included"] = True
        self.assertIn("raw project data must be explicitly absent", MODULE.validate_evidence(raw))
        raw["adaptations"][0]["repository_name"] = "private-project"
        self.assertTrue(any("repository_name is prohibited" in error for error in MODULE.validate_evidence(raw)))

    def test_relation_needs_evidence_and_unknown_is_supported(self):
        self.assertTrue(all(row["type"] == "UNKNOWN" for row in self.evidence["relations"]))
        broken = copy.deepcopy(self.evidence)
        broken["relations"][0]["evidence"] = ""
        self.assertIn("relations[0].evidence must be non-empty", MODULE.validate_evidence(broken))

    def test_meta_shortlist_keeps_correct_apply_with_fewer_checks(self):
        facts = self.facts([
            "durable_multi_session", "verified_checkpoint_used", "deterministic_completion_check",
            "bounded_verification_files", "checkpoint_receipt_supported",
            "machine_readable_evaluation", "measured_nonpass", "evolution_state_present",
        ])
        flat = MODULE.lookup(self.evidence, facts)
        meta = MODULE.meta_lookup(self.evidence, facts)
        self.assertEqual(meta["selected"], flat["selected"])
        self.assertLess(meta["compatibility_checks_executed"], flat["compatibility_checks_executed"])

    def test_no_relevant_adaptation_is_not_forced(self):
        result = MODULE.meta_lookup(
            self.evidence,
            self.facts(["one_shot_task", "passing_only_run", "single_file_change"]),
        )
        self.assertEqual(result["status"], "NO_RELEVANT_ADAPTATION")
        self.assertEqual(result["selected"], [])

    def test_contraindication_and_popularity_do_not_force_activation(self):
        evidence = copy.deepcopy(self.evidence)
        evidence["adaptations"][0]["positive_transfer_count"] = 999
        result = MODULE.meta_lookup(evidence, self.facts(["one_shot_task"]))
        self.assertNotIn("personal-checkpoint-freshness-v1", result["selected"])

    def test_revoked_and_stale_evidence_are_excluded(self):
        for field, value in (("status", "revoked"), ("freshness", {"evidence_status": "stale", "last_verified": "2026-08-13"})):
            evidence = copy.deepcopy(self.evidence)
            evidence["adaptations"][0][field] = value
            result = MODULE.meta_lookup(evidence, self.facts(evidence["adaptations"][0]["activation_conditions"]))
            self.assertNotIn(evidence["adaptations"][0]["adaptation_id"], result["selected"])

    def test_permission_mismatch_excludes_without_expansion(self):
        evidence = copy.deepcopy(self.evidence)
        adaptation = evidence["adaptations"][1]
        adaptation["permission_requirements"] = ["publish"]
        result = MODULE.meta_lookup(evidence, self.facts(adaptation["activation_conditions"]))
        self.assertEqual(result["status"], "NO_RELEVANT_ADAPTATION")

    def test_conflict_requires_resolution(self):
        evidence = copy.deepcopy(self.evidence)
        first, second = evidence["adaptations"][:2]
        second["activation_conditions"] = list(first["activation_conditions"])
        second["contraindications"] = list(first["contraindications"])
        evidence["relations"][0].update(
            type="CONFLICTS",
            evidence="A deterministic control makes both mechanisms write the same state contract.",
            reason="Concurrent writers would violate the single-writer guardrail.",
            scope="conflict control only",
        )
        result = MODULE.meta_lookup(evidence, self.facts(first["activation_conditions"]))
        self.assertEqual(result["status"], "META_CONFLICT")
        self.assertEqual(result["selected"], [])

    def test_failed_transfer_count_and_schema_fail_closed(self):
        broken = copy.deepcopy(self.evidence)
        broken["adaptations"][0].pop("failed_transfer_count")
        self.assertIn("adaptations[0] is incomplete", MODULE.validate_evidence(broken))
        broken = copy.deepcopy(self.evidence)
        broken["schema_version"] = 99
        self.assertIn("cross-project evidence must be a schema-version-1 object", MODULE.validate_evidence(broken))


if __name__ == "__main__":
    unittest.main()
