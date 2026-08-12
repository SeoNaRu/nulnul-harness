# nulnul harness 1.5.0

This release adds a scoped Generalization Gate beside the existing 100/100 behavior and safety Release Gate. Evaluation exposure is machine-readable, previously seen cases cannot be relabeled as unseen, and used holdouts cannot be recycled.

The first one-shot holdout exposed an invalid Ruby fixture and was permanently downgraded to validation. After mandatory fixture preflight, a new Perl/TAP CLI shape transferred the checkpoint-freshness mechanism: all three stale mutations were blocked and all three post-check states resumed, while champion retry and best-of-3 remained unsafe. The decision is deliberately narrower scope; harness-wide generalization is not established.

Schema-v3 checkpoints keep runner-owned bounded verification receipts, and Generalization Gate activates only for personal/core promotion or transfer claims. Ordinary project-local changes do not pay holdout cost. The plugin remains skills-only with no server, hook, daemon, authentication, external service, raw transcript store, or new permission.

All 94 repository tests, the packaged-product checks, documentation-debt check, and Release Gate pass with fresh GitHub-marketplace installation evidence for version 1.5.0.
