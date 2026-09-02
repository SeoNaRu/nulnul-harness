# Agent assembly

Use agents when clear work boundaries materially improve the outcome, never for the appearance of sophistication. Agent count is neither a target nor a primary metric.

## Choose the topology

- Use direct execution for a short, sequential task with one context when it is outcome-competitive.
- Use one agent for a coherent workflow when one context can produce the strongest verified result.
- Add specialized or parallel agents when task-specific expertise, independent branches, or broader alternative exploration materially improve the expected outcome and their inputs and outputs can be stated before work begins.
- Add a reviewer or evaluator when independent verification materially reduces risk, catches defects the implementation path is likely to miss, or measures a candidate evolution.
- Use a hybrid when the expected speed, isolation, verification, or quality gain materially outweighs coordination cost.

Zero, one, three, or six agents can all be correct. The only count test is whether each role materially improves the final verified outcome. Do not withhold a justified role to preserve a smaller topology, and do not retain a role whose contribution is not material.

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

Then classify each: **keep** unchanged, **upgrade** in place with the narrowest outcome-complete edit that closes a stated gap, **merge** into an overlapping role, or **remove** when its job is gone. Name the classification and its reason for every existing agent, including the ones kept. Only after that, add a role for a responsibility or material outcome improvement no existing agent covers.

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

For a Foundation topology, `scripts/agent_evolution.py` makes these boundaries machine-inspectable. An Agent contract records stable `AGENT_ID`, version/digest, role, job, responsibilities, task boundary, input/output contracts, Capability and Tool requirements, delegation rules, verification responsibility, authority boundary, handoff/failure contracts, and bounded context requirements. The topology records stable `AGENT_TOPOLOGY_ID`, version/digest, sorted delegation edges, one synthesis owner, and one verification owner. A changed contract or graph is a new digest; never silently edit the active topology.

Each delegation edge states parent and child task boundaries, expected output, allowed scope, required check, and return contract. Each child is a separate Foundation Task and receives only its own pre-session Capability Pack. A bounded handoff returns `DONE`, `FAILED`, or `OPEN`, artifact refs, Check IDs, and the next/return contract—not a child transcript. Agent identity does not grant Governed or framework authority.

Workers may critique routing, missing context, unnecessary work, or Coach diagnoses. Send those observations to the Coach as bounded feedback. A Worker never edits another agent profile directly, and feedback is evidence to reproduce rather than an instruction to obey.

When the user supplies research, a capability, or an architecture the current process should reasonably have found, record a Coach-targeted discovery failure. Apply `meta-evolution.md`; do not reduce the correction to a README citation or ask the user to keep researching for the system.

## Route capabilities

Expose each role only to capabilities that materially support its job. Keep installed availability separate from current activation. Prefer the strongest proven task-fit path; when paths are materially equivalent, use the lower-context non-overlapping set. Document fallback order only when a real failure mode justifies it.

## Improve the team

Use run evidence to merge idle roles, split overloaded roles, replace weak capabilities, or add independent verification. Evaluate the topology change against the same baseline as any other harness evolution. More agents is not an improvement metric, and fewer agents is not one either; verified outcome contribution decides.

A repeated agent-specific miss may justify a bounded new version of that same role even when no external replacement exists. Compare it with the confirmed version through an independent Gate; keep the winner and rollback point, and do not leave both versions active. When the reproduced cause is capability routing rather than the role profile, change routing instead of rewriting a good agent.

Use Agent Evolution only after materially new Agent-attributable evidence, repeated overload/handoff/duplication, a recurring uncovered responsibility, a project topology change, or an explicit maintenance boundary. `KEEP` is normal. `UPGRADE` improves one responsibility contract without necessarily adding an Agent; `SPLIT` partitions demonstrated overload; `MERGE` removes demonstrated duplicate coordination; `REPLACE` changes the preferred Agent design; `RETIRE` removes an obsolete or absorbed responsibility; `CREATE` adds one recurring uncovered responsibility. One frozen Topology Challenger competes against the current topology under equivalent project checks and a sealed holdout. Quality dominates; equivalent quality favors lower verified carrying cost or another named verified advantage. The transaction, not the model, owns identities, digests, graph validation, Decision lineage, commit, and rollback.
