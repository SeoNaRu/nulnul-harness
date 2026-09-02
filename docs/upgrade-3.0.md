# Upgrade to NULNUL 3.0

NULNUL 3.0 keeps the plugin skills-only and preserves project-local state. Upgrade
the plugin, start a fresh host session, and let explicit Setup/Adopt validate any
durable project contract before normal work resumes.

## Upgrade

Codex:

```bash
codex plugin marketplace upgrade nulnul-harness
codex plugin remove nulnul-harness@nulnul-harness
codex plugin add nulnul-harness@nulnul-harness
```

Claude Code:

```bash
claude plugin marketplace update nulnul-harness
claude plugin update nulnul-harness@nulnul-harness
```

Start a fresh Codex or Claude Code process after the update. Sequential host use is
supported; concurrent mutation of shared `docs/nulnul/` state is not.

## What changes

- Capability bodies are selected before the work session through a bounded
  Capability Pack. The retired Codex runtime-unlock rule, capability-specific trust,
  and activation restart are no longer part of normal execution.
- Sessions, checks, Experiences, Memory, lifecycle Decisions, and provenance are
  automatic when durable Foundation work applies. Clear Direct work stays body-free
  and does not load those schemas.
- External candidates remain quarantined, and cross-project knowledge remains a
  privacy-safe prior until the target project verifies it.

## Existing project state

- Existing `project.md`, verified checkpoints, evolution history, and project Memory
  stay project-local.
- Legacy checkpoint schemas are readable but must migrate and verify before fast
  resume. The shipped migration transaction restores earlier files if replacement
  fails.
- A known retired `.codex/rules/nulnul-activation.rules` file is removed only by an
  explicit Adopt/teardown operation. Foreign rules and Codex trust are never changed.
- Older personal or cross-project summaries do not automatically become current 3.0
  Generalization evidence.

## Verify after upgrade

Ask NULNUL to inspect the repository and continue one normal task. Confirm that it:

1. preserves the inactive host entry and any user-owned guidance;
2. uses exactly one durable state writer;
3. runs the project's authoritative completion check;
4. creates no activation rule or trust mutation;
5. keeps raw transcripts and project Memory out of cross-project knowledge.

## Roll back

Reinstall the previous plugin version and restore the project-state backup taken
before migration. Do not force an older runtime to interpret a newly migrated state
shape. Plugin removal does not delete project-local `docs/nulnul/` state.
