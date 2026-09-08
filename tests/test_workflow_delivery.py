import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins/nulnul-harness/skills/nulnul-harness"
sys.path.insert(0, str(SKILL / "scripts"))
import workflow_delivery as delivery


class WorkflowDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.spec = delivery.read_json(SKILL / "assets/workflow-example.json")
        for name, body in {"api.json": "[1, 2]", "view.json": '{"count": 2}', "notes.txt": "approved"}.items():
            (self.root / name).write_text(body, encoding="utf-8")

    def receipts(self):
        return [delivery.verify(self.root, self.spec, row["id"]) for row in self.spec["steps"]]

    def actions(self, receipts, only=()):
        result = delivery.plan(self.root, self.spec, receipts, only)
        self.assertFalse(result["promotion_eligible"])
        return {row["id"]: row["action"] for row in result["steps"]}

    def test_boundary_check_and_downstream_invalidation(self):
        receipts = self.receipts()
        self.assertTrue(all(row["verification_status"] == "verified" for row in receipts))
        (self.root / "api.json").write_text('{"projects": [1, 2]}', encoding="utf-8")
        self.assertEqual(delivery.verify(self.root, self.spec, "api")["verification_status"], "failed")
        self.assertEqual(delivery.verify(self.root, self.spec, "view")["verification_status"], "failed")
        self.assertEqual(self.actions(receipts), {"api": "RUN", "view": "RUN", "notes": "REUSE"})

    def test_partial_rerun_expands_dependencies_without_touching_unrelated_work(self):
        receipts = self.receipts()
        self.assertEqual(self.actions(receipts), {"api": "REUSE", "view": "REUSE", "notes": "REUSE"})
        self.assertEqual(self.actions(receipts, ["view"]), {"api": "REUSE", "view": "RUN", "notes": "REUSE"})
        (self.root / "api.json").write_text("[3, 4]", encoding="utf-8")
        (self.root / "notes.txt").unlink()
        self.assertEqual(self.actions(receipts, ["view"]), {"api": "RUN", "view": "RUN", "notes": "SKIP"})
        with self.assertRaisesRegex(ValueError, "unknown requested"):
            self.actions(receipts, ["missing"])

    def test_contract_and_verifier_changes_reject_old_receipts(self):
        checker = self.root / "checker.py"
        checker.write_text("assert True\n", encoding="utf-8")
        self.spec["steps"][0]["inputs"].append("checker.py")
        receipts = self.receipts()
        checker.write_text("assert False\n", encoding="utf-8")
        self.assertEqual(self.actions(receipts)["api"], "RUN")
        checker.write_text("assert True\n", encoding="utf-8")
        self.spec["steps"][0]["check"] = [sys.executable, "-c", "pass", "same", "same"]
        self.assertEqual(self.actions(receipts)["api"], "RUN")
        self.assertEqual(delivery.verify(self.root, self.spec, "api")["verification_status"], "verified")
        with self.assertRaisesRegex(ValueError, "duplicate workflow receipt"):
            delivery.plan(self.root, self.spec, [receipts[0], receipts[0]])

    def test_graph_ownership_and_path_controls(self):
        for mutate in (
            lambda s: s["steps"][0]["needs"].append("view"),
            lambda s: s["steps"][0]["needs"].append("missing"),
            lambda s: s["steps"][1].update(needs=[]),
            lambda s: s["steps"][1]["outputs"].append("api.json"),
            lambda s: s["steps"][0]["inputs"].append("../outside.json"),
            lambda s: s["steps"].append(copy.deepcopy(s["steps"][0])),
        ):
            with self.subTest(mutation=mutate):
                specification = copy.deepcopy(self.spec)
                mutate(specification)
                with self.assertRaises(ValueError):
                    delivery.plan(self.root, specification)
        (self.root / "api.json").unlink()
        (self.root / "api.json").symlink_to(self.root / "view.json")
        with self.assertRaisesRegex(ValueError, "symlink"):
            delivery.plan(self.root, self.spec)

    def test_unknown_execution_and_input_drift_never_verify(self):
        for error in (OSError("unavailable"), subprocess.TimeoutExpired("check", 1)):
            with self.subTest(error=type(error).__name__):
                with mock.patch.object(delivery.subprocess, "run", side_effect=error):
                    self.assertEqual(delivery.verify(self.root, self.spec, "api")["verification_status"], "unknown")
        def drifting(*args, **kwargs):
            (self.root / "api.json").write_text("[]", encoding="utf-8")
            return subprocess.CompletedProcess(args[0], 0)
        with mock.patch.object(delivery.subprocess, "run", side_effect=drifting):
            receipt = delivery.verify(self.root, self.spec, "api")
        self.assertEqual(receipt["verification_status"], "unknown")
        self.assertEqual(receipt["fingerprint"], "")

    def cases(self):
        bundle = delivery.read_json(SKILL / "assets/skill-cases.template.json")
        bundle["candidate_digest"] = hashlib.sha256(b"bounded fixture candidate").hexdigest()
        observations = [{"case_id": row["id"], "candidate_digest": bundle["candidate_digest"],
                         "used_capability": row["expected_use"], "check_status": "verified",
                         "check_id": hashlib.sha256(row["id"].encode()).hexdigest()} for row in bundle["cases"]]
        return bundle, observations

    def test_skill_cases_require_correct_routes_and_completed_checks(self):
        bundle, observations = self.cases()
        result = delivery.score_cases(bundle, observations)
        self.assertTrue(result["passed"])
        self.assertFalse(result["promotion_eligible"])
        for changes in ({"used_capability": False}, {"used_capability": 1}, {"check_status": "unknown"},
                        {"check_status": "failed"}, {"check_id": "prose"}, {"candidate_digest": "f" * 64}):
            with self.subTest(changes=changes):
                wrong = copy.deepcopy(observations)
                wrong[0].update(changes)
                self.assertFalse(delivery.score_cases(bundle, wrong)["passed"])
        self.assertFalse(delivery.score_cases(bundle, observations[:-1])["passed"])

    def test_skill_cases_include_near_miss_and_followup_without_duplicate_results(self):
        bundle, observations = self.cases()
        with self.assertRaisesRegex(ValueError, "duplicate observation"):
            delivery.score_cases(bundle, observations + [observations[0]])
        for mutate in (
            lambda b: b.update(candidate_digest="0" * 64),
            lambda b: b["cases"][1].update(expected_use=True),
            lambda b: b["cases"][2].update(kind="use"),
            lambda b: b["cases"][2].update(prompt=b["cases"][0]["prompt"]),
        ):
            changed = copy.deepcopy(bundle)
            mutate(changed)
            with self.assertRaises(ValueError):
                delivery.score_cases(changed, observations)

    def test_shipped_cli_demo_exercises_real_negative_control(self):
        result = subprocess.run([sys.executable, str(SKILL / "scripts/workflow_delivery.py"), "demo"],
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        report = json.loads(result.stdout)
        self.assertEqual(report["negative_control"], "failed")
        self.assertEqual(report["invalidated"], ["api", "view"])
        self.assertFalse(report["promotion_eligible"])


if __name__ == "__main__":
    unittest.main()
