# Project file contract

Create only files with a durable consumer.

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
