# NULNUL Experiment 7D — Bounded Lane Boundary Live Proof

## Decision

- Verdict: `MISCLASSIFICATION`
- Reason: D1 Candidate selected `PROJECT_FIT`; frozen expectation was `DIRECT`
- Architecture contribution: `FAIL`
- Bounded Lane Architecture: `UNPROVEN`
- Interpretation: the single frozen implementation is insufficient; the
  architecture itself is not disproven
- Model calls: `2`
- Holdout model calls/exposure: `0`
- Product changes: `0`

Experiment 7, 7B, and 7C remain `INFRASTRUCTURE_INVALID`. Diagnostic 7A
remains `STRUCTURAL_EVALUATOR_REPAIR_ONLY`.

## Candidate-relative fixture repair

The exact Experiment 7 candidate modifies the deterministic managed entry, so
fixture integration must compare each arm with that arm writer's whole-entry
output. The prior check compared the Candidate's merged entry with its raw
`managed_block` string. That fails when replacement-string semantics
deterministically materialize an escape during replacement.

The minimum repair compares the evaluated entry with
`merge_entry(pre_writer_entry, managed_block(...))` from the same arm. It
changed only benchmark files `experiments/7/run_evaluation.py` and
`experiments/7/test_experiment.py` at benchmark revision
`d0f968a7064eebc32d18b15cb0a55787afb20525`.

Classification: `CANDIDATE_RELATIVE_FIXTURE_REPAIR_ONLY`.

Deterministic evidence before live execution:

- historical D1 Champion-pass/Candidate-fail defect reproduced;
- 48/48 runner, durability, lifecycle, structural, and fixture tests passed;
- Champion and Candidate self-consistency passed for all seven development
  pairs (14/14 arm integrations);
- bounded managed-block diff, user-content preservation, inactive-host
  preservation, and same-arm idempotency passed;
- all eight forbidden-mutation controls failed as expected;
- exact Candidate structural admission and byte identity passed; and
- all three sealed holdout hashes were unchanged without task-body exposure.

No task, lane, strict/completion, authority, attribution, cost, promotion, or
candidate byte changed.

## Preregistration

The new 7D preregistration froze before model execution at SHA-256
`a3986c53b6df32799dc73f5d7ff5de375cd76d509f35934ad9d750e06d156b4c`.
It bound the exact Champion, exact Candidate, repaired benchmark, ten-pair
schedule, lane expectations, authority, attribution, cost gates, kill rules,
promotion rules, and the original eleven terminal verdicts. Conflict check:
`PASS`.

## Live stop

The frozen schedule began with D1 Champion, then D1 Candidate. The Candidate
emitted `LANE SELECTED: PROJECT_FIT` before broader context, with no pre-lane
repository read. D1's frozen class was `DIRECT`. This triggered the
preregistered `MISCLASSIFICATION` kill rule, so the remaining 18 arms and all
sealed holdouts did not run.

| D1 result | Champion | Candidate |
|---|---:|---:|
| Selected lane | none | `PROJECT_FIT` |
| Strict | fail | fail |
| Completion | pass | pass |
| Input tokens | 118,689 | 154,316 |
| Output tokens | 1,154 | 1,396 |
| Runtime | 41.779 s | 51.786 s |
| Repository reads | 6 | 6 |
| Durable NULNUL writes | 0 | 0 |
| Harness-management questions | 0 | 0 |

Candidate/Champion D1 input was `1.300x`, output `1.210x`, and runtime
`1.240x`. This is a stopped single-pair observation, not the frozen aggregate
Direct or overall cost result.

Both arms completed the requested behavior but failed strict because each
changed the fixture's forbidden test file. There was no paired strict or
completion regression. The Candidate enumerated the roster but loaded no
project Skill, made no durable state write, and performed no external
capability operation.

## Unreached gates

Project-Fit, Governed, evolution reachability, near-boundary behavior, all
three holdouts, aggregate performance, and full product validation were not
reached. No result may be inferred for them.

## Valid claim

The exact frozen Candidate can emit an early observable lane decision, but it
misclassified D1. This makes the implementation non-promotable.

## Unsupported claims

- The Bounded Lane Architecture is superior or disproven.
- Project-Fit capability activation or value is established.
- Governed behavior is preserved.
- Direct or overall aggregate cost gates pass or fail.
- The candidate may be promoted.

## State

- Architecture product state: `NOT_APPLICABLE`
- Candidate 2: not created
- Rollback: no product rollback required; Candidate remained isolated
- Product tree: unchanged Champion tree
  `7965cadc2aa55782194f3c1df31bacd403b4463b222fea3952731cabac350732`
- Version: `v2.3 ARCHITECTURE REWORK REQUIRED`
- Release: `NOT_READY`
- Next: `ARCHITECTURE HYPOTHESIS REVIEW`
