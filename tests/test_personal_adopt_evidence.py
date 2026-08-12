import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/personal_adopt_evidence.py"
EVIDENCE = ROOT / "evals/personal-evolution/public-adoption.json"
SPEC = importlib.util.spec_from_file_location("personal_adopt_evidence", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PersonalAdoptEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))

    def errors(self, payload=None):
        return MODULE.validate(payload or self.evidence, "1.7.0")

    def test_current_public_personal_adoption_is_valid(self):
        self.assertEqual(self.errors(), [])

    def test_wrong_version_or_local_source_is_rejected(self):
        altered = copy.deepcopy(self.evidence)
        altered["installed_plugin"].update(version="1.6.0", local_override=True)
        errors = self.errors(altered)
        self.assertIn("public personal adoption plugin version is stale", errors)
        self.assertIn("public personal adoption reused local source", errors)

    def test_private_path_is_rejected(self):
        altered = copy.deepcopy(self.evidence)
        altered["claim_boundary"] = "read /private/project"
        self.assertTrue(any("machine path" in error for error in self.errors(altered)))

    def test_false_activation_and_revoked_reuse_are_rejected(self):
        altered = copy.deepcopy(self.evidence)
        altered["negative_project"]["decision"] = "APPLY"
        altered["revocation_control"]["decision"] = "APPLY"
        errors = self.errors(altered)
        self.assertIn("fresh negative project did not skip", errors)
        self.assertIn("revoked adaptation remained applicable", errors)

    def test_self_approval_is_rejected(self):
        altered = copy.deepcopy(self.evidence)
        altered["personal_gate"]["gate_agent"] = "coach"
        self.assertIn("public Personal Gate failed or self-approved", self.errors(altered))


if __name__ == "__main__":
    unittest.main()
