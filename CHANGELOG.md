# Changelog

All notable changes to `nulnul harness` are recorded here.

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
- Added Harness 100, a weighted 100-point release gate covering six positive and three negative scenarios.
- Completed all nine isolated scenarios, including permission, secret, global-registration, and YouTube-to-Sheets checks.
- Added an offline YouTube classification and deduplication benchmark with deterministic scoring.
- Added a synthetic public YouTube-to-Sheets workbook example derived from read-only workflow structure, with no copied identity or contact data.
- Added recurring data-workflow safety rules for stable identity, deduplication, exclusion precedence, review routing, sensitive data, idempotent writes, and formula-safe spreadsheet output.
- Added the Obsidian product and experiment wiki.
- Rebuilt the public README around verified behavior, trust boundaries, and explicit limitations.

## 1.0.0 — 2026-08-10

- Initial skills-only Codex plugin.
- Added reuse-first capability discovery, minimal agent assembly, project setup, and evidence-gated evolution.
