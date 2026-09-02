import copy
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "plugins/nulnul-harness/skills/nulnul-harness/scripts/generalization_core.py"
FOUNDATION = ROOT / "plugins/nulnul-harness/skills/nulnul-harness/scripts/foundation_runtime.py"
SPEC = importlib.util.spec_from_file_location("cross_project_generalization", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
F_SPEC = importlib.util.spec_from_file_location("generalization_foundation", FOUNDATION)
F = importlib.util.module_from_spec(F_SPEC)
F_SPEC.loader.exec_module(F)


class CrossProjectGeneralizationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.home = self.root / "personal-home"
        self.home.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def project(self, name, count=2, *, prior=None, valid=True):
        root = self.root / name
        root.mkdir()
        F.Store(root).initialize()
        F.start_session(root, "generalization fixture", F.host_fingerprint(
            "test", "1", "fixture", project_revision="rev-1", project_root=root,
        ))
        ids = []
        for index in range(count):
            task = F.start_task(root, f"validate public API input {index}", "public API structured validation")
            outcome = {
                "quality": "VERIFIED" if valid else "PARTIAL",
                "result": "SUCCESS",
                "checks": [{"identity": "project-check", "result": "PASS"}],
                "product_outcome": "structured invalid input rejected",
                "observability_completeness": "COMPLETE",
                "source_refs": [f"generalization:{prior}"] if prior else [],
            }
            ids.append(F.finish_task(root, task["task_id"], outcome)["experience_id"])
        F.finalize_session(root, "COMPLETED", "done", "COMPLETE")
        return root, ids

    def proposal(self, sources, *, pattern=None, applies=None, excludes=None):
        ids = [identity for _, experience_ids in sources for identity in experience_ids]
        return {
            "type": "WORKFLOW",
            "abstract_pattern": pattern or "Validate structured public input before domain dispatch and preserve the canonical error catalog identity.",
            "job_problem_class": "public API structured input validation",
            "applicability_conditions": applies or ["public API", "structured error catalog"],
            "non_applicability_conditions": excludes or ["internal trusted batch"],
            "source_projects": [{"root": str(root), "experience_ids": experience_ids} for root, experience_ids in sources],
            "created_at": "2026-09-02T00:00:00+00:00",
            "diagnosis": {
                "source_experience_ids": ids,
                "observed_reusable_pattern": "Early validation preserved a stable public error contract.",
                "project_specific_details_removed": "Repository names, paths, payloads, endpoints, and business identifiers.",
                "why_pattern_may_transfer": "The control depends on a public boundary and canonical error catalog, not one codebase.",
                "known_preconditions": ["public API", "structured error catalog"],
                "known_non_applicability": ["internal trusted batch"],
                "counterevidence": [],
                "privacy_risk": "Only the abstract validation order is retained.",
                "expected_target_benefit": "Avoid dispatching invalid public input while preserving project-owned error identity.",
            },
        }

    def candidate(self, sources, **changes):
        proposal = self.proposal(sources, **changes)
        return MODULE.build_candidate(proposal)

    def create_candidate(self, sources, **changes):
        candidate = self.candidate(sources, **changes)
        decision = MODULE.evaluate(candidate=candidate)
        self.assertEqual(decision["result"], "CREATE_GENERALIZATION_CANDIDATE")
        MODULE.transact(self.home, decision["result"], candidate=candidate)
        return candidate

    def record(self, identity):
        return next(row for row in MODULE.load_generalizations(self.home)["generalizations"] if row["generalization_id"] == identity)

    def test_project_only_is_default_until_repeated_evidence(self):
        self.assertEqual(MODULE.privacy_classify({"pattern": "safe"})["state"], "PROJECT_ONLY")
        project, ids = self.project("one", count=1)
        candidate = self.candidate([(project, ids)])
        self.assertEqual(MODULE.evaluate(candidate=candidate)["result"], "MORE_PROJECT_EVIDENCE_REQUIRED")
        with self.assertRaisesRegex(MODULE.GeneralizationError, "repeated verified"):
            MODULE.transact(self.home, "CREATE_GENERALIZATION_CANDIDATE", candidate=candidate)
        self.assertFalse((self.home / MODULE.GENERALIZATION_REGISTRY).exists())

    def test_single_project_repeated_pattern_creates_candidate_not_transferable(self):
        project, ids = self.project("one")
        candidate = self.create_candidate([(project, ids)])
        record = self.record(candidate["generalization_id"])
        self.assertEqual(record["status"], "CANDIDATE")
        self.assertEqual(record["independent_project_count"], 1)
        self.assertEqual(MODULE.evaluate(existing=record)["result"], "MORE_PROJECT_EVIDENCE_REQUIRED")

    def test_two_independent_projects_deduplicate_and_promote(self):
        first, first_ids = self.project("one")
        second, second_ids = self.project("two")
        candidate = self.create_candidate([(first, first_ids)])
        duplicate = self.candidate([(second, second_ids)])
        result = MODULE.transact(self.home, "CREATE_GENERALIZATION_CANDIDATE", candidate=duplicate)
        self.assertEqual(result["generalization_id"], candidate["generalization_id"])
        record = self.record(candidate["generalization_id"])
        self.assertEqual(record["independent_project_count"], 2)
        self.assertEqual(MODULE.evaluate(existing=record)["result"], "PROMOTE_TRANSFERABLE")
        MODULE.transact(self.home, "PROMOTE_TRANSFERABLE", generalization_id=record["generalization_id"])
        self.assertEqual(self.record(record["generalization_id"])["status"], "TRANSFERABLE")

    def test_bounded_semantic_equivalence_keeps_one_runtime_owned_survivor(self):
        first, first_ids = self.project("one")
        second, second_ids = self.project("two")
        survivor = self.create_candidate([(first, first_ids)])
        paraphrase = self.candidate(
            [(second, second_ids)],
            pattern="Preserve the canonical structured rejection identity by validating public inputs before dispatch.",
        )
        result = MODULE.transact(
            self.home, "CREATE_GENERALIZATION_CANDIDATE", candidate=paraphrase,
            equivalent_generalization_id=survivor["generalization_id"],
        )
        self.assertEqual(result["generalization_id"], survivor["generalization_id"])
        self.assertEqual(len(MODULE.load_generalizations(self.home)["generalizations"]), 1)

    def test_target_confirmation_promotes_without_sharing_source_memory(self):
        source, ids = self.project("source")
        candidate = self.create_candidate([(source, ids)])
        target, target_ids = self.project("target", count=1, prior=candidate["generalization_id"])
        MODULE.transact(
            self.home, "RECORD_TARGET_VALIDATION", generalization_id=candidate["generalization_id"],
            target_root=target, target_experience_id=target_ids[0], target_result="CONFIRMED",
            applicability_summary="Target has the same public boundary and canonical structured error catalog.",
        )
        record = self.record(candidate["generalization_id"])
        self.assertEqual(MODULE.evaluate(existing=record)["result"], "PROMOTE_TRANSFERABLE")
        MODULE.transact(self.home, "PROMOTE_TRANSFERABLE", generalization_id=candidate["generalization_id"])
        prior = MODULE.retrieve_priors(self.home, {
            "schema_version": 1,
            "job_problem_class": "public API structured input validation",
            "conditions": ["public API", "structured error catalog"],
        })
        self.assertEqual(prior["item_count"], 1)
        self.assertFalse(prior["source_project_memory_included"])
        self.assertNotIn("source_evidence", prior["priors"][0])
        self.assertFalse(prior["target_authority_changed"])

    def test_target_contradiction_is_retained_and_can_narrow_scope(self):
        first, first_ids = self.project("one")
        second, second_ids = self.project("two")
        candidate = self.create_candidate([(first, first_ids)])
        MODULE.transact(self.home, "CREATE_GENERALIZATION_CANDIDATE", candidate=self.candidate([(second, second_ids)]))
        MODULE.transact(self.home, "PROMOTE_TRANSFERABLE", generalization_id=candidate["generalization_id"])
        target, target_ids = self.project("target", count=1, prior=candidate["generalization_id"])
        MODULE.transact(
            self.home, "RECORD_TARGET_VALIDATION", generalization_id=candidate["generalization_id"],
            target_root=target, target_experience_id=target_ids[0], target_result="CONTRADICTED",
            applicability_summary="Target delegates validation to a generated boundary that owns a different invariant.",
        )
        self.assertEqual(MODULE.evaluate(existing=self.record(candidate["generalization_id"]))["result"], "NARROW_SCOPE")
        MODULE.transact(
            self.home, "NARROW_SCOPE", generalization_id=candidate["generalization_id"],
            applicability_conditions=["public API", "structured error catalog", "validation owned in request boundary"],
            non_applicability_conditions=["internal trusted batch", "generated boundary owns validation"],
        )
        narrowed = self.record(candidate["generalization_id"])
        self.assertEqual(narrowed["status"], "NARROWED")
        self.assertEqual(len(narrowed["counterevidence"]), 1)

    def test_wrong_project_vocabulary_does_not_retrieve_prior(self):
        first, first_ids = self.project("one")
        second, second_ids = self.project("two")
        candidate = self.create_candidate([(first, first_ids)])
        MODULE.transact(self.home, "CREATE_GENERALIZATION_CANDIDATE", candidate=self.candidate([(second, second_ids)]))
        MODULE.transact(self.home, "PROMOTE_TRANSFERABLE", generalization_id=candidate["generalization_id"])
        result = MODULE.retrieve_priors(self.home, {
            "schema_version": 1,
            "job_problem_class": "internal API documentation release",
            "conditions": ["public API", "structured error catalog"],
        })
        self.assertEqual(result["priors"], [])

    def test_privacy_gate_rejects_raw_paths_code_and_unknown_state(self):
        for field, value in (
            ("raw_transcript", "model output"),
            ("absolute_path", "/private/repository/file.py"),
            ("source_code", "def secret_implementation(): pass"),
            ("repository_name", "private-customer-service"),
        ):
            result = MODULE.privacy_classify({field: value})
            self.assertEqual(result["state"], "REJECTED_SENSITIVE")
        with self.assertRaisesRegex(MODULE.GeneralizationError, "unknown privacy"):
            MODULE.privacy_classify({"pattern": "safe"}, "UNKNOWN")

    def test_credential_shaped_data_needs_redaction(self):
        result = MODULE.privacy_classify({"api_key": "sk-example123456789"})
        self.assertEqual(result["state"], "NEEDS_REDACTION")

    def test_unknown_or_ineligible_experience_and_dangling_project_identity_fail(self):
        project, ids = self.project("one", count=1, valid=False)
        with self.assertRaisesRegex(MODULE.GeneralizationError, "ineligible"):
            MODULE.collect_source_evidence([{"root": str(project), "experience_ids": ids}])
        project, ids = self.project("two", count=1)
        with self.assertRaisesRegex(MODULE.GeneralizationError, "unknown"):
            MODULE.collect_source_evidence([{"root": str(project), "experience_ids": ["exp-missing"]}])
        session_path = next((project / "docs/nulnul/memory/sessions").glob("*.json"))
        session = json.loads(session_path.read_text())
        session["host_fingerprint"]["project_root_identity"] = "unknown"
        session_path.write_text(json.dumps(session))
        with self.assertRaisesRegex(MODULE.GeneralizationError, "project identity"):
            MODULE.collect_source_evidence([{"root": str(project), "experience_ids": ids}])

    def test_circular_derived_source_cannot_inflate_independence(self):
        project, ids = self.project("one")
        candidate = self.candidate([(project, ids)])
        candidate["source_evidence"][0]["derived_generalization_ids"] = [candidate["generalization_id"]]
        self.assertTrue(any("circular" in error for error in MODULE.validate_record(candidate)))

    def test_supersession_retirement_and_lineage_are_preserved(self):
        one, one_ids = self.project("one")
        two, two_ids = self.project("two")
        old = self.create_candidate([(one, one_ids)])
        MODULE.transact(self.home, "CREATE_GENERALIZATION_CANDIDATE", candidate=self.candidate([(two, two_ids)]))
        MODULE.transact(self.home, "PROMOTE_TRANSFERABLE", generalization_id=old["generalization_id"])
        successor = self.candidate(
            [(one, one_ids), (two, two_ids)],
            pattern="Validate typed public input at the owning boundary and preserve canonical error identity.",
        )
        MODULE.transact(self.home, "SUPERSEDE", generalization_id=old["generalization_id"], candidate=successor)
        registry = MODULE.load_generalizations(self.home)
        self.assertEqual(MODULE.validate_registry(registry), [])
        old_record = self.record(old["generalization_id"])
        new_record = self.record(successor["generalization_id"])
        self.assertEqual(old_record["superseded_by"], new_record["generalization_id"])
        MODULE.transact(self.home, "RETIRE", generalization_id=new_record["generalization_id"], reason="Framework generation removed this boundary.")
        self.assertEqual(self.record(new_record["generalization_id"])["status"], "RETIRED")

    def test_target_local_derivative_source_ref_is_foundation_valid(self):
        source, ids = self.project("source")
        candidate = self.create_candidate([(source, ids)])
        target, target_ids = self.project("target", count=1, prior=candidate["generalization_id"])
        self.assertEqual(F.validate_lineage(target), [])
        experience = F.read_json(F.Store(target).experiences / f"{target_ids[0]}.json")
        self.assertIn(f"generalization:{candidate['generalization_id']}", experience["source_refs"])

    def test_atomic_replace_failure_preserves_registry(self):
        project, ids = self.project("one")
        candidate = self.create_candidate([(project, ids)])
        path = self.home / MODULE.GENERALIZATION_REGISTRY
        before = path.read_bytes()

        def fail(_source, _target):
            raise OSError("injected replace failure")

        with self.assertRaises(OSError):
            MODULE.transact(
                self.home, "RETIRE", generalization_id=candidate["generalization_id"],
                reason="fixture retirement", replace=fail,
            )
        self.assertEqual(path.read_bytes(), before)

    def test_legacy_personal_cross_project_evidence_is_non_authoritative(self):
        legacy = json.loads((ROOT / "evals/meta-evolution/cross-project-evidence.json").read_text())
        result = MODULE.classify_legacy(legacy)
        self.assertEqual(result["status"], "HISTORICAL_NONCURRENT")

    def test_lifecycle_seed_has_no_mutation_authority(self):
        project, ids = self.project("one")
        seed = MODULE.lifecycle_seed(self.candidate([(project, ids)]))
        self.assertEqual(seed["owner"], "NATURAL_SELECTION")
        self.assertFalse(seed["direct_mutation_authority"])

    def test_clear_direct_has_zero_generalization_load_or_state(self):
        project, _ = self.project("direct", count=1)
        runtime_source = FOUNDATION.read_text()
        self.assertNotIn("import cross_project_evolution", runtime_source)
        self.assertFalse((project / "docs/nulnul/generalizations.json").exists())
        self.assertFalse((project / "docs/nulnul/memory/generalizations.json").exists())

    def test_real_review_requires_two_independent_project_roots(self):
        project, _ = self.project("one")
        result = MODULE.real_review([project])
        self.assertEqual(result["result"], "MORE_REAL_PROJECT_EVIDENCE_REQUIRED")
        self.assertEqual(result["independent_project_count"], 1)


if __name__ == "__main__":
    unittest.main()
