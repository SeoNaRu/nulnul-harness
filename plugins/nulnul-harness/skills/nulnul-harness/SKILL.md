---
name: nulnul-harness
description: Turn a project idea or recurring workflow into a minimal, personally evolving agent system. Use automatically before implementation or automation when repository setup adequacy is unknown or the project lacks coherent agent instructions or completion checks; when the user starts or builds a project; when skills or agents must be chosen; when work spans sessions; or when user corrections, agent feedback, tests, or observed failures should upgrade a specific agent or the improvement process itself. Inspect the repository, verify existing skills or plugins before creating new ones, assemble only what the work needs, complete the original task, and promote only independently verified improvements. Do not use for simple read-only questions or isolated work already covered by a coherent setup.
---

# nulnul harness

Erase process, not judgment. Let the user describe the result; absorb capability discovery, setup, coordination, and improvement behind a small, removable project-local contract.

## Product decision gate

When an empty or evidence-poor repository and a broad request leave the intended user or recurring outcome open, inspect first and then ask one concise blocking question. Do not invent the product, stack, data source, or success metric.

## Required inputs

- the user's pending outcome or automation idea
- repository instructions, code, tests, package metadata, installed capabilities, and prior run evidence
- bounded user corrections, agent feedback, completion failures, and the last accepted checkpoint when they exist
- user answers only for material product, data, cost, privacy, credential, or publication decisions that safe inspection cannot reveal

## Workflow

1. Preserve the original request and define one observable result. Setup is not completion. For multi-session or personally evolving work, apply `references/personal-evolution.md` and resume from the last verified checkpoint before starting new work.
2. Inspect the repository and its existing `AGENTS.md`, project contracts, skills, plugins, tools, tests, and run evidence. When the existing setup already covers the requested work and its completion check, take the fast path: reuse it, skip setup and capability discovery, and continue the original task.
3. Apply `references/discovery-and-questions.md`. Ask only decisions that materially change the product, permission boundary, or success check.
4. Convert the requested workflow into a capability map with required inputs, outputs, quality checks, and external writes.
   - For recurring workflows that collect, classify, review, or sync records, apply `references/data-workflow-safety.md`.
5. Apply `references/capability-discovery.md` only for uncovered jobs. Search installed and trusted existing capabilities before creating anything, and stop when every uncovered job has one adequate verified candidate. Treat installed availability as discovery evidence, not verification. Inspect the local capability and verify fit, provenance, compatibility, maintenance, adoption evidence, documentation or tests, permissions, and license before calling it proven. Popularity is a signal, not proof of safety or fitness.
6. Select the smallest complete, non-overlapping capability set. Activate only what the current run needs. Obtain explicit approval before downloads, global installs, plugin or MCP registration, authentication, external writes, deployment, destructive operations, or publication.
7. Apply `references/agent-assembly.md`. Prefer direct execution or one agent. Add a role only for a concrete independent job, context boundary, parallel branch, or verification need; give one owner final synthesis.
8. Apply `references/project-files.md` and the templates under `assets/` only when a durable project-local setup is missing or materially insufficient. Adapt user-owned guidance instead of overwriting it.
9. Continue the original request. Implement or run the workflow, verify the user-visible result with the repository's real checks, and checkpoint the last verified state before a session boundary or risky transition.
10. On user correction, agent feedback, test failure, repeated workaround, or stale capability evidence, apply `references/personal-evolution.md`. Let the Coach propose one targeted change and an independent Gate reproduce, compare, promote, reject, or roll it back. Never let an agent approve its own upgrade, including the Coach or Gate.
11. For later runs, apply `references/evolution.md`. Compare a proposed change against the current baseline, keep it only when the primary metric improves without breaking guardrails, record the evidence briefly, and retain a rollback path.

## Outputs

- the user's original project outcome completed or actively progressing
- a brief capability decision: reused, installed with approval, or created because no adequate candidate existed
- the smallest useful agent topology and project-local contract, only when needed
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
- Confirm feedback is bounded evidence, the Coach cannot promote its own proposal, agent versions change only through an independent Gate, and permission expansion has explicit approval.
- Confirm a custom skill was created only after adequate existing candidates were checked and rejected with reasons.
- Confirm no secret, personal data, raw conversation, machine-specific path, or unapproved global or external change was introduced.
- Confirm recurring data workflows use stable identity, deterministic deduplication, exclusion precedence, explicit review states, auditable reasons, idempotent writes, and spreadsheet-safe values where applicable.
- When `docs/nulnul/evolution.json` exists, run `scripts/validate_evolution_state.py` from this skill against it before relying on or updating the state.
- Run the target repository's real checks, verify the original result, and compare evolution changes against a recorded baseline.
