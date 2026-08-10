# Evidence-gated evolution

Treat the current harness as a removable hypothesis. Improve outcomes, not the amount of setup.

## Establish a baseline

Before changing the harness, record the smallest reproducible baseline:

- the recurring task and representative input
- one primary outcome metric such as precision, duplicate rate, completion rate, elapsed time, or required manual corrections
- guardrails such as cost, privacy, permissions, latency, and regression checks
- capabilities and agent topology actually used

Do not claim improvement when the baseline or comparison cannot be reproduced.

## Observe bounded signals

Keep only durable, non-sensitive evidence:

- passed or failed completion checks
- repeated failures or manual workarounds
- user corrections that should generalize
- quality, cost, and runtime measurements needed for comparison
- capability or agent contributions that can be isolated

Never store raw conversations, secrets, credentials, personal data, or full tool logs as project memory.

When a signal identifies an agent, a bad handoff, a session-loss failure, or the Coach itself, apply `personal-evolution.md`. Convert the signal into a structured feedback event before proposing any instruction change.

## Propose one causal change

Change the nearest durable layer:

- fix product code or a mechanical test for a product defect
- update `AGENTS.md` for a stable repository-wide convention
- replace, configure, or update an existing capability before creating a new one
- update or create a skill only for a reusable workflow gap
- change agent ownership only for a demonstrated coordination problem
- change the project contract for scope, permissions, routing, or a removable assumption

Avoid bundles of unrelated changes that cannot be evaluated independently.

## Accept or roll back

Run the same representative check before and after the change. Accept the candidate only when:

1. the primary metric improves or a proven defect disappears;
2. no guardrail or unrelated regression check worsens;
3. the result is reproducible; and
4. the added complexity has a concrete continuing job.

Record the accepted change, evidence, and rollback or removal condition in concise project-local form. Otherwise restore the prior setup and keep the failure evidence without preserving the failed experiment.

Agent and Coach upgrades require an independent Gate. A proposal author may implement a candidate in isolation but cannot approve, promote, or broaden its own authority. Keep the last accepted version until the Gate records a reproducible decision.

## Prune

Remove or replace a capability or role when its job disappears, overlaps another, loses maintenance or compatibility, adds more coordination than value, or no longer improves the baseline. Installed availability does not justify activation.
