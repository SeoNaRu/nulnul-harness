---
name: project-harness
description: Prepare and evolve a repository-local agent setup, then continue the user's original work. Use automatically before implementation when a project lacks coherent agent instructions or completion checks; when the user asks to start, set up, or build a project; or when repeated failures, tests, workarounds, or user corrections show that the existing setup should change. Inspect before asking and do not use for simple read-only questions or when the existing project setup already covers the request.
---

# Project Harness

Make project preparation an invisible preflight. Never require the user to understand or operate a harness.

## Product decision gate

When the repository has no reliable product evidence and the request leaves the intended user or product outcome open, stop after one concise blocking question. Do not invent a product, choose a stack, create files, or activate downstream build or design skills until the user answers. This gate takes precedence over another skill's permission to fill in an unspecified brief.

## Required inputs

- the user's pending request
- the target repository's code, documentation, tests, instructions, and tool configuration
- user answers only for material decisions the repository cannot reveal

## Workflow

1. Preserve the pending request so setup leads back to it.
2. Audit the repository. Read applicable `AGENTS.md` files, code, docs, tests, package metadata, local skills, and project configuration. If the setup is coherent and sufficient, reuse it and continue at step 8.
3. Define the immediate outcome, non-negotiable constraints, and one observable completion check from discovered evidence.
4. Identify only the unknown decisions that would materially change the work. Follow `references/discovery-and-questions.md`; apply the product decision gate before selecting downstream skills, ask one small batch, and use narrow, reversible assumptions only for non-blocking gaps.
5. Select the smallest complete project setup:
   - keep stable repo-wide `WHAT / WHY / HOW` and pointers in a short `AGENTS.md`
   - keep detailed goal, scope, constraints, permissions, routing, checks, assumptions, and evolution signals in `docs/harness/project.md` or an existing equivalent
   - add a project-local skill or agent role only for a necessary reusable job
   - include every necessary non-overlapping capability, while activating only those relevant to the current task
   - choose direct, single-agent, multi-agent, or hybrid execution from the actual work boundaries
6. Apply the setup using `references/project-files.md` and the templates under `assets/`. Adapt existing files instead of overwriting user-owned guidance.
7. Keep authority with the user. Make reversible repository-local changes, but obtain explicit approval before credentials, global installs, MCP or plugin registration, external writes, deployment, destructive operations, or publication.
8. Continue the pending request immediately. Do not stop after producing setup files.
9. Run the repository's real checks and verify both the setup and the requested work through an observable result.
10. On later work, follow `references/evolution.md` and change the nearest durable layer only when evidence justifies it.

## Outputs

- the original request completed or actively progressing
- a small, coherent project-local setup only when one was missing or insufficient
- a concise note about user-relevant preparation, without requiring harness terminology
- durable evidence for material setup changes, without raw transcripts or secrets

## Failure handling

- Ask when a missing product or permission decision would materially change the result.
- Record a removable assumption and continue when a detail is non-blocking.
- Repair invalid setup before relying on it.
- Preserve conflicting user-owned guidance until the authoritative source is clear.
- Report missing validation or unsupported capabilities instead of pretending setup succeeded.

## Validation

- Confirm every created path and internal reference exists.
- Confirm each added capability or agent has a concrete job, activation condition, check, and removal condition.
- Confirm no secret, raw conversation, machine-specific path, or automatic global registration was introduced.
- Run the target repository's checks and verify the original request's completion condition.
