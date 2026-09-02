# NULNUL Experiment 8

## Two-Stage Capability-Fit Boundary

Date: 2026-08-28

### ARCHITECTURE STATUS BEFORE

- Hypothesis: `TWO-STAGE BOUNDED LANES`
- Status: `UNPROVEN`
- Experiment 7 implementation family: `CLOSED`

### CHAMPION

- Revision: `cee7b91e2a992adee1582702b7a4084c631443b6`
- Artifact: `48a819a3878c9611487a4a632d9a62d1c9bda403f5dbca224466082ada26136b`
- Tree: `7965cadc2aa55782194f3c1df31bacd403b4463b222fea3952731cabac350732`

### BENCHMARK

- Frozen revision: `352ef9b0737fed48ec873a817f0deced76d40703`
- Infrastructure preflight: `PASS`
- Fixture integration: 14/14 development arm preparations passed before
  Candidate freeze; Champion and Candidate used the same capability-aware
  starting state and each arm's own deterministic host writer.
- Trace evaluators: valid Direct, valid Project-Fit, invalid bare Project-Fit,
  and valid Governed probes all produced the frozen expected result.
- Structural evaluator: allowed two-surface change passed; forbidden existing
  function, second product file, evaluator edit, helper write, and other
  out-of-scope probes failed; no-difference scope validation passed.
- Deterministic suites: Experiment 8 11/11, inherited Experiment 7 9/9, and
  Diagnostic 6B lifecycle/durability 16/16 passed.
- Durability: atomic external evidence, SHA receipts, readback, patch hashes,
  and disposable cleanup passed.

The Experiment 8 fixture integration deterministically populated the existing
`project.md` Capability routing table from each fixture's frozen local Skill
frontmatter. It did so identically for both arms. It did not change prompts,
Skill bodies, product outcomes, strict/completion rules, or evaluator meaning.

### PREREGISTRATION

- SHA-256: `9953b094bed177867fd887ce1fb92fb96c7cf894aff84dbac9e7d3aabbc03678`
- Candidate budget: one generation; exhausted after Candidate 1 freeze
- Terminal verdicts: exact twelve-value Experiment 8 set; no later additions
- Holdouts sealed before Candidate freeze: `YES`
- Conflict check: `PASS`

### CANDIDATE

- Files:
  - `skills/nulnul-harness/scripts/sync_host_entry.py`
  - `skills/nulnul-harness/scripts/accepted_capabilities.py`
- Tree SHA-256: `f47648927cedc228711120aeb8c5371daeab77b71cf4dac9b8a18b6927bf8778`
- Per-file SHA-256:
  - `sync_host_entry.py`: `463d969388561957a7cde94c5c218eb64bbc04ab0339547cbdd2553253f63c70`
  - `accepted_capabilities.py`: `be753362062cfadd9117527cf9b6874d277e7961723707cf8d18f4c72e152e42`
- Byte delta: `+3751` (`+1080` existing file; `+2671` one new read-only file)
- Candidate patch SHA-256: `4d635528f71774b8791fa6d21c770db6e8b4da4e99c000327bb6b652ffc207a8`

Stage 1 mechanism: the host entry decides only `GOVERNED` versus `ORDINARY`
before a repository tool.

Stage 2 mechanism: ordinary work invokes one deterministic read-only parser of
the existing accepted `project.md` routing rows. Semantic job matching remains
model judgment.

Capability load mechanism: a concrete identity is emitted, its exact
`load_target` is read, and only then may an identity-bearing Project-Fit event
commit.

This is structurally distinct from Experiment 7: it adds a real project-evidence
read between two observable commitments and one non-classifying read-only
extractor. It is not another one-shot managed-block wording candidate.

### STAGE 1

| Credited case | Expected | Observed | Result |
| --- | --- | --- | --- |
| D1 | `ORDINARY` | `ORDINARY` | PASS |

Other Direct, Project-Fit, Governed, and holdout cases did not run after the D1
kill. Stage-1 accuracy was therefore 1/1 observed Candidate case, not a mixed
workload result.

### STAGE 2

- Bounded view source: accepted Candidate evidence and Capability routing rows
  from `docs/nulnul/project.md`
- Fields: capability ID, job, activation trigger, project check,
  accepted/verified status, and exact load target
- D1 live view: `776` observable output bytes
- D1 accepted identities: `project-api-validation`, `project-release-docs`
- Frozen expected D1 matches: `0`
- Candidate D1 match: `project-api-validation`
- Identity accuracy: `0/1`

The selected row described `api-error-code-maintenance` activated when API
request-validation behavior changes. D1 requested username normalization, not
request acceptance/rejection or error-catalog maintenance. The Candidate
nevertheless treated the row as a concrete match.

### DIRECT

| Case | D1 | D2 | D3 API false positive | H-DIRECT |
| --- | --- | --- | --- | --- |
| Executed | YES | NO | NO | NO |
| Stage 1 | `ORDINARY` | not run | not run | sealed/not run |
| Expected matches | 0 | not run | not run | sealed/not run |
| Observed match | `project-api-validation` | not run | not run | sealed/not run |
| Final lane | `PROJECT_FIT` | not run | not run | sealed/not run |
| Capability bodies | 1 | not run | not run | sealed/not run |
| Full harness reads | 0 | not run | not run | sealed/not run |
| Live-state/evolution reads | 0 | not run | not run | sealed/not run |
| Durable state writes | 0 | not run | not run | sealed/not run |
| Strict | FAIL | not run | not run | sealed/not run |
| Completion | PASS | not run | not run | sealed/not run |
| Candidate input | 136,932 | not run | not run | sealed/not run |
| Candidate runtime | 45.369 s | not run | not run | sealed/not run |
| Candidate repository reads | 7 | not run | not run | sealed/not run |

Both D1 arms completed the behavior but failed strict because each modified the
frozen forbidden test file as well as `username.py`. There was no paired strict
or completion regression.

The aggregate Direct gate was not evaluated. On the stopped D1 pair only,
Candidate/Champion input was `1.3565x`, above the eventual 1.20 aggregate
ceiling. This is a warning, not a `DIRECT_LANE_OVERHEAD` terminal verdict,
because the frozen misclassification kill took precedence and the Direct
workload was incomplete.

### PROJECT-FIT

P1, P2, and H-PROJECT-FIT (the sealed ordinary Project-Fit boundary control)
were not run. Strict gain, identity accuracy on true Project-Fit work, value,
and attribution readiness were not evaluated.

### GOVERNED

G1, G2, H-GOVERNED, and bounded evolution reachability were not run. Governed
behavior and authority preservation remain unproven for this Candidate.

### CAPABILITY ATTRIBUTION

For reached D1:

- AVAILABLE: `project-api-validation`, `project-release-docs`
- MATCHED: `project-api-validation` — incorrect for the frozen task
- SELECTED: yes, but irrelevant
- LOADED: one real body read before the first product write
- USED: its error-catalog check ran, but it did not materially govern D1
- VERIFIED: completion passed; strict failed
- ATTRIBUTED: `NO`

The match, body read, body marker, and Project-Fit marker occurred in one tool
event. The frozen event-order evaluator therefore could not prove load before
commit and classified it as a bare/invalid Project-Fit chain as well as the
wrong final lane. No capability-routing credit is granted.

### STATE AUTHORITY

Reached Candidate unauthorized durable writes: `0`.

No `project.md`, checkpoint, receipt, evolution, archive, local Skill, host
entry, or harness-source mutation occurred during D1. Candidate source tree
remained frozen.

### STRICT / COMPLETION

| Metric | Champion | Candidate |
| --- | ---: | ---: |
| Strict passes | 0/1 | 0/1 |
| Completion passes | 1/1 | 1/1 |

- Strict gain: `0`
- Paired strict regressions: `0`
- Paired completion regressions: `0`

### PERFORMANCE

Stopped D1 pair only:

| Metric | Champion | Candidate | Candidate / Champion |
| --- | ---: | ---: | ---: |
| Input tokens | 100,948 | 136,932 | 1.3565x |
| Output tokens | 1,176 | 1,209 | 1.0281x |
| Runtime | 39.189 s | 45.369 s | 1.1577x |
| Repository reads | 6 | 7 | 1.1667x |
| Bounded-view reads | 0 | 1 | — |
| Capability-body reads | 0 traced* | 1 | — |
| Durable state writes | 0 | 0 | — |

`*` The Champion combined checkpoint and Skill paths in one command; its
preactivation tracer observed the Skill load, while the coarse read-category
classifier assigned that command to live state.

- Direct: incomplete; pair warning only
- Project-Fit: not run
- Governed: not run
- Overall: incomplete; stopped pair ratio `1.3565x`
- Tokens per strict solve: not meaningful; neither arm had a strict solve
- Runtime per strict solve: not meaningful

### USER BURDEN

New harness-management questions: `0`.

### EXTERNAL OPERATIONS

External capability operations: `0`.

### DURABLE EVIDENCE

- Promotion-critical verified JSON records read back: 6/6
- Live arm receipts: 2/2
- Live patch hashes: 2/2 matched their records
- Raw transcript reconstruction: not used
- Disposable workspaces after cleanup: empty
- Model calls: 2
- Remaining development arms: 12 not run
- Holdout model calls/exposure: 0
- Candidate and Champion trees after run: exact frozen hashes

### VERDICT

`DIRECT_PROJECT_FIT_MISCLASSIFICATION`

Reason: D1 final lane was `PROJECT_FIT`; frozen expectation was `DIRECT`.

### ARCHITECTURE INTERPRETATION

- Two-stage hypothesis: `IMPLEMENTATION INSUFFICIENT`
- Bounded capability view: `INSUFFICIENT IN CANDIDATE 1`; broader hypothesis
  remains unproven

Experiment 8 proves that an early ordinary decision and a small real accepted
capability view can be made observable without loading live state or the full
harness. It also proves that this Candidate's semantic match boundary still
converted a non-governing API-adjacent row into Project-Fit.

The failure primarily identifies category C, the bounded capability-view/match
boundary, and secondarily category B, this first implementation. It does not
establish that every two-stage topology is impossible. A future architecture
review must decide whether accepted job contracts need sharper applicability
evidence or whether Stage 2 needs one bounded task anchor before model judgment.
This experiment does not authorize another Candidate.

### VALID CLAIM

The exact Experiment 8 Candidate passed deterministic infrastructure and
entered a live two-stage ordinary flow, but its accepted-capability check
misclassified D1 and produced no verified outcome or cost advantage. It is not
promotable.

### UNSUPPORTED CLAIMS

- Two-stage bounded lanes are superior or categorically disproven.
- The accepted view reliably selects relevant capabilities.
- Project-Fit creates attributable capability experience.
- Governed behavior is preserved.
- Direct or overall aggregate cost gates pass or fail.
- Any sealed holdout result.
- The Candidate may be promoted or tuned.

### FULL PRODUCT VALIDATION

`NOT RUN` — promotion conditions failed before eligibility.

### ARCHITECTURE PRODUCT STATE

`NOT_APPLICABLE`

### PRODUCT CHANGES

`0`

The exact Candidate remains isolated benchmark evidence. The shipped product
tree is still the Champion tree.

### ROLLBACK

No product rollback was required. Champion remained active; Candidate 1 is
frozen and rejected. No Candidate 2 was created.

### VERSION

`v2.3 ARCHITECTURE REWORK REQUIRED`

### RELEASE

`NOT READY`

### NEXT

`ARCHITECTURE REVIEW`

Do not implement another routing candidate automatically.
