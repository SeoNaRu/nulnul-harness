# Conditional development contracts

These are repository development invariants. Read the section matching the subsystem being changed; they are not a sequence to run for every task. The shipped skill owns project-facing workflow instructions.

## Setup and capability adoption

- Detect the host surface before writing setup files, and enumerate its installed skills, plugins, and agents before claiming a job is covered; on Claude Code adoption, first run the bounded `claude plugin list --json` command instead of inferring installed plugins from the session catalog. Treat bounded relative and fixture-local absolute `.claude/agents/` reads as roster inspection, but never credit printed paths alone. Treat Claude's `source=git` as public GitHub provenance only when the exact repository URL also matches.
- Give each host its own root session entry: Codex owns only `AGENTS.md`, Claude Code owns only `CLAUDE.md`, and both point to the same `docs/nulnul/` contract and exactly one live-state writer. On sequential host adoption, preserve the inactive entry byte-for-byte; do not claim concurrent mutation support.
- Upgrade an existing agent roster in place. Classify every existing role as kept, upgraded, merged, or removed; `reuse` is the kept classification when its profile and responsibilities stay unchanged. Setup plans encode each inspected role as `name: disposition`; the transaction rejects missing, duplicate, or unknown dispositions and writes each classification explicitly. Never recreate one that already exists.
- Reuse a verified installed capability when it is outcome-competitive. Search official, curated, and reputable public candidates for an uncovered job or concrete material quality or verification gap before creating a project-local substitute. Verify fit, provenance, compatibility, maintenance, permissions, and license; popularity alone is not verification.
- Bootstrap from a host-admitted executing plugin when no project-local contract exists; bind setup receipts to the project, host, manifest, contract, and runtime digests. Never bypass an unsafe local contract, create a shadow skill, or treat package metadata as independent publisher provenance. Cold Claude setup still requires its bounded installed-plugin listing and profile reads; setup completion requires every acceptance check, including actual shared-document updates for reported documentation debt.

## State and checkpoints

- Keep ordinary resume context bounded: compact closed evolution history into the digest-bound adjacent archive, validate deterministic full-state reconstruction, and query rejected history only when a matching proposal needs it.
- Give durable projects one validated concise resume checkpoint; keep stable setup evidence outside the host-loaded entry, and convert every reproducible nonpass verdict into Coach feedback and one bounded proposal in the same run.
- Allow fast resume only from an explicitly verified checkpoint; machine-link every nonpass verdict to its feedback and proposal, and migrate legacy durable contracts without creating a second live-state writer.
- Version concise checkpoint shapes explicitly, fail release on a missing learning-verdict inventory, and restore all earlier project files when a migration replacement fails.
- Store checkpoint completion as an exact command, execute that field before verified fast resume, and require sanitized machine-valid evidence before a paid runtime result contributes Release Gate points.

## Workflow and trace evidence

- For justified multi-stage work, check actual producer/consumer boundaries with a negative control and reuse only dependency-current verified artifacts. Keep task recipes, execution examples, skill use/skip/follow-up cases, and offline candidate preparation on demand; their advisory outputs never replace Foundation checks, grant adoption, or create another live-state writer.

Trace outcome observability uses the existing Foundation event writer and a bounded schema-versioned projection, never another live-state writer. Keep selected/loaded/checked evidence separate from availability and model claims. Require exact session binding and receipt provenance; telemetry cannot grant authority, promote a capability, prove comparative superiority, or publish private runtime data. See [trace evidence](../plugins/nulnul-harness/skills/nulnul-harness/references/trace-evidence.md). This integration candidate is not covered by frozen v3.1.0 release evidence until separately validated.

## Governed evolution and comparisons

- Keep generated setup removable. Mark a Gate-passing evolution candidate provisional while the confirmed version remains active, then use one observed live cycle and the shipped schema-v3/v4 executor to confirm it or roll it back before final validation.
- Treat evaluation exposure as state: preregister a frozen candidate before one-shot holdout use, retire every used holdout, reject leakage or recycling, compare a simple retry/selection baseline, and activate Generalization Gate only for personal/core transfer claims rather than ordinary project-local changes.
- Bound autonomous evolution before generation: one reproduced feedback item, `WHERE`/`WHY` pathology, one generation, a small candidate/evaluation/model budget, rejected-archive lookup, deterministic independent credit, sealed holdouts, permission-safe execution, a fair retry baseline on model invocations or deterministic completion checks, and an explicit stop reason including `NO_PROMOTION`.
- Treat required conflict identifiers, permission fields, and inactive-guard decisions as correctness, not optional metadata: if a bounded A/B gets any required final field wrong, reject the candidate and restore the confirmed version even when routing and cost checks pass.
- For capability-authority feedback, distinguish a missing explicit role boundary from a proven user or project decision override; keep the current capability contract when a bounded candidate has no reproducible advantage.

## Personal and cross-project reuse

- Keep personal evolution opt-in and adaptation-only: require a user-selected existing local home, preregister representative transfer plus a negative skip, let an independent Personal Gate promote or narrow, compatibility-check every new project, and fail closed on private data, missing permission, duplicate identity, conflict, stale or revoked status. Never copy raw project memory across repositories.
- Begin cross-project selection only after three independent Personal-Gate-verified mechanism families exist. Aggregate typed privacy-safe summaries inside the approved Personal Home boundary, preserve failed transfers and `unknown` relations, and never count renamed variants or cloned fixtures as independent evidence.
- Freeze one bounded meta-selection candidate before a fresh HOLDOUT, compare flat and simple baselines, retire every used case, credit only downstream apply/skip/conflict and completion results, and let an independent Meta Gate decide promotion, rejection, no advantage, narrower scope, or rollback.

## Release and publication

- Fail release on a recorded setup, workflow, activation, or fast-path regression; use version-independent champion/candidate evidence, counterbalance paired order, prefer relative budgets to absolute token ceilings, and keep fast resume inside its checkpoint and directly needed task files.
- Before pushing a version-changing commit to `main`, require exact-version public Claude adoption evidence and, when personal or cross-project reuse changes, sanitized apply/skip/revocation or Meta adoption evidence; otherwise use a non-main publication candidate first. Never knowingly leave `main` red while calling the release work complete. After any approved push, watch the resulting CI to green before reporting completion.

Public casebook examples live under `examples/`, outside the shipped plugin. Keep reference implementations, deterministic fixtures, historical adoption records, and new live-model trials explicitly distinct. The booking example's HTTP self-check belongs to the ordinary unittest suite through `tests/test_booking_service_example.py`; that check uses only local Python and loopback HTTP, not a model API. Do not turn a request for local tests into a new Claude or other paid-model experiment. Exclude unexecuted experiment drafts from publication, and preserve their unexecuted status rather than presenting them as outcome evidence.
