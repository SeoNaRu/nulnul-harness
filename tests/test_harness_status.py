import importlib.util
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/nulnul-harness"
sys.path.insert(0, str(PLUGIN / "skills/nulnul-harness/scripts"))
import harness_status
from test_foundation import FoundationCase, runtime


def script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class HarnessStatusTests(unittest.TestCase):
    def test_cold_read_is_unknown_and_installation_is_not_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(harness_status, "shipped_identity", side_effect=AssertionError("unexpected tree scan")):
                result = harness_status.snapshot(root)
            self.assertEqual(result["binding"], "unknown")
            self.assertEqual(result["receipt"], "unknown")
            self.assertFalse((root / "docs").exists())
            copy = root / "installed"
            for name in harness_status.COMPONENTS:
                target = copy / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(PLUGIN / name, target)
            result = harness_status.snapshot(root, installed_plugin=copy)
            self.assertEqual(result["installation_comparison"], "same_components")
            self.assertEqual(result["installation_status"], "stale")
            self.assertEqual(result["binding"], "unknown")
            (copy / "skills/nulnul-harness/SKILL.md").write_text("changed")
            self.assertEqual(harness_status.snapshot(root, installed_plugin=copy)["installation_comparison"], "different_components")

    def test_full_copy_comparison_catches_reference_drift_and_ignores_generated_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            copy = root / "installed"
            shutil.copytree(PLUGIN, copy, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            generated = copy / "skills/nulnul-harness/scripts/__pycache__"
            generated.mkdir()
            (generated / "extra.pyc").write_bytes(b"generated")
            (copy / "extra.pyc").write_bytes(b"generated")
            report = harness_status.snapshot(root, installed_plugin=copy)
            self.assertEqual(report["installation_status"], "same")
            self.assertEqual(report["source"]["shipped_digest"], report["installed_copy"]["shipped_digest"])
            self.assertEqual(report["installation_next_action"], "verify_fresh_session")
            unusual_directory = copy / "assets.pyc"
            unusual_directory.mkdir()
            (unusual_directory / "shipped.txt").write_text("included by the packer")
            self.assertEqual(harness_status.snapshot(root, installed_plugin=copy)["installation_status"], "stale")
            shutil.rmtree(unusual_directory)
            reference = copy / "skills/nulnul-harness/references/runtime-visibility.md"
            reference.write_text(reference.read_text() + "\nChanged reference.\n")
            report = harness_status.snapshot(root, installed_plugin=copy)
            self.assertEqual(report["installation_comparison"], "same_components")
            self.assertEqual(report["installation_status"], "stale")
            self.assertEqual(report["installation_next_action"], "refresh_registered_copy")
            for lang, message in (("en", "stale relative to source"), ("ko", "소스와 불일치")):
                text = harness_status.render(report, lang)
                self.assertIn(message, text)
                self.assertIn("codex plugin list --marketplace nulnul-harness --json", text)
                self.assertIn("codex plugin add nulnul-harness@nulnul-harness --json", text)
            self.assertFalse((root / "docs").exists())
            report = harness_status.snapshot(root, installed_plugin=PLUGIN)
            self.assertEqual(report["installation_status"], "unknown")
            self.assertEqual(report["installation_comparison"], "same_path_not_install_proof")

    def test_unsafe_and_oversized_installed_evidence_never_matches(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            copy = root / "installed"
            shutil.copytree(PLUGIN, copy, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            extra = copy / "unsafe"
            for kind in ("symlink", "outside_symlink", "directory_symlink", "fifo", "oversized"):
                with self.subTest(kind=kind):
                    if kind == "symlink":
                        extra.symlink_to(copy / "skills/nulnul-harness/SKILL.md")
                    elif kind == "outside_symlink":
                        extra.symlink_to(PLUGIN / "skills/nulnul-harness/SKILL.md")
                    elif kind == "directory_symlink":
                        extra.symlink_to(copy / "skills", target_is_directory=True)
                    elif kind == "fifo":
                        os.mkfifo(extra)
                    else:
                        extra.write_bytes(b"x" * (1024 * 1024 + 1))
                    report = harness_status.snapshot(root, installed_plugin=copy)
                    self.assertEqual(report["installation_comparison"], "same_components")
                    self.assertEqual(report["installation_status"], "unknown")
                    self.assertIsNone(report["installed_copy"]["shipped_digest"])
                    self.assertEqual(report["installation_next_action"], "check_copy_evidence")
                    for lang, message in (("en", "unknown (full comparison"), ("ko", "미확인(전체 비교")):
                        self.assertIn(message, harness_status.render(report, lang))
                    extra.unlink()
            component = copy / harness_status.COMPONENTS[1]
            component.unlink()
            os.mkfifo(component)
            report = harness_status.snapshot(root, installed_plugin=copy)
            self.assertIsNone(report["installed_copy"]["component_digest"])
            self.assertEqual(report["installation_status"], "unknown")
            alias = root / "alias"
            alias.symlink_to(copy, target_is_directory=True)
            self.assertEqual(harness_status.snapshot(root, installed_plugin=alias)["installation_status"], "unknown")
            alias.unlink()
            alias.symlink_to(alias)
            self.assertEqual(harness_status.snapshot(root, installed_plugin=alias)["installation_status"], "unknown")

    def test_full_copy_count_and_total_byte_limits_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("a", "b", "c"):
                (root / name).write_bytes(b"12")
            with patch.object(harness_status, "MAX_PLUGIN_ENTRIES", 3), patch.object(harness_status, "MAX_PLUGIN_BYTES", 6):
                self.assertEqual(harness_status.shipped_identity(root)["shipped_file_count"], 3)
                with patch.object(harness_status, "MAX_PLUGIN_ENTRIES", 2):
                    with self.assertRaises(ValueError):
                        harness_status.shipped_identity(root)
                with patch.object(harness_status, "MAX_PLUGIN_BYTES", 5):
                    with self.assertRaises(ValueError):
                        harness_status.shipped_identity(root)

    def test_host_binding_and_recorded_check_are_not_a_verified_receipt(self):
        fixture = FoundationCase()
        fixture.setUp()
        try:
            with patch.dict(os.environ, {"NULNUL_TRACE_SESSION": "host-status-test"}):
                session, task = fixture.begin()
            runtime.record_event(fixture.root, "CHECK_COMPLETED", task["task_id"], {"exit_code": 0, "result": "pass"})
            report = harness_status.snapshot(fixture.root, host_session_key="host-status-test")
            self.assertEqual(report["binding"], "host_bound")
            self.assertEqual(report["recorded_check"], "pass")
            self.assertEqual(report["receipt"], "unknown")
            self.assertEqual(report["selection"], "unknown")
            self.assertEqual(harness_status.snapshot(fixture.root, host_session_key="wrong")["binding"], "unknown")
            self.assertEqual(harness_status.snapshot(fixture.root)["binding"], "unknown")
            self.assertEqual(harness_status.snapshot(fixture.root, session_id="../escape")["binding"], "unknown")
        finally:
            fixture.tearDown()

    def test_canonical_receipt_and_conflicting_events_fail_closed(self):
        fixture = FoundationCase()
        fixture.setUp()
        try:
            with patch.dict(os.environ, {"NULNUL_TRACE_SESSION": "host-receipt-test"}):
                session, task = fixture.begin()
            outcome = fixture.valid_capability_outcome()
            runtime.finish_task(fixture.root, task["task_id"], outcome)
            report = harness_status.snapshot(fixture.root, host_session_key="host-receipt-test")
            self.assertEqual(report["receipt"], "historical_pass")
            self.assertTrue(report["body_loaded"])
            path = fixture.root / "docs/nulnul/.runtime/pack-checks" / (outcome["check_id"] + ".json")
            receipt = json.loads(path.read_text())
            receipt["exit_code"] = 7
            path.write_text(json.dumps(receipt))
            self.assertEqual(harness_status.snapshot(fixture.root, host_session_key="host-receipt-test")["receipt"], "invalid")
            events = fixture.root / "docs/nulnul/.runtime/events" / (session["session_id"] + ".jsonl")
            with events.open("a") as target:
                target.write(events.read_text().splitlines()[0] + "\n")
            report = harness_status.snapshot(fixture.root, host_session_key="host-receipt-test")
            self.assertEqual(report["receipt"], "unknown")
            self.assertEqual(report["recorded_check"], "unknown")
        finally:
            fixture.tearDown()

    def test_malformed_session_tasks_return_unknown_without_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "docs/nulnul/.runtime/active-session.json"
            path.parent.mkdir(parents=True)
            for tasks in (["bad task"], {"task_id": "bad"}, None):
                with self.subTest(tasks=tasks):
                    path.write_text(json.dumps({"session_id": "ses-status-test",
                        "trace_host_session_key": "host-test", "tasks": tasks}))
                    before = path.read_bytes()
                    report = harness_status.snapshot(root, host_session_key="host-test")
                    self.assertEqual(report["recorded_check"], "unknown")
                    self.assertIn("missing_invalid_or_oversized_evidence", report["warnings"])
                    self.assertEqual(path.read_bytes(), before)

    def test_loaded_body_requires_matching_identities_and_order(self):
        fixture = FoundationCase()
        fixture.setUp()
        try:
            session, task = fixture.begin()
            fixture.valid_capability_outcome()
            path = fixture.root / "docs/nulnul/.runtime/events" / (session["session_id"] + ".jsonl")
            original = path.read_text()
            self.assertTrue(harness_status.snapshot(fixture.root, session_id=session["session_id"])["body_loaded"])
            for mutation in ("identity", "before_creation", "duplicate"):
                with self.subTest(mutation=mutation):
                    events = [json.loads(line) for line in original.splitlines()]
                    body = next(e for e in events if e["kind"] == "CAPABILITY_BODY_INCLUDED")
                    if mutation == "identity":
                        body["details"]["capability_ids"] = ["different-capability"]
                    elif mutation == "before_creation":
                        created = next(e for e in events if e["kind"] == "CAPABILITY_PACK_CREATED")
                        body["event_id"], created["event_id"] = created["event_id"], body["event_id"]
                        events.sort(key=lambda e: e["event_id"])
                    else:
                        events.append({**body, "event_id": events[-1]["event_id"] + 1})
                    path.write_text("\n".join(json.dumps(e) for e in events) + "\n")
                    report = harness_status.snapshot(fixture.root, session_id=session["session_id"])
                    self.assertFalse(report["body_loaded"])
                    self.assertIn("invalid_body_evidence", report["warnings"])
        finally:
            fixture.tearDown()

    def test_pack_boundary_preserves_outside_research_but_rejects_leaks(self):
        packer = script("pack_plugin")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plugin = root / "plugins/nulnul-harness"
            plugin.mkdir(parents=True)
            (plugin / "SKILL.md").write_text("product")
            research = root / "docs/research"
            research.mkdir(parents=True)
            (research / "private.md").write_text("keep this outside the product")
            archive = root / "product.zip"
            self.assertEqual(packer.pack(plugin, archive), 1)
            first = archive.read_bytes()
            packer.pack(plugin, archive)
            self.assertEqual(first, archive.read_bytes())
            leaked = plugin / "docs/research"
            leaked.mkdir(parents=True)
            with self.assertRaises(ValueError):
                packer.pack(plugin, archive)
            leaked.rmdir()
            (plugin / "outside.md").symlink_to(research / "private.md")
            with self.assertRaises(ValueError):
                packer.pack(plugin, archive)
            self.assertTrue((research / "private.md").exists())

    def test_public_gate_requires_exact_true_not_local_success(self):
        gate = script("public_release_gate")
        self.assertEqual(gate.publication_exit_code({"release_ready": True}), 0)
        for report in ({"release_ready": False}, {"release_ready": "true"}, {"score": 100}, None):
            self.assertEqual(gate.publication_exit_code(report), 1)


if __name__ == "__main__":
    unittest.main()
