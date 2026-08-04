# Evidence-driven evolution

Treat the first setup as a hypothesis, not a permanent architecture.

## Keep bounded evidence

Record only durable signals:

- task and observable outcome
- capabilities and execution topology actually used
- passed or failed completion check
- repeated failure or manual workaround
- user correction that changes future work
- the resulting setup change and its removal condition

Never store raw conversations, secrets, credentials, personal data, or full tool logs as memory.

## Change the nearest durable layer

- Update `AGENTS.md` for a stable repository-wide convention.
- Update or create a skill for a reusable workflow.
- Add a mechanical test for an invariant that should not regress.
- Change the project contract for scope, permissions, routing, or a removable assumption.

Do not mutate the setup from one ambiguous failure. When the same problem recurs or a clear test proves the gap, fix it once at the closest shared layer and rerun the failing check.

## Prune

Remove or replace a capability when its job disappears, overlaps another capability, adds more coordination than value, or its check no longer demonstrates useful behavior. Installed availability does not justify session activation.
