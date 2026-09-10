# nulnul harness 3.2.0

Exact-public Claude and Meta adoption pass for 3.2.0. All 481 repository checks pass and Release Gate reports 100/100 with `release_ready=true`. Final/latest publication follows green main CI, recorded on the GitHub release. Historical 3.1.0 evidence remains immutable.

## Changes

- Route ordinary work through its existing contract; load setup, workflow, and evolution details only when needed. Move repository-specific developer invariants into a conditional development contract.
- Generate directly executable checkpoint validation and completion commands in the active host entry. Preserve the inactive host entry and one state writer; reuse a transaction-owned passing check while its inputs remain current.
- Compare all shipped files when an installed-copy check is requested. Report stale or unknown copies and use native host installation commands for refresh.
- Reject malformed checkpoint and receipt fields, invalidate previous verification before rechecking, and scan the non-Git documentation fallback once.
- Project bounded, session-bound selected/loaded/checked Trace evidence through the existing Foundation writer. Observability grants no authority, promotion, or comparative-quality claim.
- Preserve the rejected instruction-routing experiment and its frozen evaluator as historical development evidence, without reopening its exposed cases or adopting its performance claim.

## Validation boundary

[Local maintenance](../docs/runtime-maintenance.md) and [fresh Codex work sessions](../docs/live-use-validation.md) record the observed fixes and remaining limitations. The updated 3.2.0 candidate passed all 481 repository checks. A fresh metadata-only adoption follow-up reused the existing receipt through two transactions with zero additional completion executions, preserving the initial failure. Public 3.1.0 evidence and earlier nonpasses remain unchanged.

The package remains skills-only. No new dependency, service, credential scope, MCP server, hook, app, or checkpoint migration is introduced. Existing pinned users must explicitly update their host's marketplace reference and installed plugin after publication.

## Distribution

- Version: `3.2.0`
- Public tag: `v3.2.0`
- Asset: `nulnul-harness-3.2.0.zip`
- Product boundary: `plugins/nulnul-harness/`
- Product commit: `59d366f7df3a6f0633317d563786caa6893ec109`
- Archive: 65 files, 255,448 bytes; SHA-256 `95611e2f603c31f05d3be35b62aafa541b2ce86e93e2c27dfb050cf92f872bcb`
- [Claude adoption](../evals/benchmarks/claude-adopt/release-3.2.0-r1.json): 5/5 checks; roles and inactive entry preserved, zero protected writes
- [Meta adoption](../evals/meta-evolution/release-3.2.0-meta-r1.json): exact-public apply/skip/conflict, migration and rollback controls
- [Candidate CI](https://github.com/SeoNaRu/nulnul-harness/actions/runs/34445729753) and [tag CI](https://github.com/SeoNaRu/nulnul-harness/actions/runs/34445849457): passed
- [GitHub release](https://github.com/SeoNaRu/nulnul-harness/releases/tag/v3.2.0): final publication state and main CI record
