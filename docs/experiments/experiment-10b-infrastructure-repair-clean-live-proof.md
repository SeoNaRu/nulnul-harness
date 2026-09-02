# NULNUL INFRASTRUCTURE REPAIR + EXPERIMENT 10B

Date: 2026-08-30

## HISTORICAL EXPERIMENT 10

- Verdict: `INFRASTRUCTURE_INVALID`
- Architecture evidence: `NONE`
- Candidate status: `UNEVALUATED historically`

Experiment 10 records, preregistration, Candidate freeze, failed Champion arm,
decision, manifest, and hashes remain unchanged.

## PHASE A — LIVE EVIDENCE ADMISSION

### BUG REPRODUCTION

- Failed-arm record: `experiment-10-positive-activation-commit/arms/fp-a-champion.json`
- Record SHA-256: `1f7fc231af4a681fb50639ebaa44226e8c6e8be0a8f86b84c4e8cdf2e6d05451`
- Input: `agent_exit_code=1`, `token_usage=null`
- Old evaluator: `CONTINUE_EXECUTION`, nonterminal
- Expected: terminal `INFRASTRUCTURE_INVALID`
- Reproduced without a model call: `YES`
- Repaired result on the same immutable record: terminal
  `INFRASTRUCTURE_INVALID`

### AGENT EXIT-1 ROOT CAUSE

- Classification: `UNKNOWN`
- Process invocation: the frozen runner invoked `codex exec --json --ephemeral`
  with ignored user config/rules, workspace-write sandbox, disposable prepared
  workspace, `gpt-5.6-sol`, and medium reasoning.
- CWD: the disposable prepared fixture workspace; it was removed after the
  signed arm record persisted.
- Environment: inherited and not recorded.
- stdout/stderr: captured in memory but not retained.
- Wrapper: `run_evaluation.py` reached post-run augmentation and signed the arm.
- Timeout: not observed; agent runtime was `0.099 s` and no timeout note exists.
- Fixture/activation wrapper: pre-model gate valid; exact source/prepared hashes
  recorded; installed Champion harness tree unchanged.
- Executable/model/provider: Codex returned process exit 1, but provider error
  detail was not retained.
- Output: arm, empty patch, receipts, and readback remain valid.

The exact process-level cause cannot be proven from the preserved fields. No
launcher repair was made on inference.

### EVIDENCE ADMISSION CONTRACT

An official live arm is promotion-grade only when it has:

- process start and exit evidence with exit zero;
- parsed `input_tokens > 0` and nonnegative `output_tokens`;
- raw result and final status;
- patch, patch SHA, changed-file list, and durable write set;
- strict and completion result;
- durable arm record, valid SHA receipt, and matching readback.

A normal exit-zero model run with valid usage remains an admitted product result
when strict or completion fails. Empty patches and zero-write arms remain valid.

### INCREMENTAL STOP CONTRACT

Mandatory evidence is admitted before architecture, paired-result, completion,
or cost gates. Missing or malformed evidence returns terminal
`INFRASTRUCTURE_INVALID`; the next official arm does not start.

### TESTS

| Control | Result |
| --- | --- |
| Valid success | PASS |
| Valid product failure | PASS; admitted as product evidence |
| Nonzero pre-evidence exit | PASS; immediate infrastructure stop |
| Null usage | PASS; stop |
| Malformed usage | PASS; stop |
| Missing receipt | PASS; stop |
| Invalid receipt | PASS; stop |
| Missing patch/write-set record | PASS; stop |
| Valid zero-write | PASS |
| Stop before next arm | PASS |

- Experiment admission/architecture tests: `22/22 PASS`
- Shared runner/durability tests: `23/23 PASS`
- Dedicated smoke-fixture test: `1/1 PASS`

### NON-CREDIT LIVE SMOKE

- Arm: exact Champion only; dedicated non-holdout zero-write fixture
- Exit: `0`
- Usage: valid
- Tokens: input `122,907`; output `1,161`
- Strict/completion: `PASS / PASS`
- Durable arm, empty patch, SHA receipt, and readback: `PASS`
- Result: `PASS`
- Promotion credit: `0`

### PHASE A CLASSIFICATION

`LIVE_EVIDENCE_ADMISSION_REPAIR_ONLY`

No product, Candidate, task-semantic, scientific-fixture, strict/completion,
cost, capability, or architecture behavior changed.

### BENCHMARK REVISION

- Old: `b68fc9813a392dc7efa113ecd6e4e59da3790dd7`
- New Phase A repair: `1121ccab0e752930d9cfb8024f9594a657e35e6b`

Changed infrastructure SHA-256:

| File | Old | New |
| --- | --- | --- |
| `scripts/run.py` | `11063c5671039260310c6ae0e62a7baf8d86c66c04a9307ff65b543efd7a63e2` | `e147568a98f37e3046666157a318621dc8b325e8c9360b33bb3574fd63891ba7` |
| `experiments/10/aggregate.py` | `7cd020063a63fefb6f5b2792d265773f3823542b718b980d5285dd7f5133fe57` | `0d91be2a338eceff80035f94951826817aae406395eebdb6b87e86bf6d0b5bd5` |
| `experiments/10/test_experiment.py` | `947a31a1c55f59798c2d9343c26e6f6952bcd8a96457b0775a630ded2e418ad8` | `e5c5fcafcbcee82ea5bc651632e7cb3d8dcbdc0eb4d84cb64e4844e4ca5cc613` |

## PHASE B — EXPERIMENT 10B

Executed: `YES`, then stopped at the second scheduled wrapper invocation.

### PREREGISTRATION

- Hash: `60e6326d1e8461abb6f1a552a7a24557497c7eae47868a270c585ce1a53b8845`
- Benchmark revision: `f969221932a7a09cd1c0148cd57573e2b968fdc7`
- Candidate budget: exact Experiment 10 byte reuse; generations/retries `0`
- Terminal verdicts: exact frozen 13-value set
- Holdouts: fresh replacements `100`–`103` sealed; Experiment 10 holdouts
  `96`–`99` retired
- Conflict check before first arm: `PASS`

### CHAMPION

- Revision: `cee7b91e2a992adee1582702b7a4084c631443b6`
- Artifact: `48a819a3878c9611487a4a632d9a62d1c9bda403f5dbca224466082ada26136b`
- Complete tree: `7965cadc2aa55782194f3c1df31bacd403b4463b222fea3952731cabac350732`

### CANDIDATE

- Tree: `d9f845851b6756c023434c7c78927346163bae328d884c7ef05b93f3e58b97f6`
- Files:
  - `skills/nulnul-harness/SKILL.md`
  - `skills/nulnul-harness/scripts/activation_boundary.py`
  - `skills/nulnul-harness/scripts/sync_host_entry.py`
- Per-file SHA-256:
  - `aa4445a9448f82de461f7232af15b801456ad9d6ba944ad6cb4b19c994fc107a`
  - `b4fb1fb3e683c7f8ef09e46f108267b385ea57cdc42fa81bcde448cf9d712d56`
  - `e0c06320a583218ab2786496958000a5cfbeabbeb1b26a0d157baedbaf437872`
- Byte delta: `+14,290`
- Byte-identical to Experiment 10: `YES`

### FALSE POSITIVES

| Case | Result |
| --- | --- |
| FP-A Champion | exit 0; usage valid; strict/completion PASS |
| FP-A Candidate | wrapper exit 2 before arm/model evidence |
| FP-B | not started after kill |
| H-FALSE-POSITIVE | sealed, unused, and retired with the stopped experiment |

FP-A Champion input was `107,191`, runtime `34.792 s`, and repository reads
were `6`. Candidate activation, bodies, state, strict/completion, input,
runtime, and reads are unavailable because no Candidate process started.

### TRUE PROJECT-FIT

TP-A, TP-B, and H-TRUE-PROJECT-FIT did not run. No ID, commit, body, activation,
pre-work order, check, attribution, strict/completion, or cost claim is supported.

### DISTINCT CAPABILITY

Development and H-DISTINCT-CAPABILITY did not run. No exact-identity or
single-body claim is supported.

### GOVERNED

G1, G2, and H-GOVERNED did not run. No stage, host, writer, authority,
strict/completion, or cost claim is supported.

### ATTRIBUTION

- Eligible: `0/0` Candidate Project-Fit arms
- Records: none
- Ordering: deterministic controls only; no live Candidate evidence

### STRICT / COMPLETION

- Champion: `1/1 strict`, `1/1 completion`
- Candidate: `0` model arms
- Project-Fit gain: unavailable
- Paired strict/completion regressions: unavailable

### PERFORMANCE

- Direct-like Champion observed: input `107,191`, output `888`, runtime
  `34.792 s`, reads `6`
- Candidate Direct-like: unavailable
- Project-Fit: not run
- Governed: not run
- Overall ratio: unavailable

No Direct or overall performance gate passed or failed mathematically.

### STATE AUTHORITY

The admitted Champion arm recorded zero durable writes. No Candidate,
Project-Fit, Governed, continuity, evolution, Skill, or harness-source write
was evaluated. Shipped product writes: `0`.

### USER BURDEN

Champion routing questions: `0`. Candidate/global zero-burden behavior remains
unproven.

### EXTERNAL OPERATIONS

External capability operations: `0`. No search, marketplace, MCP, plugin
installation, deployment, tag, publication, or release occurred.

### DURABLE EVIDENCE

- Phase A old/repaired reproduction receipts: `PASS`
- Phase A freeze and smoke receipts/readback: `PASS`
- 10B benchmark freeze: `PASS`
- Champion FP-A arm, patch, and receipt/readback: `PASS`
- Incremental decision 1: `PASS`
- Candidate wrapper-failure receipt: `PASS`
- Terminal decision and final report receipts: `PASS`
- Candidate arm record: absent, as required by the recorded pre-arm failure
- Later model arms: `0`

### VERDICT

`INFRASTRUCTURE_INVALID`

Reason: `candidate_evidence_root_overlap_before_arm_record`.

The exact frozen Candidate path was a descendant of the durable evidence root.
The runner's containment guard correctly rejected that arrangement and the
wrapper exited `2` before `run_one`, arm record, patch, or model usage. This
official invocation lacked promotion-grade evidence, so no retry or later arm
was allowed.

### ARCHITECTURE INTERPRETATION

Experiment 10B produced no Candidate model arm. The failure challenges the 10B
root-arrangement preflight and wrapper-level admission surface, not Positive
Activation, deterministic commit, semantic fit judgment, or Candidate bytes.
The architecture remains `UNPROVEN`.

### VALID CLAIM

Phase A repaired and live-smoked record-level evidence admission. Experiment
10B then proved that its Champion-only smoke and record-level tests did not
preflight all scheduled plugin/evidence root relationships or represent a
wrapper failure that occurs before arm-record creation.

### UNSUPPORTED CLAIMS

- Direct remains near Champion cost.
- False positives yield zero Candidate activation.
- True Project-Fit activates the exact capability or improves outcome.
- Governed activation and authority remain correct.
- Attribution ordering works live.
- Any holdout passes.
- The Candidate or architecture should be promoted or rejected on product value.

### EVOLUTION READINESS

- Attribution record complete: `NO`
- Ready for live Skill Evolution: `NO`

### FULL PRODUCT VALIDATION

`NOT RUN` — promotion eligibility was not reached.

### ARCHITECTURE PRODUCT STATE

`NOT_APPLICABLE`

### PRODUCT CHANGES

Shipped `plugins/nulnul-harness/` changes: `0`. Phase A changed only isolated
benchmark infrastructure. The Candidate remains frozen, isolated, and unapplied.

### ROLLBACK

No product rollback is needed. Champion remains active. Discarding the isolated
Candidate copy changes no shipped bytes.

### VERSION

`v2.3 ARCHITECTURE REWORK REQUIRED`

### RELEASE

`NOT READY`

### NEXT

Infrastructure review: preflight every scheduled arm's resolved roots before
arm 1 and make pre-`run_one` wrapper exits durable and terminal. Any future
clean proof requires a new preregistration; do not reuse 10B evidence or tune
the Candidate in this run.
