# Project file contract

Create only files with a durable consumer.

## Surface map

The file names below are the Codex layout. Detect the host before inspecting or writing, and use its paths; writing Codex paths into a Claude Code project produces a setup nothing loads.

| Role | Codex | Claude Code |
| --- | --- | --- |
| Repo-wide instructions | `AGENTS.md`, owned by Codex | `CLAUDE.md`, owned by Claude Code |
| Project-local workflow | `.agents/skills/<name>/` | `docs/nulnul/workflows/<name>.md`, referenced from `CLAUDE.md` |
| Existing agent definitions to inspect | project contract roles | `.claude/agents/<name>.md` with YAML frontmatter; read-only in unattended sessions |
| Session entry | `AGENTS.md` points to the verified checkpoint | `CLAUDE.md` points to the verified checkpoint |
| Host configuration and hooks | host settings | `.claude/settings.json`, or `~/.claude/settings.json` for user scope; inspect only |
| Installed capabilities to enumerate | installed skills and plugins | session skill and agent listings, `.claude/`, `~/.claude/plugins/` |

Treat a path that does not exist on the detected host as not applicable, not as a missing file to create. Presence does not imply write authority: Claude Code's `.claude/**` tree is a discovery surface, not an unattended write target. Do not probe that boundary by attempting a write. Put generated Claude Code setup in repository-owned guidance, `docs/nulnul/`, or another existing product path instead.

The root entries are peers, not copies and not shared writers. A Codex run never creates or edits `CLAUDE.md`; a Claude Code run never creates or edits `AGENTS.md`. When both hosts are used sequentially, each entry points to the same shared `docs/nulnul/project.md` and exactly one checkpoint or evolution state. A host switch changes the new active host entry only. Concurrent sessions need separate coordination evidence and are outside this contract.

## Day-one setup output

A cold project has no accepted version or history for the Coach to learn from. Bootstrap the initial conditions in `meta-evolution.md`, then add only the mechanisms whose jobs the inspected workflow already exposes. Coldness is about evidence, not age, but it does not justify speculative infrastructure.

Include, before any extra agent:

- a **documentation debt detector** when source and durable agent guidance evolve together — `../scripts/check_doc_debt.py` ships with this skill;
- a **minimal frozen benchmark** when the workflow repeats judgement or will evaluate competing versions;
- one **deliverable-unit function** when recurring work is counted toward a target (see `personal-evolution.md`);
- a **single-writer lock** when a long-running or concurrent loop mutates shared state (see `data-workflow-safety.md`).

Record an omitted mechanism as `not applicable` with one reason. The Coach may add it later when a live run reveals the job; that evidence-driven construction is part of the meta-harness rather than a setup failure. These mechanisms matter more than a large agent roster when their jobs exist.

One durable **session entry instruction** and one concise checkpoint belong in day-one output. Put the instruction in the repository file the detected host already loads: `AGENTS.md` for Codex or `CLAUDE.md` for Claude Code. For a project without agent-specific evolution, create `docs/nulnul/checkpoint.json` from `assets/checkpoint.template.json`, validate it, then run `../scripts/sync_host_entry.py <codex|claude> --root .`; do not write the inactive host entry. The checkpoint owns only the current goal, milestone, completion check, bounded verification files, explicit verification status, last verified result, next action, permission constraints and approvals, and blockers; `project.md` keeps stable setup evidence and does not duplicate those live fields. The completion runner alone owns the sibling verification receipt. When `evolution.json` already owns the checkpoint, do not create a second writer. Existing Claude Code agents still get classified and may be upgraded through shared repository guidance, but an unattended session must not create or edit `.claude/**`. Worker, Coach, and Gate stay merged until concrete evidence splits them.

## Documentation debt detection

A fix that lands in code but not in the harness documents is knowledge the next session cannot see, and the next session is where it was needed.

- Warn when source files are newer than the harness documents that describe them. Comparing modification times is enough; a precise detector is not required.
- A false positive costs one warning line. A miss costs re-digging a hole that was already dug.

Run the shipped detector instead of writing one:

```bash
python3 ../scripts/check_doc_debt.py . --host codex           # AGENTS.md plus shared documents
python3 ../scripts/check_doc_debt.py . --host claude          # CLAUDE.md plus shared documents
python3 ../scripts/check_doc_debt.py . --document AGENTS.md   # narrow it to one document
```

The active-host option excludes the inactive root entry. Dirty working-tree documents take precedence over commit order, so a document already updated in the current change is not falsely reported as stale; dirty source with a clean document is still reported. The command exits non-zero when a listed document is older than the newest source file, so it works as a pre-push hook or a final check before ending a session.

## Root host entries

Use `AGENTS.md` for Codex and `CLAUDE.md` for Claude Code. Keep each entry short:

- identify its owning host;
- point to the stable shared project contract;
- point to the single active checkpoint or evolution state;
- forbid modifying the other host entry.

Do not copy one host entry into the other or duplicate directory tours, temporary plans, generated capability lists, live checkpoint values, or model-specific retry advice. Keep shared repository truth in `docs/nulnul/`.

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

Use the concise checkpoint for durable projects that do not need agent-specific feedback or promotion history. New checkpoints use schema version 3. Versions 1 and 2 remain readable for migration but cannot take the fast path; unknown future versions fail validation. Start from `../assets/checkpoint.template.json`, give `checkpoint.json` one Navigator writer, record `completion_check` as the exact repository command, and list only the relative files whose state that check verifies. Run the command through `../scripts/run_checkpoint_check.py`; it is the sole writer of `checkpoint.verification.json`, a bounded receipt containing only status, file names, and a SHA-256 state fingerprint. Never edit that receipt directly. Fast resume requires schema-version-3 `verified`, a verified receipt over the same file list, and a current fingerprint match. `failed`, `unknown`, missing evidence, and stale evidence remain valid diagnostic states that fall through to the full workflow. Session entry files point here so ordinary continuation does not reload the full roster and setup evidence. Remove both checkpoint files when continuity is no longer needed; replace them with `evolution.json`, rather than duplicating them, when governed agent evolution begins.

For a legacy durable setup, run `../scripts/migrate_legacy_checkpoint.py docs/nulnul/project.md AGENTS.md` on Codex or use the detected root `CLAUDE.md` on Claude Code. The migrator uses the same managed host-entry block, never writes the inactive root entry or `.claude/**`, and skips when `evolution.json` already owns live state. It preserves legacy contract values and permission constraints, creates schema version 3 as `unknown`, and updates only the active session entry. Add the bounded verification file list, then run the recorded completion check to create verified evidence. All target files are prepared before replacement; if any replacement fails, earlier replacements are restored.

## `docs/nulnul/evolution.json`

Create this only for multi-session work, agent-specific feedback, or personal evolution. Start from `../assets/evolution-state.template.json`. Keep the current checkpoint, confirmed and provisional agent versions, bounded feedback, proposals, and Gate decisions. Validate it with `../scripts/validate_evolution_state.py` after every update.

After terminal decisions accumulate, run `../scripts/compact_evolution_state.py docs/nulnul/evolution.json`. The active file keeps open work and the latest accepted rollback point per agent; the adjacent `evolution.archive.json` keeps full closed records behind a digest. Validate both with `--check`, keep the archive out of normal resume context, and use `--rejected-for <agent>` for bounded replay checks. The compactor is the only writer of the archive and updates active state plus archive as one rollback-safe batch.

Keep project feedback project-local by default. Promote a rule to a user-selected private personal evolution home only after it passes preregistered representative transfer checks and an independent Personal Gate. The home must be an existing local directory explicitly selected by the user; otherwise fail with `PERSONAL_HOME_REQUIRED`. Use `../scripts/personal_adaptation.py` to validate, promote, discover, deduplicate, or revoke generalized adaptations. Never commit a private personal-home path, source code, raw conversation, secret, credential, personal data, full transcript, or project identity to a public repository.

## `.agents/skills/<name>/`

Create a project-local skill only when a workflow will recur and verified native, installed, curated, or suitable public skills do not adequately cover it. Record why the closest candidates were rejected. Keep the main `SKILL.md` concise; place detailed conditional material in `references/` and deterministic output templates in `assets/`.

In an unattended Claude Code session, keep the equivalent reusable workflow under `docs/nulnul/workflows/` and reference it from `CLAUDE.md`; do not write `.claude/skills/**`. Installing it as a host-native skill is a separate manual action that requires an explicit user request.

## Agent roles and handoffs

Add durable agent roles only for concrete specialization, context isolation, independent verification, or parallel work. Give every role a distinct job and one owner final synthesis. Persist handoff files only when work must be resumable, inspectable, audited, or shared across agent boundaries.

## Existing files

Merge with user-owned instructions rather than replacing them. Preserve conflicts long enough to identify precedence. Keep generated setup easy to remove without damaging product code.
