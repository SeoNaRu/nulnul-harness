import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "plugins/nulnul-harness/skills/nulnul-harness/scripts/validate_project_setup.py"
SPEC = importlib.util.spec_from_file_location("validate_project_setup", SCRIPT)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)

VALID = """# nulnul project setup

## Goal
Ship a useful local tool.
## Current milestone
The health route works.
Observable completion check: python3 -m unittest -v
## Constraints and permissions
No external writes.
## Inspected roster
- Host surface: Codex
- Skills: nulnul-harness
- Plugins: nulnul-harness
- Agents: one direct agent
## Capability requirements
Native Python is sufficient.
## Candidate evidence
The standard library covers the route.
## Capability routing
Python handles the local request.
## Setup decisions
- Reuse now: Python standard library
- Add now: focused route test
- Needs approval: none
- Skip: MCP and extra agents because the job is local and sequential
## Agent topology
Direct execution with an independent test.
## Evolution baseline
Existing tests pass before and after.
## Continuity
- Active checkpoint: not needed for this single session.
"""


class ProjectSetupTests(unittest.TestCase):
    def test_complete_contract_is_valid(self):
        self.assertEqual(validator.validate(VALID), [])

    def test_missing_required_section_is_rejected(self):
        errors = validator.validate(VALID.replace("## Inspected roster", "## Inventory"))
        self.assertIn("missing heading: Inspected roster", errors)

    def test_unfinished_template_field_is_rejected(self):
        errors = validator.validate(VALID.replace("Codex", "{detected host}", 1))
        self.assertIn("unfinished field: - Host surface:", errors)
        self.assertIn("contract contains template placeholders", errors)


if __name__ == "__main__":
    unittest.main()
