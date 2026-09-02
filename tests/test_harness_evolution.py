import copy
import os
import sys
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins/nulnul-harness/skills/nulnul-harness"
sys.path.insert(0, str(SKILL / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

import capability_pack
import foundation_runtime as runtime
import harness_control
import harness_evolution
from test_natural_selection import NaturalSelectionCase


class HarnessEvolutionCase(NaturalSelectionCase):
    def harness_experience(self, control_id="control-capability-selection", *, weakness=True):
        control = harness_control.current_control(self.root, control_id)
        task = self.start("Validate API behavior and error catalog", "project API validation")
        pack = capability_pack.prepare(
            self.root, self.root / "docs/nulnul/project.md", task["task_id"], "codex",
            selected=["project-api-validation"], evidence="the accepted API contract governs this task",
        )
        capability_pack.work_start(self.root, pack["pack_id"])
        (self.root / f"work-{task['task_id']}.txt").write_text("done\n", encoding="utf-8")
        actual = "adjacent candidate admitted" if weakness else "only exact project-fit candidate admitted"
        result = capability_pack.finalize_pack_task(self.root, pack["pack_id"], {
            "control_id": control_id,
            "observed_decision": "rank the bounded accepted capability metadata",
            "expected_effect": "only exact project-fit candidate admitted",
            "actual_effect": actual,
            "harness_cost": {"input_tokens": 12, "model_calls": 0, "runtime_ms": 3},
            "harness_attribution_class": control["attribution_class"],
        })["experience"]
        runtime.finalize_session(self.root, "COMPLETED", completeness="COMPLETE")
        self.assertTrue(result["harness_evolution_eligible"])
        return result

    def review(self, signal, experiences, target="control-capability-selection", **extra):
        payload = {
            "trigger": extra.pop("trigger", "material-evidence"),
            "signal": signal,
            "target_control_id": target,
            "source_experience_ids": [row["experience_id"] for row in experiences],
        }
        if signal not in {"success-only", "none", "insufficient"}:
            payload.update({
                "observed_weakness": "the current bounded control repeatedly produced the wrong observable effect",
                "why_harness_control_contributed": "the frozen control digest owned the observed decision",
                "generalizable_repair": "change only the bounded policy while preserving Kernel contracts",
                "expected_benefit": "stronger verified project control precision",
                "quality_risk": "a stricter policy could miss a true positive",
                "cost_risk": "a replacement could add fixed control work",
                "safety_risk": "policy scope must not broaden authority",
                "what_must_not_change": "identity, provenance, checks, rollback, authority, and context hard limits",
            })
        payload.update(extra)
        return harness_evolution.evaluate(self.root, payload)

    def control_spec(self, identity="control-capability-selection", **changes):
        source = harness_control.current_control(self.root, "control-capability-selection")
        row = {
            key: copy.deepcopy(source[key])
            for key in harness_control.CONTROL_FIELDS
            if key not in {"current_version", "current_digest", "status"}
        }
        row["control_id"] = identity
        row.update(changes)
        return row

    def competition(self, challenger_digest, *, metric=(2, 0), challenger_pass=True, cheaper=False):
        passed = {
            "strict": True,
            "authoritative_checks": True,
            "correct_capability_choice": True,
            "correct_agent_topology": True,
            "correct_memory_retrieval": True,
            "unauthorized_writes": 0,
            "regressions": 0,
        }
        failed = dict(passed, strict=False)
        groups = [
            {
                "group": "TARGET_WEAKNESS", "task_hash": "a" * 64,
                "fixture_hash": "b" * 64, "project_revision": "fixture-v1",
                "check_identities": ["project-contract"], "champion": passed,
                "challenger": passed if challenger_pass else failed,
            },
            {
                "group": "SEALED_HOLDOUT", "task_hash": "c" * 64,
                "fixture_hash": "d" * 64, "project_revision": "fixture-v1",
                "check_identities": ["project-contract"], "champion": passed,
                "challenger": passed if challenger_pass else failed,
                "sealed_after_challenger_digest": challenger_digest,
                "exposed_before_freeze": False,
            },
        ]
        champion_cost = {field: 10 for field in harness_evolution.COST_FIELDS}
        challenger_cost = {field: (5 if cheaper else 10) for field in harness_evolution.COST_FIELDS}
        return {
            "task_groups": groups,
            "champion_cost": champion_cost,
            "challenger_cost": challenger_cost,
            "control_metric": {
                "name": "false_positive_count", "direction": "LOWER",
                "champion": metric[0], "challenger": metric[1], "verified": True,
            },
        }

    def freeze_and_apply(self, evaluation, specification, **competition_options):
        challenger = harness_evolution.freeze_challenger(self.root, evaluation, specification)
        safety = harness_evolution.safety_gate(self.root, evaluation, challenger["challenger_digest"])
        competition = harness_evolution.freeze_competition(
            self.root, evaluation, challenger["challenger_digest"], safety["safety_digest"],
            self.competition(challenger["challenger_digest"], **competition_options),
        )
        self.start("Apply Harness lifecycle", "Harness control maintenance")
        result = harness_evolution.transact(
            self.root, evaluation, challenger["challenger_digest"], safety["safety_digest"],
            competition["competition_digest"],
        )
        return result, challenger, safety, competition


class HarnessControlContractTests(HarnessEvolutionCase):
    def test_guarded_kernel_and_five_declarative_controls_are_canonical(self):
        registry = harness_control.shipped_registry()
        self.assertEqual({row["invariant_id"] for row in registry["guarded_kernel"]}, harness_control.REQUIRED_KERNEL)
        self.assertEqual(len(registry["controls"]), 5)
        self.assertTrue(all(harness_control.KERNEL_FORBIDDEN_EFFECTS <= set(row["forbidden_effects"]) for row in registry["controls"]))
        self.assertEqual(harness_evolution.validate_state(self.root), [])

    def test_clear_direct_reads_no_control_registry_and_adds_no_model_context(self):
        task = self.start("Rename one fixture label", "ordinary fixture cleanup")
        with mock.patch.object(harness_control, "project_policy", side_effect=AssertionError("registry loaded")):
            boot = capability_pack.bootstrap(
                self.root, self.root / "docs/nulnul/project.md", task["task_id"], "codex"
            )
        self.assertEqual(boot["selection_method"], "deterministic-zero")
        self.assertFalse(capability_pack.load_pack(self.root, boot["pack_id"])["selection_control_loaded"])
        self.assertEqual(boot["model_context"], {})
        self.assertNotIn("harness", str(boot["model_context"]).lower())

    def test_pack_authoritative_receipt_creates_harness_attributed_experience(self):
        experience = self.harness_experience(weakness=True)
        self.assertTrue(experience["harness_evolution_eligible"])
        self.assertTrue(experience["check_id"])
        self.assertIn(f"check:{experience['check_id']}", experience["source_refs"])
        self.assertIn("control:control-capability-selection@", " ".join(experience["source_refs"]))
        query = harness_evolution.evolution_query(self.root, "control-capability-selection")
        self.assertEqual([row["experience_id"] for row in query["records"]], [experience["experience_id"]])
        self.assertFalse(query["raw_transcripts_returned"])

    def test_non_harness_and_unverified_evidence_cannot_authorize_mutation(self):
        generic = self.generic_experience()
        with self.assertRaisesRegex(ValueError, "Harness-attributed"):
            self.review("selection-false-positive", [generic])
        experiences = [self.harness_experience(), self.harness_experience()]
        path = runtime.Store(self.root).experiences / f"{experiences[0]['experience_id']}.json"
        row = runtime.read_json(path)
        row["quality"] = "PARTIAL"
        runtime.write_json(path, row)
        with self.assertRaisesRegex(ValueError, "active VERIFIED"):
            self.review("selection-false-positive", experiences)


class HarnessLifecycleTests(HarnessEvolutionCase):
    def test_keep_records_anti_churn_without_materializing_registry(self):
        experiences = [self.harness_experience(weakness=False), self.harness_experience(weakness=False)]
        evaluation = self.review("success-only", experiences, trigger="explicit-maintenance")
        self.assertEqual(evaluation["result"], "KEEP")
        self.start()
        result = harness_evolution.transact(self.root, evaluation)
        self.assertEqual(result["operation"], "KEEP")
        runtime.finalize_session(self.root, "ABORTED")
        self.assertFalse(harness_control.paths(self.root)["current"].exists())
        repeated = self.review("success-only", experiences)
        self.assertEqual(repeated["result"], "NO_ACTION")

    def test_tune_promotes_bounded_policy_and_runtime_resolves_it(self):
        experiences = [self.harness_experience(), self.harness_experience()]
        evaluation = self.review("selection-false-positive", experiences)
        self.assertEqual(evaluation["result"], "TUNE_CANDIDATE")
        policy = dict(harness_control.current_control(self.root, "control-capability-selection")["policy"])
        policy["strong_match_terms"] = 3
        result, _, safety, competition = self.freeze_and_apply(evaluation, {"policy": policy})
        self.assertEqual(safety["result"], "PASS")
        self.assertEqual(competition["outcome"], "PROMOTE_CHALLENGER")
        self.assertEqual(result["operation"], "TUNE")
        resolved, loaded = capability_pack.selection_policy(self.root)
        self.assertTrue(loaded)
        self.assertEqual(resolved["strong_match_terms"], 3)
        self.assertEqual(harness_evolution.validate_state(self.root), [])

    def test_replace_preserves_identity_but_changes_strategy(self):
        experiences = [self.harness_experience(), self.harness_experience()]
        evaluation = self.review("replacement-advantage", experiences)
        spec = self.control_spec(policy={
            "candidate_limit": 3, "semantic_fallback": False,
            "strategy": "deterministic_only", "strong_match_terms": 3,
        })
        result, _, _, _ = self.freeze_and_apply(evaluation, {"control": spec})
        current = harness_control.current_control(self.root, "control-capability-selection")
        self.assertEqual(result["operation"], "REPLACE")
        self.assertEqual(current["current_version"], 2)
        self.assertEqual(current["policy"]["strategy"], "deterministic_only")

    def test_retire_and_create_keep_runtime_resolution_valid(self):
        experiences = [
            self.harness_experience("control-maintenance-trigger"),
            self.harness_experience("control-maintenance-trigger"),
        ]
        create = self.review("uncovered-control", experiences, target="control-project-privacy-query")
        spec = self.control_spec(
            "control-project-privacy-query",
            job="Sanitize maintenance discovery queries before crossing a project boundary.",
        )
        result, _, _, _ = self.freeze_and_apply(create, {"control": spec})
        self.assertEqual(result["operation"], "CREATE")
        self.assertEqual(harness_control.current_control(self.root, "control-project-privacy-query")["status"], "CURRENT")
        active = runtime.read_json(runtime.Store(self.root).active)
        runtime.finish_task(self.root, active["tasks"][-1]["task_id"], {"result": "SUCCESS"})
        runtime.finalize_session(self.root, "COMPLETED", completeness="COMPLETE")

        experiences = [
            self.harness_experience("control-project-privacy-query"),
            self.harness_experience("control-project-privacy-query"),
        ]
        retire = self.review(
            "control-subsumed", experiences, target="control-project-privacy-query",
            subsumed_by_control_id="control-maintenance-trigger",
        )
        result, _, _, _ = self.freeze_and_apply(retire, {})
        self.assertEqual(result["operation"], "RETIRE")
        with self.assertRaisesRegex(ValueError, "not uniquely current"):
            harness_control.current_control(self.root, "control-project-privacy-query")
        active = runtime.read_json(runtime.Store(self.root).active)
        runtime.finish_task(self.root, active["tasks"][-1]["task_id"], {"result": "SUCCESS"})
        runtime.finalize_session(self.root, "COMPLETED", completeness="COMPLETE")
        task = self.start("Rename one fixture label", "ordinary fixture cleanup")
        boot = capability_pack.bootstrap(
            self.root, self.root / "docs/nulnul/project.md", task["task_id"], "codex"
        )
        self.assertEqual(boot["selection_method"], "deterministic-zero")
        self.assertTrue(any(harness_control.paths(self.root)["history"].glob("*.json")))

    def test_required_runtime_control_cannot_retire_or_change_schema(self):
        experiences = [self.harness_experience(), self.harness_experience()]
        retire = self.review(
            "control-subsumed", experiences, subsumed_by_control_id="control-maintenance-trigger"
        )
        with self.assertRaisesRegex(ValueError, "still required by the runtime"):
            harness_evolution.freeze_challenger(self.root, retire, {})

        replace = self.review("replacement-advantage", experiences)
        spec = self.control_spec(policy_schema={"unknown_strategy": {"type": "boolean"}}, policy={"unknown_strategy": True})
        with self.assertRaisesRegex(ValueError, "compiled runtime contract"):
            harness_evolution.freeze_challenger(self.root, replace, {"control": spec})

    def test_lower_cost_cannot_hide_quality_regression(self):
        experiences = [self.harness_experience(), self.harness_experience()]
        evaluation = self.review("selection-false-positive", experiences)
        policy = dict(harness_control.current_control(self.root, "control-capability-selection")["policy"])
        policy["strong_match_terms"] = 3
        challenger = harness_evolution.freeze_challenger(self.root, evaluation, {"policy": policy})
        safety = harness_evolution.safety_gate(self.root, evaluation, challenger["challenger_digest"])
        competition = harness_evolution.freeze_competition(
            self.root, evaluation, challenger["challenger_digest"], safety["safety_digest"],
            self.competition(challenger["challenger_digest"], challenger_pass=False, cheaper=True),
        )
        self.assertEqual(competition["outcome"], "KEEP_CURRENT")

    def test_missing_holdout_and_kernel_or_self_promotion_are_rejected(self):
        experiences = [self.harness_experience(), self.harness_experience()]
        evaluation = self.review("selection-false-positive", experiences)
        policy = dict(harness_control.current_control(self.root, "control-capability-selection")["policy"])
        policy["strong_match_terms"] = 3
        challenger = harness_evolution.freeze_challenger(self.root, evaluation, {"policy": policy})
        safety = harness_evolution.safety_gate(self.root, evaluation, challenger["challenger_digest"])
        evidence = self.competition(challenger["challenger_digest"])
        evidence["task_groups"] = evidence["task_groups"][:1]
        with self.assertRaisesRegex(ValueError, "two or three"):
            harness_evolution.freeze_competition(
                self.root, evaluation, challenger["challenger_digest"], safety["safety_digest"], evidence,
            )
        row = copy.deepcopy(challenger)
        tuned = next(item for item in row["proposed_registry"]["controls"] if item["control_id"] == "control-capability-selection")
        tuned["status"] = "CURRENT"
        row["proposed_registry"] = harness_control.with_digests(row["proposed_registry"])
        row["challenger_digest"] = harness_evolution.canonical_digest({key: value for key, value in row.items() if key != "challenger_digest"})
        path = harness_evolution.paths(self.root)["challengers"] / f"{row['challenger_digest']}.json"
        runtime.write_json(path, row)
        receipt = harness_evolution.safety_gate(self.root, evaluation, row["challenger_digest"])
        self.assertEqual(receipt["result"], "FAIL")
        self.assertFalse(receipt["checks"]["self_promotion_blocked"])

        row = copy.deepcopy(challenger)
        row["proposed_registry"]["guarded_kernel"][0]["behavior"] = "the Challenger owns identity"
        row["proposed_registry"] = harness_control.with_digests(row["proposed_registry"])
        row["challenger_digest"] = harness_evolution.canonical_digest({key: value for key, value in row.items() if key != "challenger_digest"})
        runtime.write_json(
            harness_evolution.paths(self.root)["challengers"] / f"{row['challenger_digest']}.json", row
        )
        receipt = harness_evolution.safety_gate(self.root, evaluation, row["challenger_digest"])
        self.assertEqual(receipt["result"], "FAIL")
        self.assertFalse(receipt["checks"]["kernel_unchanged"])

    def test_forbidden_provenance_check_and_authority_changes_fail_contract_validation(self):
        registry = harness_control.shipped_registry()
        for forbidden in ("rewrite_provenance", "disable_authoritative_check", "broaden_authority"):
            candidate = copy.deepcopy(registry)
            row = candidate["controls"][0]
            row["forbidden_effects"].remove(forbidden)
            with self.assertRaisesRegex(ValueError, "Kernel boundaries"):
                harness_control.with_digests(candidate)

    def test_stale_champion_and_partial_write_rollback(self):
        experiences = [self.harness_experience(), self.harness_experience()]
        evaluation = self.review("selection-false-positive", experiences)
        policy = dict(harness_control.current_control(self.root, "control-capability-selection")["policy"])
        policy["strong_match_terms"] = 3
        challenger = harness_evolution.freeze_challenger(self.root, evaluation, {"policy": policy})
        safety = harness_evolution.safety_gate(self.root, evaluation, challenger["challenger_digest"])
        competition = harness_evolution.freeze_competition(
            self.root, evaluation, challenger["challenger_digest"], safety["safety_digest"],
            self.competition(challenger["challenger_digest"]),
        )
        self.start()
        real_replace, count = os.replace, 0
        def fail_after_one(source, target):
            nonlocal count
            count += 1
            if count == 2:
                raise OSError("injected Harness transaction failure")
            return real_replace(source, target)
        with self.assertRaisesRegex(OSError, "injected"):
            harness_evolution.transact(
                self.root, evaluation, challenger["challenger_digest"], safety["safety_digest"],
                competition["competition_digest"], replace=fail_after_one,
            )
        self.assertFalse(harness_control.paths(self.root)["current"].exists())
        self.assertEqual(runtime.read_jsonl(runtime.Store(self.root).decisions), [])
        self.assertEqual(harness_evolution.validate_state(self.root), [])

        registry = harness_control.shipped_registry()
        changed = copy.deepcopy(registry)
        target = next(row for row in changed["controls"] if row["control_id"] == "control-context-ranking")
        target["policy"]["module_weight"] = 7
        target["current_version"] = 2
        changed = harness_control.with_digests(changed)
        runtime.write_json(harness_control.paths(self.root)["current"], changed)
        with self.assertRaisesRegex(ValueError, "stale HARNESS CHAMPION"):
            harness_evolution.validate_evaluation(self.root, evaluation)

    def test_post_write_validation_failure_rolls_back(self):
        experiences = [self.harness_experience(), self.harness_experience()]
        evaluation = self.review("selection-false-positive", experiences)
        policy = dict(harness_control.current_control(self.root, "control-capability-selection")["policy"])
        policy["strong_match_terms"] = 3
        challenger = harness_evolution.freeze_challenger(self.root, evaluation, {"policy": policy})
        safety = harness_evolution.safety_gate(self.root, evaluation, challenger["challenger_digest"])
        competition = harness_evolution.freeze_competition(
            self.root, evaluation, challenger["challenger_digest"], safety["safety_digest"],
            self.competition(challenger["challenger_digest"]),
        )
        self.start()
        with mock.patch.object(harness_evolution, "validate_state", return_value=["negative control"]):
            with self.assertRaisesRegex(ValueError, "negative control"):
                harness_evolution.transact(
                    self.root, evaluation, challenger["challenger_digest"], safety["safety_digest"],
                    competition["competition_digest"],
                )
        self.assertFalse(harness_control.paths(self.root)["current"].exists())
        self.assertEqual(runtime.read_jsonl(runtime.Store(self.root).decisions), [])

    def test_real_review_does_not_reopen_fixed_historical_failures(self):
        self.capability_experience()
        review = harness_evolution.real_review(self.root)
        self.assertEqual(review["decision"], "NO_REAL_HARNESS_MUTATION_JUSTIFIED")
        self.assertFalse(review["mutation_justified"])


if __name__ == "__main__":
    unittest.main()
