# NULNUL EXPERIMENT 10

## POSITIVE ACTIVATION COMMIT BOUNDARY

Date: 2026-08-30

### ARCHITECTURE STATUS BEFORE

- Positive Activation + Deterministic Commit: `UNPROVEN`
- Experiment 9 family: `CLOSED`
- Experiment 9 verdict remains `FALSE_POSITIVE_PROJECT_FIT`

### CHAMPION

- Revision: `cee7b91e2a992adee1582702b7a4084c631443b6`
- Artifact: `48a819a3878c9611487a4a632d9a62d1c9bda403f5dbca224466082ada26136b`
- Tree: `7965cadc2aa55782194f3c1df31bacd403b4463b222fea3952731cabac350732`

### BENCHMARK

- Revision: `b68fc9813a392dc7efa113ecd6e4e59da3790dd7`
- Infrastructure preflight: `PASS` before Candidate generation
- Direct evaluator: `PASS` positive and negative deterministic controls
- Project-Fit commit evaluator: `PASS` accepted identity, rejected identity,
  path containment, exact body, stale receipt, and read-only controls
- Governed commit evaluator: `PASS` valid stage, invalid stage, host ownership,
  and stage-before-context controls
- Attribution evaluator: `PASS` valid order and attribution-before-check negative control
- Durability: `PASS` atomic JSON receipt round trip
- Deterministic tests: `12/12 PASS`

The first official live arm then exposed a frozen infrastructure failure. The
Champion agent process exited with code `1` before producing usage evidence.
The incremental aggregate incorrectly returned `CONTINUE_EXECUTION` for that
record instead of immediately classifying missing usage as infrastructure
failure. The explicit Experiment 10 evidence-failure kill rule therefore owns
the terminal result.

### PREREGISTRATION

- Hash: `949764ae255f2a2bc0c8d7b73ca66c83f6b67cffd257ac8f6e3580b02408f5c6`
- Benchmark-freeze hash: `311a7fa1e1cfe95ae25682043a3c359dfb13bc92b77f13b93eab7cf86e181bb5`
- Candidate budget: one generation; exhausted
- Terminal verdict set: exact frozen 13-value Experiment 10 set
- Holdouts sealed: `YES`; all four case and source-tree hashes passed
- Conflict check: `PASS`

### CANDIDATE

- Files:
  - `skills/nulnul-harness/SKILL.md`
  - `skills/nulnul-harness/scripts/activation_boundary.py`
  - `skills/nulnul-harness/scripts/sync_host_entry.py`
- Tree SHA: `d9f845851b6756c023434c7c78927346163bae328d884c7ef05b93f3e58b97f6`
- Candidate-freeze SHA: `2b3db4ca5d22bec68ab16f2334ceb2a62877ea82dff3a5cd247ae8de9683e717`
- Patch SHA: `a3fa302308371ba3c4a69a81e8ac4f920e70a2508118cd4ae44385d1a627664d`
- Byte delta: `+14,290`
- Per-file SHA:
  - `SKILL.md`: `aa4445a9448f82de461f7232af15b801456ad9d6ba944ad6cb4b19c994fc107a`
  - `activation_boundary.py`: `b4fb1fb3e683c7f8ef09e46f108267b385ea57cdc42fa81bcde448cf9d712d56`
  - `sync_host_entry.py`: `e0c06320a583218ab2786496958000a5cfbeabbeb1b26a0d157baedbaf437872`

Bounded view: every ordinary task receives the accepted/current `project.md`
view without bodies or live state.

Project-Fit commit: one read-only deterministic helper validates the exact
accepted identity and contained path, loads only the selected body, records its
digest, and returns a receipt.

Governed commit: the same helper validates the named stage, active host,
eligibility, and existing authority surface before stage-specific context.

Direct semantics: no Direct event exists. Credit requires the available/read
view, available positive boundary, zero positive commits, zero bodies and
governed state, completed work, and verification.

This is structurally different from Experiment 9: Experiment 9 relied on
model-authored ordered prose commitments; Experiment 10 instantiated exact
positive transitions as executable receipts and removed Direct ceremony.

### FALSE POSITIVES / DIRECT

| Case | Result |
| --- | --- |
| FP-A | Champion process attempted; invalid before model evidence |
| FP-B | Not run after kill |
| H-FALSE-POSITIVE | Sealed; not run |

- Bounded view opportunity: not live-evaluated on Candidate
- Project-Fit activation: not live-evaluated on Candidate
- Governed activation: not live-evaluated on Candidate
- Capability bodies: not live-evaluated on Candidate
- Governed state: not live-evaluated on Candidate
- Strict: no valid paired result
- Completion: no valid paired result
- Input: unavailable
- Runtime: Champion failed arm `0.243 s`; Candidate unavailable
- Reads: Champion `0`; Candidate unavailable

### TRUE PROJECT-FIT

TP-A, TP-B, and H-TRUE-PROJECT-FIT did not run. Match evidence, capability ID,
commit, body, pre-work load, receipt, product work, project check, attribution,
strict/completion, input, runtime, and read results are not available.

### DISTINCT CAPABILITY

Development and H-DISTINCT-CAPABILITY did not run. No exact-ID or body claim is
supported.

### GOVERNED

G1, G2, and H-GOVERNED did not run. No live stage, host, write-authority,
strict/completion, input, runtime, or read claim is supported.

### DIRECT JUSTIFICATION

- View available: deterministic preflight only
- Positive activation boundary available: deterministic preflight only
- Project-Fit activation: no Candidate arm
- Governed activation: no Candidate arm
- Body loads: no Candidate arm
- State loads: no Candidate arm
- Verification: no Candidate arm
- Credited Direct: `0/0` executed Candidate arms; `0/3` scheduled

### PROJECT-FIT ACTIVATION

- Exact ID: `0/0`
- Commit success: `0/0`
- Pre-work body: `0/0`
- Irrelevant body: not live-evaluated

### ATTRIBUTION

- Eligible: `0/0`
- Ordering: deterministic controls passed; no live record
- Records: none

### STRICT / COMPLETION

- Champion: one invalid-for-comparison arm (`fail/fail`) after pre-model exit
- Candidate: not run
- Gain: not measurable
- Project-Fit gain: not measurable
- Paired strict regressions: not measurable
- Paired completion regressions: not measurable

### PERFORMANCE

- Direct Champion input: unavailable
- Direct Candidate input: unavailable
- Direct ratio: unavailable
- Project-Fit: not run
- Governed: not run
- Overall: not run

No cost gate passed or failed mathematically; input evidence was absent.

### STATE AUTHORITY

The failed Champion arm changed no files and recorded no durable writes.
Candidate, Project-Fit, and Governed authority were not live-evaluated.

### USER BURDEN

No user routing question was asked. The Candidate did not run, so the global
zero-burden requirement remains unproven.

### EXTERNAL OPERATIONS

External capability operations: `0`. No search, marketplace, MCP, plugin
installation, deployment, tag, publication, or release occurred.

### DURABLE EVIDENCE

- Signed benchmark freeze: `PASS`
- Signed Candidate freeze: `PASS`
- Exact Candidate tree copied and tree-verified: `PASS`
- Signed official arm record: `PASS`
- Signed incremental aggregate: `PASS`
- Signed final decision: `PASS`
- Official process attempts: `1`
- Arms with model usage: `0`
- Candidate arms: `0`
- Holdout model calls: `0`
- Raw transcript retained: `NO`

### VERDICT

`INFRASTRUCTURE_INVALID`

Reason: the first official arm exited before model evidence with
`agent_exit_code=1` and `token_usage=null`; the frozen aggregate then failed to
make this immediately terminal. The explicit evidence-failure kill rule stops
the experiment. No retry, Candidate repair, Candidate 2, later development
arm, or holdout followed.

### ARCHITECTURE INTERPRETATION

This failure challenges experiment infrastructure and evidence admission. It
does not test or challenge architecture A (positive activation), B
(deterministic commit), C (semantic material-fit judgment), or D (the first
Candidate implementation). Positive Activation + Deterministic Commit remains
`UNPROVEN`.

### VALID CLAIM

The exact Experiment 10 infrastructure and one structurally new Candidate
passed deterministic preflight and were frozen, but the live experiment became
invalid before any evidenced model execution because the first official arm
had no usage evidence and the incremental aggregate did not reject it
immediately.

### UNSUPPORTED CLAIMS

- Direct remains near Champion cost.
- False positives produce zero positive activations live.
- True Project-Fit activates the exact capability and improves strict outcome.
- Governed stage and authority behavior are preserved live.
- Attribution ordering or experience records work live.
- Any sealed holdout passes.
- The Candidate should be applied or promoted.
- The architecture is better or worse than Champion.

### EVOLUTION READINESS

- Attribution record complete: `NO`
- Ready for attribution-grounded Skill Evolution: `NO`

The infrastructure nonpass is linked to one bounded Coach feedback and future
proposal. No Skill candidate, evolution candidate, or promotion was performed.

### FULL PRODUCT VALIDATION

`NOT RUN` — promotion eligibility was never reached.

### ARCHITECTURE PRODUCT STATE

`NOT_APPLICABLE`

### PRODUCT CHANGES

Shipped `plugins/nulnul-harness/` changes: `0`.

Only benchmark infrastructure, durable experiment evidence, this report, and
the required nonpass feedback/proposal were recorded. Candidate bytes remain
isolated and unapplied.

### ROLLBACK

No shipped-product rollback is needed. Champion remains active. The frozen
Candidate can be discarded without changing the product; no Candidate 2 exists.

### VERSION

`v2.3 ARCHITECTURE REWORK REQUIRED`

### RELEASE

`NOT READY`

### NEXT

`ARCHITECTURE REVIEW`

Do not tune Experiment 10 or resume live execution from this evidence set.
