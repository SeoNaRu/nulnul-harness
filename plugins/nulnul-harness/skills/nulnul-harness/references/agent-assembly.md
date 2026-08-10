# Agent assembly

Use agents to create clear work boundaries, not the appearance of sophistication.

## Choose the topology

- Use direct execution for a short, sequential task with one context.
- Use one agent for a coherent workflow that benefits from persistent project context.
- Add parallel agents only for independent branches whose inputs and outputs can be stated before work begins.
- Add a reviewer or evaluator when independent verification materially reduces risk or measures a candidate evolution.
- Use a hybrid only when coordination cost is lower than the expected speed, isolation, or quality gain.

## Define each role

Give every role:

- one concrete job and activation condition
- bounded inputs and allowed capabilities
- an output contract and completion check
- authority and external-write limits
- a handoff destination
- a removal or merge condition

Assign one synthesis owner. Do not let multiple agents silently write the same files, mutate the same external records, or decide the same product question.

## Route capabilities

Expose each role only to the capabilities its job needs. Keep installed availability separate from current activation. Prefer one proven capability per job; document fallback order only when a real failure mode justifies it.

## Improve the team

Use run evidence to merge idle roles, split overloaded roles, replace weak capabilities, or add independent verification. Evaluate the topology change against the same baseline as any other harness evolution. More agents is not an improvement metric.
