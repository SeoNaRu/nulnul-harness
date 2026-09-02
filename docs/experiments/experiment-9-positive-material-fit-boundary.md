# NULNUL Experiment 9

## Contrastive Capability Applicability + Attribution Boundary

Date: 2026-08-28

### ARCHITECTURE STATUS BEFORE

- Two-stage bounded lanes: `UNPROVEN`
- Applicability hypothesis: `POSITIVE MATERIAL FIT WITH ONE AMBIGUITY ANCHOR`
- Applicability status: `UNPROVEN`
- Experiment 8 Candidate family: `CLOSED`

### HISTORICAL EXPERIMENT 8

- Verdict: `DIRECT_PROJECT_FIT_MISCLASSIFICATION`
- Candidate family: `CLOSED`

### CHAMPION

- Revision: `cee7b91e2a992adee1582702b7a4084c631443b6`
- Artifact: `48a819a3878c9611487a4a632d9a62d1c9bda403f5dbca224466082ada26136b`
- Tree: `7965cadc2aa55782194f3c1df31bacd403b4463b222fea3952731cabac350732`

### BENCHMARK

- Revision: `e10b3c8893aeb521734334e294a8eb015c3b2391`
- Infrastructure preflight: `PASS`
- Fixture integration: `PASS`, 24/24 exact Champion/Candidate arm-relative
  preparations across the complete scheduled workload
- Trace evaluator: `PASS`
- Identity/path evaluator: `PASS`
- Attribution evaluator: `PASS`
- Durability: `PASS`

Before Candidate generation, 53 runner, durability, Diagnostic 6B, and
Experiment 9 deterministic tests passed. Experiment 9's 14 direct tests
covered the exact terminal set, structural positive/negative scope,
arm-relative fixture preparation, accepted identity/path containment, valid
clear and ambiguous Direct/Project-Fit orders, premature body load, bare
Project-Fit, two anchors, wrong identity, write authority, paired outcome
regressions, lane-separated cost aggregation, holdout hashes, and atomic
evidence readback.

The final model-free preflight then prepared every scheduled case once with
each exact arm. Champion and Candidate fixture outputs were self-consistent,
user content and inactive-host guidance were preserved, and Candidate source
passed its frozen structural admission. Model calls before this point: `0`.

### PREREGISTRATION

- SHA-256: `4610c6f593b6ee7b123f4f9123b3cdd001ca361439d21190d56af18c650b1ed7`
- Benchmark-freeze SHA-256:
  `906347fb9ee43b23aa79c4da9024bb709cd9d658705373613d11981f316646bc`
- Candidate budget: one generation; exhausted
- Terminal verdicts: exact 13-value Experiment 9 set
- Holdouts sealed: `YES`
- Conflict check: `PASS`

### CANDIDATE

- Files:
  - `skills/nulnul-harness/scripts/sync_host_entry.py`
  - `skills/nulnul-harness/scripts/capability_boundary.py`
- Tree SHA-256:
  `4c85803926ece0b542ddefec2d3b5feeaa7a53dc763640ce0180acb4cfa46d15`
- Per-file SHA-256:
  - `sync_host_entry.py`:
    `312a15c9b1b917cffb3ffea1bc4305f3255ff299813a3ae28eef7de02a7ec71e`
  - `capability_boundary.py`:
    `ab2c6afe995eeba585630bfedd26e72be333140cb9e9c53d7ad3829bdaa91355`
- Byte delta: `+6252` (`+1486` existing managed-block function;
  `+4766` one new read-only helper)
- Candidate patch SHA-256:
  `345e1364aa98f9411ffd3be6cfe588e7f090df046019cba343cc35a869d75e70`

Stage 1 preserved the `GOVERNED` versus `ORDINARY` concept. The bounded helper
implemented three read-only operations: derive the current accepted view,
validate one selected identity/path, and validate one product-file anchor.
Semantic material fit remained model judgment.

The managed boundary required separately ordered material match, exact
identity validation, body read, digest-bound load, Project-Fit commitment,
first product write, project check, and attribution. This is structurally
different from Experiment 8's combined match/load/commit event.

### CAPABILITY VIEW

- Source: accepted Candidate evidence and Capability routing rows in
  `docs/nulnul/project.md`
- FP-A observable output: `619` bytes
- Fields: capability ID, job, activation trigger, project check,
  accepted/current status, exact load target
- Accepted identities: `project-api-validation`, `project-release-docs`
- Path validation: `PASS` in deterministic preflight
- Capability bodies exposed by the view: `0`

### FALSE POSITIVES

| Case | FP-A | FP-B | H-FALSE-POSITIVE |
| --- | --- | --- | --- |
| Executed | YES | NO | sealed/not run |
| Expected lane | `DIRECT` | not run | sealed/not run |
| Stage 1 observed | none | not run | sealed/not run |
| Material-match event | none | not run | sealed/not run |
| No-match event | none | not run | sealed/not run |
| Anchor | none | not run | sealed/not run |
| Identity | none | not run | sealed/not run |
| Capability body loads | 0 | not run | sealed/not run |
| Final committed lane | none | not run | sealed/not run |
| Strict | PASS | not run | sealed/not run |
| Completion | PASS | not run | sealed/not run |
| Input | 103,348 | not run | sealed/not run |
| Runtime | 45.841 s | not run | sealed/not run |
| Repository reads | 5 | not run | sealed/not run |

FP-A did not repeat Experiment 8's concrete behavioral false positive: it
loaded no Skill body and emitted no Project-Fit commitment. It nevertheless
failed the frozen architecture contract because its bounded-view read was not
preceded by an observable Stage-1 event and was not followed by an evidenced
no-match or Direct commitment.

The frozen aggregate maps any false-positive fixture that fails to remain an
observable ordinary Direct chain to the preregistered terminal class
`FALSE_POSITIVE_PROJECT_FIT`. The measured trace must therefore be kept
separate from the class name: affirmative Project-Fit events observed on FP-A
were `0`.

### TRUE POSITIVES

TP-A, TP-B, H-TRUE-PROJECT-FIT, and all other Project-Fit cases did not run
after the FP-A kill. No true-positive applicability, load ordering, verified
value, or attribution result exists.

### DISTINCT CAPABILITY

Development and sealed distinct-capability cases were not run. Exact Skill-B
selection remains untested.

### AMBIGUITY

Development and sealed ambiguity cases were not run. The one-anchor policy
passed deterministic positive and negative controls but produced no live
architecture evidence.

### APPLICABILITY

- False-positive observable Direct chains: `0/1`
- Affirmative false-positive Project-Fit events: `0/1`
- True-positive Project-Fit: `0/0` live; not evaluated
- Ambiguous correct: `0/0` live; not evaluated

### IDENTITY

- Exact identity on credited live Project-Fit: not applicable
- Wrong identity: `0`
- Irrelevant body load: `0`
- Bare Project-Fit: `0`

### ATTRIBUTION

- Eligible Project-Fit: `0/0`; no Project-Fit task ran
- Match/select/load/commit/write/check/attribution ordering: not live-evaluated
- Attribution records: none

### STRICT / COMPLETION

| Metric | Champion | Candidate |
| --- | ---: | ---: |
| Strict passes | 1/1 | 1/1 |
| Completion passes | 1/1 | 1/1 |

- Total gain: `0`
- Project-Fit gain: not evaluated
- Paired strict regressions: `0`
- Paired completion regressions: `0`
- Product patch SHA was identical across arms:
  `31fa93e483eb1a0ee09d779d34a4a7fa01e6ba9d33d826e99dae7c7cfe6d9805`

### STATE AUTHORITY

- Candidate unrelated durable writes: `0`
- Candidate primary NULNUL loads: `0`
- Candidate live-state/evolution reads: `0`
- Candidate capability-body reads: `0`
- Candidate harness source remained byte-identical: `YES`
- User routing questions: `0`

### PERFORMANCE

Stopped FP-A pair only:

| Metric | Champion | Candidate | Candidate / Champion |
| --- | ---: | ---: | ---: |
| Input | 103,366 | 103,348 | 0.9998x |
| Output | 904 | 1,085 | 1.2002x |
| Runtime | 40.272 s | 45.841 s | 1.1383x |
| Repository reads | 6 | 5 | 0.8333x |
| Bounded-view reads | 0 | 1 | — |
| Capability-body reads | 0 | 0 | — |
| Durable writes | 0 | 0 | — |

- Direct aggregate: incomplete; the stopped pair was below the 1.20 input
  ceiling but does not prove the aggregate gate.
- Project-Fit: not run.
- Governed: not run.
- Overall workload: incomplete; stopped-pair input ratio `0.9998x`.
- Tokens per strict solve: Champion `103,366`; Candidate `103,348`.
- Runtime per strict solve: Champion `40.272 s`; Candidate `45.841 s`.

### USER BURDEN

New harness-management questions: `0`.

### EXTERNAL OPERATIONS

External capability operations: `0`.

### DURABLE EVIDENCE

- Live model arms: `2`
- Verified live records and SHA receipts: `2/2`
- Candidate/benchmark/preflight manifests and receipts: `3/3`
- Decision snapshots and receipts: `2/2`
- Live patch hashes: `2/2`
- Evidence was read back before cleanup: `YES`
- Disposable workspace residue: `0`
- Raw transcript reconstruction: not used
- Holdout model calls/live exposure: `0`

### VERDICT

`FALSE_POSITIVE_PROJECT_FIT`

Frozen reason: `fp-a did not remain ordinary Direct`.

The kill occurred after the first complete Champion/Candidate pair. No later
development arm or sealed holdout ran.

### ARCHITECTURE INTERPRETATION

- Positive-material-fit hypothesis: `IMPLEMENTATION INSUFFICIENT`; true
  material-fit behavior was not reached, so the hypothesis remains unproven.
- One-anchor policy: `UNTESTED IN LIVE EXECUTION`; deterministic controls only.
- `project.md` capability view: `PARTIAL SIGNAL`; the small accepted view was
  available without state, full harness, or body load, but it did not yield an
  observable commitment.

The failure is primarily Candidate implementation D, not proof against every
positive-material-fit architecture. The host contract caused the model to run
the bounded view but did not reliably turn its semantic decision into the
separately observable Stage-1/no-match/Direct events required for later causal
attribution. A future review must decide whether those commitments need a
stronger executable boundary rather than another natural-language marker
instruction.

### VALID CLAIM

The exact Experiment 9 Candidate kept reached FP-A capability-free, state-free,
strictly correct, and near Champion input cost, but failed to produce the
required observable applicability commitment. It is rejected and supplies no
Project-Fit or evolution-ready evidence.

### UNSUPPORTED CLAIMS

- Positive material fit or the one-anchor strategy works in live execution.
- The Candidate produced an affirmative false-positive Project-Fit event.
- True positives select or load the correct capability.
- Project-Fit produces verified advantage or attributable experience.
- Governed behavior is preserved.
- Direct or overall mixed-workload cost gates pass.
- Any holdout result.
- Skill Evolution is ready.

### EVOLUTION READINESS

- Attribution record complete: `NO`
- Ready for attribution-grounded Skill Evolution: `NO`

### FULL PRODUCT VALIDATION

`NOT RUN` — the Candidate failed before development eligibility.

### ARCHITECTURE PRODUCT STATE

`NOT_APPLICABLE`

### PRODUCT CHANGES

`0`

Candidate bytes remain isolated evidence. The local shipped-product boundary
was not modified.

### ROLLBACK

No product rollback was needed. Champion remained active; Candidate 1 is
frozen and rejected. No Candidate 2 was created.

### VERSION

`v2.3 ARCHITECTURE REWORK REQUIRED`

### RELEASE

`NOT READY`

### NEXT

`ARCHITECTURE REVIEW`

Do not tune Candidate 1 or start Skill Evolution.
