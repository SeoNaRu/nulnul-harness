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

One durable **session entry instruction** belongs in day-one output. Put it in the repository instruction file the detected host already loads: `AGENTS.md` for Codex or `CLAUDE.md` for Claude Code. It points to the verified checkpoint and assigns Navigator responsibility — current state, next action, permissions, and final synthesis — without requiring another agent file. Existing Claude Code agents still get classified and may be upgraded through the shared repository contract they load, but an unattended session must not create or edit `.claude/**`. Profile- or plugin-specific changes remain a manual, explicitly requested operation. Worker, Coach, and Gate stay merged until concrete evidence splits them.

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

Start from `../assets/project-contract.template.md`, remove unused optional content, and run `../scripts/validate_project_setup.py docs/nulnul/project.md`. Keep the stable headings and required fields so the next session can verify the setup without interpreting prose.

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
