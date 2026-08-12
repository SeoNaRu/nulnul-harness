import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "plugins/nulnul-harness/skills/nulnul-harness/scripts/personal_adaptation.py"
PREREGISTRATION = ROOT / "evals/personal-evolution/preregistration.json"
RESULTS = ROOT / "evals/personal-evolution/results.json"
SPEC = importlib.util.spec_from_file_location("personal_adaptation", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PersonalAdaptationTests(unittest.TestCase):
    def setUp(self):
        self.preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
        self.results = json.loads(RESULTS.read_text(encoding="utf-8"))
        self.facts = {
            "schema_version": 1,
            "conditions": self.preregistration["personal_candidate"]["activation_conditions"],
            "approved_permissions": [],
        }

    def errors(self, preregistration=None, results=None):
        return MODULE.validate_evidence(
            preregistration or self.preregistration,
            results or self.results,
            ROOT,
        )

    def test_current_personal_evolution_evidence_is_valid(self):
        self.assertEqual(self.errors(), [])

    def test_transferless_personal_promotion_is_rejected(self):
        altered = copy.deepcopy(self.results)
        altered["transfer_results"].pop()
        self.assertIn("failed or missing transfer result was hidden", self.errors(results=altered))

    def test_raw_project_data_is_rejected(self):
        altered = copy.deepcopy(self.results)
        altered["personal_adaptation"]["source_code"] = "private implementation"
        self.assertTrue(any("source_code is prohibited" in error for error in self.errors(results=altered)))

    def test_credential_and_private_path_are_rejected(self):
        altered = copy.deepcopy(self.results)
        altered["personal_gate"]["evidence"] = "sk-abcdefghijk from /opt/private-project"
        self.assertTrue(any("private or machine-specific" in error for error in self.errors(results=altered)))

    def test_activation_conditions_are_required(self):
        altered = copy.deepcopy(self.preregistration)
        altered["personal_candidate"]["activation_conditions"] = []
        self.assertIn(
            "personal_candidate.activation_conditions must not be empty",
            self.errors(preregistration=altered),
        )

    def test_transfer_identity_mismatch_is_rejected(self):
        altered = copy.deepcopy(self.results)
        altered["transfer_results"][0]["candidate_ref"] = "different"
        self.assertIn(
            "transfer result identity mismatch: personal:node-package-transfer-1",
            self.errors(results=altered),
        )
        adaptation = copy.deepcopy(self.results["personal_adaptation"])
        adaptation["transfer_results"][0]["candidate_ref"] = "different"
        self.assertTrue(any("identity mismatch" in error for error in MODULE.validate_adaptation(adaptation)))

    def test_personal_gate_cannot_self_approve(self):
        altered = copy.deepcopy(self.results)
        altered["personal_gate"]["gate_agent"] = "coach"
        self.assertIn("Personal Gate self-approval or author identity mismatch", self.errors(results=altered))

    def test_failed_transfer_cannot_be_hidden_or_promoted(self):
        altered = copy.deepcopy(self.results)
        altered["transfer_results"][0]["completion_check_passed"] = False
        errors = self.errors(results=altered)
        self.assertIn("positive transfer failed: personal:node-package-transfer-1", errors)
        self.assertIn("Personal Gate promoted without complete transfer evidence", errors)

    def test_negative_shape_cannot_auto_apply(self):
        altered = copy.deepcopy(self.results)
        negative = altered["transfer_results"][2]
        negative.update(activation_decision="APPLY", application_status="applied", completion_check_passed=True)
        self.assertIn(
            "transfer activation decision failed: personal:one-shot-skip-3",
            self.errors(results=altered),
        )

    def test_personal_home_is_required(self):
        with self.assertRaisesRegex(MODULE.PersonalEvolutionError, "PERSONAL_HOME_REQUIRED"):
            MODULE.load_registry(None)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            selected = root / "selected"
            selected.mkdir()
            alias = root / "alias"
            alias.symlink_to(selected, target_is_directory=True)
            with self.assertRaisesRegex(MODULE.PersonalEvolutionError, "PERSONAL_HOME_REQUIRED"):
                MODULE.load_registry(alias)

    def test_revoked_or_stale_adaptation_is_not_applied(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            MODULE.promote(home, self.preregistration, self.results, ROOT)
            MODULE.revoke(home, "personal-checkpoint-freshness-v1", "later regression", "2026-08-12")
            discovered = MODULE.discover(home, self.facts)
            self.assertEqual(discovered["status"], "SKIP")
            self.assertEqual(discovered["skipped"][0]["reason"], "revoked")
            registry = MODULE.load_registry(home)
            registry["adaptations"][0]["status"] = "stale"
            (home / MODULE.REGISTRY_NAME).write_text(json.dumps(registry), encoding="utf-8")
            self.assertEqual(MODULE.discover(home, self.facts)["skipped"][0]["reason"], "stale")

    def test_conflicting_adaptations_fail_closed(self):
        first = copy.deepcopy(self.results["personal_adaptation"])
        second = copy.deepcopy(first)
        first["conflicts_with"] = ["alternative-checkpoint-policy"]
        second.update(
            adaptation_id="alternative-checkpoint-policy",
            mechanism_id="alternative-checkpoint-mechanism",
            conflicts_with=[first["adaptation_id"]],
        )
        for row in second["transfer_results"]:
            row["mechanism_id"] = second["mechanism_id"]
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            (home / MODULE.REGISTRY_NAME).write_text(
                json.dumps({"schema_version": 1, "adaptations": [first, second]}),
                encoding="utf-8",
            )
            self.assertEqual(MODULE.discover(home, self.facts)["status"], "CONFLICT_REQUIRES_RESOLUTION")

    def test_permission_expansion_is_rejected(self):
        altered_preregistration = copy.deepcopy(self.preregistration)
        altered_results = copy.deepcopy(self.results)
        altered_preregistration["personal_candidate"]["required_permissions"] = ["publish"]
        altered_results["personal_adaptation"]["required_permissions"] = ["publish"]
        self.assertIn(
            "personal candidate expands permission without approval",
            self.errors(altered_preregistration, altered_results),
        )

    def test_unsupported_registry_schema_fails_closed(self):
        self.assertIn(
            "personal registry must be a schema-version-1 object",
            MODULE.validate_registry({"schema_version": 99, "adaptations": []}),
        )

    def test_duplicate_adaptation_identity_merges_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            self.assertEqual(MODULE.promote(home, self.preregistration, self.results, ROOT)["status"], "promoted")
            self.assertEqual(MODULE.promote(home, self.preregistration, self.results, ROOT)["status"], "merged")
            self.assertEqual(len(MODULE.load_registry(home)["adaptations"]), 1)

    def test_narrower_scope_cannot_be_recorded_as_universal(self):
        altered = copy.deepcopy(self.results)
        altered["personal_gate"].update(
            decision="NARROWER_PERSONAL_SCOPE",
            established_scope="Universal personal rule",
        )
        altered["personal_adaptation"]["status"] = "narrowed"
        altered["personal_adaptation"]["activation_conditions"].append("local_offline_repository")
        self.assertIn(
            "narrower scope cannot be recorded as a universal personal rule",
            self.errors(results=altered),
        )

    def test_false_activation_conditions_skip(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            MODULE.promote(home, self.preregistration, self.results, ROOT)
            facts = {"schema_version": 1, "conditions": ["one_shot_task"], "approved_permissions": []}
            self.assertEqual(MODULE.discover(home, facts)["status"], "SKIP")


if __name__ == "__main__":
    unittest.main()
