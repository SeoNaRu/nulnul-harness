import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = (
    ROOT
    / "plugins/nulnul-harness/skills/nulnul-harness/scripts/validate_autonomous_evolution.py"
)
SPEC = importlib.util.spec_from_file_location("validate_autonomous_evolution", VALIDATOR)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class AutonomousEvolutionTests(unittest.TestCase):
    def setUp(self):
        self.state = json.loads(
            (ROOT / "docs/nulnul/evolution.json").read_text(encoding="utf-8")
        )
        self.episode = self.state["autonomous_episodes"][0]

    def test_current_bounded_episode_is_valid(self):
        self.assertEqual(MODULE.validate(self.state), [])

    def test_budget_bypass_is_rejected(self):
        self.episode["budget"]["max_candidates"] = 1
        self.assertIn(
            "autonomous_episodes[0] exceeded max_candidates",
            MODULE.validate(self.state),
        )

    def test_candidate_cannot_credit_itself(self):
        self.episode["candidates"][1]["evaluation"]["owner_agent"] = "coach"
        self.assertIn(
            "autonomous_episodes[0].candidates[1] is self-credited",
            MODULE.validate(self.state),
        )

    def test_rejected_replay_must_be_deduplicated(self):
        self.episode["candidates"][0]["archive_match"] = None
        self.assertIn(
            "autonomous_episodes[0].candidates[0] replays rejected archive knowledge",
            MODULE.validate(self.state),
        )

    def test_holdout_leakage_is_rejected(self):
        self.episode["holdout_case_ids_read"] = ["holdout:retired"]
        self.assertIn(
            "autonomous_episodes[0] leaked holdout material into autonomous search",
            MODULE.validate(self.state),
        )

    def test_permission_expansion_is_blocked_before_evaluation(self):
        self.episode["candidates"][1]["permission_delta"] = ["publish"]
        self.assertIn(
            "autonomous_episodes[0].candidates[1] expands permission without approval",
            MODULE.validate(self.state),
        )

    def test_missing_prediction_is_rejected(self):
        self.episode["candidates"][1]["prediction"] = ""
        self.assertIn(
            "autonomous_episodes[0].candidates[1].prediction must be non-empty",
            MODULE.validate(self.state),
        )

    def test_missing_evidence_is_rejected(self):
        self.episode["candidates"][1]["evaluation"]["evidence"] = ""
        self.assertIn(
            "autonomous_episodes[0].candidates[1].evaluation.evidence must be non-empty",
            MODULE.validate(self.state),
        )

    def test_archive_identity_cannot_be_relinked(self):
        self.episode["candidates"][0]["mechanism_id"] = "different-mechanism"
        self.assertIn(
            "autonomous_episodes[0].candidates[0].archive_match identity mismatch",
            MODULE.validate(self.state),
        )

    def test_stop_decision_cannot_force_promotion(self):
        self.episode["decision"] = "NO_PROMOTION"
        self.episode["stop_reason"] = "NO_PROMOTION"
        self.assertIn(
            "autonomous_episodes[0] cannot select a candidate for decision NO_PROMOTION",
            MODULE.validate(self.state),
        )

    def test_no_promotion_is_a_valid_outcome(self):
        episode = self.episode
        candidate = episode["candidates"][1]
        candidate["evaluation"].update(status="failed", primary_success=False)
        candidate["decision"] = "rejected"
        candidate["rejection_reason"] = "No deterministic improvement."
        episode["cost"]["failed_candidates"] = 1
        episode["decision"] = "NO_PROMOTION"
        episode["selected_candidate_id"] = None
        episode["stop_reason"] = "NO_PROMOTION"
        self.assertEqual(MODULE.validate(self.state), [])
        episode["stop_reason"] = "SUCCESS"
        self.assertIn(
            "autonomous_episodes[0].stop_reason does not match decision",
            MODULE.validate(self.state),
        )

    def test_parent_identity_must_match_proposal(self):
        self.episode["candidates"][1]["parent_version"] = 14
        self.assertIn(
            "autonomous_episodes[0].candidates[1] parent identity does not match proposal",
            MODULE.validate(self.state),
        )
        self.episode["candidates"][1]["author_agent"] = "navigator"
        self.assertIn(
            "autonomous_episodes[0].candidates[1] author identity does not match proposal",
            MODULE.validate(self.state),
        )


if __name__ == "__main__":
    unittest.main()
