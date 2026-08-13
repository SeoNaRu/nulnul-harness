import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREREG = json.loads((ROOT / "evals/capability-authority/preregistration.json").read_text(encoding="utf-8"))
RESULTS = json.loads((ROOT / "evals/capability-authority/results.json").read_text(encoding="utf-8"))
SKILL = (ROOT / "plugins/nulnul-harness/skills/nulnul-harness/SKILL.md").read_text(encoding="utf-8")


class CapabilityAuthorityEvidenceTests(unittest.TestCase):
    def test_bounded_search_stopped_without_promotion(self):
        self.assertEqual(PREREG["episode_id"], RESULTS["episode_id"])
        budget = PREREG["budget"]
        measured = RESULTS["model_evaluation"]
        self.assertLessEqual(measured["model_invocations"], budget["max_model_invocations"])
        self.assertLessEqual(measured["evaluation_runs"], budget["max_evaluation_runs"])
        self.assertEqual(RESULTS["gate"]["decision"], "NO_ADVANTAGE")
        self.assertFalse(RESULTS["gate"]["candidate_promoted"])
        self.assertNotIn("relevance-versus-authority boundary", SKILL)

    def test_gate_preserves_failed_and_unestablished_evidence(self):
        arms = {row["id"]: row for row in RESULTS["model_evaluation"]["arms"]}
        self.assertEqual(arms["champion"]["correct_decisions"], 2)
        self.assertEqual(arms["candidate-secondary-boundary"]["explicit_role_attribution"], 1)
        self.assertEqual(arms["candidate-observable-binding"]["explicit_role_attribution"], 1)
        controls = {row["id"]: row["status"] for row in RESULTS["controls"]}
        self.assertEqual(controls["positive-design"], "passed")
        self.assertEqual(controls["project-override"], "passed")
        self.assertEqual(controls["explicit-user-override"], "not-established")
        self.assertEqual(controls["skill-only-fallback"], "not-established")
        self.assertEqual(controls["implementation-only"], "not-established")

    def test_evidence_is_bounded_and_privacy_safe(self):
        privacy = RESULTS["context_and_privacy"]
        self.assertEqual(privacy["approved_personal_sources_per_run"], 1)
        self.assertEqual(privacy["unrelated_personal_reads"], 0)
        self.assertEqual(privacy["entire_personal_store_reads"], 0)
        self.assertEqual(privacy["permission_delta"], [])
        self.assertFalse(privacy["durable_raw_personal_content"])
        serialized = json.dumps(RESULTS).lower()
        for forbidden in ("/home/", "/mnt/", "raw_transcript", "raw_prompt", "raw_response"):
            self.assertNotIn(forbidden, serialized)


if __name__ == "__main__":
    unittest.main()
