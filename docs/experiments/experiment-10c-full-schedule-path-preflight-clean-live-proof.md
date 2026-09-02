# NULNUL FULL-SCHEDULE INFRASTRUCTURE REPAIR + EXPERIMENT 10C

Date: 2026-08-31

## HISTORICAL

- Experiment 10: `INFRASTRUCTURE_INVALID`
- Experiment 10B: `INFRASTRUCTURE_INVALID`
- Architecture: `POSITIVE ACTIVATION + DETERMINISTIC COMMIT — UNPROVEN`
- Exact Candidate: `NOT LIVE-EVALUATED`

All Experiment 10 and 10B evidence, receipts, manifests, and verdicts remain
unchanged.

## PHASE A

### 10B PATH FAILURE REPRODUCTION

The exact 10B Candidate and evidence paths were replayed at frozen revision
`f969221932a7a09cd1c0148cd57573e2b968fdc7` without a model call. The wrapper
again exited `2` because the Candidate source was inside the evidence root.

- Historical layout reproduced: `YES`
- Reason: `candidate_evidence_root_overlap_before_arm_record`
- Model processes: `0`

### ROOT CAUSE

The 10B wrapper was correctly strict. The defect was the absence of a complete
resolved-path check for later scheduled arms before arm 1.

### CANONICAL PATH CONTRACT

Every scheduled path is made absolute, normalized, collapsed, and resolved
through symlinks before filesystem containment checks. The contract enforces:

- product/Candidate/evidence separation;
- disposable workspace/evidence separation;
- outputs outside frozen sources;
- read-only scientific inputs;
- pairwise arm-workspace isolation;
- holdouts outside product roots; and
- durable evidence outside cleanup roots.

### FULL-SCHEDULE PREFLIGHT

- Scheduled arms: `22`
- Passed: `22`
- Failed: `0`
- Signed SHA-256:
  `f9ba4488f9cb862a01e924b0ca1a69a5a82b36719c4d76e6b54af6bd4cfd5a61`

Every arm recorded its identity, arm, fixture, product source, workspace,
evidence/patch/receipt destinations, holdout status, and path result before the
first model process.

### NEGATIVE TESTS

All rejected as required:

- Candidate inside evidence root;
- evidence root inside Candidate;
- workspace inside evidence and evidence inside workspace;
- patch inside Candidate;
- receipt inside product source;
- shared mutable workspace;
- symlink alias into evidence; and
- relative parent escape into evidence.

### POSITIVE TESTS

All passed:

- Champion and Candidate outside evidence;
- per-arm isolated workspaces;
- external durable evidence and receipts;
- valid zero-write evidence; and
- cleanup after evidence readback.

### PRE-RUN ATTEMPT EVIDENCE

Synthetic wrapper failure before `run_one` produced a signed, readback-valid,
terminal non-credit attempt with no model process, usage, or product write.

### CANDIDATE MATERIALIZATION

- Original tree:
  `d9f845851b6756c023434c7c78927346163bae328d884c7ef05b93f3e58b97f6`
- Execution tree:
  `d9f845851b6756c023434c7c78927346163bae328d884c7ef05b93f3e58b97f6`
- All three frozen file hashes: `PASS`
- Read-only execution source: `PASS`
- Byte-identical: `YES`

### PHASE A CLASSIFICATION

`FULL_SCHEDULE_PATH_PREFLIGHT_REPAIR_ONLY`

### BENCHMARK REVISION

- Core repair: `5eb9d89ab750e3f501af7dcb2a5aa86958add3eb`
- Frozen 10C benchmark: `acc121e94b9cefd5577e4e5f6514cdb1757b3f3d`
- Final reporting revision: `cf05a5eff73d0a626b3c2d21cb10b743a8020a90`
- Deterministic gate: `57/57 PASS`

## EXPERIMENT 10C

Executed: `YES`, stopped after official arm 1.

### PREREGISTRATION

- SHA-256:
  `9678a2fa225026406d40eccbbfeffbe586f2952300aa6c94636941ebcfc58c0e`
- Terminal set: exact frozen 13 values
- Fresh holdouts: `104`–`107`
- Retired holdouts: Experiment 10 `96`–`99`; Experiment 10B `100`–`103`
- Candidate generations/retries: `0 / 0`

### CHAMPION

- Revision: `cee7b91e2a992adee1582702b7a4084c631443b6`
- Artifact:
  `48a819a3878c9611487a4a632d9a62d1c9bda403f5dbca224466082ada26136b`
- Tree:
  `7965cadc2aa55782194f3c1df31bacd403b4463b222fea3952731cabac350732`

FP-A Champion model execution:

- agent exit: `0`
- token usage: input `124,538`, output `916`
- product completion check: `PASS`
- changed product file in disposable workspace: `api_labels.py`
- durable source/state writes: `0`
- runtime: `38.629 s`
- repository reads: `2`
- evidence status: `cleanup_invalid`

The arm receives no product or performance credit because cleanup failed after
the signed result was written.

### CANDIDATE

- Tree:
  `d9f845851b6756c023434c7c78927346163bae328d884c7ef05b93f3e58b97f6`
- Files and hashes: unchanged from Experiments 10 and 10B
- Byte-identical to Experiment 10: `YES`
- Candidate model arms: `0`

### FALSE POSITIVES / DIRECT-LIKE

- FP-A Champion: model ran; evidence inadmissible after cleanup failure
- FP-A Candidate: not started
- FP-B: not started
- H-FALSE-POSITIVE: sealed and not run

No Direct accuracy or cost claim is supported.

### TRUE PROJECT-FIT

TP-A, TP-B, and H-TRUE-PROJECT-FIT: `NOT RUN`

### DISTINCT CAPABILITY

Development and holdout cases: `NOT RUN`

### GOVERNED

G1, G2, and H-GOVERNED: `NOT RUN`

### ATTRIBUTION

- Eligible Candidate records: `0/0`
- Live ordering evidence: none

### STRICT / COMPLETION

- Admitted Champion arms: `0`
- Inadmissible Champion product completion: `1 PASS`
- Candidate arms: `0`
- Gain and paired regressions: unavailable

### PERFORMANCE

The inadmissible Champion sample used input `124,538`, output `916`, runtime
`38.629 s`, and two repository reads. Direct-like, Project-Fit, Governed, and
overall Candidate ratios are unavailable.

### STATE AUTHORITY

Frozen Champion and Candidate trees retained their exact hashes. The model
changed only the disposable fixture product file. Durable structural,
continuity, evolution, Skill, and harness-source writes were `0`.

### USER BURDEN

New harness-management questions: `0`

### DURABLE EVIDENCE

The path preflight, benchmark freeze, arm record, patch, and terminal decision
were atomically persisted with SHA receipts and successful readback before the
experiment stopped. The failed cleanup workspace was preserved for diagnosis.

- Manifest artifacts: `21/21 PASS`
- SHA receipts: `11/11 PASS`
- Artifact manifest SHA-256:
  `7c2ce24672025d3be8eccab2a635581bf78d424f19b72297d3ad97ad2eb8ea1f`
- Historical Experiment 10 and 10B manifests: unchanged and readback-valid

### VERDICT

`INFRASTRUCTURE_INVALID`

Reason: `readonly_materialization_mode_propagation_cleanup_failure`.

The read-only scientific source mode was preserved when the harness tree was
copied into the disposable workspace. `shutil.rmtree` assumed that disposable
copy was removable and failed with `PermissionError`. Evidence admission
correctly rejected `cleanup_invalid`; the incremental controller started no
later arm.

### ARCHITECTURE INTERPRETATION

Experiment 10C produced no Candidate model arm. It does not support or
challenge Positive Activation, deterministic commit, semantic fit, attribution,
Governed authority, or Candidate quality. Architecture remains `UNPROVEN`.

After Experiments 10, 10B, and 10C all stopped on benchmark infrastructure, the
benchmark system is the dominant source of failure. Further experimental
precision is not automatically worth another repair cycle. Roadmap review
should compare one simpler end-to-end proof path against stopping activation
routing work; do not automatically begin Diagnostic 10D.

### EVOLUTION READINESS

- Attribution complete: `NO`
- Ready for Skill Evolution: `NO`

### FULL PRODUCT VALIDATION

`NOT RUN`

### ARCHITECTURE PRODUCT STATE

`NOT_APPLICABLE`

### PRODUCT CHANGES

Shipped `plugins/nulnul-harness/` changes: `0`. The Candidate remains isolated
and unapplied. Only benchmark infrastructure, evidence, reports, and bounded
project learning records changed.

### VERSION

`v2.3 ARCHITECTURE REWORK REQUIRED`

### RELEASE

`NOT READY`

### NEXT

Roadmap review. Do not automatically start Diagnostic 10D or another Candidate.
