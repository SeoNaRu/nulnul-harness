# Project file contract

Create only files with a durable consumer.

## Surface map

The file names below are the Codex layout. Detect the host before inspecting or writing, and use its paths; writing Codex paths into a Claude Code project produces a setup nothing loads.

| Role | Codex | Claude Code |
| --- | --- | --- |
| Repo-wide instructions | `AGENTS.md` | `CLAUDE.md` (a repository may keep both; `AGENTS.md` stays canonical here and `CLAUDE.md` points at it) |
| Project-local workflow | `.agents/skills/<name>/` | `docs/nulnul/workflows/<name>.md`, referenced from `CLAUDE.md` |
| Existing agent definitions to inspect | project contract roles | `.claude/agents/<name>.md` with YAML frontmatter; read-only in unattended sessions |
| Session entry | `AGENTS.md` points to the verified checkpoint | `CLAUDE.md` points to the verified checkpoint |
| Host configuration and hooks | host settings | `.claude/settings.json`, or `~/.claude/settings.json` for user scope; inspect only |
| Installed capabilities to enumerate | installed skills and plugins | session skill and agent listings, `.claude/`, `~/.claude/plugins/` |

Treat a path that does not exist on the detected host as not applicable, not as a missing file to create. Presence does not imply write authority: Claude Code's `.claude/**` tree is a discovery surface, not an unattended write target. Do not probe that boundary by attempting a write. Put generated Claude Code setup in repository-owned guidance, `docs/nulnul/`, or another existing product path instead.

## Day-one setup output

A cold project has no accepted version or history for the Coach to learn from. Bootstrap the initial conditions in `meta-evolution.md`, then add only the mechanisms whose jobs the inspected workflow already exposes. Coldness is about evidence, not age, but it does not justify speculative infrastructure.

Include, before any extra agent:

- a **documentation debt detector** when source and durable agent guidance evolve together — `../scripts/check_doc_debt.py` ships with this skill;
- a **minimal frozen benchmark** when the workflow repeats judgement or will evaluate competing versions;
- one **deliverable-unit function** when recurring work is counted toward a target (see `personal-evolution.md`);
- a **single-writer lock** when a long-running or concurrent loop mutates shared state (see `data-workflow-safety.md`).

Record an omitted mechanism as `not applicable` with one reason. The Coach may add it later when a live run reveals the job; that evidence-driven construction is part of the meta-harness rather than a setup failure. These mechanisms matter more than a large agent roster when their jobs exist.

One durable **session entry instruction** and one concise checkpoint belong in day-one output. Put the instruction in the repository file the detected host already loads: `AGENTS.md` for Codex or `CLAUDE.md` for Claude Code. For a project without agent-specific evolution, create `docs/nulnul/checkpoint.json` from `assets/checkpoint.template.json`, validate it, and point the session entry there rather than at the full setup contract. The checkpoint owns only the current goal, milestone, completion check, explicit verification status, last verified result, next action, permission constraints and approvals, and blockers; `project.md` keeps stable setup evidence and does not duplicate those live fields. When `evolution.json` already owns the checkpoint, do not create a second writer. Existing Claude Code agents still get classified and may be upgraded through shared repository guidance, but an unattended session must not create or edit `.claude/**`. Worker, Coach, and Gate stay merged until concrete evidence splits them.

## Documentation debt detection

A fix that lands in code but not in the harness documents is knowledge the next session cannot see, and the next session is where it was needed.

- Warn when source files are newer than the harness documents that describe them. Comparing modification times is enough; a precise detector is not required.
- A false positive costs one warning line. A miss costs re-digging a hole that was already dug.

Run the shipped detector instead of writing one:

```bash
python3 ../scripts/check_doc_debt.py .                       # AGENTS.md, CLAUDE.md, docs/nulnul/project.md, README.md
python3 ../scripts/check_doc_debt.py . --document AGENTS.md  # narrow it to one document
```

It exits non-zero when a listed document is older than the newest tracked source file, so it works as a pre-push hook or a final check before ending a session.

## `AGENTS.md`

Use for short repo-wide guidance that matters in most sessions:

- project purpose and canonical boundaries
- exact build, test, and verification commands
- a pointer to `docs/nulnul/checkpoint.json` when it exists, otherwise the active evolution checkpoint or detailed project contract

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
- a pointer to the active checkpoint without duplicating its live fields

Start from `../assets/project-contract.template.md`, remove unused optional content, and run the currently loaded skill's `scripts/validate_project_setup.py` against `docs/nulnul/project.md`. Do not record the installed skill's machine-specific path. Keep the stable headings and required fields so the next session can verify the setup without interpreting prose.

## `docs/nulnul/checkpoint.json`

Use the concise checkpoint for durable projects that do not need agent-specific feedback or promotion history. Start from `../assets/checkpoint.template.json`, give it one Navigator writer, and validate it with `../scripts/validate_checkpoint.py`. Only `verification_status: verified` may take the resume fast path; `failed` and `unknown` are valid diagnostic states that fall through to the full workflow. Session entry files point here so ordinary continuation does not reload the full roster and setup evidence. Remove it when continuity is no longer needed; replace it with `evolution.json`, rather than duplicating it, when governed agent evolution begins.

For a pre-1.3.2 durable setup, run `../scripts/migrate_legacy_checkpoint.py docs/nulnul/project.md AGENTS.md` or use the detected root `CLAUDE.md` instead. The migrator never writes under `.claude/**` and skips when `evolution.json` already owns live state. It preserves legacy contract values and permission constraints, creates an `unknown` checkpoint for 1.3.0 contracts or fills only the missing safety fields in a 1.3.1 checkpoint, and updates the existing session entry. Run the recorded completion check before marking it `verified`.

## `docs/nulnul/evolution.json`

Create this only for multi-session work, agent-specific feedback, or personal evolution. Start from `../assets/evolution-state.template.json`. Keep the current checkpoint, agent versions, bounded feedback, proposals, and Gate decisions. Validate it with `../scripts/validate_evolution_state.py` after every update.

Keep project feedback project-local by default. Promote a rule to a user-selected private personal evolution home only after it generalizes across representative projects or the user explicitly requests that scope. Never commit a private personal-home path, raw conversation, secret, credential, personal data, or full transcript to a public repository.

## `.agents/skills/<name>/`

Create a project-local skill only when a workflow will recur and verified native, installed, curated, or suitable public skills do not adequately cover it. Record why the closest candidates were rejected. Keep the main `SKILL.md` concise; place detailed conditional material in `references/` and deterministic output templates in `assets/`.

In an unattended Claude Code session, keep the equivalent reusable workflow under `docs/nulnul/workflows/` and reference it from `CLAUDE.md`; do not write `.claude/skills/**`. Installing it as a host-native skill is a separate manual action that requires an explicit user request.

## Agent roles and handoffs

Add durable agent roles only for concrete specialization, context isolation, independent verification, or parallel work. Give every role a distinct job and one owner final synthesis. Persist handoff files only when work must be resumable, inspectable, audited, or shared across agent boundaries.

## Existing files

Merge with user-owned instructions rather than replacing them. Preserve conflicts long enough to identify precedence. Keep generated setup easy to remove without damaging product code.
