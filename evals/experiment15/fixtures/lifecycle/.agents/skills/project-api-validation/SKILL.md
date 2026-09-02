---
name: project-api-validation
description: Apply this repository's alert request-validation and error-code contract when API acceptance or rejection behavior changes.
metadata:
  job: api-error-code-maintenance
---

# Project API validation

Use this procedure for request-validation changes:

1. Inspect the target alert handler and its unit tests.
2. Preserve absent, empty, and already accepted inputs.
3. Preserve `errors.problem(field, code)` and reject invalid input before any outbox mutation.
4. Add every new error code to `contracts/error-codes.json`; keep it sorted and unique.
5. Run `python3 -m unittest -q`.
6. Run `python3 tools/verify_error_catalog.py`.

Do not use this Skill for internal algorithms or release documentation.
