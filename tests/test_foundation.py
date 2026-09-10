import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins/nulnul-harness/skills/nulnul-harness"
SCRIPTS = SKILL / "scripts"
sys.path.insert(0, str(SCRIPTS))

import activation_boundary
import capability_contract
import capability_pack
import foundation_runtime as runtime
import setup_transaction
import sync_host_entry
import validate_checkpoint
import validate_project_setup


CAPABILITIES = [
    {
        "capability_id": "project-api-validation",
        "job": "Preserve the project API contract",
        "activation_trigger": "API behavior or error catalog changes",
        "project_check_identity": "api-contract",
        "status": "accepted/current",
        "version_or_digest": "v1",
        "logical_load_target": "capabilities/project-api-validation/SKILL.md",
    },
    {
        "capability_id": "project-release-docs",
        "job": "Preserve release documentation",
        "activation_trigger": "release documentation changes",
        "project_check_identity": "release-docs",
        "status": "accepted/current",
        "version_or_digest": "v2",
        "logical_load_target": "capabilities/project-release-docs/SKILL.md",
    },
]
SETUP_CAPABILITIES = [
    {
        key: row[key]
        for key in (
            "capability_id", "job", "activation_trigger", "project_check_identity",
            "version_or_digest",
        )
    }
    for row in CAPABILITIES
]


def project_text(rows=CAPABILITIES, completion_check="true"):
    base = f"""# nulnul project setup

## Goal
Ship a verified local product.

## Current milestone
The requested behavior and checks pass.
Observable completion check: `{completion_check}`

## Constraints and permissions
No external writes.

## Inspected roster
- Host surface: Codex
- Skills: nulnul-harness and accepted project skills
- Plugins: nulnul-harness
- Agents: direct owner

## Capability requirements
The API contract and release documentation are recurring project jobs.

## Candidate evidence
Project-local capabilities were inspected and verified for their named jobs.

## Capability routing
The canonical Accepted capabilities table is the only activation source.

## Setup decisions
- Reuse now: accepted project capabilities only when materially relevant
- Add now: none
- Needs approval: none
- Skip: unrelated capabilities and external services

## Agent topology
Direct execution with deterministic verification.

## Evolution baseline
Current tests pass.

## Continuity
- Active checkpoint: `docs/nulnul/checkpoint.json`
"""
    marker = "## Capability routing"
    insertion = capability_contract.render(rows) + "\n"
    return base.replace(marker, insertion + marker)


class FoundationCase(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="nulnul-foundation-test.")
        self.root = Path(self.temporary.name)
        (self.root / "docs/nulnul").mkdir(parents=True)
        (self.root / "docs/nulnul/project.md").write_text(project_text(), encoding="utf-8")
        (self.root / "docs/nulnul/checkpoint.json").write_text("{}\n", encoding="utf-8")
        for row in CAPABILITIES:
            body = self.root / ".agents/skills" / row["capability_id"] / "SKILL.md"
            body.parent.mkdir(parents=True, exist_ok=True)
            body.write_text(f"# {row['capability_id']}\n\n{row['job']}\n", encoding="utf-8")
        self.fingerprint = runtime.host_fingerprint(
            "codex", "1.2.3", "gpt-test", {"profile": "test"}, "nulnul-rev", "project-rev",
            "host-owned", "PRE_SESSION_CAPABILITY_PACK", [], "test-platform",
        )

    def tearDown(self):
        self.temporary.cleanup()

    def begin(self, goal="Implement API behavior", job="API validation", **kwargs):
        session = runtime.start_session(self.root, goal, self.fingerprint)
        task = runtime.start_task(self.root, goal, job, **kwargs)
        return session, task

    def valid_capability_outcome(self, include_check=True, check_pass=True, **updates):
        active = runtime.read_json(runtime.Store(self.root).active)
        task = next(row for row in active["tasks"] if row["status"] == "ACTIVE")
        if not check_pass:
            (self.root / "docs/nulnul/project.md").write_text(
                project_text(completion_check="false"), encoding="utf-8"
            )
        pack = capability_pack.prepare(
            self.root, self.root / "docs/nulnul/project.md", task["task_id"], "codex",
            selected=["project-api-validation"],
            evidence="API behavior is governed by the accepted API contract.",
        )
        capability_pack.work_start(self.root, pack["pack_id"])
        check = capability_pack.run_check(self.root, pack["pack_id"]) if include_check else None
        payload = {
            "quality": "VERIFIED",
            "observability_completeness": "COMPLETE",
            "result": "SUCCESS" if check_pass else "FAILURE",
            "product_outcome": "API behavior implemented",
            "changes": ["api.py"],
            "checks": [{"id": "api-contract", "result": "pass" if check_pass else "fail"}],
            "pack_id": pack["pack_id"],
            "check_id": check["check_id"] if check else None,
        }
        if not check_pass:
            payload["verified_failure_reason"] = "the configured API check failed"
        payload.update(updates)
        return payload

    def promoted(self, quality="VERIFIED", suffix=""):
        _, task = self.begin(f"Task {suffix}")
        experience = runtime.finish_task(
            self.root,
            task["task_id"],
            {"quality": quality, "result": "SUCCESS", "product_outcome": "done", "checks": [{"result": "pass"}]},
            {
                "decisions": [{"decision": f"Use API catalog {suffix}", "why": "verified invariant"}],
                "lessons": [{"lesson": f"Run API catalog check {suffix}".strip(), "scope": "api"}],
                "open_threads": [{"thread": f"Follow API migration {suffix}".strip(), "tags": ["api"]}],
            },
        )
        runtime.finalize_session(self.root)
        return experience


class CapabilityContractTests(FoundationCase):
    def test_current_capability_passes_bounded_view(self):
        rows = capability_contract.bounded_view(self.root / "docs/nulnul/project.md")
        self.assertEqual([row["capability_id"] for row in rows], ["project-api-validation", "project-release-docs"])

    def test_noncurrent_capability_is_not_admitted(self):
        rows = [dict(CAPABILITIES[0], status="retired")]
        path = self.root / "docs/nulnul/project.md"
        path.write_text(project_text(rows), encoding="utf-8")
        self.assertEqual(capability_contract.bounded_view(path), [])

    def test_unknown_capability_fails_selection(self):
        with self.assertRaisesRegex(ValueError, "accepted/current"):
            capability_contract.selected(self.root / "docs/nulnul/project.md", "unknown")

    def test_missing_canonical_table_with_legacy_routes_fails(self):
        text = project_text().replace(capability_contract.render(CAPABILITIES) + "\n", "")
        text = text.replace(
            "The canonical Accepted capabilities table is the only activation source.",
            "| Capability | Source | Job | Activate when | Check | Permission boundary | Remove or replace when |\n"
            "| --- | --- | --- | --- | --- | --- | --- |\n"
            "| project-api-validation | local | API | API changes | api-contract | local | loses |",
        )
        with self.assertRaisesRegex(ValueError, "missing canonical"):
            capability_contract.parse(text)

    def test_invalid_status_field_fails_setup(self):
        text = project_text([CAPABILITIES[0]]).replace("| accepted/current |", "|  |", 1)
        self.assertTrue(any("missing status" in error for error in validate_project_setup.validate(text)))

    def test_new_setup_writer_and_runtime_share_parser(self):
        path = self.root / "docs/nulnul/project.md"
        path.write_text(project_text([]), encoding="utf-8")
        written = capability_contract.write_rows(path, [CAPABILITIES[0]])
        self.assertEqual(written[0], capability_contract.bounded_view(path)[0])
        self.assertEqual(validate_project_setup.validate(path.read_text(encoding="utf-8")), [])

    def test_adopt_writer_replaces_rows_atomically(self):
        path = self.root / "docs/nulnul/project.md"
        capability_contract.write_rows(path, [CAPABILITIES[1]])
        self.assertEqual(capability_contract.selected(path, "project-release-docs")["version_or_digest"], "v2")
        with self.assertRaises(ValueError):
            capability_contract.selected(path, "project-api-validation")

    def test_duplicate_and_escaping_rows_fail(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            capability_contract.render([CAPABILITIES[0], CAPABILITIES[0]])
        with self.assertRaisesRegex(ValueError, "CAPABILITY_TARGET_MISMATCH"):
            capability_contract.render([dict(CAPABILITIES[0], logical_load_target="../SKILL.md")])

    def test_capability_identity_owns_one_canonical_target(self):
        self.assertEqual(
            capability_contract.canonical_logical_target("project-api-validation"),
            "capabilities/project-api-validation/SKILL.md",
        )
        accepted = capability_contract.accepted_record(SETUP_CAPABILITIES[0])
        self.assertEqual(accepted, dict(CAPABILITIES[0], accepted_current=True))

    def test_wrong_legacy_absolute_and_other_identity_targets_fail(self):
        bad_targets = (
            ".agents/skills/project-api-validation/SKILL.md",
            "/capabilities/project-api-validation/SKILL.md",
            "capabilities/../project-api-validation/SKILL.md",
            "capabilities/project-release-docs/SKILL.md",
        )
        for target in bad_targets:
            with self.subTest(target=target), self.assertRaisesRegex(
                ValueError, "CAPABILITY_TARGET_MISMATCH"
            ):
                capability_contract.render([
                    dict(CAPABILITIES[0], logical_load_target=target)
                ])

    def test_wrong_id_with_valid_looking_target_fails(self):
        with self.assertRaisesRegex(ValueError, "CAPABILITY_TARGET_MISMATCH"):
            capability_contract.render([
                dict(
                    CAPABILITIES[0],
                    capability_id="project-api-renamed",
                    logical_load_target="capabilities/project-api-validation/SKILL.md",
                )
            ])


class DirectSurfaceTests(FoundationCase):
    def test_direct_entry_is_bounded_and_defers_heavy_context(self):
        block = sync_host_entry.managed_block("codex", Path("docs/nulnul/checkpoint.json"))
        # Installed paths vary by machine; bound guidance independently of those paths.
        guidance = block.replace(str(sync_host_entry.Path(sync_host_entry.__file__).resolve().parent), "")
        self.assertLessEqual(len(guidance.encode()), 800)
        for forbidden in (
            "trust_level", "CODEX_RESTART_REQUIRED", "new-setup", "adopt-upgrade",
            "evolution history", "rule installation", "SETUP_TRANSACTION", "Experience schema",
        ):
            self.assertNotIn(forbidden, block)
        self.assertIn("No selected body is Direct", block)
        self.assertNotIn("capability_pack.py", block)
        self.assertNotIn("capability_pack.py prepare", block)
        self.assertNotIn("work-start", block)
        self.assertNotIn("activation_boundary.py", block)

    def test_bounded_view_has_metadata_but_no_body(self):
        payload = capability_contract.bounded_view(self.root / "docs/nulnul/project.md")
        text = json.dumps(payload)
        self.assertLess(len(text.encode()), 2048)
        self.assertNotIn("Skill instructions", text)
        self.assertNotIn("body", text.lower())

    def test_direct_model_context_does_not_repeat_the_task_or_empty_pack_schema(self):
        goal = "Rename one local value without loading historical setup state."
        runtime.start_session(self.root, goal, self.fingerprint)
        task = runtime.start_task(self.root, goal)
        envelope = task["model_context"]
        serialized = json.dumps(envelope, separators=(",", ":"))
        self.assertNotIn(goal, serialized)
        self.assertEqual(envelope["items"], [])
        self.assertLess(len(serialized.encode()), 180)

    def test_negated_glob_is_not_a_state_read(self):
        reads = runtime.structured_file_reads(["rg", "-n", "term", "-g", "!docs/nulnul/checkpoint.json", "."])
        self.assertNotIn("docs/nulnul/checkpoint.json", reads)

    def test_product_contract_failure_is_not_infrastructure(self):
        self.assertEqual(runtime.classify_failure(True, "product-prerequisite"), "PRODUCT_CONTRACT_FAILURE")
        self.assertEqual(runtime.classify_failure(False, "product-prerequisite"), "INFRASTRUCTURE_FAILURE")


class SessionLifecycleTests(FoundationCase):
    def test_automatic_start_creates_internal_ids(self):
        session, task = self.begin()
        self.assertTrue(session["session_id"].startswith("ses-"))
        self.assertTrue(task["task_id"].startswith("tsk-"))
        self.assertEqual(session["current_checkpoint"], "docs/nulnul/checkpoint.json")
        self.assertRegex(session["host_fingerprint"]["project_root_identity"], r"^[a-f0-9]{64}$")
        self.assertNotIn(str(self.root), json.dumps(session))
        self.assertEqual(runtime.Store(self.root).active.read_text(encoding="utf-8").count("session_id"), 1)

    def test_normal_completion_creates_bounded_session_and_handoff(self):
        session, task = self.begin()
        runtime.finish_task(self.root, task["task_id"], {"quality": "VERIFIED", "result": "SUCCESS", "product_outcome": "done", "checks": [{"result": "pass"}]})
        record = runtime.finalize_session(self.root, "COMPLETED", "Continue next milestone", "COMPLETE")
        self.assertEqual(record["status"], "COMPLETED")
        self.assertFalse(runtime.Store(self.root).active.exists())
        self.assertEqual(json.loads(runtime.Store(self.root).handoff.read_text())["next"], "Continue next milestone")

    def test_failure_and_blocked_states_are_preserved(self):
        _, task = self.begin()
        runtime.finish_task(self.root, task["task_id"], {"quality": "PARTIAL", "result": "FAILURE", "product_outcome": "failed", "verified_failure_reason": "check failed"})
        record = runtime.finalize_session(self.root, "BLOCKED", "Fix check")
        self.assertEqual(record["status"], "BLOCKED")
        self.assertIn("check failed", record["failures"])

    def test_abrupt_session_is_recovered_without_fabrication(self):
        first, _ = self.begin()
        second = runtime.start_session(self.root, "Resume work", self.fingerprint)
        prior = json.loads((runtime.Store(self.root).sessions / f"{first['session_id']}.json").read_text())
        self.assertEqual(prior["status"], "PARTIAL")
        self.assertEqual(second["status"], "RECOVERED")
        self.assertEqual(second["recovered_from"], first["session_id"])
        recovery = runtime.read_json(
            runtime.Store(self.root).experiences / f"{prior['experience_ids'][-1]}.json"
        )
        self.assertEqual(recovery["experience_type"], "RECOVERY_EXPERIENCE")
        self.assertFalse(recovery["evolution_eligible"])

    def test_explicit_aborted_finalize(self):
        self.begin()
        self.assertEqual(runtime.finalize_session(self.root, "ABORTED")["status"], "ABORTED")

    def test_unfinished_task_cannot_be_finalized_as_complete(self):
        self.begin()
        with self.assertRaisesRegex(ValueError, "unfinished"):
            runtime.finalize_session(self.root, "COMPLETED")

    def test_live_writer_conflict_fails_safely(self):
        store = runtime.Store(self.root)
        store.initialize()
        runtime.write_json(store.lock, {"pid": os.getpid(), "token": "other"})
        with self.assertRaisesRegex(RuntimeError, "another NULNUL session writer"):
            with runtime.writer(store):
                pass

    def test_stale_writer_lock_is_recovered(self):
        store = runtime.Store(self.root)
        store.initialize()
        runtime.write_json(store.lock, {"pid": 999999999, "token": "stale"})
        with runtime.writer(store):
            self.assertTrue(store.lock.exists())
        self.assertFalse(store.lock.exists())

    def test_local_runtime_is_gitignored(self):
        runtime.Store(self.root).initialize()
        self.assertIn(".runtime/", (self.root / "docs/nulnul/.gitignore").read_text())

    def test_read_only_surfaces_do_not_initialize_memory(self):
        memory = self.root / "docs/nulnul/memory"
        self.assertFalse(memory.exists())
        self.assertEqual(runtime.inspect(runtime.Store(self.root), "stats")["sessions"], 0)
        self.assertEqual(runtime.context_pack(self.root, "ordinary task")["items"], [])
        self.assertEqual(runtime.evolution_query(self.root)["count"], 0)
        self.assertEqual(runtime.validate_lineage(self.root), [])
        self.assertFalse(memory.exists())
        self.assertFalse((self.root / "docs/nulnul/.runtime").exists())

    def test_raw_retention_is_local_and_configurable(self):
        policy = runtime.configure_raw_retention(self.root, 30)
        store = runtime.Store(self.root)
        self.assertEqual(policy["raw_evidence"], {"mode": "expire", "days": 30})
        self.assertTrue(store.retention.is_relative_to(store.local))
        self.assertEqual(runtime.inspect(store, "stats")["raw_evidence_retention"]["days"], 30)
        self.assertEqual(runtime.configure_raw_retention(self.root)["raw_evidence"]["mode"], "keep")


class ExperienceTests(FoundationCase):
    def test_generic_success_experience(self):
        _, task = self.begin()
        record = runtime.finish_task(self.root, task["task_id"], {"quality": "VERIFIED", "result": "SUCCESS", "product_outcome": "done"})
        self.assertEqual(record["experience_type"], "TASK_EXPERIENCE")
        self.assertFalse(record["evolution_eligible"])

    def test_generic_failure_and_blocked_experience(self):
        _, task = self.begin()
        record = runtime.finish_task(self.root, task["task_id"], {"quality": "PARTIAL", "result": "BLOCKED", "product_outcome": "blocked"})
        self.assertEqual(record["result"], "BLOCKED")

    def test_valid_capability_experience_is_evolution_eligible(self):
        _, task = self.begin()
        record = runtime.finish_task(self.root, task["task_id"], self.valid_capability_outcome())
        self.assertTrue(record["evolution_eligible"])
        self.assertEqual(record["eligibility_reasons"], [])
        self.assertEqual(
            record["logical_load_target"],
            "capabilities/project-api-validation/SKILL.md",
        )

    def test_pack_target_must_match_the_canonical_target(self):
        _, task = self.begin()
        record = runtime.finish_task(self.root, task["task_id"], self.valid_capability_outcome())
        altered = json.loads(json.dumps(record))
        altered["pack_receipt"]["capability_refs"][0]["logical_load_target"] = ".agents/skills/project-api-validation/SKILL.md"
        eligible, reasons = runtime.experience_eligibility(altered, self.root / "docs/nulnul/project.md")
        self.assertFalse(eligible)
        self.assertIn("pack capability target does not match canonical target", reasons)

    def test_attributed_verified_failure_is_evolution_eligible(self):
        _, task = self.begin()
        outcome = self.valid_capability_outcome(check_pass=False)
        outcome["control_candidate"] = {
            "suggestion": "Add a deterministic API regression guard",
            "evidence_refs": [f"check:{outcome['check_id']}"],
        }
        record = runtime.finish_task(self.root, task["task_id"], outcome)
        self.assertEqual(record["quality"], "VERIFIED")
        self.assertTrue(record["evolution_eligible"])
        self.assertEqual(record["control_candidate"]["class"], "CONTROL_CANDIDATE")

    def test_missing_pack_id_stores_but_is_ineligible(self):
        _, task = self.begin()
        record = runtime.finish_task(self.root, task["task_id"], {
            "experience_type": "CAPABILITY_EXPERIENCE", "capability_id": "project-api-validation",
            "quality": "VERIFIED", "result": "SUCCESS", "product_outcome": "done",
            "checks": [{"result": "pass"}],
        })
        self.assertFalse(record["evolution_eligible"])

    def test_missing_check_id_stores_but_is_ineligible(self):
        _, task = self.begin()
        record = runtime.finish_task(self.root, task["task_id"], self.valid_capability_outcome(include_check=False))
        self.assertFalse(record["evolution_eligible"])

    def test_partial_causal_observability_is_ineligible(self):
        _, task = self.begin()
        record = runtime.finish_task(
            self.root,
            task["task_id"],
            self.valid_capability_outcome(observability_completeness="PARTIAL"),
        )
        self.assertFalse(record["evolution_eligible"])

    def test_receipts_need_external_source_references(self):
        _, task = self.begin()
        record = runtime.finish_task(self.root, task["task_id"], self.valid_capability_outcome())
        altered = json.loads(json.dumps(record))
        altered["source_refs"] = [reference for reference in altered["source_refs"] if not reference.startswith("pack:")]
        self.assertFalse(runtime.experience_eligibility(altered, self.root / "docs/nulnul/project.md")[0])

    def test_wrong_ordering_is_ineligible(self):
        _, task = self.begin()
        record = runtime.finish_task(self.root, task["task_id"], self.valid_capability_outcome())
        altered = json.loads(json.dumps(record))
        altered["ordering"]["selection"], altered["ordering"]["pack_created"] = altered["ordering"]["pack_created"], altered["ordering"]["selection"]
        self.assertFalse(runtime.experience_eligibility(altered, self.root / "docs/nulnul/project.md")[0])

    def test_success_claim_must_match_check_receipt(self):
        _, task = self.begin()
        record = runtime.finish_task(self.root, task["task_id"], self.valid_capability_outcome())
        altered = json.loads(json.dumps(record))
        altered["success"] = False
        self.assertFalse(runtime.experience_eligibility(altered, self.root / "docs/nulnul/project.md")[0])

    def test_unknown_capability_is_rejected_before_pack_creation(self):
        _, task = self.begin()
        with self.assertRaisesRegex(ValueError, "bounded accepted/current"):
            capability_pack.prepare(
                self.root, self.root / "docs/nulnul/project.md", task["task_id"], "codex",
                selected=["unknown"], evidence="unknown",
            )

    def test_wrong_pack_digest_is_ineligible(self):
        _, task = self.begin()
        record = runtime.finish_task(self.root, task["task_id"], self.valid_capability_outcome())
        altered = json.loads(json.dumps(record))
        altered["pack_receipt"]["capability_refs"][0]["body_digest"] = "0" * 64
        self.assertFalse(runtime.experience_eligibility(altered, self.root / "docs/nulnul/project.md")[0])

    def test_duplicate_experience_id_is_rejected(self):
        _, task = self.begin()
        identity = "exp-fixed"
        runtime.finish_task(self.root, task["task_id"], {"experience_id": identity, "result": "SUCCESS", "product_outcome": "done"})
        runtime.finalize_session(self.root)
        _, other = self.begin("Second")
        with self.assertRaisesRegex(ValueError, "duplicate experience"):
            runtime.finish_task(self.root, other["task_id"], {"experience_id": identity, "result": "SUCCESS", "product_outcome": "done"})


class MemoryTests(FoundationCase):
    def test_verified_experience_promotes_decision_lesson_and_thread(self):
        self.promoted()
        store = runtime.Store(self.root)
        self.assertEqual(len(runtime.read_jsonl(store.decisions)), 1)
        self.assertEqual(len(runtime.read_jsonl(store.lessons)), 1)
        self.assertEqual(len(runtime.read_json(store.open_threads)["threads"]), 1)

    def test_partial_experience_does_not_promote(self):
        self.promoted("PARTIAL")
        self.assertEqual(runtime.read_jsonl(runtime.Store(self.root).decisions), [])

    def test_decision_supersession_preserves_links(self):
        self.promoted(suffix="old")
        self.promoted(suffix="new")
        rows = runtime.read_jsonl(runtime.Store(self.root).decisions)
        runtime.lifecycle_update(self.root, "decision", rows[1]["decision_id"], "ACTIVE", rows[0]["decision_id"])
        updated = runtime.read_jsonl(runtime.Store(self.root).decisions)
        self.assertEqual(updated[0]["status"], "SUPERSEDED")
        self.assertEqual(updated[1]["supersedes"], updated[0]["decision_id"])

    def test_retired_lesson_stops_being_active(self):
        self.promoted()
        lesson = runtime.read_jsonl(runtime.Store(self.root).lessons)[0]
        runtime.lifecycle_update(self.root, "lesson", lesson["lesson_id"], "RETIRED")
        self.assertEqual(runtime.read_jsonl(runtime.Store(self.root).lessons)[0]["status"], "RETIRED")

    def test_resolved_open_thread_stops_entering_context(self):
        self.promoted()
        store = runtime.Store(self.root)
        thread = runtime.read_json(store.open_threads)["threads"][0]
        runtime.lifecycle_update(self.root, "thread", thread["thread_id"], "RETIRED")
        pack = runtime.context_pack(self.root, "Follow API migration")
        self.assertNotIn(thread["thread_id"], {item["item_id"] for item in pack["items"]})

    def test_equivalent_lessons_compact_with_lineage(self):
        self.promoted(suffix="")
        self.promoted(suffix="")
        result = runtime.compact_lessons(self.root)
        rows = runtime.read_jsonl(runtime.Store(self.root).lessons)
        self.assertEqual(result["compacted"], 1)
        self.assertEqual(sum(row["status"] == "ACTIVE" for row in rows), 1)
        self.assertTrue(any(row["status"] == "COMPACTED" for row in rows))

    def test_dangling_lineage_is_rejected(self):
        self.promoted()
        store = runtime.Store(self.root)
        rows = runtime.read_jsonl(store.lessons)
        rows[0]["derived_from"] = ["experience:missing"]
        runtime.write_jsonl(store.lessons, rows)
        self.assertTrue(any("dangling" in error for error in runtime.validate_lineage(self.root)))

    def test_session_noise_is_not_promoted(self):
        _, task = self.begin()
        runtime.record_event(self.root, "TOOL_EXECUTION", task["task_id"], {"temporary_path": "/tmp/noise"})
        runtime.finish_task(self.root, task["task_id"], {"quality": "VERIFIED", "result": "SUCCESS", "product_outcome": "done"})
        runtime.finalize_session(self.root)
        self.assertEqual(runtime.read_jsonl(runtime.Store(self.root).lessons), [])


class ContextAssemblyTests(FoundationCase):
    def test_relevant_decision_and_lesson_are_included(self):
        self.promoted()
        pack = runtime.context_pack(self.root, "change API catalog")
        self.assertIn("decision", {item["type"] for item in pack["items"]})
        self.assertIn("lesson", {item["type"] for item in pack["items"]})

    def test_unrelated_session_and_experience_are_excluded(self):
        self.promoted()
        pack = runtime.context_pack(self.root, "adjust image colors")
        self.assertEqual(pack["items"], [])

    def test_unverified_experience_is_excluded(self):
        _, task = self.begin()
        runtime.finish_task(
            self.root,
            task["task_id"],
            {"quality": "PARTIAL", "result": "FAILURE", "product_outcome": "API attempt failed"},
        )
        runtime.finalize_session(self.root, "PARTIAL")
        self.assertEqual(runtime.context_pack(self.root, "API attempt")["items"], [])

    def test_same_capability_experience_is_preferred(self):
        _, task = self.begin(modules=["api.py"])
        runtime.finish_task(self.root, task["task_id"], self.valid_capability_outcome())
        runtime.finalize_session(self.root)
        pack = runtime.context_pack(self.root, "unrelated wording", "project-api-validation")
        self.assertEqual(pack["items"][0]["why_included"], "same capability")

    def test_open_thread_is_included_when_relevant(self):
        self.promoted()
        pack = runtime.context_pack(self.root, "API migration follow-up")
        self.assertIn("thread", {item["type"] for item in pack["items"]})

    def test_superseded_and_retired_records_are_excluded(self):
        self.promoted(suffix="old")
        self.promoted(suffix="new")
        store = runtime.Store(self.root)
        decisions = runtime.read_jsonl(store.decisions)
        lessons = runtime.read_jsonl(store.lessons)
        runtime.lifecycle_update(self.root, "decision", decisions[1]["decision_id"], "ACTIVE", decisions[0]["decision_id"])
        runtime.lifecycle_update(self.root, "lesson", lessons[0]["lesson_id"], "RETIRED")
        pack = runtime.context_pack(self.root, "API catalog old new")
        ids = {item["item_id"] for item in pack["items"]}
        self.assertNotIn(decisions[0]["decision_id"], ids)
        self.assertNotIn(lessons[0]["lesson_id"], ids)

    def test_budget_and_deduplication_are_enforced(self):
        for number in range(12):
            self.promoted(suffix=str(number))
        pack = runtime.context_pack(self.root, "API", max_items=3, max_bytes=700)
        self.assertLessEqual(pack["item_count"], 3)
        self.assertLessEqual(pack["byte_count"], 700)
        self.assertEqual(len({item["bounded_content"] for item in pack["items"]}), len(pack["items"]))

    def test_provenance_is_retained_and_raw_transcript_excluded(self):
        self.promoted()
        pack = runtime.context_pack(self.root, "API")
        self.assertTrue(all("provenance" in item for item in pack["items"]))
        self.assertFalse(pack["raw_transcripts_included"])
        self.assertTrue(all("transcript" not in item["bounded_content"].lower() for item in pack["items"]))

    def test_invalid_budget_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "budget"):
            runtime.context_pack(self.root, "task", max_items=99)


class ProvenanceTests(FoundationCase):
    def test_valid_finalized_lineage_passes(self):
        self.promoted()
        self.assertEqual(runtime.validate_lineage(self.root), [])

    def test_invalid_source_ref_is_rejected(self):
        self.promoted()
        store = runtime.Store(self.root)
        rows = runtime.read_jsonl(store.decisions)
        rows[0]["source_refs"] = ["file:../../secret"]
        runtime.write_jsonl(store.decisions, rows)
        self.assertTrue(any("invalid source_ref" in error for error in runtime.validate_lineage(self.root)))

    def test_self_supersession_is_rejected(self):
        self.promoted()
        store = runtime.Store(self.root)
        rows = runtime.read_jsonl(store.lessons)
        rows[0]["supersedes"] = rows[0]["lesson_id"]
        runtime.write_jsonl(store.lessons, rows)
        self.assertTrue(any("self-supersession" in error for error in runtime.validate_lineage(self.root)))

    def test_layer_contract_registry_is_complete(self):
        self.assertEqual(runtime.validate_layer_registry(), [])
        payload = json.loads((SKILL / "assets/layer-contracts.json").read_text())
        self.assertEqual(len(payload["layers"]), 12)


class HostFingerprintTests(FoundationCase):
    def test_codex_fingerprint_records_host_state(self):
        self.assertEqual(self.fingerprint["host"], "codex")
        self.assertEqual(self.fingerprint["host_trust"], "host-owned")
        self.assertEqual(self.fingerprint["admission_state"], "PRE_SESSION_CAPABILITY_PACK")

    def test_unknown_host_and_missing_version_are_explicit(self):
        value = runtime.host_fingerprint()
        self.assertEqual(value["host"], "unknown")
        self.assertEqual(value["host_version"], "unknown")

    def test_project_and_nulnul_revision_change_fingerprint(self):
        changed_project = runtime.host_fingerprint(project_revision="other")
        changed_nulnul = runtime.host_fingerprint(nulnul_revision="other")
        self.assertNotEqual(changed_project["fingerprint_id"], changed_nulnul["fingerprint_id"])

    def test_structured_secrets_are_redacted(self):
        value = runtime.host_fingerprint(configuration={"api_key": "secret", "profile": "safe"})
        self.assertEqual(value["configuration"]["api_key"], "[REDACTED]")
        self.assertNotIn("secret", json.dumps(value))


class EvolutionQueryTests(FoundationCase):
    def capability_experience(self, **updates):
        _, task = self.begin(job="API validation")
        record = runtime.finish_task(self.root, task["task_id"], self.valid_capability_outcome(**updates))
        runtime.finalize_session(self.root)
        return record

    def test_query_by_capability_and_job(self):
        self.capability_experience()
        self.assertEqual(runtime.evolution_query(self.root, capability_id="project-api-validation")["count"], 1)
        self.assertEqual(runtime.evolution_query(self.root, job="API")["count"], 1)

    def test_only_verified_attributable_experiences_return(self):
        self.capability_experience(quality="PARTIAL")
        self.assertEqual(runtime.evolution_query(self.root)["count"], 0)

    def test_retired_experience_is_excluded(self):
        record = self.capability_experience()
        runtime.lifecycle_update(self.root, "experience", record["experience_id"], "RETIRED")
        self.assertEqual(runtime.evolution_query(self.root)["count"], 0)

    def test_query_is_bounded(self):
        for number in range(3):
            self.capability_experience(tags=[str(number)])
        self.assertEqual(runtime.evolution_query(self.root, limit=2)["count"], 2)

    def test_since_digest_excludes_boundary_record(self):
        record = self.capability_experience()
        self.assertEqual(runtime.evolution_query(self.root, since=record["body_digest"])["count"], 0)

    def test_unknown_since_boundary_fails_closed(self):
        self.capability_experience()
        self.assertEqual(runtime.evolution_query(self.root, since="missing-version")["count"], 0)


class SetupTransactionTests(FoundationCase):
    def setUp(self):
        super().setUp()
        self.installed = self.root / ".agents/skills/nulnul-harness"
        self.installed.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(SKILL, self.installed)
        self.codex_home = self.root.parent / f"setup-codex-home-{self.root.name}"
        self.codex_home.mkdir()
        value = str(self.root).replace("\\", "\\\\").replace('"', '\\"')
        (self.codex_home / "config.toml").write_text(
            f'[projects."{value}"]\ntrust_level = "trusted"\n', encoding="utf-8"
        )
        (self.root / "product.txt").write_text("ok", encoding="utf-8")

    def plan(self, mode="adopt-upgrade", **updates):
        payload = {
            "schema_version": 2,
            "mode": mode,
            "host": "codex",
            "goal": "Keep the project locally verified.",
            "milestone": "Create one runtime-valid NULNUL setup.",
            "completion_check": (
                "python3 -c \"from pathlib import Path; "
                "assert Path('product.txt').read_text() == 'ok'\""
            ),
            "verification_files": ["product.txt"],
            "constraints": ["Keep every write inside this repository."],
            "roster": {
                "skills": ["nulnul-harness"],
                "plugins": [],
                "agents": ["direct owner: reuse"],
            },
            "agent_topology": "One direct owner with deterministic verification.",
            "accepted_capabilities": [SETUP_CAPABILITIES[0]],
        }
        payload.update(updates)
        return payload

    def prepare(self, mode="adopt-upgrade", *, runtime_state=False):
        if mode == "new-setup":
            for name in ("project.md", "checkpoint.json", "checkpoint.verification.json"):
                (self.root / "docs/nulnul" / name).unlink(missing_ok=True)
        task = None
        if runtime_state:
            runtime.start_session(self.root, "Configure NULNUL", self.fingerprint)
            task = runtime.start_task(self.root, "Configure NULNUL", "Governed setup")
        governed = activation_boundary.governed_stage(
            self.installed / "scripts/activation_boundary.py", self.root, mode, "codex"
        )
        return governed["activation_receipt"], task

    def execute(self, mode="adopt-upgrade", plan=None, receipt=None, *, runtime_state=False):
        if receipt is None:
            receipt, task = self.prepare(mode, runtime_state=runtime_state)
        else:
            task = None
        with mock.patch.dict(os.environ, {"CODEX_HOME": str(self.codex_home)}):
            result = setup_transaction.execute(
                self.root, plan or self.plan(mode), receipt, timeout=30
            )
        return result, task

    def setup_bytes(self):
        paths = (
            "docs/nulnul/project.md", "docs/nulnul/checkpoint.json",
            "docs/nulnul/checkpoint.verification.json", "AGENTS.md",
        )
        return {
            name: (self.root / name).read_bytes() if (self.root / name).is_file() else None
            for name in paths
        }

    def test_valid_new_setup_is_runtime_accepted_without_activation_restart(self):
        trust_before = hashlib.sha256((self.codex_home / "config.toml").read_bytes()).hexdigest()
        result, _ = self.execute("new-setup")
        self.assertEqual(result["status"], "SETUP_TRANSACTION_PASS")
        self.assertEqual(result["validation_result"], "PASS")
        self.assertFalse(result["restart_required"])
        self.assertFalse((self.root / ".codex/rules/nulnul-activation.rules").exists())
        self.assertEqual(
            capability_contract.bounded_view(self.root / "docs/nulnul/project.md"),
            [dict(CAPABILITIES[0], accepted_current=True)],
        )
        self.assertEqual(
            result["canonical_capabilities"],
            [dict(CAPABILITIES[0], accepted_current=True)],
        )
        checkpoint = json.loads((self.root / "docs/nulnul/checkpoint.json").read_text())
        evidence = json.loads((self.root / "docs/nulnul/checkpoint.verification.json").read_text())
        self.assertTrue(runtime.validate_lineage(self.root) == [])
        self.assertTrue(validate_checkpoint.fast_path_ready(checkpoint, self.root, evidence))
        self.assertEqual(
            hashlib.sha256((self.codex_home / "config.toml").read_bytes()).hexdigest(),
            trust_before,
        )

    def test_valid_adopt_uses_the_same_runtime_contract(self):
        result, _ = self.execute()
        self.assertEqual(result["status"], "SETUP_TRANSACTION_PASS")
        self.assertEqual(result["rollback_result"], "NOT_REQUIRED")
        self.assertEqual(
            capability_contract.load(
                self.root / "docs/nulnul/project.md", require_canonical=True, current_only=True
            ),
            capability_contract.bounded_view(self.root / "docs/nulnul/project.md"),
        )

    def test_metadata_only_adopt_reuses_the_executed_check_and_receipt(self):
        inactive = self.root / "CLAUDE.md"
        inactive.write_text("# Keep the other host unchanged\n", encoding="utf-8")
        with mock.patch.object(
            setup_transaction.run_checkpoint_check, "run",
            wraps=setup_transaction.run_checkpoint_check.run,
        ) as runner:
            first, _ = self.execute("new-setup")
            self.assertEqual(first["status"], "SETUP_TRANSACTION_PASS")
            self.assertFalse(first["completion_check"]["reused"])
            self.assertEqual(runner.call_count, 1)
            before = self.setup_bytes()
            result, _ = self.execute(plan=self.plan(goal="A shorter goal.", milestone="Continue."))
        self.assertEqual(result["status"], "SETUP_TRANSACTION_PASS")
        self.assertTrue(result["completion_check"]["reused"])
        self.assertIsNone(result["completion_check"]["exit_code"])
        self.assertEqual(runner.call_count, 1)
        self.assertEqual(
            self.setup_bytes()["docs/nulnul/checkpoint.verification.json"],
            before["docs/nulnul/checkpoint.verification.json"],
        )
        self.assertNotEqual(
            self.setup_bytes()["docs/nulnul/checkpoint.json"], before["docs/nulnul/checkpoint.json"]
        )
        self.assertEqual(inactive.read_text(), "# Keep the other host unchanged\n")

    def test_changed_verified_source_rechecks_and_rolls_back_failure(self):
        first, _ = self.execute()
        self.assertEqual(first["status"], "SETUP_TRANSACTION_PASS")
        before = self.setup_bytes()
        (self.root / "product.txt").write_text("broken", encoding="utf-8")
        with mock.patch.object(
            setup_transaction.run_checkpoint_check, "run",
            wraps=setup_transaction.run_checkpoint_check.run,
        ) as runner:
            result, _ = self.execute()
        self.assertEqual(runner.call_count, 1)
        self.assertFalse(result["completion_check"]["reused"])
        self.assertEqual(result["failed_phase"], "checkpoint-verification")
        self.assertEqual(result["rollback_result"], "PASS")
        self.assertEqual(self.setup_bytes(), before)

    def test_changed_command_or_verification_file_set_requires_execution(self):
        for field in ("completion_check", "verification_files"):
            with self.subTest(field=field):
                first, _ = self.execute()
                self.assertEqual(first["status"], "SETUP_TRANSACTION_PASS")
                plan = self.plan()
                if field == "completion_check":
                    plan[field] += " && true"
                else:
                    (self.root / "extra.txt").write_text("input", encoding="utf-8")
                    plan[field] += ["extra.txt"]
                with mock.patch.object(
                    setup_transaction.run_checkpoint_check, "run",
                    wraps=setup_transaction.run_checkpoint_check.run,
                ) as runner:
                    result, _ = self.execute(plan=plan)
                self.assertEqual(result["status"], "SETUP_TRANSACTION_PASS")
                self.assertFalse(result["completion_check"]["reused"])
                self.assertEqual(runner.call_count, 1)

    def test_untrusted_prior_checkpoint_or_receipt_requires_execution(self):
        first, _ = self.execute()
        self.assertEqual(first["status"], "SETUP_TRANSACTION_PASS")
        checkpoint = self.root / "docs/nulnul/checkpoint.json"
        receipt = checkpoint.with_name("checkpoint.verification.json")
        valid_checkpoint = checkpoint.read_text()
        valid_receipt = receipt.read_text()
        for target, update in (
            (checkpoint, {"verification_status": "unknown"}),
            (checkpoint, {"verification_status": "failed"}),
            (checkpoint, {"schema_version": 2}),
            (checkpoint, "invalid JSON"),
            (receipt, {"verification_status": "unknown"}),
            (receipt, {"verification_status": "failed"}),
            (receipt, {"verification_fingerprint": "invalid"}),
            (receipt, {"completion_check_digest": None}),
            (receipt, "invalid JSON"),
            (receipt, None),
        ):
            with self.subTest(target=target.name, update=update):
                checkpoint.write_text(valid_checkpoint, encoding="utf-8")
                receipt.write_text(valid_receipt, encoding="utf-8")
                if update is None:
                    target.unlink()
                elif isinstance(update, dict):
                    target.write_text(
                        json.dumps({**json.loads(target.read_text()), **update}), encoding="utf-8"
                    )
                else:
                    target.write_text(update, encoding="utf-8")
                with mock.patch.object(
                    setup_transaction.run_checkpoint_check, "run",
                    wraps=setup_transaction.run_checkpoint_check.run,
                ) as runner:
                    result, _ = self.execute()
                self.assertEqual(result["status"], "SETUP_TRANSACTION_PASS")
                self.assertFalse(result["completion_check"]["reused"])
                self.assertEqual(runner.call_count, 1)

    def test_changed_setup_or_host_verification_input_requires_execution(self):
        for name in ("docs/nulnul/project.md", "AGENTS.md"):
            with self.subTest(name=name):
                plan = self.plan(verification_files=["product.txt", name])
                first, _ = self.execute(plan=plan)
                self.assertEqual(first["status"], "SETUP_TRANSACTION_PASS")
                plan["milestone"] = "Shorten setup metadata."
                managed_block = sync_host_entry.managed_block

                def updated_block(host, state):
                    block = managed_block(host, state)
                    return block.replace("Stable setup:", "Shared setup:") if name == "AGENTS.md" else block

                with mock.patch.object(
                    setup_transaction.run_checkpoint_check, "run",
                    wraps=setup_transaction.run_checkpoint_check.run,
                ) as runner, mock.patch.object(sync_host_entry, "managed_block", side_effect=updated_block):
                    result, _ = self.execute(plan=plan)
                self.assertEqual(result["status"], "SETUP_TRANSACTION_PASS")
                self.assertFalse(result["completion_check"]["reused"])
                self.assertEqual(runner.call_count, 1)

    def test_pack_setup_neither_requires_nor_mutates_codex_trust(self):
        config = self.codex_home / "config.toml"
        config.write_text("# host-owned config without project trust\n", encoding="utf-8")
        before = config.read_bytes()
        result, _ = self.execute()
        self.assertEqual(result["status"], "SETUP_TRANSACTION_PASS")
        self.assertEqual(config.read_bytes(), before)
        self.assertFalse(result["restart_required"])

    def test_invalid_capability_fails_before_writes(self):
        receipt, _ = self.prepare()
        before = self.setup_bytes()
        plan = self.plan(accepted_capabilities=[dict(SETUP_CAPABILITIES[0], status="")])
        result, _ = self.execute(plan=plan, receipt=receipt)
        self.assertEqual(result["status"], "SETUP_TRANSACTION_FAIL")
        self.assertEqual(result["failed_phase"], "plan-validation")
        self.assertEqual(result["failure_classification"], "PRODUCT_CONTRACT_FAILURE")
        self.assertEqual(self.setup_bytes(), before)

    def test_plan_without_status_or_target_derives_the_canonical_record(self):
        plan = setup_transaction.validate_plan(self.plan())
        self.assertEqual(
            plan["capabilities"], [dict(CAPABILITIES[0], accepted_current=True)]
        )

    def test_schema_v1_exact_target_remains_assertion_compatible(self):
        legacy = self.plan()
        legacy["schema_version"] = 1
        legacy["capabilities"] = [CAPABILITIES[0]]
        del legacy["accepted_capabilities"]
        result, _ = self.execute(plan=legacy)
        self.assertEqual(result["status"], "SETUP_TRANSACTION_PASS")

    def test_e15_legacy_target_mismatch_fails_before_any_write(self):
        receipt, _ = self.prepare()
        before = self.setup_bytes()
        legacy = self.plan()
        legacy["schema_version"] = 1
        legacy["capabilities"] = [dict(
            CAPABILITIES[0],
            logical_load_target=".agents/skills/project-api-validation/SKILL.md",
        )]
        del legacy["accepted_capabilities"]
        result, _ = self.execute(plan=legacy, receipt=receipt)
        self.assertEqual(result["failed_phase"], "plan-validation")
        self.assertIn("CAPABILITY_TARGET_MISMATCH", result["reason"])
        self.assertEqual(result["files_written"], [])
        self.assertEqual(self.setup_bytes(), before)

    def test_invalid_governed_receipt_has_no_write_authority(self):
        before = self.setup_bytes()
        result, _ = self.execute(plan=self.plan(), receipt="invalid")
        self.assertEqual(result["failed_phase"], "governed-authority")
        self.assertEqual(result["authorized_write_set"], [])
        self.assertEqual(self.setup_bytes(), before)

    def test_host_entry_failure_rolls_back_every_owned_surface(self):
        receipt, _ = self.prepare()
        before = self.setup_bytes()
        original = sync_host_entry.atomic_write

        def fail_entry(path, text):
            if Path(path).name == "AGENTS.md":
                raise OSError("host entry failed")
            return original(path, text)

        with mock.patch.dict(os.environ, {"CODEX_HOME": str(self.codex_home)}), mock.patch.object(
            sync_host_entry, "atomic_write", side_effect=fail_entry
        ):
            result = setup_transaction.execute(self.root, self.plan(), receipt, timeout=30)
        self.assertEqual(result["rollback_result"], "PASS")
        self.assertEqual(self.setup_bytes(), before)

    def test_checkpoint_failure_rolls_back_the_transaction(self):
        receipt, _ = self.prepare()
        before = self.setup_bytes()
        with mock.patch.dict(os.environ, {"CODEX_HOME": str(self.codex_home)}), mock.patch.object(
            setup_transaction.run_checkpoint_check,
            "run",
            return_value={"passed": False, "errors": ["simulated checkpoint failure"]},
        ):
            result = setup_transaction.execute(self.root, self.plan(), receipt, timeout=30)
        self.assertEqual(result["failed_phase"], "checkpoint-verification")
        self.assertEqual(result["rollback_result"], "PASS")
        self.assertEqual(self.setup_bytes(), before)

    def test_setup_result_creates_a_bounded_governed_experience(self):
        result, task = self.execute(runtime_state=True)
        experience = runtime.finish_task(self.root, task["task_id"], result["experience_outcome"])
        self.assertEqual(experience["experience_type"], "GOVERNED_EXPERIENCE")
        self.assertEqual(experience["setup_transaction_id"], result["setup_transaction_id"])
        self.assertEqual(experience["validation_result"], "PASS")
        self.assertFalse(experience["restart_required"])
        self.assertFalse(experience["evolution_eligible"])
        events = runtime.read_jsonl(
            runtime.Store(self.root).local / "events" /
            f"{runtime.read_json(runtime.Store(self.root).active)['session_id']}.jsonl"
        )
        kinds = [event["kind"] for event in events]
        self.assertIn("SETUP_TRANSACTION_STARTED", kinds)
        self.assertIn("SETUP_COMPLETED", kinds)

    def test_failed_transaction_creates_an_exact_failure_experience(self):
        receipt, task = self.prepare(runtime_state=True)
        with mock.patch.dict(os.environ, {"CODEX_HOME": str(self.codex_home)}), mock.patch.object(
            setup_transaction.run_checkpoint_check,
            "run",
            return_value={"passed": False, "errors": ["failed checkpoint"]},
        ):
            result = setup_transaction.execute(self.root, self.plan(), receipt, timeout=30)
        experience = runtime.finish_task(self.root, task["task_id"], result["experience_outcome"])
        self.assertEqual(experience["result"], "FAILURE")
        self.assertEqual(experience["failure_phase"], "checkpoint-verification")
        self.assertEqual(experience["rollback_result"], "PASS")
        self.assertEqual(experience["verified_failure_reason"], result["reason"])

    def test_setup_complexity_is_bounded_and_model_does_not_write_artifacts(self):
        result, _ = self.execute()
        self.assertEqual(len(result["model_semantic_inputs"]), 8)
        self.assertEqual(len(result["phases"]), 5)
        self.assertLessEqual(len(result["files_written"]), 4)
        self.assertGreaterEqual(len(result["validators"]), 8)
        self.assertTrue(all(size > 0 for size in result["generated_bytes"].values()))


class CapabilityPackTests(FoundationCase):
    def prepare(self, goal, job=None, selected=None, evidence=None, no_capability=False):
        _, task = self.begin(goal, job or goal)
        pack = capability_pack.prepare(
            self.root, self.root / "docs/nulnul/project.md", task["task_id"], "codex",
            selected=selected, evidence=evidence, no_capability=no_capability,
        )
        return task, pack

    def test_clear_direct_creates_an_empty_pack_without_body_context(self):
        task, pack = self.prepare("Rename one private local variable", "cosmetic rename")
        self.assertEqual(pack["selection_method"], "deterministic-zero")
        self.assertEqual(pack["capability_refs"], [])
        self.assertIn(pack["pack_id"], runtime.read_json(
            runtime.Store(self.root).active
        )["capability_packs"])
        started = capability_pack.work_start(self.root, pack["pack_id"])
        self.assertEqual(started["model_context"]["capabilities"], [])
        self.assertIsNone(started["body_included_event_id"])
        with self.assertRaisesRegex(ValueError, "already exists"):
            capability_pack.prepare(
                self.root, self.root / "docs/nulnul/project.md", task["task_id"], "codex"
            )

    def test_host_bootstrap_hides_empty_pack_and_binds_single_body(self):
        _, direct = self.begin("Rename one private local variable", "cosmetic rename")
        empty = capability_pack.bootstrap(
            self.root, self.root / "docs/nulnul/project.md", direct["task_id"], "codex"
        )
        self.assertEqual(empty["selection_method"], "deterministic-zero")
        self.assertEqual(empty["model_context"], {})
        runtime.finalize_session(self.root, "PARTIAL")
        _, task = self.begin("Change API behavior and error catalog", "API validation")
        selected = capability_pack.bootstrap(
            self.root, self.root / "docs/nulnul/project.md", task["task_id"], "codex"
        )
        self.assertEqual(selected["selection_method"], "deterministic-single")
        self.assertEqual(
            [row["capability_id"] for row in selected["model_context"]["capabilities"]],
            ["project-api-validation"],
        )
        self.assertNotIn("candidates", selected["model_context"])
        self.assertNotIn("selection_evidence", selected["model_context"])

    def test_authoritative_finalize_owns_check_and_verified_experience(self):
        _, task = self.begin("Change API behavior and error catalog", "API validation")
        boot = capability_pack.bootstrap(
            self.root, self.root / "docs/nulnul/project.md", task["task_id"], "codex"
        )
        (self.root / "api.py").write_text("VALUE = 1\n", encoding="utf-8")
        result = capability_pack.finalize_pack_task(self.root, boot["pack_id"])
        check = result["check"]
        experience = result["experience"]
        self.assertEqual(check["session_id"], experience["session_id"])
        self.assertEqual(check["task_id"], experience["task_id"])
        self.assertEqual(check["capability_digest"], experience["body_digest"])
        self.assertEqual(check["command"], "true")
        self.assertEqual(experience["quality"], "VERIFIED")
        self.assertTrue(experience["evolution_eligible"])

    def test_authoritative_failed_check_is_verified_evolution_input(self):
        (self.root / "docs/nulnul/project.md").write_text(
            project_text(completion_check="false"), encoding="utf-8"
        )
        _, task = self.begin("Change API behavior and error catalog", "API validation")
        boot = capability_pack.bootstrap(
            self.root, self.root / "docs/nulnul/project.md", task["task_id"], "codex"
        )
        (self.root / "api.py").write_text("VALUE = 1\n", encoding="utf-8")
        result = capability_pack.finalize_pack_task(self.root, boot["pack_id"])
        self.assertEqual(result["check"]["result"], "fail")
        self.assertEqual(result["experience"]["result"], "FAILURE")
        self.assertEqual(result["experience"]["quality"], "VERIFIED")
        self.assertTrue(result["experience"]["evolution_eligible"])

    def test_authoritative_finalize_requires_work_and_ignores_prior_raw_check(self):
        _, task = self.begin("Change API behavior and error catalog", "API validation")
        boot = capability_pack.bootstrap(
            self.root, self.root / "docs/nulnul/project.md", task["task_id"], "codex"
        )
        with self.assertRaisesRegex(ValueError, "observable product work"):
            capability_pack.finalize_pack_task(self.root, boot["pack_id"])
        subprocess.run("true", cwd=self.root, shell=True, check=True)
        (self.root / "api.py").write_text("VALUE = 1\n", encoding="utf-8")
        result = capability_pack.finalize_pack_task(self.root, boot["pack_id"])
        self.assertEqual(result["check"]["result"], "pass")
        self.assertTrue(result["experience"]["evolution_eligible"])

    def test_clear_skill_a_and_skill_b_select_one_canonical_body(self):
        cases = (
            ("Change API behavior and error catalog", "API contract", "project-api-validation"),
            ("Update release documentation changes", "release docs", "project-release-docs"),
        )
        for number, (goal, job, expected) in enumerate(cases):
            if number:
                runtime.finalize_session(self.root, "PARTIAL")
            _, pack = self.prepare(goal, job)
            self.assertEqual([row["capability_id"] for row in pack["capability_refs"]], [expected])
            self.assertEqual(pack["selection_method"], "deterministic-single")
            started = capability_pack.work_start(self.root, pack["pack_id"])
            self.assertEqual([row["capability_id"] for row in started["model_context"]["capabilities"]], [expected])

    def test_adjacent_and_ambiguous_tasks_require_bounded_selection_without_bodies(self):
        for number, goal in enumerate((
            "Rename api client variable",
            "Rename release variable",
            "Update API contract and release documentation",
        )):
            if number:
                runtime.finalize_session(self.root, "PARTIAL")
            task, payload = self.prepare(goal, "maintenance")
            self.assertEqual(payload["status"], "SELECTION_REQUIRED")
            self.assertFalse(payload["body_content_included"])
            self.assertLessEqual(len(payload["candidates"]), capability_pack.MAX_CANDIDATES)
            if number == 2:
                pack = capability_pack.prepare(
                    self.root, self.root / "docs/nulnul/project.md", task["task_id"], "codex",
                    evidence="Neither bounded candidate materially governs this maintenance task.",
                    no_capability=True,
                )
                self.assertEqual(pack["selection_method"], "bounded-semantic")
                self.assertEqual(capability_pack.work_start(
                    self.root, pack["pack_id"]
                )["model_context"]["capabilities"], [])

    def test_unknown_and_noncurrent_capabilities_are_rejected(self):
        _, task = self.begin("Change API behavior", "API validation")
        with self.assertRaisesRegex(ValueError, "bounded accepted/current"):
            capability_pack.prepare(
                self.root, self.root / "docs/nulnul/project.md", task["task_id"], "codex",
                selected=["unknown"], evidence="unknown",
            )
        path = self.root / "docs/nulnul/project.md"
        capability_contract.write_rows(path, [dict(CAPABILITIES[0], status="retired")])
        pack = capability_pack.prepare(self.root, path, task["task_id"], "codex")
        self.assertEqual(pack["capability_refs"], [])

    def test_pack_binds_canonical_target_digest_and_task(self):
        task, pack = self.prepare(
            "Change API behavior", "API validation", ["project-api-validation"], "API contract applies",
        )
        reference = pack["capability_refs"][0]
        self.assertEqual(reference["logical_load_target"], CAPABILITIES[0]["logical_load_target"])
        self.assertEqual(reference["body_digest"], hashlib.sha256(
            (self.root / reference["body_source"]).read_bytes()
        ).hexdigest())
        other = runtime.start_task(self.root, "Unrelated follow-up", "maintenance")
        with self.assertRaisesRegex(ValueError, "different task"):
            capability_pack.load_pack(self.root, pack["pack_id"], other["task_id"])
        self.assertEqual(capability_pack.load_pack(self.root, pack["pack_id"], task["task_id"])["pack_digest"], pack["pack_digest"])

    def test_stale_body_digest_and_body_change_fail_closed(self):
        path = self.root / "docs/nulnul/project.md"
        capability_contract.write_rows(path, [dict(CAPABILITIES[0], version_or_digest="0" * 64)])
        _, task = self.begin("Change API behavior", "API validation")
        with self.assertRaisesRegex(ValueError, "accepted digest"):
            capability_pack.prepare(
                self.root, path, task["task_id"], "codex",
                selected=["project-api-validation"], evidence="API contract applies",
            )
        capability_contract.write_rows(path, CAPABILITIES)
        pack = capability_pack.prepare(
            self.root, path, task["task_id"], "codex",
            selected=["project-api-validation"], evidence="API contract applies",
        )
        body = self.root / pack["capability_refs"][0]["body_source"]
        body.write_text("changed", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "changed after pack creation"):
            capability_pack.work_start(self.root, pack["pack_id"])

    def test_single_pack_check_creates_evolution_eligible_experience(self):
        _, task = self.begin("Change API behavior and error catalog", "API validation")
        outcome = self.valid_capability_outcome()
        record = runtime.finish_task(self.root, task["task_id"], outcome)
        self.assertTrue(record["evolution_eligible"])
        self.assertEqual(record["attribution_scope"], "CAPABILITY")
        self.assertEqual(record["active_capability_ids"], ["project-api-validation"])
        self.assertEqual(record["derived_from"][:2], [
            f"session:{record['session_id']}", f"task:{record['task_id']}"
        ])

    def test_pack_without_relevant_check_is_stored_but_not_eligible(self):
        _, task = self.begin("Change API behavior and error catalog", "API validation")
        record = runtime.finish_task(self.root, task["task_id"], self.valid_capability_outcome(include_check=False))
        self.assertEqual(record["experience_type"], "CAPABILITY_EXPERIENCE")
        self.assertFalse(record["evolution_eligible"])

    def test_multi_capability_pack_gets_pack_level_not_individual_credit(self):
        _, task = self.begin("Update API contract and release documentation", "combined maintenance")
        pack = capability_pack.prepare(
            self.root, self.root / "docs/nulnul/project.md", task["task_id"], "codex",
            selected=[row["capability_id"] for row in CAPABILITIES], evidence="both accepted jobs apply",
        )
        capability_pack.work_start(self.root, pack["pack_id"])
        check = capability_pack.run_check(self.root, pack["pack_id"], "project-api-validation")
        record = runtime.finish_task(self.root, task["task_id"], {
            "pack_id": pack["pack_id"], "check_id": check["check_id"],
            "capability_id": "project-api-validation", "quality": "VERIFIED",
            "observability_completeness": "COMPLETE", "result": "SUCCESS",
            "product_outcome": "combined work complete", "checks": [{"result": "pass"}],
        })
        self.assertEqual(record["experience_type"], "TASK_EXPERIENCE")
        self.assertEqual(record["attribution_scope"], "PACK")
        self.assertFalse(record["evolution_eligible"])

    def test_pack_id_is_unique_and_receipt_is_read_only(self):
        _, first = self.prepare("Change API behavior", "API validation", ["project-api-validation"], "API applies")
        path = capability_pack.pack_file(self.root, first["pack_id"])
        self.assertEqual(path.stat().st_mode & 0o222, 0)
        runtime.finalize_session(self.root, "PARTIAL")
        _, second = self.prepare("Change API behavior again", "API validation", ["project-api-validation"], "API applies")
        self.assertNotEqual(first["pack_id"], second["pack_id"])

    def test_legacy_runtime_rule_cleanup_is_explicit_exact_and_trust_neutral(self):
        target = self.root / sync_host_entry.LEGACY_RULE
        target.parent.mkdir(parents=True)
        target.write_bytes(b"legacy exact rule")
        expected = hashlib.sha256(target.read_bytes()).hexdigest()
        with mock.patch.object(sync_host_entry, "LEGACY_RULE_SHA256", expected):
            result = sync_host_entry.retire_legacy_runtime_rule(self.root)
        self.assertEqual(result["status"], "LEGACY_RUNTIME_RULE_RETIRED")
        self.assertFalse(result["trust_mutated"])
        target.write_bytes(b"foreign rule")
        with self.assertRaisesRegex(ValueError, "foreign"):
            sync_host_entry.retire_legacy_runtime_rule(self.root)

    def test_claude_governed_authority_remains_separate_from_pack_context(self):
        claude_skill = self.root / ".claude/skills/nulnul-harness"
        claude_skill.parent.mkdir(parents=True)
        shutil.copytree(SKILL, claude_skill)
        payload = activation_boundary.governed_stage(
            claude_skill / "scripts/activation_boundary.py", self.root, "adopt-upgrade", "claude"
        )
        self.assertIn("CLAUDE.md", payload["authority"])
        self.assertNotIn("AGENTS.md", payload["authority"])
        self.assertFalse(any(path.startswith(".codex/") for path in payload["authority"]))


class FoundationLoopIntegrationTests(FoundationCase):
    def test_session_memory_recovery_loop(self):
        _, task = self.begin(modules=["api.py"])
        runtime.finish_task(
            self.root,
            task["task_id"],
            {"quality": "VERIFIED", "result": "SUCCESS", "product_outcome": "API fixed", "checks": [{"result": "pass"}]},
            {"decisions": [{"decision": "Use API catalog", "why": "verified"}], "lessons": [{"lesson": "Run API catalog", "scope": "api"}]},
        )
        runtime.finalize_session(self.root, "COMPLETED", "Continue API work", "COMPLETE")
        resumed = runtime.start_session(self.root, "Continue API work", self.fingerprint)
        pack = runtime.context_pack(self.root, "API catalog")
        self.assertEqual(resumed["status"], "STARTED")
        self.assertGreaterEqual(pack["item_count"], 2)

    def test_attribution_loop_and_missing_cause_control(self):
        _, task = self.begin()
        valid = runtime.finish_task(self.root, task["task_id"], self.valid_capability_outcome())
        runtime.finalize_session(self.root)
        self.assertTrue(valid["evolution_eligible"])
        _, second = self.begin("Second API task")
        invalid = runtime.finish_task(self.root, second["task_id"], self.valid_capability_outcome(include_check=False))
        self.assertFalse(invalid["evolution_eligible"])

    def test_setup_to_runtime_uses_identical_rows(self):
        path = self.root / "docs/nulnul/project.md"
        capability_contract.write_rows(path, CAPABILITIES)
        setup_rows = capability_contract.load(path, require_canonical=True, current_only=True)
        runtime_rows = capability_contract.bounded_view(path)
        self.assertEqual(setup_rows, runtime_rows)

    def test_large_history_keeps_direct_context_bounded(self):
        store = runtime.Store(self.root)
        store.initialize()
        index = runtime.load_index(store)
        for number in range(500):
            index["search"].append({
                "item_id": f"exp-history-{number}", "type": "experience", "status": "ACTIVE",
                "created_at": f"2020-01-01T00:{number % 60:02}:00Z", "summary": f"unrelated historical item {number}",
                "terms": ["unrelated", str(number)], "capability_id": None, "modules": [], "quality": "VERIFIED",
                "evolution_eligible": False, "provenance": [],
            })
        runtime.save_index(store, index)
        pack = runtime.context_pack(self.root, "rename one local variable")
        self.assertLessEqual(pack["item_count"], runtime.MAX_CONTEXT_ITEMS)
        self.assertLessEqual(pack["byte_count"], runtime.MAX_CONTEXT_BYTES)
        self.assertEqual(pack["items"], [])
        self.assertFalse(pack["raw_transcripts_included"])


if __name__ == "__main__":
    unittest.main()
