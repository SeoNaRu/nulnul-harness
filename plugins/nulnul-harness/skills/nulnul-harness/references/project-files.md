# Project file contract

Create only files with a durable consumer.

## Day-one setup output

A cold project has no accepted version, no baseline, and no history for the Coach to learn from, so the first setup ships the mechanisms that make later sessions possible. Include, before any extra agent:

- a **documentation debt detector**, so a fix never stays only in code (see below);
- a **minimal frozen benchmark**, even a handful of hand-labelled cases, because a Gate without one cannot run on day one;
- the **deliverable-unit function** that defines the goal metric, plus its source of truth (see `personal-evolution.md`);
- the **single-writer lock** for any long-running loop's state file (see `data-workflow-safety.md`).

These four matter more than the agent roster. Most measured gains come from correcting an existing judgment function, not from adding another agent.

## Documentation debt detection

A fix that lands in code but not in the harness documents is knowledge the next session cannot see, and the next session is where it was needed.

- Warn when source files are newer than the harness documents that describe them. Comparing modification times in a hook is enough; a precise detector is not required.
- A false positive costs one warning line. A miss costs re-digging a hole that was already dug.

## `AGENTS.md`

Use for short repo-wide guidance that matters in most sessions:

- project purpose and canonical boundaries
- exact build, test, and verification commands
- a pointer to the detailed project contract or reusable workflow

Do not copy directory tours, temporary plans, generated capability lists, or model-specific retry advice into it.

## `docs/nulnul/project.md`

Use when the project needs a durable setup contract. Include:

- goal and current scope
- constraints and permission boundaries
- one observable completion check for the current milestone
- capability requirements and the existing candidates checked before custom work
- available capabilities versus capabilities active for the current run
- each selected capability's source, job, trigger, check, permission boundary, and removal condition
- execution topology, ownership, handoffs, and synthesis only when coordination is needed
- baseline metrics, guardrails, accepted improvements, rollback conditions, and removable assumptions
- the current verified checkpoint and a pointer to `docs/nulnul/evolution.json` when work spans sessions or agent-specific learning is enabled

Start from `../assets/project-contract.template.md` and remove unused sections.

## `docs/nulnul/evolution.json`

Create this only for multi-session work, agent-specific feedback, or personal evolution. Start from `../assets/evolution-state.template.json`. Keep the current checkpoint, agent versions, bounded feedback, proposals, and Gate decisions. Validate it with `../scripts/validate_evolution_state.py` after every update.

Keep project feedback project-local by default. Promote a rule to a user-selected private personal evolution home only after it generalizes across representative projects or the user explicitly requests that scope. Never commit a private personal-home path, raw conversation, secret, credential, personal data, or full transcript to a public repository.

## `.agents/skills/<name>/`

Create a project-local skill only when a workflow will recur and verified native, installed, curated, or suitable public skills do not adequately cover it. Record why the closest candidates were rejected. Keep the main `SKILL.md` concise; place detailed conditional material in `references/` and deterministic output templates in `assets/`.

## Agent roles and handoffs

Add durable agent roles only for concrete specialization, context isolation, independent verification, or parallel work. Give every role a distinct job and one owner final synthesis. Persist handoff files only when work must be resumable, inspectable, audited, or shared across agent boundaries.

## Existing files

Merge with user-owned instructions rather than replacing them. Preserve conflicts long enough to identify precedence. Keep generated setup easy to remove without damaging product code.
