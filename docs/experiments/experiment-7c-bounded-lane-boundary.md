# NULNUL Experiment 7C — Bounded Lane Boundary Final Clean Live Proof

## Decision

- Verdict: `INFRASTRUCTURE_INVALID`
- Reason code: `fixture_integration_preflight_failure`
- Architecture contribution: no live evidence
- Bounded Lane Architecture: `UNPROVEN`
- Candidate: `UNEVALUATED_IN_LIVE_EXECUTION`
- Model calls: `0`
- Holdout exposure: `0`
- Product changes: `0`

Historical Experiment 7 and 7B remain `INFRASTRUCTURE_INVALID`. Diagnostic 7A
remains `STRUCTURAL_EVALUATOR_REPAIR_ONLY`.

## Preregistration

Experiment 7C froze a new protocol before model execution at SHA-256
`fc6a3f525a3ef49f259dba9cc73dcf500bd5a9f56d6640a0558486764c174334`.
It preserved the exact Champion, candidate, benchmark, task schedule, lane
expectations, authority, capability-attribution, cost, promotion, and terminal
verdict contracts from Experiment 7.

The sole 7B conflict was removed: Champion or candidate integrity failure maps
to `INFRASTRUCTURE_INVALID` with a specific reason, not a new terminal verdict.
The frozen terminal set therefore exactly matches the original Experiment 7
family.

## Deterministic preflight

Passed before the terminal failure:

- preregistration conflict and receipt validation;
- 46/46 deterministic runner, durability, lifecycle, and structural tests;
- allowed-boundary positive probe;
- allowed-plus-forbidden negative probe;
- exact candidate structural admission;
- Champion tree/file identity;
- candidate tree/file identity and `+1104` byte delta;
- critical evaluator and benchmark hashes; and
- `d1` Champion fixture integration.

The next mandatory check failed for the exact candidate:

- Pair: `d1`
- Case: `77-routing-v3-simple-username`
- Arm: candidate
- Failure type: `FixtureInvalidError`
- Error: `evaluated host entry is not its exact deterministic managed block`

The frozen 7C contract classifies any fixture-integration preflight failure as
`INFRASTRUCTURE_INVALID` and requires an immediate stop. No candidate repair,
preflight retry, model arm, holdout, aggregation, full product validation, or
product application followed.

## Identities after stop

- Champion tree:
  `7965cadc2aa55782194f3c1df31bacd403b4463b222fea3952731cabac350732`
- Candidate tree:
  `1305587c574405991e9cb2223509245baf853b414d7c427b2a98613db5c1179e`
- Candidate file:
  `d5ea23fc890e48663f7106169da0d686a6f8397ff1846a149cdb8bcac101f3f4`
- Product tree before/after:
  `7965cadc2aa55782194f3c1df31bacd403b4463b222fea3952731cabac350732`

Candidate and product bytes are unchanged.

## Holdouts and live results

The preregistration freeze cryptographically bound all three original holdouts.
The mandatory preflight stopped before dedicated holdout readback or task-body
access. No holdout was passed to a model.

Direct, Project-Fit, Governed, evolution reachability, activation attribution,
write-authority, strict/completion, and performance results were not measured.

## Valid claim

The exact candidate could not pass the frozen evaluated-entry fixture
integration boundary for the first candidate development arm. This invalidated
the live experiment before model execution.

## Unsupported claims

- The Bounded Lane Architecture is better or worse than Champion.
- The candidate classifies any lane correctly in live work.
- Direct cost, Project-Fit value, Governed behavior, or state authority meets
  or misses its live gate.

## State

- Architecture product state: `NOT_APPLICABLE`
- Rollback: none required
- Version: `v2.3 ARCHITECTURE REWORK REQUIRED`
- Release: `NOT_READY`

Do not tune the candidate or create Candidate 2 from this run. The next action,
if separately authorized, is an infrastructure/preflight contract review. The
architecture hypothesis itself received no new evidence.
