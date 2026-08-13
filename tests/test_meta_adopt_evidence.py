import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("meta_adopt_evidence", ROOT / "scripts/meta_adopt_evidence.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
PREREGISTRATION = json.loads((ROOT / "evals/meta-evolution/release-preregistration.json").read_text(encoding="utf-8"))


def valid_payload():
    frozen = PREREGISTRATION["frozen_candidate"]
    families = PREREGISTRATION["adaptation_inventory"]["families"]
    return {
        "schema_version": 1,
        "episode_id": PREREGISTRATION["episode_id"],
        "run_date": "2026-08-13",
        "installed_plugin": {"version": "2.0.0", "distribution_source": "github-tag", "marketplace_ref": "v2.0.0", "local_override": False, "symlink": False},
        "distribution": {"release_tag": "v2.0.0", "release_commit": "a" * 40, "asset": "nulnul-harness-2.0.0.zip", "asset_sha256": "b" * 64, "local_public_byte_identity": True, "manifest_identity": True},
        "meta_candidate": frozen,
        "available_adaptation_families": families,
        "personal_home": {"configured": True, "existing_directory": True, "not_symlink": True, "registry_valid": True, "privacy_passed": True, "path_stored": False},
        "project_m": {
            "user_named_adaptation": False,
            "available": families,
            "flat_lookup": {"status": "APPLY", "selected": ["personal-transactional-migration-v1"], "compatibility_checks_executed": 3},
            "meta_selector": {"status": "APPLY", "selected": ["personal-transactional-migration-v1"], "shortlisted": ["personal-transactional-migration-v1"], "excluded": [{"adaptation_id": "personal-checkpoint-freshness-v1", "reason": "conditions_not_met"}], "compatibility_checks_executed": 1},
            "false_activations": 0,
            "relevant_omissions": 0,
            "downstream_completion_checks": [{"check": "migration state", "exit_code": 0}],
            "permission_delta": [],
            "privacy_result": "passed",
        },
        "no_relevant_control": {"status": "NO_RELEVANT_ADAPTATION", "selected": [], "forced_apply_count": 0, "project_local_flow_continued": True},
        "conflict_control": {"status": "META_CONFLICT", "selected": [], "auto_apply": False, "arbitrary_winner": None, "permission_delta": []},
        "live_cycle": {"downstream_completion_passed": True, "false_activations": 0, "relevant_omissions": 0, "unsupported_conflict_resolutions": 0, "permission_expansions": 0},
        "rollback_control": {"isolated": True, "threshold_breached": True, "rolled_back_to": "flat-lookup-v1", "unrelated_state_corruption": False},
        "exposure": {"classification": "release_adoption", "candidate_tuning": False, "retired_local_holdouts_reused": False},
        "meta_gate": {"decision": "META_PROMOTION", "gate_agent": "product-builder", "candidate_author": "coach", "target_agent": "gate"},
        "generalization": {"decision": "narrower_scope", "harness_wide": False},
    }


class MetaAdoptEvidenceTests(unittest.TestCase):
    def errors(self, payload=None):
        return MODULE.validate(payload or valid_payload(), PREREGISTRATION, "2.0.0")

    def test_valid_public_meta_adoption(self):
        self.assertEqual(self.errors(), [])

    def test_wrong_version_or_local_source_is_rejected(self):
        altered = valid_payload()
        altered["installed_plugin"].update(version="1.7.0", local_override=True)
        errors = self.errors(altered)
        self.assertIn("public meta adoption plugin version is stale", errors)
        self.assertIn("public meta adoption reused local source", errors)

    def test_decision_regression_and_private_path_are_rejected(self):
        altered = valid_payload()
        altered["project_m"]["meta_selector"]["selected"] = []
        altered["claim_boundary"] = "read /private/project"
        errors = self.errors(altered)
        self.assertIn("fresh Project M meta decision differs from flat lookup", errors)
        self.assertTrue(any("machine path" in error for error in errors))

    def test_no_match_conflict_and_rollback_fail_closed(self):
        altered = copy.deepcopy(valid_payload())
        altered["no_relevant_control"]["forced_apply_count"] = 1
        altered["conflict_control"]["auto_apply"] = True
        altered["rollback_control"]["rolled_back_to"] = "meta-selector-v1"
        errors = self.errors(altered)
        self.assertIn("public no-relevant control failed", errors)
        self.assertIn("public conflict control did not fail closed", errors)
        self.assertIn("public meta rollback control failed", errors)


if __name__ == "__main__":
    unittest.main()
