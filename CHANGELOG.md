# Changelog

All notable changes to `nulnul harness` are recorded here.

## Unreleased

- Added an adopt-and-upgrade mode so a setup request on a repository that already has work no longer asks what to build.
- Required the host's installed skills, plugins, and agents to be enumerated before coverage is judged, and reported as a roster.
- Required every existing agent to be classified as kept, upgraded, merged, or removed instead of recreated.
- Added a host surface map covering Codex and Claude Code paths, a context-cost verification dimension, and a durable session entry agent in day-one output.
- Added multilingual setup triggers to the skill description (English, Korean, Chinese, Japanese) with a deterministic test that fails if a phrase is dropped.
- Published the plugin for Claude Code: `.claude-plugin/plugin.json` and a repository-root `.claude-plugin/marketplace.json`.
- Renamed Harness 100 to Release Gate, matching what the script actually computes.
- Added `references/capability-registry.md`: where to search when the installed roster falls short, with the host marketplace commands, the sources already trusted on the machine, and named context-economy candidates.
- Fixed both halves of the gate that let an adopt run skip day-one output: step 8 judged sufficiency before reading the list, and the list described itself as belonging to a "cold project", which a repository with code and agents read as excluding itself. Measured runs delivered the `CLAUDE.md` contract and nothing else — no checkpoint, no benchmark, no debt detector.
- Added the `positive-adopt-existing-harness` and `positive-multilingual-setup-trigger` scenarios. Both passed on measured runs: the trigger fired in four languages, and the adoption run shipped every day-one mechanism with the repository's checks still green. Release Gate is back to 100/100.

## 1.2.1 — 2026-08-10

- Skip harness activation when a user-named local task contract already contains explicit inputs, outputs, constraints, and a runnable completion check.
- Preserved activation for project setup, capability selection, external writes, multi-session checkpoints, and evidence-gated evolution.
- Added reproducible 3×3 A/B evidence and two cross-task activation guards; Navigator v3 reduced median elapsed time 25.76% versus 1.2.0 without changing exact-result success or intervention rate.

## 1.2.0 — 2026-08-10

- Added equivalent English and Korean product onboarding with deterministic locale, version, command, evidence, and local-link checks.
- Added a direct fast path for repositories whose existing setup already covers the requested work, and bounded discovery to uncovered jobs.
- Fixed evolution-state validation so continuous multi-promotion history and rejected candidates remain valid while the current agent links only to its latest accepted promotion.
- Added proposal-author records and reject promotions whose declared author also serves as Gate.
- Independently gated the bilingual onboarding, fast path, and historical promotion behavior before release.

## 1.1.0 — 2026-08-10

- Added Navigator, Worker, Coach, and independent Gate responsibilities for personal agent evolution.
- Added a removable repository checkpoint for verified multi-session resume.
- Added bounded feedback, versioned proposals, promotion, rejection, and rollback contracts.
- Added a deterministic validator that rejects self-approval, invalid state, sensitive fields, and unapproved permission expansion.
- Added regression tests for Coach upgrades, independent promotion, permissions, and checkpoint validity.

## 1.0.1 — 2026-08-10

- Strengthened implicit activation when repository setup is missing or unknown.
- Added Release Gate, a weighted 100-point release gate covering six positive and three negative scenarios.
- Completed all nine isolated scenarios, including permission, secret, global-registration, and YouTube-to-Sheets checks.
- Added an offline YouTube classification and deduplication benchmark with deterministic scoring.
- Added a synthetic public YouTube-to-Sheets workbook example derived from read-only workflow structure, with no copied identity or contact data.
- Added recurring data-workflow safety rules for stable identity, deduplication, exclusion precedence, review routing, sensitive data, idempotent writes, and formula-safe spreadsheet output.
- Added the Obsidian product and experiment wiki.
- Rebuilt the public README around verified behavior, trust boundaries, and explicit limitations.

## 1.0.0 — 2026-08-10

- Initial skills-only Codex plugin.
- Added reuse-first capability discovery, minimal agent assembly, project setup, and evidence-gated evolution.
