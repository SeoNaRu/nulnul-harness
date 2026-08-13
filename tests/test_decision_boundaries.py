import copy
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "evals/decision-boundaries/candidate_validator.py"
SPEC = importlib.util.spec_from_file_location("decision_boundaries", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def decision(layer, status, source, value, action, proposed, kind, basis_source, dependency=None):
    return {
        "layer": layer,
        "current": {"status": status, "source": source, "value": value},
        "action": action,
        "proposed": proposed,
        "basis": {
            "kind": kind,
            "source": basis_source,
            "evidence": "bounded fixture evidence",
            "depends_on": dependency,
        },
    }


def artifact(decisions):
    return {
        "schema_version": 1,
        "decision_id": "fixture-1",
        "target": "fixture",
        "required_layers": [row["layer"] for row in decisions],
        "decisions": decisions,
        "capabilities_used": ["frontend-design"],
        "personal_sources_read": 1,
        "unrelated_personal_reads": 0,
        "permission_delta": [],
    }


class DecisionBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.design = artifact([
            decision("design.component_shape", "accepted", "project", "low", "preserve", "low", "accepted_contract", "project"),
            decision("design.visual_tone", "undecided", "none", None, "change", "quiet", "approved_preference", "approved_personal"),
        ])
        self.web = artifact([
            decision("frontend.architecture", "insufficient", "project", "python_templates", "change", "component_frontend", "observed_failure", "outcome_fit"),
            decision("backend.architecture", "working", "project", "python_api", "preserve", "python_api", "accepted_contract", "project"),
        ])

    def test_valid_scoped_design_and_web_decisions(self):
        self.assertEqual(MODULE.validate(self.design, self.design["required_layers"]), [])
        self.assertEqual(MODULE.validate(self.web, self.web["required_layers"]), [])

    def test_personal_preference_cannot_override_project_scope(self):
        altered = copy.deepcopy(self.design)
        altered["decisions"][0] = decision(
            "design.component_shape", "accepted", "project", "low", "change", "rounded",
            "approved_preference", "approved_personal",
        )
        self.assertTrue(MODULE.validate(altered))

    def test_external_skill_cannot_override_project_scope(self):
        altered = copy.deepcopy(self.design)
        altered["decisions"][0] = decision(
            "design.component_shape", "accepted", "project", "low", "change", "rounded",
            "observed_failure", "external_capability",
        )
        self.assertIn(
            "decisions[0] lets lower-scope guidance override an accepted project decision",
            MODULE.validate(altered),
        )

    def test_personal_preference_can_fill_undecided_design_scope(self):
        self.assertEqual(MODULE.validate(self.design), [])

    def test_frontend_change_cannot_rewrite_working_backend_by_outcome_fit(self):
        altered = copy.deepcopy(self.web)
        altered["decisions"][1] = decision(
            "backend.architecture", "working", "project", "python_api", "change", "javascript_api",
            "outcome_fit", "outcome_fit",
        )
        self.assertIn(
            "decisions[1] changes an established layer without independent justification",
            MODULE.validate(altered),
        )

    def test_invalid_backend_cannot_be_preserved_as_working(self):
        altered = copy.deepcopy(self.web)
        altered["decisions"][1]["current"]["status"] = "invalid"
        self.assertIn("decisions[1] cannot preserve a non-established layer", MODULE.validate(altered))

    def test_required_cross_layer_dependency_is_allowed(self):
        altered = copy.deepcopy(self.web)
        altered["decisions"][1] = decision(
            "backend.architecture", "working", "project", "python_api_v1", "change", "python_api_v2",
            "required_dependency", "project", "frontend.architecture",
        )
        self.assertEqual(MODULE.validate(altered), [])

    def test_explicit_full_rewrite_is_allowed(self):
        altered = copy.deepcopy(self.web)
        for row, proposed in zip(altered["decisions"], ("component_frontend", "javascript_api")):
            row.update(action="change", proposed=proposed)
            row["basis"].update(kind="explicit_user_request", source="current_user")
        self.assertEqual(MODULE.validate(altered), [])

    def test_greenfield_can_choose_both_layers(self):
        greenfield = artifact([
            decision("frontend.architecture", "absent", "none", None, "change", "component_frontend", "outcome_fit", "outcome_fit"),
            decision("backend.architecture", "absent", "none", None, "change", "python_api", "outcome_fit", "outcome_fit"),
        ])
        self.assertEqual(MODULE.validate(greenfield), [])

    def test_stack_uniformity_or_popularity_is_not_a_basis(self):
        altered = copy.deepcopy(self.web)
        altered["decisions"][1] = decision(
            "backend.architecture", "working", "project", "python_api", "change", "javascript_api",
            "popularity", "external_capability",
        )
        self.assertIn("decisions[1].basis.kind is invalid", MODULE.validate(altered))

    def test_explicit_user_can_change_an_accepted_project_decision(self):
        altered = copy.deepcopy(self.design)
        altered["decisions"][0] = decision(
            "design.component_shape", "accepted", "project", "low", "change", "rounded",
            "explicit_user_request", "current_user",
        )
        self.assertEqual(MODULE.validate(altered), [])

    def test_prose_only_or_raw_personal_content_fails_closed(self):
        self.assertTrue(MODULE.validate({"instruction": "preserve scope"}))
        altered = copy.deepcopy(self.design)
        altered["raw_personal_notes"] = "private"
        self.assertIn("root fields are not allowed: raw_personal_notes", MODULE.validate(altered))

    def test_permission_expansion_fails(self):
        altered = copy.deepcopy(self.design)
        altered["permission_delta"] = ["publish"]
        self.assertIn("permission_delta must remain empty", MODULE.validate(altered))

    def test_unsupported_schema_layer_and_missing_required_layer_fail(self):
        altered = copy.deepcopy(self.design)
        altered["schema_version"] = 2
        altered["required_layers"][0] = "infrastructure.universal"
        altered["decisions"][0]["layer"] = "infrastructure.universal"
        errors = MODULE.validate(altered, ["backend.architecture"])
        self.assertIn("schema_version must be 1", errors)
        self.assertTrue(any("unsupported" in error for error in errors))
        self.assertIn("required layer missing: backend.architecture", errors)


if __name__ == "__main__":
    unittest.main()
