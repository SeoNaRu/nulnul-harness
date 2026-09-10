---
name: nulnul-harness
description: Set up, inspect, or resume a project-local harness. Use for explicit harness requests, recurring work missing a usable contract, or measured capability failures. Skip ordinary edits and unrelated questions already covered by local instructions.
---

# nulnul harness

Complete the user's requested outcome with the strongest justified capability path. Quality comes first; simplicity breaks ties between materially equivalent outcomes. The user should not need to operate the harness.

## Start with the current task

Inspect a user-named task contract such as `TASK.md` before activating. If the existing inputs, outputs, constraints and runnable check already cover an ordinary task, work directly: read the relevant files, make the change, run the applicable check, inspect the result and fix attributable failures. Answer a covered read-only question directly. Do not initialize setup, enumerate capabilities or load evolution procedures for that work.

An explicit harness setup request is actionable even in an existing project; use the setup route below. Ask only for a material product or permission decision that safe inspection cannot resolve. Continue the original task after setup.

A requested product edit or instruction cleanup is ordinary development. Validate the affected behavior, required checks and document links; it does not establish a performance gain or advance a governed capability or agent version. A normal defect is repaired in its task. Repeated work or multiple sessions alone do not trigger evolution; use a concise checkpoint when continuity needs one.

## Shared boundaries

- Stay within the requested scope and existing authorization. Continue reversible local implementation and attributable repairs through verification. Obtain approval before unapproved cost, credentials, downloads, global registration, external writes, destructive operations, deployment or publication.
- Keep availability, selection, execution and verification distinct. Unknown evidence stays `unknown`; do not infer provenance from package metadata or adopt an unverified capability. Never bypass an unsafe contract or create a shadow skill.
- Preserve one writer per state file and the existing receipt owners. Codex owns `AGENTS.md`; Claude Code owns `CLAUDE.md`. Preserve the inactive entry during sequential adoption; concurrent shared-state mutation is unsupported. Unattended Claude sessions treat `.claude/**` as read-only, including attempted writes.
- Keep independent acceptance, permission boundaries, negative controls and executable rollback for governed evolution. Do not expose raw transcripts, secrets or private project memory in durable or external evidence.

## Resume fast path

Resolve `scripts/` from this skill's directory, not the target repository. Prefer the executable commands in the managed host entry.

When host-loaded guidance points to `docs/nulnul/checkpoint.json`, validate it with `python3 scripts/validate_checkpoint.py docs/nulnul/checkpoint.json` before any repository-wide inspection. If it reports `fast_path_ready: true`, the user asks for one specific task inside its goal or milestone, the named task files exist, and permissions are unchanged, enter fast path immediately. Read that checkpoint and the current task files, not the full setup contract. The entire allowed read set is this skill entry, the checkpoint, validator output, files directly needed by the requested change, and files loaded by its recorded check; any other repository listing or read is a measured fast-path failure. Do not run `rg --files`, `find`, or another repository-discovery command on this path; fall through when the named files are insufficient. Implement the task, refresh only stale checkpoint fields, then run the recorded check once through `scripts/run_checkpoint_check.py`; do not run the completion command separately or repeat either validator. Stop after that check passes. Do not load setup, discovery, assembly, or evolution references. Do not inspect deterministic validator source, re-enumerate the roster, or repeat an unchanged passing check. Fall through to the full workflow only when verification is `failed` or `unknown`, the checkpoint is missing or invalid, the task is outside its goal or milestone, required task files are absent, permissions change, or measured feedback requires evolution.

When host-loaded guidance points to a compacted `docs/nulnul/evolution.json`, run `scripts/compact_evolution_state.py docs/nulnul/evolution.json --check`, then read only the active state for ordinary resume. The check verifies the archive digest and reconstructs the full state without putting closed history into model context. Open the archive only through a targeted `--rejected-for <agent>` lookup when the Coach is about to propose a matching change. Reproduced feedback requiring a durable capability, agent or harness change falls through to governed evolution.

## Workflows on demand

Choose the relevant row; this is not a sequence of steps or a list of documents to load together.

| Current need | Read |
| --- | --- |
| Explicit setup/adoption, or recurring work with missing or materially insufficient setup | [Setup and adoption](references/setup.md) |
| Status or an operation question | [Runtime visibility](references/runtime-visibility.md) |
| Durable continuity, host-entry repair or legacy checkpoint migration | [Project files](references/project-files.md) |
| NULNUL-aware Session/Task recovery or inspected Memory work | [Foundation](references/foundation.md) |
| An uncovered capability job or a concrete quality/verification gap | [Capability discovery](references/capability-discovery.md) |
| A real producer/consumer boundary or partial rerun | [Workflow delivery](references/workflow-delivery.md) |
| Recurring persistent records or collection/sync writes | [Data workflow safety](references/data-workflow-safety.md) |
| A reproduced durable capability, agent or harness problem | [Evidence-gated evolution](references/evolution.md) |
| Explicit personal reuse or a justified transfer claim | [Personal evolution](references/personal-evolution.md) |
| Creating or adapting a skill for a demonstrated recurring gap | [Skill acceptance](references/skill-acceptance.md) |
| Preparing a justified external candidate offline | [Candidate preparation](references/external-candidate-preparation.md) |

A reproducible benchmark or live-cycle nonpass uses [the learning loop](references/meta-evolution.md#close-a-measured-learning-loop) to record linked feedback and one pending proposal. That record does not authorize evaluation, personal reuse or promotion. Personal/generalization/Meta procedures require their own justified trigger and permissions.

## Finish the task

Give each check one execution owner. Reuse a current authoritative transaction or runner result for the checks it performed. Repeat after changed inputs, a failure or a concrete unresolved concern. Run scripts without reading their implementation unless it needs diagnosis or modification.

Outside verified fast resume, source changes require `scripts/check_doc_debt.py` with the detected `--host`; update the documents it reports. Apply the target repository's required checks and only the conditional checks for the selected workflow. Fast resume keeps its exact read and check boundaries above.

Stop after the requested outcome and applicable checks pass, or report the concrete blocker. State the result, verification and next action briefly; include setup, capability or evolution details only when they help the user assess that result.
