# NULNUL Diagnostic 7A — Bounded-Lane Structural Evaluator Repair

## Historical Experiment 7

- Verdict: `INFRASTRUCTURE_INVALID`
- Architecture status: `UNPROVEN`
- Candidate status: `UNEVALUATED_IN_LIVE_EXECUTION`

Diagnostic 7A does not alter or reinterpret Experiment 7. Its benchmark
freeze, candidate, decision, report, sealed holdouts, and SHA receipts remain
immutable. No model arm ran in either Experiment 7 or this diagnostic.

## Bug reproduction

The old checker at benchmark revision
`116c5ce6347b82afe851c8f13210571f4575f12e` was run against two minimal
one-file product trees. The files used the exact Champion and preserved
Experiment 7 candidate `sync_host_entry.py` bytes; their only difference was
inside `managed_block`.

- Expected: `PASS`
- Observed: `FAIL — code outside managed_block changed`
- Reproduced: **YES**
- Old checker SHA-256:
  `ba39aae75317825c36a20b287e4d11c60a71451421680bb92eba3cf968b6f657`

## Root cause

The old AST selection condition was:

```python
if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or node.name == "managed_block"
```

It retained the module docstring, imports, constants, `managed_block`, and the
`__main__` guard while removing every other function. The evaluator therefore
compared the permitted changing boundary and discarded the unchanged functions
it was intended to protect.

The old selected nodes in both arms were the module docstring, imports,
`HOST_ENTRIES`, `START`, `END`, `managed_block`, and the `__main__` guard. It
removed `temporary_file`, `atomic_write`, `atomic_batch_write`, `merge_entry`,
`shared_state`, `sync`, and `main`.

The normalized old AST hashes differed:

- Champion: `c2af04a0e426432112d254150c14235bd831ed5acdd871ede6e276d2703c84f6`
- Candidate: `75990d0968dc00cff89983fe8f03a8c3c18c086665d34ee990f6ea78e8b9653b`

With only `managed_block` excluded, both normalized hashes are
`8aef8fff33b3f1251f4fc42bda52d0a382bf63a14ab1df893bd374933367ec7a`.

## Frozen structural contract

- Allowed product file:
  `skills/nulnul-harness/scripts/sync_host_entry.py`
- Allowed structural scope: `managed_block` only
- Valid: only that boundary changes, or there is no product difference
- Invalid: another function, semantic module-level node, unpreregistered
  import, second product file, or candidate-side benchmark/evaluator file
  changes

This check admits structural scope only. It does not assess candidate quality,
lane behavior, outcome, cost, or promotion eligibility.

AST normalization uses `ast.dump(..., include_attributes=False)` after removing
only the allowed function definition. It ignores locations, comments, and
nonsemantic formatting. It retains all parsed semantic syntax outside the
boundary, including imports and module-level executable nodes.

## Evaluator repair

Benchmark files changed:

- `experiments/7/check_candidate.py`
- `experiments/7/freeze.py`
- `experiments/7/test_experiment.py`
- Diagnostic 7A contract/reproduction records
- Experiment 7B preregistration/protocol

The causal repair changes the boundary predicate from equality to inequality.
A small shared scope check now enforces changed-file and outside-boundary AST
rules, and the future benchmark freeze refuses to proceed unless its synthetic
positive and negative controls match their frozen expectations.

No generic diff framework, dependency, product rule, model runner, task case,
fixture, strict/completion evaluator, or promotion rule was added or changed.

## Deterministic controls

| Probe | Evaluator result | Control status |
| --- | --- | --- |
| Allowed `managed_block` change only | PASS | PASS |
| Same allowed change plus another function | FAIL | PASS |
| Other function change | FAIL | PASS |
| Semantic module-level change | FAIL | PASS |
| Second product file change | FAIL | PASS |
| Candidate evaluator self-modification | FAIL | PASS |
| Import change | FAIL | PASS |
| No product difference | PASS | PASS |

The allowed-only probe fails under the frozen inverted filter and passes under
the repaired evaluator.

## Exact Experiment 7 candidate

- Tree SHA-256:
  `1305587c574405991e9cb2223509245baf853b414d7c427b2a98613db5c1179e`
- Champion file SHA-256:
  `849c206b2f2b0a5fe3ad2a97c8d7f6fb72407d9d7902c97f1bb9884079ffdb50`
- Candidate file SHA-256:
  `d5ea23fc890e48663f7106169da0d686a6f8397ff1846a149cdb8bcac101f3f4`
- Byte delta: `+1104`
- Bytes unchanged: **YES**
- Repaired scope admission: **PASS**

This is not product promotion or live architecture evidence.

## Sealed holdout integrity

Only immutable case and fixture hashes were checked; Diagnostic 7A did not
open the holdout task bodies.

| Holdout | Case | Fixture | Status |
| --- | --- | --- | --- |
| H-Direct | `1af6bcc87385ca9cb97cb30778c87b0e6d078aac97d48657bf5fa7fa0d059897` | `beb9df855e9ad03a7dbacbb78d21da502c2cacbb87beaff339a15cbdd6832af6` | UNCHANGED |
| H-Project-Fit | `0b665de3f887fe7363bbff51fe2dd01623f0820302528ee1bac74f318e979b0f` | `a2497caab91b89ad29e8faf09c09417b3f4edbc01f0c6341d4d4bb7669b580d3` | UNCHANGED |
| H-Governed | `0db2ef03464063ae4c94f748b0db8cb079fe7a07b07f6d738e9ec1db4bcf2f56` | `537d929b549a185ffb71a0dad4f29dfb7b0e41f53558a1a22a7388f3cbd30fc0` | UNCHANGED |

All are reusable for Experiment 7B. The candidate was already frozen, no
post-generation candidate edit occurred, and no live model received a holdout.

## Semantic immutability

- Model execution semantics: **UNCHANGED**
- Task semantics: **UNCHANGED**
- Strict/completion evaluators: **UNCHANGED**
- Promotion and kill criteria: **UNCHANGED**
- Direct, Project-Fit, and Governed definitions: **UNCHANGED**
- Candidate bytes: **UNCHANGED**

The diff from the old Experiment 7 revision is confined to the structural
admission checker, its freeze preflight/tests, Diagnostic 7A records, and the
unexecuted Experiment 7B preregistration.

## Benchmark validation

The final benchmark revision passed 46 model-free tests:

- runner/path tests: 10
- durability tests: 13
- Diagnostic 6B fixture-integration tests: 16
- Experiment 7 and structural-scope tests: 7

JSON validation, candidate integrity, all eight historical Experiment 7 SHA
receipts, `git diff --check`, clean-worktree validation, and remote revision
readback also passed. Model calls: **0**.

## Classification and benchmark revision

Verdict: **STRUCTURAL_EVALUATOR_REPAIR_ONLY**

- Old Experiment 7 benchmark:
  `116c5ce6347b82afe851c8f13210571f4575f12e`
- New benchmark revision:
  `262bd3aa9717c92a57253d325c9a0b10bf16d1ea`
- Durable branch: `diagnostic-7a-structural-evaluator-repair`

Only structural-candidate admission infrastructure changed. This classification
does not make the candidate eligible under historical Experiment 7 and does
not prove the architecture.

## Product tree

- Before:
  `7965cadc2aa55782194f3c1df31bacd403b4463b222fea3952731cabac350732`
- After:
  `7965cadc2aa55782194f3c1df31bacd403b4463b222fea3952731cabac350732`
- Byte-identical: **YES**
- Product changes: **0**

## Experiment 7B

Preregistration: **PREPARED — NOT EXECUTED**

Experiment 7B is the clean live proof of the same Bounded Lane Architecture.
It binds the exact shipped Champion, exact preserved Experiment 7 candidate,
unchanged Experiment 7 semantic protocol and promotion criteria, and unchanged
sealed holdouts. Candidate generations allowed: zero. Model runs performed:
zero.

The next highest-value action is to run Experiment 7B without modifying the
candidate. Do not begin that experiment automatically.
