---
name: nulnul-harness
description: Turn a project idea or recurring workflow into a minimal, personally evolving agent system. Before activating, inspect any user-named local task contract such as TASK.md; do not activate when it already provides explicit local inputs, outputs, constraints, and a runnable completion check. Use for project setup, skill or plugin selection, external-write planning, multi-session checkpointing, or evidence-gated agent evolution, and when implementation lacks a coherent repository setup or complete task contract. Inspect the repository, verify existing capabilities before creating new ones, complete the original task, and promote only independently verified improvements. Trigger on a plain setup request in any language, including "set up the harness", "하네스 세팅해줘", "하네스 구성해줘", "配置一下 harness", "设置这个项目的 harness", "ハーネスをセットアップして", and "ハーネスを構成して". Do not use for simple read-only questions or isolated work already covered by those contracts.
---

# nulnul harness

Erase process, not judgment. Let the user describe the result; absorb capability discovery, setup, coordination, and improvement behind a small, removable project-local contract.

## Product decision gate

When an empty or evidence-poor repository and a broad request leave the intended user or recurring outcome open, inspect first and then ask one concise blocking question. Do not invent the product, stack, data source, or success metric.

A request to adopt, install, or upgrade the harness in a repository that already contains work is not an open product decision. The observable result is the upgraded setup itself: an inspected capability roster, an adopted or upgraded agent team, and the project's own checks still passing. Do not ask the user what to build, and do not treat the setup request as too broad to act on.

## Required inputs

- the user's pending outcome or automation idea
- repository instructions, code, tests, package metadata, installed capabilities, and prior run evidence
- bounded user corrections, agent feedback, completion failures, and the last accepted checkpoint when they exist
- user answers only for material product, data, cost, privacy, credential, or publication decisions that safe inspection cannot reveal

## Workflow

1. Preserve the original request and define one observable result. Setup is not completion. For multi-session or personally evolving work, apply `references/personal-evolution.md` and resume from the last verified checkpoint before starting new work.
2. Inspect the repository and its existing agent instructions, project contracts, skills, plugins, tools, tests, and run evidence. Read the surface map in `references/project-files.md` first so the inspection looks in the paths this host actually uses. Then take exactly one of three modes:
   - **Fast path** — a specific task the existing setup already covers with a runnable completion check: reuse it, skip setup and capability discovery, continue the original task.
   - **Adopt and upgrade** — the repository already has agents, skills, or instructions, and the request is to adopt or extend the harness: keep what works, audit the existing roster against `references/agent-assembly.md`, and upgrade it in place. Never recreate a role that already exists.
   - **New setup** — no durable setup exists: build the smallest one from step 4 onward.
3. Apply `references/discovery-and-questions.md`. Ask only decisions that materially change the product, permission boundary, or success check.
4. Convert the requested workflow into a capability map with required inputs, outputs, quality checks, and external writes.
   - For recurring workflows that collect, classify, review, or sync records, apply `references/data-workflow-safety.md`.
5. Apply `references/capability-discovery.md`. Enumerate the host's installed skills, plugins, and agents before judging coverage; an uninspected roster is not an adequate one. Report that roster and one decision per job, including the jobs already covered. Search beyond the installed set only for uncovered jobs, using `references/capability-registry.md` for candidate sources, and stop when every uncovered job has one adequate verified candidate. Treat installed availability as discovery evidence, not verification. Inspect the local capability and verify fit, provenance, compatibility, maintenance, adoption evidence, documentation or tests, permissions, and license before calling it proven. Popularity is a signal, not proof of safety or fitness.
6. Select the smallest complete, non-overlapping capability set. Activate only what the current run needs. Context is a budget like any other: prefer the candidate that costs less context for the same job, and treat a capability that measurably reduces context or output cost across the whole session as a covered job, not an optional extra. Obtain explicit approval before downloads, global installs, plugin or MCP registration, authentication, external writes, deployment, destructive operations, or publication.
7. Apply `references/agent-assembly.md`. Prefer direct execution or one agent. Add a role only for a concrete independent job, context boundary, parallel branch, or verification need; give one owner final synthesis.
8. Apply `references/project-files.md` and the templates under `assets/` only when a durable project-local setup is missing or materially insufficient. Adapt user-owned guidance instead of overwriting it. On a new setup or adopt-and-upgrade run, read its day-one output list before judging sufficiency: an existing agent roster is not a sufficient setup when the day-one mechanisms and the session entry agent are absent, and "the team already exists" is not a reason to skip them.
9. Continue the original request. Implement or run the workflow, verify the user-visible result with the repository's real checks, and checkpoint the last verified state before a session boundary or risky transition.
10. On user correction, agent feedback, test failure, repeated workaround, or stale capability evidence, apply `references/personal-evolution.md`. Let the Coach propose one targeted change and an independent Gate reproduce, compare, promote, reject, or roll it back. Never let an agent approve its own upgrade, including the Coach or Gate.
11. For later runs, apply `references/evolution.md`. Compare a proposed change against the current baseline, keep it only when the primary metric improves without breaking guardrails, record the evidence briefly, and retain a rollback path.

## Outputs

- the user's original project outcome completed or actively progressing
- the inspected capability roster and a brief decision per job: reused, upgraded, installed with approval, or created because no adequate candidate existed
- the smallest useful agent topology and project-local contract, only when needed; when a team already existed, what was kept, upgraded, merged, or removed and why
- a resumable checkpoint and versioned agent state for multi-session or personally evolving work
- an observable result and concise verification evidence
- accepted improvements and removal or rollback conditions, without raw transcripts or secrets

## Failure handling

- Ask when missing product intent, data authority, credentials, cost limits, or publication approval would materially change the result.
- If discovery is unavailable, say which candidate sources or dimensions were not checked; label the candidate provisional and do not call it verified or proven without evidence.
- Reject candidates with unclear provenance, incompatible instructions, excessive permissions, or missing license when copying would be required.
- Record a narrow reversible assumption for non-blocking gaps and continue.
- Do not add agents to compensate for an unclear goal or an unreliable capability.
- Leave an upgrade pending when no independent Gate or reproducible check is available; do not convert feedback directly into memory or instructions.
- Roll back an evolution that worsens the primary metric, violates a guardrail, or cannot be reproduced.

## Validation

- Confirm every selected capability has a concrete job, inspectable source, activation condition, check, permission boundary, verification status, and removal condition.
- Confirm every agent role has distinct ownership, bounded inputs and outputs, a completion check, and one synthesis owner.
- Confirm feedback is bounded evidence, the Coach cannot promote its own proposal, agent versions change only through an independent Gate, permission expansion has explicit approval, and every promotion has one observed live cycle with an automatic rollback threshold.
- Confirm a custom skill was created only after adequate existing candidates were checked and rejected with reasons.
- Confirm the host's installed skills, plugins, and agents were actually enumerated, and that a setup request on a non-empty repository produced an upgraded roster rather than a question about what to build.
- Confirm no secret, personal data, raw conversation, machine-specific path, or unapproved global or external change was introduced.
- Confirm recurring data workflows use stable identity, deterministic deduplication, exclusion precedence, explicit review states, auditable reasons, idempotent writes, and spreadsheet-safe values where applicable.
- Confirm one writer per state file, a distinct `unknown` verification state, validity checks proven against a negative control, and cursors persisted even on an empty cycle.
- When `docs/nulnul/evolution.json` exists, run `scripts/validate_evolution_state.py` from this skill against it before relying on or updating the state.
- Before ending a session that changed source, run `scripts/check_doc_debt.py` from this skill and update any document it reports as stale.
- Run the target repository's real checks, verify the original result, and compare evolution changes against a recorded baseline.
