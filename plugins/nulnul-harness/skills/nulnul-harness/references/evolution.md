# Evidence-gated evolution

Treat the current harness as a removable hypothesis. Improve outcomes, not the amount of setup.

## Establish a baseline

Before changing the harness, record the smallest reproducible baseline:

- the recurring task and representative input
- one primary outcome metric such as precision, duplicate rate, completion rate, elapsed time, or required manual corrections
- guardrails such as cost, privacy, permissions, latency, and regression checks
- capabilities and agent topology actually used

Do not claim improvement when the baseline or comparison cannot be reproduced.

## Measure before optimizing

- Every stage records its own start and end. Never infer one stage's duration from the gap between other stages' records: the unrecorded time attaches to its neighbour and names the wrong bottleneck.
- An unrecorded span is the first thing to fix. Add the instrumentation before touching the code it points at.
- Prove a new aggregation tool on a case with a known answer before trusting its output. A tool that mixes throughput with yield reports a healthy stage as producing nothing.

## Observe bounded signals

Keep only durable, non-sensitive evidence:

- passed or failed completion checks
- repeated failures or manual workarounds
- user corrections that should generalize
- quality, cost, and runtime measurements needed for comparison
- capability or agent contributions that can be isolated

Never store raw conversations, secrets, credentials, personal data, or full tool logs as project memory.

When aggregate counts cannot identify a causal stage or owner, use the existing evaluation record as a bounded Experience Digest rather than adding a trace system. Keep only stable stage names, logical owner, elapsed time, aggregate tool/read/validator/test/completion-check counts, bounded signals, candidate/champion identity, and verification status. Reject prompts, responses, transcripts, command lists, sensitive fields, and machine paths with `scripts/validate_experience_digest.py`. Compute `first_divergence` only from a stable structural difference; otherwise record `unknown`.

For an ordering question, reduce the existing event sequence to bounded facts such as implementation completed, verification entered, wrapper observed, and final synthesis observed. Count verification only after the final implementation change, keep behavior and read-scope guardrails separate, and discard the event text. Expose a capability path in an already-read fixture before blaming resolution; if the path is available but final synthesis still precedes verification, classify the ordering evidence without turning the count into a release invariant.

When a signal identifies an agent, a bad handoff, a session-loss failure, or the Coach itself, apply `personal-evolution.md`. Convert the signal into a structured feedback event before proposing any instruction change.

## Propose one causal change

Change the nearest durable layer:

- fix product code or a mechanical test for a product defect
- update only the detected host entry for host-specific session routing; keep stable cross-host repository conventions in `docs/nulnul/project.md`
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

For a product release, behavior passing is necessary but does not excuse a measured cost regression. Re-run each activation case at least three times, keep positive and negative routing coverage, and compare a candidate with a same-model champion in counterbalanced paired rounds. Gate the median paired change against a relative budget rather than an absolute token ceiling. Record fixture, agent, verification, and total time plus bounded tool/read/validator/test counts without persisting raw transcripts. A fast-resume candidate also fails when it reads the full setup contract or setup references.

## Prune

Remove or replace a capability or role when its job disappears, overlaps another, loses maintenance or compatibility, adds more coordination than value, or no longer improves the baseline. Installed availability does not justify activation.
