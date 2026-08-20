import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins/nulnul-harness/skills/nulnul-harness"
TEMPLATE = SKILL / "assets/evolution-state.template.json"
SCRIPT = SKILL / "scripts/apply_live_cycle_rollback.py"
VALIDATOR = SKILL / "scripts/validate_evolution_state.py"


def state(metric_value, live_status="observed"):
    payload = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    payload["feedback"].append(
        {
            "id": "feedback-rollback",
            "source": "test",
            "target_agent": "coach",
            "observed": "The live completion rate dropped.",
            "expected": "Keep completion rate at or above 0.9.",
            "evidence": "frozen sample and next live cycle",
            "scope": "agent",
            "status": "converted",
        }
    )
    payload["proposals"].append(
        {
            "id": "proposal-rollback",
            "feedback_ids": ["feedback-rollback"],
            "target_agent": "coach",
            "author_agent": "coach",
            "from_version": 1,
            "to_version": 2,
            "cause": "Candidate overfit the frozen sample.",
            "change_target": "Coach routing rule",
            "regression_check": "python3 -m unittest -v",
            "primary_metric": "completion rate",
            "permission_delta": [],
            "rollback": "coach v1",
            "change_level": "meta",
            "discovery_evidence": "The next live cycle exposed the drop.",
            "transfer_check": None,
            "status": "provisional",
        }
    )
    payload["promotions"].append(
        {
            "id": "promotion-rollback",
            "proposal_id": "proposal-rollback",
            "gate_agent": "gate",
            "before": "completion rate 0.9",
            "after": f"completion rate {metric_value}",
            "regressions_passed": True,
            "decision": "provisional",
            "live_cycle": {
                "status": live_status,
                "metric": "completion rate",
                "rollback_threshold": "roll back below 0.9",
                "metric_value": metric_value,
                "rollback_operator": "lt",
                "rollback_value": 0.9,
                "evidence": "measured on the next live cycle",
            },
        }
    )
    payload["agents"]["coach"].update(
        trial_version=2, trial_promotion_id="promotion-rollback"
    )
    return payload


def accepted_state(metric_value):
    payload = state(metric_value)
    payload["proposals"][0]["status"] = "accepted"
    payload["promotions"][0]["decision"] = "accepted"
    payload["agents"]["coach"].update(
        version=2,
        last_promotion_id="promotion-rollback",
        trial_version=None,
        trial_promotion_id=None,
    )
    return payload


class LiveCycleRollbackTests(unittest.TestCase):
    def run_rollback(self, payload):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "evolution.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            result = subprocess.run(
                ["python3", str(SCRIPT), str(path)], capture_output=True, text=True
            )
            updated = json.loads(path.read_text(encoding="utf-8"))
            validation = subprocess.run(
                ["python3", str(VALIDATOR), str(path)], capture_output=True, text=True
            )
            return result, updated, validation

    def test_threshold_breach_restores_previous_version(self):
        result, updated, validation = self.run_rollback(state(0.7))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(validation.returncode, 0, validation.stdout)
        self.assertEqual(updated["agents"]["coach"]["version"], 1)
        self.assertIsNone(updated["agents"]["coach"]["last_promotion_id"])
        self.assertIsNone(updated["agents"]["coach"]["trial_version"])
        self.assertEqual(updated["proposals"][0]["status"], "rolled_back")
        self.assertEqual(updated["promotions"][0]["decision"], "rolled_back")
        self.assertEqual(updated["promotions"][0]["live_cycle"]["status"], "rolled_back")

    def test_healthy_live_cycle_confirms_provisional_version(self):
        result, updated, validation = self.run_rollback(state(0.95))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(validation.returncode, 0, validation.stdout)
        self.assertEqual(updated["agents"]["coach"]["version"], 2)
        self.assertEqual(updated["agents"]["coach"]["last_promotion_id"], "promotion-rollback")
        self.assertIsNone(updated["agents"]["coach"]["trial_version"])
        self.assertEqual(updated["proposals"][0]["status"], "accepted")
        self.assertEqual(updated["promotions"][0]["decision"], "accepted")
        self.assertEqual(json.loads(result.stdout)["confirmed"], ["promotion-rollback"])

    def test_pending_live_cycle_leaves_provisional_state_unchanged(self):
        original = state(None, live_status="pending")
        result, updated, validation = self.run_rollback(original)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(validation.returncode, 0, validation.stdout)
        self.assertEqual(updated, original)
        self.assertEqual(json.loads(result.stdout), {"confirmed": [], "rolled_back": []})

    def test_legacy_accepted_version_still_rolls_back_on_breach(self):
        result, updated, validation = self.run_rollback(accepted_state(0.7))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(validation.returncode, 0, validation.stdout)
        self.assertEqual(updated["agents"]["coach"]["version"], 1)
        self.assertEqual(updated["promotions"][0]["decision"], "rolled_back")


if __name__ == "__main__":
    unittest.main()
