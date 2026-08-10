import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins/nulnul-harness/skills/nulnul-harness"
TEMPLATE = SKILL / "assets/evolution-state.template.json"
VALIDATOR = SKILL / "scripts/validate_evolution_state.py"

spec = importlib.util.spec_from_file_location("validate_evolution_state", VALIDATOR)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class PersonalEvolutionTests(unittest.TestCase):
    def setUp(self):
        self.state = json.loads(TEMPLATE.read_text(encoding="utf-8"))

    def add_accepted_coach_upgrade(self, gate_agent="gate", permission_delta=None):
        self.state["feedback"].append(
            {
                "id": "feedback-1",
                "source": "agent",
                "target_agent": "coach",
                "observed": "The Coach changed an unrelated rule.",
                "expected": "Change only the layer that caused the reproduced failure.",
                "evidence": "tests/test_coach_scope.py::test_one_layer failed",
                "scope": "personal",
                "status": "converted",
            }
        )
        self.state["proposals"].append(
            {
                "id": "proposal-1",
                "feedback_ids": ["feedback-1"],
                "target_agent": "coach",
                "author_agent": "coach",
                "from_version": 1,
                "to_version": 2,
                "cause": "The profile did not require a single change target.",
                "change_target": "Coach profile",
                "regression_check": "tests/test_coach_scope.py::test_one_layer",
                "primary_metric": "unrelated changes",
                "permission_delta": permission_delta or [],
                "rollback": "coach v1",
                "status": "accepted",
            }
        )
        self.state["promotions"].append(
            {
                "id": "promotion-1",
                "proposal_id": "proposal-1",
                "gate_agent": gate_agent,
                "before": "failure reproduced",
                "after": "regression passed",
                "regressions_passed": True,
                "decision": "accepted",
            }
        )
        self.state["agents"]["coach"].update(version=2, last_promotion_id="promotion-1")

    def test_template_is_valid_and_resumable(self):
        self.state["checkpoint"].update(
            goal="Ship the personal evolution loop.",
            milestone="Validator implemented.",
            completion_check="python3 -m unittest discover -s tests -p 'test_*.py' -v",
            last_verified="Template validation passed.",
            next_action="Run the product suite.",
        )
        self.assertEqual(validator.validate(self.state), [])

    def test_independent_gate_can_promote_coach(self):
        self.add_accepted_coach_upgrade()
        self.assertEqual(validator.validate(self.state), [])

    def test_agent_cannot_approve_its_own_upgrade(self):
        self.add_accepted_coach_upgrade(gate_agent="coach")
        self.assertIn("promotion promotion-1 is self-approved", validator.validate(self.state))

    def test_unapproved_permission_expansion_is_rejected(self):
        self.add_accepted_coach_upgrade(permission_delta=["publish"])
        self.assertIn(
            "promotion promotion-1 expands permission without approval",
            validator.validate(self.state),
        )

    def test_invalid_checkpoint_cannot_be_resumed(self):
        broken = copy.deepcopy(self.state)
        broken["checkpoint"]["status"] = "guessing"
        self.assertIn("checkpoint.status is invalid", validator.validate(broken))

    def test_malformed_state_returns_errors_instead_of_crashing(self):
        broken = copy.deepcopy(self.state)
        broken["agents"]["coach"] = []
        broken["feedback"] = [{"id": [], "source": [], "target_agent": [], "observed": "x", "expected": "y", "evidence": "z", "scope": [], "status": []}]
        broken["proposals"] = [{"id": "p", "feedback_ids": [[]], "target_agent": "coach", "author_agent": [], "from_version": 1, "to_version": 2, "cause": "x", "change_target": "y", "regression_check": "z", "primary_metric": "m", "permission_delta": [[]], "rollback": "v1", "status": "accepted"}]
        broken["promotions"] = [{"id": "g", "proposal_id": [], "gate_agent": [], "before": "x", "after": "y", "regressions_passed": "yes", "decision": []}]
        self.assertTrue(validator.validate(broken))

    def test_promotion_cannot_disagree_with_proposal_status(self):
        self.add_accepted_coach_upgrade()
        self.state["proposals"][0]["status"] = "proposed"
        self.state["agents"]["coach"].update(version=1, last_promotion_id=None)
        self.assertIn(
            "promotion promotion-1 disagrees with the proposal status",
            validator.validate(self.state),
        )

    def test_empty_reproduction_evidence_is_rejected(self):
        self.add_accepted_coach_upgrade()
        self.state["feedback"][0]["evidence"] = ""
        self.assertIn(
            "feedback feedback-1.evidence must be non-empty",
            validator.validate(self.state),
        )

    def test_agent_can_keep_history_after_a_second_promotion(self):
        self.add_accepted_coach_upgrade()
        self.state["feedback"].append(
            {"id": "feedback-2", "source": "test", "target_agent": "coach", "observed": "v2 failed", "expected": "v3 passes", "evidence": "regression-2", "scope": "agent", "status": "converted"}
        )
        self.state["proposals"].append(
            {"id": "proposal-2", "feedback_ids": ["feedback-2"], "target_agent": "coach", "author_agent": "coach", "from_version": 2, "to_version": 3, "cause": "v2 gap", "change_target": "Coach profile", "regression_check": "regression-2", "primary_metric": "failures", "permission_delta": [], "rollback": "coach v2", "status": "accepted"}
        )
        self.state["promotions"].append(
            {"id": "promotion-2", "proposal_id": "proposal-2", "gate_agent": "gate", "before": "v2 failed", "after": "v3 passed", "regressions_passed": True, "decision": "accepted"}
        )
        self.state["agents"]["coach"].update(version=3, last_promotion_id="promotion-2")
        self.assertEqual(validator.validate(self.state), [])

    def test_feedback_can_reference_a_rejected_proposal(self):
        self.add_accepted_coach_upgrade()
        self.state["proposals"][0]["status"] = "rejected"
        self.state["promotions"][0]["decision"] = "rejected"
        self.state["feedback"][0]["rejected_proposals"] = ["proposal-1"]
        self.assertEqual(validator.validate(self.state), [])

    def test_feedback_cannot_reference_an_accepted_proposal_as_rejected(self):
        self.add_accepted_coach_upgrade()
        self.state["feedback"][0]["rejected_proposals"] = ["proposal-1"]
        self.assertIn(
            "feedback feedback-1.rejected_proposals must reference rejected or rolled back proposals",
            validator.validate(self.state),
        )

    def test_proposal_author_cannot_serve_as_gate(self):
        self.add_accepted_coach_upgrade()
        self.state["proposals"][0]["author_agent"] = "gate"
        self.assertIn(
            "promotion promotion-1 is approved by its proposal author",
            validator.validate(self.state),
        )


if __name__ == "__main__":
    unittest.main()
