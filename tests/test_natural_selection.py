import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins/nulnul-harness/skills/nulnul-harness"
sys.path.insert(0, str(SKILL / "scripts"))

import capability_contract
import capability_pack
import foundation_runtime as runtime
import natural_selection
import sync_host_entry


ROWS = [
    {
        "capability_id": "project-api-validation",
        "job": "Preserve the project API contract",
        "activation_trigger": "API behavior or error catalog changes",
        "project_check_identity": "project-contract",
        "status": "accepted/current",
        "version_or_digest": "v1",
        "logical_load_target": "capabilities/project-api-validation/SKILL.md",
    },
    {
        "capability_id": "project-release-docs",
        "job": "Preserve release documentation",
        "activation_trigger": "release documentation changes",
        "project_check_identity": "project-contract",
        "status": "accepted/current",
        "version_or_digest": "v1",
        "logical_load_target": "capabilities/project-release-docs/SKILL.md",
    },
]


def project_text(rows=ROWS):
    return f"""# nulnul project setup

## Goal
Ship a verified local product.

## Current milestone
The requested behavior and checks pass.
Observable completion check: `true`

## Constraints and permissions
No external writes.

## Inspected roster
- Host surface: Codex
- Skills: accepted project skills
- Plugins: nulnul-harness
- Agents: direct owner

## Capability requirements
API and release contracts are recurring project jobs.

## Candidate evidence
Project-local capabilities were inspected for their named jobs.

{capability_contract.render(rows)}
## Capability routing
The canonical table is the only Pack source.

## Setup decisions
- Reuse now: accepted capabilities
- Add now: none
- Needs approval: none
- Skip: unrelated capabilities

## Agent topology
Direct execution with deterministic verification.

## Evolution baseline
Current checks pass.

## Continuity
- Active checkpoint: `docs/nulnul/checkpoint.json`
"""


class NaturalSelectionCase(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="nulnul-natural-selection.")
        self.root = Path(self.temporary.name)
        (self.root / "docs/nulnul").mkdir(parents=True)
        (self.root / "docs/nulnul/project.md").write_text(project_text(), encoding="utf-8")
        (self.root / "docs/nulnul/checkpoint.json").write_text("{}\n", encoding="utf-8")
        for row in ROWS:
            path = natural_selection.body_path(self.root, row["capability_id"])
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"# {row['capability_id']}\n\n{row['job']}\n", encoding="utf-8")
        self.fingerprint = runtime.host_fingerprint(
            "codex", "test", "test-model", nulnul_revision="test-nulnul",
            project_revision="test-project", host_trust="host-owned",
            admission_state="PRE_SESSION_CAPABILITY_PACK", project_root=self.root,
        )

    def tearDown(self):
        self.temporary.cleanup()

    def start(self, goal="Review capability ecosystem", job="capability ecosystem review"):
        runtime.start_session(self.root, goal, self.fingerprint)
        return runtime.start_task(self.root, goal, job)

    def capability_experience(self, identity="project-api-validation", success=True):
        task = self.start(f"Change {identity}", "project contract work")
        if not success:
            project = self.root / "docs/nulnul/project.md"
            project.write_text(project.read_text(encoding="utf-8").replace("`true`", "`false`", 1), encoding="utf-8")
        pack = capability_pack.prepare(
            self.root, self.root / "docs/nulnul/project.md", task["task_id"], "codex",
            selected=[identity], evidence="the accepted project contract governs this task",
        )
        capability_pack.work_start(self.root, pack["pack_id"])
        marker = self.root / f"work-{task['task_id']}.txt"
        marker.write_text("done\n", encoding="utf-8")
        result = capability_pack.finalize_pack_task(self.root, pack["pack_id"])["experience"]
        runtime.finalize_session(self.root, "COMPLETED" if success else "PARTIAL", completeness="COMPLETE")
        if not success:
            project = self.root / "docs/nulnul/project.md"
            project.write_text(project.read_text(encoding="utf-8").replace("`false`", "`true`", 1), encoding="utf-8")
        return result

    def generic_experience(self, job="uncovered deployment validation"):
        task = self.start(job, job)
        result = runtime.finish_task(self.root, task["task_id"], {
            "quality": "VERIFIED",
            "observability_completeness": "COMPLETE",
            "result": "SUCCESS",
            "product_outcome": "manual project procedure completed",
            "checks": [{"id": "manual-procedure", "result": "pass"}],
        })
        runtime.finalize_session(self.root, completeness="COMPLETE")
        return result

    def co_selection_experience(self):
        task = self.start("Update API release documentation", "project contract work")
        pack = capability_pack.prepare(
            self.root, self.root / "docs/nulnul/project.md", task["task_id"], "codex",
            selected=[row["capability_id"] for row in ROWS], evidence="both project contracts govern this task",
        )
        capability_pack.work_start(self.root, pack["pack_id"])
        result = runtime.finish_task(self.root, task["task_id"], {
            "pack_id": pack["pack_id"],
            "quality": "VERIFIED",
            "observability_completeness": "COMPLETE",
            "result": "SUCCESS",
            "product_outcome": "joint project contract work completed",
            "checks": [{"id": "joint-contract", "result": "pass"}],
        })
        runtime.finalize_session(self.root, completeness="COMPLETE")
        return result

    def review(self, signal, experiences, affected=None, **extra):
        payload = {
            "trigger": extra.pop("trigger", "material-evidence"),
            "signal": signal,
            "affected_capability_ids": affected or [],
            "source_experience_ids": [row["experience_id"] for row in experiences],
        }
        if signal not in {"success-only", "none", "insufficient", "conflict"}:
            payload.update({
                "diagnosis": "verified evidence identifies one bounded ecosystem weakness",
                "what_must_not_change": "existing project checks and state authority",
                "risk_analysis": "the proposed lifecycle change could regress existing work",
                "rollback_plan": "restore the frozen ecosystem Champion",
            })
        payload.update(extra)
        return natural_selection.evaluate(self.root, payload)

    def competition(self, outcome="IMPROVED"):
        result = {
            "champion": {"strict": True, "project_check": True, "completion": True, "unauthorized_writes": 0},
            "challenger": {"strict": True, "project_check": True, "completion": True, "unauthorized_writes": 0},
            "regressions": 0,
            "holdout_pass": True,
            "primary_outcome": outcome,
        }
        if outcome == "EQUIVALENT":
            result["secondary_advantage"] = "less duplicate capability context"
        return result

    def candidate(self, identity="project-api-validation"):
        return {
            "capability_type": "SKILL",
            "capability_id": identity,
            "job": "Preserve the project API contract",
            "activation_trigger": "API behavior or error catalog changes",
            "project_check_identity": "project-contract",
        }

    def apply(self, evaluation, candidate=None, body=None, competition=None, **kwargs):
        self.start()
        candidate = natural_selection.freeze_candidate(candidate, body) if candidate else None
        return natural_selection.transact(
            self.root, evaluation, competition, candidate, body, **kwargs,
        )


class NaturalSelectionEvaluatorTests(NaturalSelectionCase):
    def test_keep_uses_real_evolution_input_and_establishes_cooldown(self):
        experience = self.capability_experience()
        evaluation = self.review(
            "success-only", [experience], ["project-api-validation"], trigger="explicit-maintenance"
        )
        self.assertEqual(evaluation["result"], "KEEP")
        committed = self.apply(evaluation)
        self.assertEqual(committed["operation"], "KEEP")
        covered = self.review("success-only", [experience], ["project-api-validation"])
        self.assertEqual(covered["result"], "NO_ACTION")

    def test_upgrade_requires_attributable_failure(self):
        success = self.capability_experience()
        weak = self.review("skill-contract-gap", [success], ["project-api-validation"])
        self.assertEqual(weak["result"], "MORE_EXPERIENCE_REQUIRED")
        failure = self.capability_experience(success=False)
        justified = self.review("skill-contract-gap", [failure], ["project-api-validation"])
        self.assertEqual(justified["result"], "UPGRADE_CANDIDATE")

    def test_retire_needs_obsolete_job_or_replacement_coverage(self):
        experience = self.capability_experience()
        unsupported = self.review("obsolete-job", [experience], ["project-api-validation"])
        self.assertEqual(unsupported["result"], "MORE_EXPERIENCE_REQUIRED")
        supported = self.review(
            "obsolete-job", [experience], ["project-api-validation"], job_no_longer_exists=True
        )
        self.assertEqual(supported["result"], "RETIRE_CANDIDATE")

    def test_merge_requires_repeated_evidence_backed_overlap(self):
        first = self.co_selection_experience()
        early = self.review(
            "strong-overlap", [first], ["project-api-validation", "project-release-docs"]
        )
        self.assertEqual(early["result"], "MORE_EXPERIENCE_REQUIRED")
        second = self.co_selection_experience()
        supported = self.review(
            "strong-overlap", [first, second], ["project-api-validation", "project-release-docs"]
        )
        self.assertEqual(supported["result"], "MERGE_CANDIDATE")

    def test_create_requires_repeated_uncovered_work(self):
        first = self.generic_experience()
        early = self.review("recurring-uncovered-job", [first], uncovered_job="deployment validation")
        self.assertEqual(early["result"], "MORE_EXPERIENCE_REQUIRED")
        second = self.generic_experience()
        supported = self.review(
            "recurring-uncovered-job", [first, second], uncovered_job="deployment validation"
        )
        self.assertEqual(supported["result"], "CREATE_CANDIDATE")

    def test_conflict_is_not_automatically_a_merge(self):
        experience = self.capability_experience()
        result = self.review("conflict", [experience], ["project-api-validation", "project-release-docs"], conflict={
            "capability_a": "project-api-validation",
            "capability_b": "project-release-docs",
            "conflicting_invariant": "the same response field has incompatible required forms",
            "affected_jobs": ["project contract work"],
            "risk": "one task could receive contradictory guidance",
        })
        self.assertEqual(result["result"], "MORE_EXPERIENCE_REQUIRED")
        self.assertEqual(result["conflict_record"]["capability_a"], "project-api-validation")


class NaturalSelectionTransactionTests(NaturalSelectionCase):
    def test_upgrade_supersedes_body_version_and_pack_resolves_successor(self):
        failure = self.capability_experience(success=False)
        evaluation = self.review("skill-contract-gap", [failure], ["project-api-validation"])
        old_digest = natural_selection.body_digest(self.root, "project-api-validation")
        body = "# project-api-validation\n\nRequire explicit boundary validation.\n"
        result = self.apply(evaluation, self.candidate(), body, self.competition())
        current = capability_contract.selected(self.root / "docs/nulnul/project.md", "project-api-validation")
        self.assertEqual(result["operation"], "UPGRADE")
        self.assertEqual(current["version_or_digest"], hashlib.sha256(body.encode()).hexdigest())
        self.assertTrue((natural_selection.body_path(self.root, "project-api-validation").parent / "versions" / old_digest / "SKILL.md").is_file())
        lifecycle = runtime.read_jsonl(runtime.Store(self.root).decisions)[-1]["natural_selection"]
        self.assertTrue(lifecycle["diagnosis"])
        self.assertTrue(lifecycle["rollback_plan"])
        self.assertEqual(natural_selection.validate_ecosystem(self.root), [])

    def test_retire_excludes_pack_selection_but_retains_history(self):
        experience = self.capability_experience()
        evaluation = self.review(
            "obsolete-job", [experience], ["project-api-validation"], job_no_longer_exists=True
        )
        result = self.apply(evaluation, competition=self.competition("EQUIVALENT"))
        self.assertEqual(result["operation"], "RETIRE")
        self.assertNotIn("project-api-validation", result["current_capability_ids"])
        self.assertTrue((runtime.Store(self.root).experiences / f"{experience['experience_id']}.json").is_file())
        self.assertEqual(natural_selection.validate_ecosystem(self.root), [])

    def test_create_adds_one_canonical_pack_resolvable_capability(self):
        evidence = [self.generic_experience(), self.generic_experience()]
        evaluation = self.review(
            "recurring-uncovered-job", evidence, uncovered_job="deployment validation"
        )
        candidate = self.candidate("project-deployment-validation") | {
            "job": "Preserve deployment validation",
            "activation_trigger": "deployment contract changes",
        }
        result = self.apply(
            evaluation, candidate, "# project-deployment-validation\n\nVerify deployment state.\n", self.competition()
        )
        self.assertIn("project-deployment-validation", result["current_capability_ids"])
        self.assertEqual(natural_selection.validate_ecosystem(self.root), [])

    def test_replace_moves_source_out_of_pack_and_promotes_distinct_survivor(self):
        experience = self.capability_experience()
        evaluation = self.review(
            "replacement-advantage", [experience], ["project-api-validation"],
            replacement_capability_id="project-request-contract",
        )
        candidate = self.candidate("project-request-contract")
        result = self.apply(
            evaluation, candidate, "# project-request-contract\n\nValidate requests.\n", self.competition()
        )
        statuses = {row["capability_id"]: row["status"] for row in capability_contract.load(self.root / "docs/nulnul/project.md")}
        self.assertEqual(statuses["project-api-validation"], "superseded")
        self.assertEqual(statuses["project-request-contract"], "accepted/current")
        self.assertEqual(result["current_capability_ids"], ["project-release-docs", "project-request-contract"])

    def test_merge_preserves_sources_and_selects_only_merged_survivor(self):
        evidence = [self.co_selection_experience(), self.co_selection_experience()]
        evaluation = self.review(
            "strong-overlap", evidence, ["project-api-validation", "project-release-docs"]
        )
        candidate = self.candidate("project-contract") | {
            "job": "Preserve API and release contracts",
            "activation_trigger": "API or release contract changes",
        }
        result = self.apply(
            evaluation, candidate, "# project-contract\n\nVerify both contracts.\n", self.competition("EQUIVALENT")
        )
        self.assertEqual(result["current_capability_ids"], ["project-contract"])
        statuses = {row["capability_id"]: row["status"] for row in capability_contract.load(self.root / "docs/nulnul/project.md")}
        self.assertEqual(statuses["project-api-validation"], "superseded")
        self.assertEqual(statuses["project-release-docs"], "superseded")

    def test_decision_memory_records_provenance_and_context_summary(self):
        experience = self.capability_experience()
        evaluation = self.review(
            "success-only", [experience], ["project-api-validation"], trigger="explicit-maintenance"
        )
        result = self.apply(evaluation)
        decision = runtime.read_jsonl(runtime.Store(self.root).decisions)[-1]
        self.assertEqual(decision["decision_id"], result["decision_id"])
        self.assertEqual(decision["derived_from"], [f"experience:{experience['experience_id']}"])
        self.assertEqual(decision["natural_selection"]["operation"], "KEEP")
        self.assertEqual(runtime.validate_lineage(self.root), [])


class NaturalSelectionFailureTests(NaturalSelectionCase):
    def test_unknown_or_dangling_inputs_fail(self):
        with self.assertRaisesRegex(ValueError, "unknown source Experience"):
            natural_selection.evaluate(self.root, {
                "signal": "success-only", "affected_capability_ids": ["project-api-validation"],
                "source_experience_ids": ["exp-missing"],
            })
        experience = self.capability_experience()
        with self.assertRaisesRegex(ValueError, "unknown or noncurrent"):
            self.review("obsolete-job", [experience], ["missing-capability"], job_no_longer_exists=True)

    def test_stale_champion_digest_fails_before_write(self):
        experience = self.capability_experience()
        evaluation = self.review(
            "success-only", [experience], ["project-api-validation"], trigger="explicit-maintenance"
        )
        natural_selection.body_path(self.root, "project-api-validation").write_text("changed\n", encoding="utf-8")
        before = (self.root / "docs/nulnul/project.md").read_bytes()
        self.start()
        with self.assertRaisesRegex(ValueError, "stale ECOSYSTEM CHAMPION"):
            natural_selection.transact(self.root, evaluation)
        self.assertEqual((self.root / "docs/nulnul/project.md").read_bytes(), before)

    def test_duplicate_create_and_invalid_replacement_fail(self):
        evidence = [self.generic_experience(), self.generic_experience()]
        create = self.review("recurring-uncovered-job", evidence, uncovered_job="deployment validation")
        self.start()
        duplicate = natural_selection.freeze_candidate(
            self.candidate("project-api-validation"), "new\n"
        )
        with self.assertRaisesRegex(ValueError, "duplicates"):
            natural_selection.transact(
                self.root, create, self.competition(), duplicate, "new\n"
            )
        runtime.finalize_session(self.root, "ABORTED")
        capability = self.capability_experience()
        replace = self.review(
            "replacement-advantage", [capability], ["project-api-validation"],
            replacement_capability_id="project-request-contract",
        )
        self.start()
        with self.assertRaisesRegex(ValueError, "requires job"):
            natural_selection.freeze_candidate(
                {"capability_id": "project-request-contract", "capability_type": "SKILL"}, "new\n"
            )

    def test_partial_write_failure_rolls_back_every_file(self):
        evidence = [self.generic_experience(), self.generic_experience()]
        evaluation = self.review("recurring-uncovered-job", evidence, uncovered_job="deployment validation")
        self.start()
        project = self.root / "docs/nulnul/project.md"
        store = runtime.Store(self.root)
        before = {path: path.read_bytes() if path.exists() else None for path in (project, store.decisions, store.index, store.active)}
        calls = 0

        def fail_second(source, target):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("injected replace failure")
            os.replace(source, target)

        candidate = self.candidate("project-deployment-validation")
        candidate = natural_selection.freeze_candidate(candidate, "# project-deployment-validation\n")
        with self.assertRaisesRegex(OSError, "injected"):
            natural_selection.transact(
                self.root, evaluation, self.competition(), candidate,
                "# project-deployment-validation\n", replace=fail_second,
            )
        for path, content in before.items():
            self.assertEqual(path.read_bytes() if path.exists() else None, content)
        self.assertFalse(natural_selection.body_path(self.root, "project-deployment-validation").exists())

    def test_invalid_post_write_pack_resolution_rolls_back(self):
        evidence = [self.generic_experience(), self.generic_experience()]
        evaluation = self.review("recurring-uncovered-job", evidence, uncovered_job="deployment validation")
        self.start()
        project = self.root / "docs/nulnul/project.md"
        before = project.read_bytes()
        with mock.patch.object(natural_selection, "validate_ecosystem", return_value=["invalid Pack resolution"]):
            with self.assertRaisesRegex(ValueError, "invalid Pack resolution"):
                candidate = natural_selection.freeze_candidate(
                    self.candidate("project-deployment-validation"), "# project-deployment-validation\n"
                )
                natural_selection.transact(
                    self.root, evaluation, self.competition(), candidate,
                    "# project-deployment-validation\n",
                )
        self.assertEqual(project.read_bytes(), before)
        self.assertFalse(natural_selection.body_path(self.root, "project-deployment-validation").exists())

    def test_broken_natural_selection_provenance_is_rejected(self):
        experience = self.capability_experience()
        evaluation = self.review(
            "success-only", [experience], ["project-api-validation"], trigger="explicit-maintenance"
        )
        self.apply(evaluation)
        store = runtime.Store(self.root)
        decisions = runtime.read_jsonl(store.decisions)
        decisions[-1]["natural_selection"]["source_experience_ids"] = ["exp-dangling"]
        runtime.write_jsonl(store.decisions, decisions)
        self.assertTrue(any("dangling Natural Selection Experience" in error for error in natural_selection.validate_ecosystem(self.root)))

    def test_competition_rejects_quality_or_authority_regression(self):
        failed_check = self.competition()
        failed_check["challenger"]["project_check"] = False
        with self.assertRaisesRegex(ValueError, "primary competition outcome"):
            natural_selection.validate_competition(failed_check)
        no_advantage = self.competition("EQUIVALENT")
        no_advantage["secondary_advantage"] = ""
        with self.assertRaisesRegex(ValueError, "secondary advantage"):
            natural_selection.validate_competition(no_advantage)
        unauthorized = self.competition()
        unauthorized["challenger"]["unauthorized_writes"] = 1
        with self.assertRaisesRegex(ValueError, "state authority"):
            natural_selection.validate_competition(unauthorized)

    def test_direct_guidance_has_no_natural_selection_fixed_context(self):
        class State:
            def as_posix(self):
                return "docs/nulnul/checkpoint.json"

        block = sync_host_entry.managed_block("codex", State())
        self.assertNotIn("Natural Selection", block)
        self.assertNotIn("natural_selection.py", block)


if __name__ == "__main__":
    unittest.main()
