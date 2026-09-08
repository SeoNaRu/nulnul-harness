# Workflow delivery

Read only when the selected task crosses producer/consumer boundaries, benefits from bounded delegation, or needs partial reruns. Ordinary Direct execution and verified fast resume do not load this reference. This is task guidance, not a scheduler, live-state writer, or acceptance authority.

## Check both sides of the boundary

Read the actual producer and consumer, define their shared contract, and check each changed boundary as soon as both sides exist. Keep the final project completion check.

| Boundary | Check together | Negative control |
| --- | --- | --- |
| API / UI | Response wrapper, nullability, errors, pagination, immediate 202 versus eventual result | Change the response shape without changing its consumer |
| Routes / links | Registered route, parameters, actual navigation target | Remove a required route or parameter |
| State / event | Allowed transition, persisted state, consumer expectation | Replay a duplicate or out-of-order event |
| Data / destination | Identity, mapping, exclusions, cursor, reconciliation | Duplicate a row or interrupt before cursor persistence |
| Harness writer / reader | Schema, authority fields, checkpoint, receipt consumer | Omit a required field or substitute stale evidence |
| Claim / source | Exact claim, supporting source, date, uncertainty | Substitute a source that does not support the claim |

Use only relevant rows. Retain one reproducible bad control with the smallest runnable check. Passing components alone do not prove integration. Missing evidence is `unknown`; a reproduced mismatch is `failed`. Neither becomes PASS after a retry limit. Send reproducible nonpass results through the existing feedback/proposal writer.

## Conditional execution shapes

| Shape | Use when | Direct alternative |
| --- | --- | --- |
| Pipeline | Downstream artifacts need upstream results | One owner performs stages in order |
| Fan-out / fan-in | Bounded independent inputs benefit from concurrent work | One owner handles the short input list |
| Expert pool | Distinct specialties materially improve a decision | One owner consults an on-demand reference |
| Producer / reviewer | Independent checking catches material failure modes | One owner runs an authoritative deterministic check |
| Supervisor | Bounded assignments need synthesis and escalation | One owner with a task list |
| Hierarchical | A large task requires independent subprojects | A flat set of bounded assignments |

Use the inspected host roster and real execution interface, not a fixed model, mandatory team, or assumed tools named `Agent` or `Task`. Map justified roles to the existing Agent/Task/Pack and handoff contracts in `agent-assembly.md`: one synthesis owner, one writer per artifact, bounded inputs/outputs, permissions, completion check, and escalation destination. Changed roles still use `agent_evolution.py`. See `workflow-recipes.md` for task-sized examples; none grants activation authority.

## Dependency-aware partial reruns

The optional `scripts/workflow_delivery.py` helper accepts a schema-v1 workflow with at most 32 steps, each containing `id`, `needs`, `inputs`, `outputs`, and a shell-free `check` argument list. Paths are explicit project-relative files, not globs. Include check implementation and relevant configuration in `inputs`; undeclared external dependencies are not verified. Each output has one producer; consuming its output requires a declared dependency. `assets/workflow-example.json` supplies an executable API/consumer/independent-notes example.

After producing outputs, run an inspected check within existing permissions:

```bash
python3 <skill>/scripts/workflow_delivery.py --root . verify workflow.json api
python3 <skill>/scripts/workflow_delivery.py --root . plan workflow.json --receipt api-receipt.json --only api
```

The existing task owner captures `verify` JSON in its ignored runtime area; the helper writes no live state. The exact argument list executes in the project with a timeout and no interactive input. Shell-free is not a sandbox. A verified receipt binds the step contract and current input/output fingerprints. Input mutation, missing files, unavailable commands, or timeout cannot produce verified reuse; a nonzero check is failed.

`plan` reads one current receipt per supplied step. It reuses only matching verified contracts and fingerprints with fresh dependencies, and marks stale selected work, stale prerequisites, and affected consumers `RUN`. Unrelated fresh work is `REUSE`; unrelated stale work outside an explicit selection is `SKIP`, not verified. Command or dependency changes invalidate receipts. Planning executes no work.

These are local advisory receipts, not authenticated Foundation checks. Do not accept hand-authored JSON as promotion evidence, replace the final authoritative check, or use this planner for fast resume. Existing Foundation and checkpoint executors retain authority. This helper covers declared local files, not database snapshots, remote freshness, resource scheduling, or concurrent writers; those retain their task-specific checks.

```bash
python3 <skill>/scripts/workflow_delivery.py demo
```

The demo checks valid producer/consumer artifacts in a disposable directory, breaks the API shape, observes a failing boundary check, and invalidates that dependency chain while retaining unrelated verified work. It proves fixture mechanics, not live quality or speed. Exposed examples are development cases, never sealed holdouts.

Design inputs at the inspected revision: [boundary QA](https://github.com/revfactory/harness/blob/cceac68ea1d0ad198ef4b7b906cd238375836387/skills/harness/references/qa-agent-guide.md), [execution patterns](https://github.com/revfactory/harness/blob/cceac68ea1d0ad198ef4b7b906cd238375836387/skills/harness/references/agent-design-patterns.md), and [orchestrator guidance](https://github.com/revfactory/harness/blob/cceac68ea1d0ad198ef4b7b906cd238375836387/skills/harness/references/orchestrator-template.md). These are references, not installed or accepted capabilities.
