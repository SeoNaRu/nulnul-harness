# Generalization Gate

Use this gate only when promoting a mechanism to personal or core scope, making a
transfer claim, or publishing that the harness generalizes. Ordinary project-local
changes still use the existing behavior and Release Gate.

## Evaluation roles

- **DEV** may be read by the Coach for reproduction, diagnosis, candidate creation,
  and iteration.
- **VALIDATION** may select or reject a candidate and protect known regressions. It
  is not unseen evidence once its result or fixture influenced development.
- **HOLDOUT** must not exist in the candidate snapshot or be exposed to the Coach
  before the candidate is frozen. It estimates transfer only once.

Evaluation exposure is state. Keep a machine-readable inventory with a stable case
ID, first exposed version and run, development/selection/release uses, current role,
and evaluated mechanism IDs. A previously exposed case cannot become HOLDOUT by
renaming it.

## One claim, one fresh estimate

Before evaluating a holdout, record the originating development failure, causal
mechanism, transferable behavior, transfer domain, expected failure boundary,
primary metric, guardrails, falsification condition, candidate Git ref, and bounded
candidate-source hashes. The Gate must prove that the holdout material was absent
from that ref.

Run the smallest representative local fixture. Reuse the Experience Digest's
bounded cost and guardrail vocabulary where it applies; do not store prompts,
responses, transcripts, commands, private project data, secrets, or machine paths.
Compare the evolved candidate with a single champion run and a repeated or
best-of-N champion baseline on at least one explicitly fair dimension. If token,
runtime, or inference budgets are not comparable, record that and do not claim a
win on those dimensions.

After the first result, retire the holdout. A failure may become DEV or VALIDATION
evidence for the next proposal, but a revised candidate needs a new unseen case.
Reject or narrow the claim when the holdout task or completion check fails, a
guardrail regresses, identity does not match, exposure leaks, a case is reused, or
the comparison cannot support the stated conclusion. `unknown` and insufficient
evidence are not success.
