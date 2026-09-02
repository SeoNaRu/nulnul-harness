# Post-2.2.1 baseline findings

Status: frozen untuned result from benchmark commit
`f624d77` in the independent `nulnul-benchmarks` repository.

The run compared Vanilla with the exact v2.2.1 archive
`f2d320804c5b86a7d1797c8088a36cf824a8009a6b825f19dcda8b8fa2c3388e`.
It used one clean, counterbalanced, zero-retry execution of 25 pairs. Raw
transcripts were not retained. Patches and structured results are preserved in
`../nulnul-benchmarks/results/`.

## Frozen result

| Variant | Strict pass | Completion check pass | Runtime total | Runtime median | Input-token proxy | Repository reads | Disturbed files |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Vanilla | 19/25 | 21/25 | 1,206.732 s | 31.024 s | 2,493,155 | 135 | 8 |
| exact v2.2.1 | 17/25 | 22/25 | 1,281.718 s | 35.030 s | 3,026,313 | 139 | 13 |

The strict totals include six cases later found to have invalid benchmark
contracts. They remain in the frozen result and are not rewritten or silently
excluded. Excluding cases 3, 13, 15, 19, 23, and 24 leaves 19 valid frozen cases.
The v1 freeze therefore does not meet the 20-valid-case minimum by itself. A
versioned corrected amendment must restore that coverage, and all published
summaries must display both the raw and validity-filtered views.

| Validity-filtered variant | Strict pass | Completion check pass | Runtime total | Runtime median | Input-token proxy | Repository reads | Disturbed files |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Vanilla | 18/19 | 18/19 | 565.287 s | 27.730 s | 1,381,618 | 85 | 4 |
| exact v2.2.1 | 17/19 | 19/19 | 780.538 s | 31.782 s | 1,918,810 | 99 | 8 |

## Failure families

### Family A — resume fallthrough disturbs protected or unnecessary state

Cases 22 and 25 reproduce one bounded family: v2.2.1 correctly falls through
from an unusable checkpoint and completes the product change, but also rewrites
the Codex host entry and, in case 25, replaces checkpoint state that the task did
not require. This is classified as `CONTINUITY`, `HOST_OWNERSHIP`,
`REPOSITORY_DISTURBANCE`, and `RESUME_COST` rather than task-correctness failure.

CASE: `22-resume-stale-files`

EXPECTED: Reject the stale fast path, fix `totals.py`, refresh only the permitted
verification receipt, and leave `AGENTS.md` unchanged.

VANILLA: PASS. Changed `totals.py` and the verification receipt; completion check
passed.

NULNUL: FAIL strict boundaries. Product and completion check passed, but it also
appended a sentence to `AGENTS.md`.

DIFFERENCE: One forbidden host-entry change, two versus six measured repository
reads, and 94.598 s versus 38.760 s.

LIKELY CAUSE: The resume fallthrough contract preserves stale-state safety but does
not make “do not rewrite a truthful host entry during ordinary product resume”
explicit enough.

CONFIDENCE: High for the observed disturbance; medium for the instruction-level
cause until a bounded challenger is compared.

REPRODUCIBLE: Yes. The exact patch and starting commit are preserved.

PRODUCT IMPACT: Users can receive unrelated harness edits during a successful
product fix, increasing review surface and weakening calm continuity.

PROPOSE CHANGE: Compare one narrow resume rule that leaves a truthful host entry
and unrelated checkpoint fields untouched unless restoring invalid state is
necessary. Do not add a mechanism or schema.

CASE: `25-resume-required-fallthrough`

EXPECTED: Reject the checkpoint because the task differs, implement and test JSON
CLI output, and avoid changing the host entry or checkpoint files.

VANILLA: PASS. Changed only `cli.py` and `test_cli.py`; completion check passed.

NULNUL: FAIL strict boundaries. Product and completion check passed, but it rewrote
`AGENTS.md`, `checkpoint.json`, and the verification receipt.

DIFFERENCE: Three forbidden/out-of-scope harness changes, 122.135 s versus 38.952
s, and a much larger input-token proxy.

LIKELY CAUSE: The full-workflow fallthrough is being interpreted as permission to
refresh durable harness state even when the task only authorizes a product change.

CONFIDENCE: High.

REPRODUCIBLE: Yes. It is the second independent symptom in Family A.

PRODUCT IMPACT: Product completion is preserved, but repository disturbance and
resume cost are materially worse than Vanilla.

PROPOSE CHANGE: Use the same bounded challenger as case 22. A separate feature is
not justified.

### Family B — stale instruction repair advantage

CASE: `17-stale-claude-instruction`

EXPECTED: Fix word splitting, replace the stale test command with the exact current
repository check, and pass it.

VANILLA: FAIL completion. It chose `python3 -m unittest discover`, which the frozen
completion check rejected.

NULNUL: PASS. It used the exact `python3 -m unittest -q` command and fixed the
product.

DIFFERENCE: A task-correctness and `INSTRUCTION_COLLISION` win for v2.2.1; no extra
files were disturbed.

LIKELY CAUSE: Repository inspection plus the existing stale-instruction contract
selected the precise runnable check.

CONFIDENCE: High for this case, not a universal host claim.

REPRODUCIBLE: Frozen once; important wins may receive the preregistered diagnostic
repeat but may not replace this result.

PRODUCT IMPACT: Supports preserving the existing instruction-repair behavior.

PROPOSE CHANGE: None. Guard this behavior against regression.

## Invalid benchmark contracts

These cases are `INVALID`, not hidden losses or wins. Corrected successors may be
added under a versioned amendment; the frozen originals and results remain intact.

CASE: `03-regression-js-cache-zero`

EXPECTED: Fix the zero-cache regression and verify existing behavior.

VANILLA: Product/check passed after changing `cache.js` and `cache.test.js`, but the
hidden allowed-change scorer failed it.

NULNUL: Product/check passed with the same two changed files and the same scorer
failure.

DIFFERENCE: No outcome difference can be scored from the hidden boundary.

LIKELY CAUSE: The prompt requests verification and does not forbid test changes,
while the scorer silently permits only `cache.js`.

CONFIDENCE: Certain contract mismatch.

REPRODUCIBLE: Yes.

PRODUCT IMPACT: None established.

PROPOSE CHANGE: A corrected successor must either permit the focused test or state
the product-only boundary in the task.

CASE: `13-agents-existing-skill-date`

EXPECTED: Fix impossible-date handling, reuse the existing skill, add no harness
files, and verify.

VANILLA: Product/check passed after changing only `datecheck.py`.

NULNUL: Product/check passed after also adding focused cases to
`test_datecheck.py`; the hidden allowed-change scorer failed it.

DIFFERENCE: The patch differs, but the task never forbids test changes and the
required no-new-harness condition was met.

LIKELY CAUSE: The scorer silently treats an ordinary product test as forbidden.

CONFIDENCE: Certain contract mismatch; no product causality may be inferred.

REPRODUCIBLE: Yes, including the frozen current arm.

PRODUCT IMPACT: None established. This cannot justify weakening verification.

PROPOSE CHANGE: Add a corrected successor that explicitly permits the existing
focused test file.

CASE: `15-duplicate-skills-cleanup`

EXPECTED: Product normalization plus exact duplicate-skill consolidation.

VANILLA: FAIL completion after changing the product.

NULNUL: FAIL completion after changing the product.

DIFFERENCE: None that can be scored reliably.

LIKELY CAUSE: The fixture's `check.py` has invalid indentation and an accidental
literal newline inside a string.

CONFIDENCE: Certain; Python cannot parse the completion check.

REPRODUCIBLE: Yes.

PRODUCT IMPACT: None established.

PROPOSE CHANGE: Repair only in a new benchmark amendment and rerun every variant.

CASE: `19-messy-harness-login`

EXPECTED: Fix login, consolidate exact duplicate skills, preserve inactive-host and
MCP files, and add nothing.

VANILLA: FAIL completion.

NULNUL: FAIL completion.

DIFFERENCE: None that can be scored reliably.

LIKELY CAUSE: The fixture's `check.py` has invalid indentation and malformed
multiline literals.

CONFIDENCE: Certain.

REPRODUCIBLE: Yes.

PRODUCT IMPACT: The intended messy-harness and killer-demo hypothesis remains
untested.

PROPOSE CHANGE: Add a corrected successor; never overwrite the exposed fixture.

CASE: `23-resume-permission-change`

EXPECTED: Honor the changed permission boundary, modify only `src/formatter.py`,
and refresh verified state.

VANILLA: Product/check passed but strict scoring failed.

NULNUL: Product/check passed but strict scoring failed.

DIFFERENCE: None that can be scored reliably.

LIKELY CAUSE: The prompt explicitly says “modify only `src/formatter.py`” while the
scorer requires `tests/test_formatter.py` and a hidden `STRASSE` marker.

CONFIDENCE: Certain contract contradiction.

REPRODUCIBLE: Yes.

PRODUCT IMPACT: Changed-permission resume behavior is not validly measured.

PROPOSE CHANGE: Create a corrected successor with one consistent authority boundary
and observable completion behavior.

CASE: `24-resume-named-file-fast-path`

EXPECTED: Collapse repeated whitespace, update the focused test, run the checkpoint
check, and stay within the named-file read set.

VANILLA: Correct product behavior but failed the frozen scorer.

NULNUL: Correct product behavior but failed the frozen scorer.

DIFFERENCE: Both reported two measured reads; no reliable outcome difference.

LIKELY CAUSE: The scorer requires the undisclosed literal `many   spaces`, and the
agent subprocess does not invoke the runner-owned checkpoint validation that is
later scored.

CONFIDENCE: High that the required-content marker is invalid; medium on how the
runner should measure command execution.

REPRODUCIBLE: Yes.

PRODUCT IMPACT: No fast-path claim is supported by this case.

PROPOSE CHANGE: Use a corrected successor with task-visible assertions and explicit
command telemetry.

## Untuned decision

- `ADVANTAGE`: case 17 within its exact scope.
- `REGRESSION`: cases 22 and 25.
- `NO_ADVANTAGE`: all remaining valid equal pairs.
- `INVALID`: cases 3, 13, 15, 19, 23, and 24.
- Runtime/context signals from single runs, including cases 14 and 18, remain
  descriptive only. No product change is justified until repeated or tied to a
  reproducible failure family.

The first bounded challenger, if the frozen current candidate does not already
resolve it, is Family A. It changes an existing resume/fallthrough rule only. No new
Agent, Gate, state schema, service, or lifecycle is justified.

## Corrected Project-Fit proof amendment

The original six invalid contracts remain frozen. Preregistered successors 26–31
restore the intended observable boundaries without replacing their raw evidence.
Together with the 19 valid originals they form a 25-case proof view.

| Variant | Strict pass | Completion pass | Runtime total | Input-token proxy | Repository reads | Disturbed files |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Vanilla | 21/25 | 21/25 | 889.613 s | 2,123,954 | 122 | 6 |
| exact v2.2.1 | 21/25 | 23/25 | 1,154.986 s | 2,813,285 | 144 | 11 |
| frozen Project-Fit candidate | 21/25 | 23/25 | 1,248.134 s | 3,367,586 | 141 | 12 |

The frozen current candidate neither fixes Family A nor improves aggregate strict
or completion success over exact v2.2.1. Its observed runtime is 8.1% higher and
its input-token proxy is 19.7% higher. Because this third arm ran after the
counterbalanced original pairs, those cost differences are descriptive rather than
causal paired estimates. The suite records `NO_ADVANTAGE`, not promotion.

### Family C — requested capability cleanup is not completed

CASE: `28-duplicate-skills-cleanup-v2`, `29-messy-harness-login-v2`

EXPECTED: Complete the product task and leave one active copy of an exactly
duplicated Skill job without adding replacement support.

VANILLA: Both product changes were made, but both strict completion checks failed
because the duplicate Skill files remained.

NULNUL: exact v2.2.1 and the frozen Project-Fit candidate produced the same two
strict failures. Case 29 observed NULNUL activation; case 28 did not.

DIFFERENCE: No outcome advantage. This is a shared model failure and a reproduced
NULNUL identity failure because explicit cleanup remained incomplete even after
activation in case 29.

LIKELY CAUSE: The product contract recognizes overlap but does not reliably route
an explicit cleanup request into a capability-file merge or retirement action.

CONFIDENCE: High for the observed incomplete cleanup; low that instruction wording
alone can solve it.

REPRODUCIBLE: Yes, across all three frozen variants and two corrected cases.

PRODUCT IMPACT: NULNUL cannot currently support a measured harness-cleanup or
capability-retirement advantage claim.

PROPOSE CHANGE: One preregistered single-file routing clarification was compared
twice. It failed both target cases in both rounds and used 38.3% more input tokens
than the parent, so it was rejected. Stop rather than add a new mechanism in this
Proof scope.

## Bounded challenger disposition

- `resume-state-preservation-v1`: `REJECT`.
- `resume-state-preservation-v2`: `NARROWER_SCOPE`, not promoted.
- `different-task-state-preservation-v1`: `REJECT` after a guardrail regression.
- `capability-cleanup-routing-v1`: `REJECT`; target 0/4, guardrails 8/8.

No product behavior challenger was promoted. The exact raw results, patches,
protocols, decisions, and generated aggregate report remain in the independent
benchmark workspace.
