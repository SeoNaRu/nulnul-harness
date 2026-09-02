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

## Cross-project knowledge contract

Project Memory never becomes global Memory. `../scripts/generalization_core.py` is
the only writer for the schema-version-1 `generalizations.json` in
the explicitly approved existing Personal Home. It extends the existing personal
and Meta cross-project surface instead of creating another provenance service.
The old `cross-project-evidence.json` remains valid historical Meta-selection
evidence, but it is `HISTORICAL_NONCURRENT` for Foundation Experience transfer
because it lacks the current privacy-state and target-validation lineage.

Knowledge has three levels. A verified Foundation Experience stays in its source
project. Repeated eligible source evidence may freeze one `CANDIDATE` containing
only an abstract pattern, job class, applicability and non-applicability
conditions, privacy-safe hashed project refs, Experience identities and digests,
bounded Capability/Agent/Control refs, diagnosis, counterevidence, and lineage. It
becomes `TRANSFERABLE` only after support from two independent source projects or
one different target project's verified confirmation. `NARROWED`, `SUPERSEDED`,
and `RETIRED` records preserve counterevidence and reciprocal history.

The exportability default is `PROJECT_ONLY`. Candidate proposals may be
`GENERALIZATION_CANDIDATE`; promoted records are `TRANSFERABLE`. Machine paths,
human-readable repository/customer identity, source bodies, transcripts, prompts,
logs, contacts, and private Decisions are `REJECTED_SENSITIVE`; credential-shaped
structured data is `NEEDS_REDACTION`. Unknown privacy state fails closed. The
runtime validates source Experience and Session lineage and computes project
counts, digests, status, writes, and rollback. A model may propose only the
abstraction and applicability diagnosis; it cannot invent evidence or promote
itself.

## Target prior and authority

Retrieval is trigger-only and returns at most three items and 2048 serialized
bytes. A Target Prior contains the Generalization ID, abstract pattern, relevance,
conditions, independent-project count, evidence strength, and bounded
counterevidence summary. It never contains source names, paths, Memory, code,
Experiences, or transcripts. `CANDIDATE`, stale, superseded, retired,
non-applicable, and adjacent-vocabulary records do not enter the pack. Ordinary
Direct performs zero Generalization lookup and receives zero Generalization bytes.

A target result is `CONFIRMED`,
`USEFUL_BUT_PROJECT_SPECIFIC_ADAPTATION_REQUIRED`, `NOT_APPLICABLE`,
`CONTRADICTED`, or `INSUFFICIENT_EVIDENCE`. The target Foundation Experience must
link `generalization:<GENERALIZATION_ID>` and its own authoritative verification.
Confirmation can support transferability; contradiction is retained and may
narrow or retire the prior. A target-local Decision or Lesson derives from that
target Experience, never from copied source Memory.

The authority order is fixed: verified target-project truth, target Decisions,
target Experience, transferable prior, then an unvalidated Candidate. A prior may
seed Natural Selection, Agent Evolution, or Harness Evolution, but cannot mutate a
Capability, topology, control, project contract, or guarded Kernel. Those existing
lifecycle transactions remain the only mutation owners.
