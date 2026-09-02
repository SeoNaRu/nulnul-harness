---
name: project-api-validation
description: Apply this repository's request-validation and structured error-catalog contract when public API acceptance or rejection changes.
metadata:
  job: api-error-catalog-maintenance
---

# Project API validation

For public request-validation changes:

1. Preserve absent, empty, and already accepted inputs.
2. Reject invalid input with `errors.problem(field, code)` before queue, registry,
   outbox, or other durable mutation.
3. Name a new enum error `INVALID_<UPPERCASE_FIELD>` and add it to
   `contracts/error-codes.json`, keeping that catalog sorted and unique.
4. Never mutate the caller-owned request.
5. Run the unit suite and `python3 tools/verify_error_catalog.py`.

Do not use this capability for internal algorithms or release documentation.
