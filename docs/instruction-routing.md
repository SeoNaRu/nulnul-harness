# Instruction routing evaluation — 2026-09-10

Decision: **NO_PROMOTION**. The instruction candidate was rejected and this episode's product and guidance changes were restored exactly to the pre-task snapshot. Existing unrelated changes remain. The repaired evaluator is retained as local tooling outside the shipped plugin; no instruction-performance improvement is established.

## Attempted changes, now preserved as rejected artifacts

1. Shorter discovery description with explicit use/skip conditions.
2. Conditional setup and evolution references, keeping fast resume self-contained.
3. Scoped developer and generated host guidance with explicit local execution permissions.
4. Completion ownership and stop conditions, reusing current authoritative checks.
5. Concise checkpoints for continuity without automatically activating evolution or personal reuse.
6. Reachability-based packaging checks and frozen, counterbalanced model comparison.

The proposed skill entry went from 4,800 to 1,192 words and its description from 994 to 311 characters. Developer guidance went from 1,533 to 492 words. These are artifact sizes, not runtime gains. The [product patch](../evals/instruction-routing/candidate.patch) and [guidance/test patch](../evals/instruction-routing/rejected-guidance.patch) preserve the rejected design; none of those changes is active.

## Observed model results

| Evaluation | Attempts | Result |
| --- | ---: | --- |
| Original evaluator | 6: five completed, one interrupted | Invalid for promotion: reproduced read and check-attribution blind spots |
| Repaired evaluator, champion round 1 | 1 | Passed exact reads, initial validator, worker check, fixed fields and product/checkpoint verification |
| Repaired evaluator, candidate round 1 | 1 | Unknown execution event 8; independent product verification skipped |
| Remaining pairs, controls and live cycle | 0 | Not run after the registered nonpass stop |

The user approved a cumulative maximum of 17 calls. Eight were consumed and nine were not used. The [v1 record](../evals/instruction-routing/invalid-evaluator-v1.json), [v2 results](../evals/instruction-routing/results-v2.json), [independent Gate decision](../evals/instruction-routing/gate-decision.json), and [rollback receipt](../evals/instruction-routing/rollback.json) preserve the accounting and decision.

The [replacement protocol](../evals/instruction-routing/preregistration-v2.json) required four eligible counterbalanced pairs, lower median paired input tokens, and no more than 10% median elapsed increase. Zero pairs were eligible. The candidate's unknown event establishes missing acceptance evidence; it does not establish a product defect or eligible cost regression. Neither raw transcripts nor the unidentified command are retained, so the exact unsupported form is unknown. No sealed or retired holdout was used.

## Retained evaluator repair

The [runner](../evals/instruction-routing/run_ab.py) reuses the existing activation evaluator and gives both arms the same closed development command grammar. It resolves literal reads, counts normalized Python checks, validates protected files and fixed checkpoint fields, and requires native edit evidence plus worker-owned completion. Unsupported syntax, unsuccessful or incomplete execution, extra reads, and missing evidence receive no acceptance credit. The cumulative budget includes invalid and interrupted prior attempts and is checked before login access or model execution.

Independent review approved this limited evaluator scope. It is not an operating-system audit, arbitrary-shell verifier, or general model-performance benchmark. Conflict, inactive-host and transfer behavior were outside these model tasks. The bounded diagnostic reason at the candidate's first unknown event is too coarse to identify the exact cause; one linked future proposal records that limitation without modifying the frozen evaluator or reopening this episode.

## Deterministic validation and closure

The rejected candidate passed 465/465 local tests, including nine evaluator tests, and 17/17 product tests before the model trial. That local success did not override the model acceptance condition. After restoration, 464/464 local tests and 16/16 product tests passed; the package contains 64 files, documentation debt is zero, and learning/archive reconstruction is valid. Release Gate remains local 100/100 with public release blocked. Exact results are recorded in [validation.json](../evals/instruction-routing/validation.json).

At this experiment’s closure, the shipped product tree matched the pre-task champion digest, and original developer guidance and product tests were restored. A subsequent user-requested documentation cleanup is described in the current README; it neither reopens this experiment nor inherits performance evidence from it. Packaging, full local tests, documentation debt, Release Gate and learning/archive reconstruction are checked on the restored state. Public 3.1.0 evidence remains historical; unrelated local integration work still has its own publication blockers.

This one-candidate episode is closed. Do not rerun exposed cases or spend the remaining allowance to change its verdict. A future proposal must preserve unknown evidence and be justified separately; it is not an accepted instruction or permission for personal evolution, installation or publication.
