# Agent assembly

Use agents to create clear work boundaries, not the appearance of sophistication.

## Choose the topology

- Use direct execution for a short, sequential task with one context.
- Use one agent for a coherent workflow that benefits from persistent project context.
- Add parallel agents only for independent branches whose inputs and outputs can be stated before work begins.
- Add a reviewer or evaluator when independent verification materially reduces risk or measures a candidate evolution.
- Use a hybrid only when coordination cost is lower than the expected speed, isolation, or quality gain.

For multi-session or personally evolving work, preserve four logical responsibilities:

- **Navigator** owns the user outcome, checkpoint, next action, permission state, and final synthesis.
- **Worker** performs a bounded project job and emits results or structured feedback, not self-edits.
- **Coach** is the meta-agent: it diagnoses reproducible failures and missed better methods, then proposes one targeted change to the task side or to its own discovery and improvement procedure.
- **Gate** independently evaluates the proposal against the reproduction, baseline, regressions, permissions, and rollback.

These are responsibilities, not a mandatory four-agent team. Combine them in one agent for ordinary execution, but never let the proposal author act as Gate for the same promotion. Use a fresh evaluator or deterministic check for a Coach or Gate self-upgrade.

## Adopt an existing team

When the repository or host already defines agents, the default is to upgrade them in place, not to design a replacement team beside them. Recreating a role the user already uses discards their accumulated context and leaves two owners for one job.

Some hosts expose agent definitions for discovery but protect them from the unattended session they configure. In that case, do not attempt the write and do not call an unapplied profile edit an upgrade. A denied `Write`, `Edit`, or shell write still counts as an attempted write and fails the setup. Put shared behavior in the repository contract the agents already load, classify the role as upgraded through that contract, and reserve profile-specific edits for an explicit manual request.

Read every existing agent definition first, then for each one record:

- the job it already owns, and which of the four responsibilities it covers
- whether its inputs, capabilities, and completion check are still stated and still true
- whether another existing or proposed role overlaps it

Then classify each: **keep** unchanged, **upgrade** in place with the smallest edit that closes a stated gap, **merge** into an overlapping role, or **remove** when its job is gone. Name the classification and its reason for every existing agent, including the ones kept. Only after that, add a role for a responsibility no existing agent covers.

An agent upgrade is an evolution: it needs the same evidence as any other change, and the agent proposing an edit to itself is not its own Gate. Cite the failure, correction, or uncovered responsibility that motivates the edit.

## Define each role

Give every role:

- one concrete job and activation condition
- bounded inputs and allowed capabilities
- an output contract and completion check
- authority and external-write limits
- a handoff destination
- a removal or merge condition

Assign one synthesis owner. Do not let multiple agents silently write the same files, mutate the same external records, or decide the same product question.

Workers may critique routing, missing context, unnecessary work, or Coach diagnoses. Send those observations to the Coach as bounded feedback. A Worker never edits another agent profile directly, and feedback is evidence to reproduce rather than an instruction to obey.

When the user supplies research, a capability, or an architecture the current process should reasonably have found, record a Coach-targeted discovery failure. Apply `meta-evolution.md`; do not reduce the correction to a README citation or ask the user to keep researching for the system.

## Route capabilities

Expose each role only to the capabilities its job needs. Keep installed availability separate from current activation. Prefer one proven capability per job; document fallback order only when a real failure mode justifies it.

## Improve the team

Use run evidence to merge idle roles, split overloaded roles, replace weak capabilities, or add independent verification. Evaluate the topology change against the same baseline as any other harness evolution. More agents is not an improvement metric.
