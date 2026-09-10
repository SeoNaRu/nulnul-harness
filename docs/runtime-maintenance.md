# Local runtime maintenance — 2026-09-10

This user-requested maintenance pass addresses ordinary developer guidance, status/resume correctness, and unnecessary validation work. It is separate from the closed instruction-routing experiment and does not promote a governed capability, change a release version, or claim model superiority. Existing unrelated workspace changes remain intact.

## Reproduced problems and repairs

| Path | Reproduced before the fix | Current behavior and regression check |
| --- | --- | --- |
| Developer entry | Every task received subsystem-specific setup, evolution and publication rules | `AGENTS.md` is 615 words, down from 1,533. All 31 invariant bullets survive verbatim and exactly once across the entry and [conditional contract](development-contract.md); independent review verified the routes. Word counts are document sizes. |
| Checkpoint fields | Arrays/objects in version, status or file fields raised `TypeError`; booleans and floating versions could pass | Invalid field types and NUL paths are rejected before command execution. `test_malformed_fields_are_rejected_before_running_a_check` covers eight malformed cases. |
| Interrupted recheck | Interruption or command-start failure left the previous `verified` receipt eligible for fast resume | The existing runner writes `unknown` before launching the check. `test_interrupted_or_unstarted_recheck_invalidates_prior_success` covers both failures; existing success/failure checks cover completion. |
| Non-Git document scan | Each suffix triggered another recursive traversal; an empty source result triggered another whole scan for each document | One traversal skips `.git`, preserves supported source names, and caches empty results. Two new checks cover scan count, excluded files, supported hidden source names, and empty-result reuse; existing Git-order checks remain. |
| Malformed status | A host-bound session with `tasks=["bad task"]` raised `AttributeError` | Malformed task collections return unknown with a warning, without changing stored records. |
| Body-loading status | A same-Pack inclusion with different capability IDs, wrong ordering or duplicate events still reported `body_loaded=true` | One inclusion must follow Pack creation and match its capability IDs. Three negative controls reject contradictions; unfinished work can still report valid body loading. |

Each new runtime regression check failed against the preceding source before its fix. Independent review found no remaining material regression in these four scripts or the developer routing change.

## Bounded local A/B

The non-Git newest-source fallback was compared before/after on one temporary tree containing 481 source files and one excluded `.git` source file. Six paired rounds alternated execution order. All twelve results selected the same newest source.

| Measure | Before | After |
| --- | ---: | ---: |
| Median seconds, fallback function only | 0.0096545 | 0.004567 |
| Directory reads (`os.scandir` calls) | 572 | 25 |

These are local measurements of one filesystem fallback, not model token savings, end-to-end harness speed, or public-adoption evidence. A reproducible small scan-count guard remains in `tests/test_doc_debt.py`; the Git-history path retains its existing no-fallback check. No paid model experiment was launched.

## Validation

The focused checkpoint, document-debt and status suites pass 11, 11 and 7 checks respectively. Final validation:

- Reproducible package: 65 files; the product suite's 17 checks pass within the full run.
- Full suite: 471 checks executed, 470 passed in the restricted sandbox. The sole failure was the booking example's loopback socket creation being denied; rerunning that one unchanged test with local socket permission passed. Every check is therefore accounted for, without repeating the other 470.
- Active Codex documentation debt: none. `git diff --check`: clean.
- Local Release Gate: 100/100, `local_candidate_ready=true`, `release_ready=false`. Exact public Claude/Meta adoption does not cover these integration bytes.
- Independent review verified the four changed runtime scripts and all developer-contract routes. Historical release counts and frozen experimental records are unchanged.

The reviewed paths have no remaining reproduced issue from this pass. Larger architecture changes and an end-to-end speed claim need fresh evidence; neither is inferred from this fallback measurement.
