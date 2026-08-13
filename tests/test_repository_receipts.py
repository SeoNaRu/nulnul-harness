import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "evals/repository-receipts"
SPEC = importlib.util.spec_from_file_location("repository_receipt", EVAL / "candidate_repository_receipt.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
CASES = json.loads((EVAL / "cases.json").read_text(encoding="utf-8"))["cases"]


class RepositoryReceiptTests(unittest.TestCase):
    def fixture(self, case_id):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        for name, content in CASES[case_id]["files"].items():
            (root / name).write_text(content, encoding="utf-8")
        return temporary, root

    def design_receipt(self, root):
        return MODULE.derive(root, "design.component_shape", ["project-design.json"])

    def web_receipt(self, root, required=False):
        return MODULE.derive(
            root,
            "backend.architecture",
            ["server.py"],
            "check_backend.py",
            ["server.py"],
            "check_realtime.py" if required else None,
            ["server.py"] if required else (),
        )

    def test_design_truth_is_derived_from_the_accepted_contract(self):
        temporary, root = self.fixture("design-primary")
        with temporary:
            receipt = self.design_receipt(root)
            self.assertEqual(receipt["observed_value"], "low_radius")
            self.assertEqual(receipt["derived_decision"], "preserve")
            self.assertEqual(receipt["evidence"][0]["strength"], "authoritative")
            self.assertEqual(MODULE.validate(receipt, root), [])

    def test_working_backend_identity_and_check_are_derived(self):
        temporary, root = self.fixture("web-primary")
        with temporary:
            receipt = self.web_receipt(root)
            self.assertEqual(receipt["observed_value"], "python:wsgi")
            self.assertEqual(receipt["current_check"]["status"], "passed")
            self.assertEqual(receipt["derived_decision"], "preserve")
            self.assertEqual(MODULE.validate(receipt, root), [])

    def test_fabricated_anchor_and_mismatched_value_fail(self):
        temporary, root = self.fixture("design-primary")
        with temporary:
            receipt = self.design_receipt(root)
            fabricated = copy.deepcopy(receipt)
            fabricated["evidence"][0]["path"] = "missing.json"
            self.assertTrue(MODULE.validate(fabricated, root))
            mismatch = copy.deepcopy(receipt)
            mismatch["observed_value"] = "rounded"
            self.assertIn("receipt does not match current repository evidence", MODULE.validate(mismatch, root))

    def test_receipt_is_stale_after_bounded_anchor_mutation(self):
        temporary, root = self.fixture("design-primary")
        with temporary:
            receipt = self.design_receipt(root)
            (root / "project-design.json").write_text(
                '{"accepted":{"component_shape":"square"}}\n', encoding="utf-8"
            )
            self.assertIn("receipt does not match current repository evidence", MODULE.validate(receipt, root))

    def test_isolated_css_and_personal_note_are_insufficient(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "card.css").write_text(".card { border-radius: 4px; }\n", encoding="utf-8")
            (root / "personal-design.json").write_text(
                '{"status":"approved","component_shape":"rounded"}\n', encoding="utf-8"
            )
            for name in ("card.css", "personal-design.json"):
                with self.subTest(name=name), self.assertRaisesRegex(
                    MODULE.ReceiptError, "authoritative accepted design contract not found"
                ):
                    MODULE.derive(root, "design.component_shape", [name])

    def test_generic_backend_cannot_be_mislabeled(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "server.py").write_text("def app(): return 'ok'\n", encoding="utf-8")
            (root / "check_backend.py").write_text("from server import app\nassert app() == 'ok'\n", encoding="utf-8")
            with self.assertRaisesRegex(MODULE.ReceiptError, "entrypoint not found"):
                MODULE.derive(
                    root, "backend.architecture", ["server.py"],
                    "check_backend.py", ["server.py"],
                )

    def test_failing_backend_check_cannot_claim_working(self):
        temporary, root = self.fixture("web-primary")
        with temporary:
            receipt = self.web_receipt(root)
            (root / "check_backend.py").write_text("raise SystemExit(1)\n", encoding="utf-8")
            self.assertIn("current backend check failed", MODULE.validate(receipt, root))

    def test_required_capability_failure_allows_a_bounded_challenge(self):
        temporary, root = self.fixture("backend-challenge")
        with temporary:
            receipt = self.web_receipt(root, required=True)
            self.assertEqual(receipt["observed_value"], "python:wsgi")
            self.assertEqual(receipt["current_check"]["status"], "passed")
            self.assertEqual(receipt["required_check"]["status"], "failed")
            self.assertEqual(receipt["derived_decision"], "challenge")
            self.assertEqual(MODULE.validate(receipt, root), [])

    def test_unsupported_schema_scope_and_permission_fail_closed(self):
        temporary, root = self.fixture("design-primary")
        with temporary:
            receipt = self.design_receipt(root)
            for field, value, expected in (
                ("schema_version", 2, "schema_version must be 1"),
                ("scope", "architecture.universal", "receipt scope is unsupported"),
                ("permission_delta", ["publish"], "permission_delta must remain empty"),
            ):
                altered = copy.deepcopy(receipt)
                altered[field] = value
                self.assertIn(expected, MODULE.validate(altered, root))

    def test_identity_hashes_only_the_declared_read_set(self):
        temporary, root = self.fixture("web-primary")
        with temporary:
            receipt = self.web_receipt(root)
            self.assertEqual(receipt["read_set"], ["check_backend.py", "server.py"])
            before = receipt["identity"]
            (root / "frontend.html").write_text("<main>changed</main>\n", encoding="utf-8")
            self.assertEqual(MODULE.validate(receipt, root), [])
            self.assertEqual(receipt["identity"], before)


if __name__ == "__main__":
    unittest.main()
