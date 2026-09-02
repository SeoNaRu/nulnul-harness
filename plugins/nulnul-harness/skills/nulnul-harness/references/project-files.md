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
| Foundation records | `docs/nulnul/memory/`; local raw evidence in ignored `docs/nulnul/.runtime/` | same host-independent durable records; host evidence may be less complete |
| Current Agent topology when evolved | `docs/nulnul/agent-topology.json`; history in `docs/nulnul/memory/agent-topologies/` | same host-independent topology contract |
| Current Harness controls when evolved | `docs/nulnul/harness-controls.json`; history in `docs/nulnul/memory/harness-controls/` | same host-independent declarative policy contract |
| Host configuration and hooks | host settings | `.claude/settings.json`, or `~/.claude/settings.json` for user scope; inspect only |
| Installed capabilities to enumerate | installed skills and plugins | session skill and agent listings, `.claude/`, `~/.claude/plugins/` |

Treat a path that does not exist on the detected host as not applicable, not as a missing file to create. Presence does not imply write authority: Claude Code's `.claude/**` tree is a discovery surface, not an unattended write target. Do not probe that boundary by attempting a write. Put generated Claude Code setup in repository-owned guidance, `docs/nulnul/`, or another existing product path instead.

The root entries are peers, not copies and not shared writers. A Codex run never creates or edits `CLAUDE.md`; a Claude Code run never creates or edits `AGENTS.md`. When both hosts are used sequentially, each entry points to the same shared `docs/nulnul/project.md` and exactly one checkpoint or evolution state. A host switch changes the new active host entry only. Concurrent sessions need separate coordination evidence and are outside this contract.

## Day-one setup output

A cold project has no accepted version or history for the Coach to learn from. Bootstrap the initial conditions in `meta-evolution.md`, add every mechanism whose concrete job materially improves the expected verified outcome, and omit the rest. Coldness is about evidence, not age, and does not justify speculative infrastructure.

Include, before any extra agent:

- a **documentation debt detector** when source and durable agent guidance evolve together — `../scripts/check_doc_debt.py` ships with this skill;
- a **minimal frozen benchmark** when the workflow repeats judgement or will evaluate competing versions;
- one **deliverable-unit function** when recurring work is counted toward a target (see `personal-evolution.md`);
- a **single-writer lock** when a long-running or concurrent loop mutates shared state (see `data-workflow-safety.md`).

Record an omitted mechanism as `not applicable` with one reason. The Coach may add it later when a live run reveals the job; that evidence-driven construction is part of the meta-harness rather than a setup failure. These mechanisms matter more than a large agent roster when their jobs exist.

One durable **session entry instruction** and one concise checkpoint belong in day-one output. Put the instruction in the repository file the detected host already loads: `AGENTS.md` for Codex or `CLAUDE.md` for Claude Code. For `new-setup` or `adopt-upgrade`, give the exact Governed receipt and one bounded Setup Plan to `../scripts/setup_transaction.py`; it writes and validates the project contract, accepted rows, active entry, checkpoint, and verification receipt as one rollback-safe unit. Pre-session Capability Packs require no activation rule, trust mutation, or capability-only restart. Do not hand-author those files or write the inactive host entry. The checkpoint owns only the current goal, milestone, completion check, bounded verification files, explicit verification status, last verified result, next action, permission constraints and approvals, and blockers; `project.md` keeps stable setup evidence and does not duplicate those live fields. The completion runner alone owns the sibling verification receipt. When `evolution.json` already owns the checkpoint, the Setup transaction fails rather than creating a second writer. Existing Claude Code agents still get classified and may be upgraded through shared repository guidance, but an unattended session must not create or edit `.claude/**`. Worker, Coach, and Gate stay merged until concrete evidence splits them.

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

The `Accepted capabilities` table is the single machine-readable acceptance source. New Setup and Adopt schema-v2 plans pass accepted IDs plus project-specific semantic facts; `../scripts/setup_transaction.py` derives `accepted/current` and the exact host-independent `capabilities/ID/SKILL.md` logical target before it writes anything. `.agents/skills/ID/SKILL.md` is a host materialization path, not an accepted logical target. A separate governed capability-table update may use `../scripts/capability_contract.py write docs/nulnul/project.md --rows ROWS.json`, followed by the project setup validator; mismatched or legacy targets fail rather than normalize. An evidence-triggered `../scripts/natural_selection.py` transaction is the only other capability-table writer: it preserves the same target contract while changing validated lifecycle status/digests atomically. The bounded view, pre-session Pack construction, Memory references, and later Evolution consume the same canonical row and must not reinterpret `Candidate evidence` prose independently. Only `accepted/current` rows enter Pack selection.

## `docs/nulnul/checkpoint.json`

Use the concise checkpoint for durable projects that do not need agent-specific feedback or promotion history. New checkpoints use schema version 3. Versions 1 and 2 remain readable for migration but cannot take the fast path; unknown future versions fail validation. Start from `../assets/checkpoint.template.json`, give `checkpoint.json` one Navigator writer, record `completion_check` as the exact repository command, and list only the relative files whose state that check verifies. Run the command through `../scripts/run_checkpoint_check.py`; it is the sole writer of `checkpoint.verification.json`, a bounded receipt containing only status, file names, and a SHA-256 state fingerprint. Never edit that receipt directly. Fast resume requires schema-version-3 `verified`, a verified receipt over the same file list, and a current fingerprint match. `failed`, `unknown`, missing evidence, and stale evidence remain valid diagnostic states that fall through to the full workflow. Session entry files point here so ordinary continuation does not reload the full roster and setup evidence. Remove both checkpoint files when continuity is no longer needed; replace them with `evolution.json`, rather than duplicating them, when governed agent evolution begins.

For a legacy durable setup, run `../scripts/migrate_legacy_checkpoint.py docs/nulnul/project.md AGENTS.md` on Codex or use the detected root `CLAUDE.md` on Claude Code. The migrator uses the same managed host-entry block, never writes the inactive root entry or `.claude/**`, and skips when `evolution.json` already owns live state. It preserves legacy contract values and permission constraints, creates schema version 3 as `unknown`, and updates only the active session entry. Add the bounded verification file list, then run the recorded completion check to create verified evidence. All target files are prepared before replacement; if any replacement fails, earlier replacements are restored.

## `docs/nulnul/evolution.json`

Create this only for multi-session work, agent-specific feedback, or personal evolution. Start from `../assets/evolution-state.template.json`. Keep the current checkpoint, confirmed and provisional agent versions, bounded feedback, proposals, and Gate decisions. Validate it with `../scripts/validate_evolution_state.py` after every update.

After terminal decisions accumulate, run `../scripts/compact_evolution_state.py docs/nulnul/evolution.json`. The active file keeps open work and the latest accepted rollback point per agent; the adjacent `evolution.archive.json` keeps full closed records behind a digest. Validate both with `--check`, keep the archive out of normal resume context, and use `--rejected-for <agent>` for bounded replay checks. The compactor is the only writer of the archive and updates active state plus archive as one rollback-safe batch.

Keep project feedback project-local by default. Promote a rule to a user-selected private personal evolution home only after it passes preregistered representative transfer checks and an independent Personal Gate. The home must be an existing local directory explicitly selected by the user; otherwise fail with `PERSONAL_HOME_REQUIRED`. Use `../scripts/personal_adaptation.py` to validate, promote, discover, deduplicate, or revoke generalized adaptations. Never commit a private personal-home path, source code, raw conversation, secret, credential, personal data, full transcript, or project identity to a public repository.

Cross-project Foundation learning reuses that same approved home. `../scripts/generalization_core.py` is the sole writer of `generalizations.json`; it stores privacy-safe abstract Candidates, Transferable priors, target validations, counterevidence, and lifecycle lineage, never project Memory or source paths. A project-local setup must not create its own copy or load the registry on ordinary Direct work. The frozen `cross_project_evolution.py` keeps ownership of the historical Meta selector and its exact public evidence.

## `docs/nulnul/memory/`

Initialize lazily through `../scripts/foundation_runtime.py`; absence is not setup or checkpoint corruption. The Foundation runtime is the sole writer for finalized Sessions, Experiences, Decisions, Lessons, Open Threads, handoff, and the active index. `project.md` remains stable truth and checkpoint remains current position. Local active state, lock, ordered events, and raw transcripts live only in ignored `docs/nulnul/.runtime/`.

Read `foundation.md` for the canonical Layer Map, ownership registry, Context Pack budgets, provenance rules, lifecycle, inspection commands, and Evolution-input boundary. Do not load it during ordinary no-fit Direct work.

Triggered external competition keeps frozen source bytes, normalized manifests, competition receipts, and outcomes under ignored `docs/nulnul/.runtime/external-competition/`. This is local execution/audit state, not durable project truth or ordinary Memory. Its quarantine paths never enter the accepted-capability table or Pack lookup. Only the existing Natural Selection transaction may copy a verified licensed survivor into the canonical project-local capability materialization; durable Memory stores bounded source/digest/decision provenance, never the candidate body or machine-specific source path.

## `docs/nulnul/agent-topology.json`

Absence means the implicit `SINGLE_AGENT` Foundation topology and is valid. Create this machine-critical current topology only through a successful `../scripts/agent_evolution.py` lifecycle transaction. It binds Agent contracts, sorted delegation edges, Pack requirements, synthesis and verification owners, version, digest, and source Decision lineage. Prior topologies remain under `memory/agent-topologies/<digest>.json`; do not delete their Experiences or rewrite their digests.

Frozen Topology Challengers, competition receipts, per-Agent Pack bindings, and Agent handoffs stay in ignored `.runtime/agent-evolution/`. Agent handoffs are execution evidence, not Session handoff or durable project truth. Durable lifecycle decisions use the existing `memory/decisions.jsonl`; do not create a second Agent history database. Ordinary Direct tasks neither materialize the implicit topology nor load Agent Evolution instructions or catalogs.

## `docs/nulnul/harness-controls.json`

Absence means the shipped five-control Champion in `assets/harness-controls.json` and is valid. Create current project policy only through a successful `../scripts/harness_evolution.py` transaction. The registry stores declarative control contracts and bounded policy values; it does not grant authority and cannot change the guarded Kernel digest. Prior registries remain under `memory/harness-controls/<digest>.json`, while the existing `memory/decisions.jsonl` owns bounded lifecycle provenance.

Harness Experience remains an attributed Foundation Experience linked to its real Pack/Check evidence. Frozen control Challengers, safety receipts, and competitions stay in ignored `.runtime/harness-evolution/`; they are not Memory or ordinary Context. No control registry, Challenger, or competition history enters an ordinary Direct model context. Harness Evolution itself, its evidence rules, safety gate, transaction, rollback, and provenance verifier are outside first-order control evolution.

## Pre-session Capability Pack and retired Codex rule

`../scripts/capability_pack.py` creates ignored execution-scoped Packs from canonical accepted rows before product work. Selection sees only bounded metadata; work context receives only selected bodies. Pack construction needs no Codex project rule, trust change, restart, or privileged runtime command, and grants no write authority.

`.codex/rules/nulnul-activation.rules` belongs only to the retired runtime-exclusive architecture. New Setup does not create it. Explicit Adopt/teardown may call `../scripts/sync_host_entry.py codex --root . --retire-runtime-activation`; cleanup removes only the frozen known digest, fails closed on a foreign rule, and never changes Codex trust. Ordinary work never silently migrates or removes it.

## `.agents/skills/<name>/`

Create a project-local skill only when a workflow will recur, a material outcome or verification gap exists, and verified native, installed, curated, or suitable public skills are not outcome-competitive. Record why the closest candidates were rejected. Keep the main `SKILL.md` concise; place detailed conditional material in `references/` and deterministic output templates in `assets/`.

In an unattended Claude Code session, keep the equivalent reusable workflow under `docs/nulnul/workflows/` and reference it from `CLAUDE.md`; do not write `.claude/skills/**`. Installing it as a host-native skill is a separate manual action that requires an explicit user request.

## Agent roles and handoffs

Add durable agent roles only for concrete specialization, context isolation, independent verification, or parallel work. Give every role a distinct job and one owner final synthesis. Persist handoff files only when work must be resumable, inspectable, audited, or shared across agent boundaries.

## Existing files

Merge with user-owned instructions rather than replacing them. Preserve conflicts long enough to identify precedence. Keep generated setup easy to remove without damaging product code.
