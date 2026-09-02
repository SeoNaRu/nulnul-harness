# Diagnostic 1C — Resume Benchmark Stability

Status: `COMPLETE`
Preregistered at: `2026-08-26T07:54:29Z`
Product-change budget: zero
Candidate-generation budget: zero
Retry budget: zero

This diagnostic estimates the reproducibility of the frozen champion on Cases
17, 22, 25, and 31. It does not reopen Experiment 1 (`REJECT`) or Experiment 1B
(`MODE GAP PROVEN`, candidate `REJECT`). The definitions, run count, order, and
decision rule below were frozen before any repeated agent run.

## Frozen champion

| Field | Value |
| --- | --- |
| Revision | `cee7b91e2a992adee1582702b7a4084c631443b6` |
| Archive SHA-256 | `48a819a3878c9611487a4a632d9a62d1c9bda403f5dbca224466082ada26136b` |
| Frozen `SKILL.md` SHA-256 | `133978c82c7f9cfaf638c711e206a597a828ff239b10da5f0a031aebbf32307f` |
| Archive files | 38 |
| Benchmark revision | `a3599dcbba975e1696a5fd4ca68f6f822d86d572` |
| Runner SHA-256 | `589f3216133cde35609fca5bb6b83207e05299da0d20ac6c18c14f50154ceef1` |

The archive is extracted afresh for this diagnostic. The mutable product
worktree and both rejected candidates are not execution inputs.

## Pre-agent reproducibility gate

Each case is prepared five times using the unchanged runner. The gate requires
all five observations to have the same prepared worktree hash, deterministic Git
commit, task, completion command, durable-state bytes, product-file bytes, and
strict-check contract. Initial completion status must also agree. Any mismatch
ends the diagnostic as `BENCHMARK_INFRASTRUCTURE_DEFECT` before agent execution.

The gate passed for all four cases. The machine-readable observations are stored
next to the raw run results.

## Frozen repetitions and order

Five independent champion runs per case, 20 runs total. Every run uses a fresh
temporary repository; no failed, invalid, or unfavorable result is retried.

| Round | Order |
| --- | --- |
| 1 | 17 → 22 → 25 → 31 |
| 2 | 31 → 25 → 22 → 17 |
| 3 | 22 → 17 → 31 → 25 |
| 4 | 25 → 31 → 17 → 22 |
| 5 | 17 → 22 → 25 → 31 |

The first four rounds counterbalance position exactly. The fifth repeats the
canonical order because the requested odd repetition count cannot balance four
positions perfectly.

## Frozen execution protocol

- Codex: `gpt-5.6-sol`, reasoning `medium`, ephemeral, user config and rules
  ignored, `workspace-write` sandbox.
- Claude Code: `sonnet`, effort `high`, no session persistence, project settings
  only, bounded local tool allowlist, maximum budget USD 0.5.
- Timeout: 420 seconds per run.
- Prompt: the unchanged case `task` string.
- Retry budget: 0.
- Raw transcript: not retained.
- Measurements: strict result, completion, changed files, durable/product write
  sets, input-token proxy, runtime, repository-read proxy, question proxy, and
  behavior fingerprint.

Exact provider-side model build, historical CLI versions, historical relevant
environment variables, and hidden provider/cache state were not recorded by
Experiments 1 or 1B and remain `UNKNOWN`; they are not invented here.

## Frozen fingerprints

Fingerprints are derived from result JSON and patches, never private reasoning.

- `EXPECTED_GUIDANCE_REPAIR`: Case 17 changes only requested `CLAUDE.md` among
  durable files and completes the product change.
- `RECEIPT_REFRESH_ONLY`: a relevant resume case changes the receipt, product
  files, and no other durable file.
- `EXPECTED_CHECKPOINT_REFRESH`: a relevant resume case changes only the
  checkpoint and/or receipt among durable files.
- `PRODUCT_ONLY`: Case 25 changes only `cli.py` and `test_cli.py`.
- `UNRELATED_HOST_SYNC`: an unrelated task changes `AGENTS.md` or `CLAUDE.md`.
- `CHECKPOINT_REPLACEMENT`: Case 25 changes checkpoint or receipt state outside
  the recorded milestone.
- `COMPLETION_FAILURE`: the repository completion check fails.
- `OTHER`: no preregistered fingerprint describes the observed write set.

A run may carry secondary fingerprints; one primary fingerprint is selected by
the order: completion failure, unauthorized host write, unrelated checkpoint
replacement, expected case-specific write, other.

## Frozen stability classifications

- `STABLE_PASS`: at least 4/5 strict passes and at most one contradictory result;
  passing observations show the expected non-harmful fingerprint.
- `STABLE_FAIL`: at least 4/5 strict failures and at least 4/5 observations share
  the same primary harmful fingerprint.
- `UNSTABLE`: neither rule holds, or materially different harmful behaviors keep
  any one failure fingerprint below 4/5.
- `INFRASTRUCTURE_INVALID`: starting-state reproducibility fails or any runner
  result is invalid.

For use as a future **absolute single-run kill-condition control**, the stricter
bar is 5/5 strict pass with no harmful fingerprint. A 4/5 `STABLE_PASS` is not
automatically an absolute control.

## Frozen final decision rule

1. Any infrastructure invalidity → `BENCHMARK_INFRASTRUCTURE_DEFECT`.
2. Case 25 `STABLE_FAIL` and Case 22 `UNSTABLE` →
   `CASE25_STABLE_DEFECT_CASE22_UNSTABLE`.
3. Cases 22 and 25 both `STABLE_FAIL` →
   `CASE22_AND_CASE25_STABLE_DEFECTS`.
4. Cases 22 and 25 both `UNSTABLE` → `RESUME_FAILURES_UNSTABLE`.
5. Any other combination → `OTHER`, reported without forcing it into an
   unsupported category.

Case 17 and Case 31 control eligibility is reported independently. Historical
verdicts remain immutable regardless of this diagnostic's outcome.

## Results

### Environment comparison

| Condition, Experiment 1 vs 1B | Classification | Evidence |
| --- | --- | --- |
| Champion archive and source revision | `SAME` | Exact archive `48a819...136b`, source `cee7b91...43b6` |
| Benchmark revision, tracked runner, relevant cases/fixtures | `SAME` | Revision `a3599dcb...d572`, runner `589f321...eef1`; preserved case and fixture hashes agree |
| Prompt, host, model alias/effort, permissions, timeout, retry | `SAME` | Same case JSON and unchanged runner/protocol |
| Fresh task workspace and starting commit | `SAME` | Every repeated case has its historical deterministic commit |
| Case order | `DIFFERENT` | Experiment 1: 17→22→25→31; Experiment 1B champion observations: 25→17→22 |
| Benchmark outer worktree | `DIFFERENT` | Experiment 1B added untracked experiment evidence, none copied into the four task workspaces |
| Exact provider model build | `UNKNOWN` | Not exposed in historical result records |
| Historical CLI versions and relevant environment variables | `UNKNOWN` | No sanitized historical environment snapshot exists |
| Hidden provider/cache state | `UNKNOWN` | Ephemeral/no-session-persistence settings do not expose provider-side state |

The diagnostic environment used Git 2.43.0, Python 3.12.3, Codex CLI
0.149.1, Claude Code 2.1.246, and WSL2 Linux
5.15.167.4-microsoft-standard. `CODEX_HOME`, `CLAUDE_CONFIG_DIR`, API-key
variables, and proxy variables were unset. This current snapshot does not fill
unknown historical values.

### Fixture and runner reproducibility

| Case | Prepared tree SHA-256 | Starting commit | Five preparations |
| --- | --- | --- | --- |
| 17 | `caf0acb57319c2c867da5b885306449634163702ae17d9294bfd0da23c732b20` | `d3cdff578784bd071e7807be789e687b2e435e7c` | identical |
| 22 | `c9972f5f196c04a8cd1c8e8bef820846a07dc2b20a443672f10d1d8ad8f24b5f` | `ce2921ddbf106887dfa4040e94f5c17388139912` | identical |
| 25 | `275dc1c3a5e95560fb7b9879721c98e6283fb090a8e29ad00050e892feeb5b9f` | `7598c73e41107131f5718e4af42843ffc92a3fd6` | identical |
| 31 | `d226ffb200dac37ee9ce5fcd07ded7ba752e4202d49a00df04c57fd96caddd18` | `345143100bd7bef9cb600fe3ebef3d1ff5f64a76` | identical |

For every case, the task, completion command, strict contract, durable files,
product files, prepared tree, starting commit, and initial completion status also
matched across all five preparations. The prepared hashes for checkpoint Cases
22, 25, and 31 intentionally differ from their source-fixture hashes because the
unchanged runner creates the receipt and removes `.benchmark/`; Case 22 then
applies its sealed stale-file overlay. Those transformations were themselves
identical five times.

### Repeated champion observations

| Case | Strict | Completion | Primary write fingerprint | Classification | Absolute control? |
| --- | ---: | ---: | --- | --- | --- |
| 17 | 5 pass / 0 fail | 5/5 | `EXPECTED_GUIDANCE_REPAIR` 5/5 | `STABLE_PASS` | yes |
| 22 | 0 pass / 5 fail | 5/5 | `UNRELATED_HOST_SYNC` 5/5 | `STABLE_FAIL` | no |
| 25 | 0 pass / 5 fail | 5/5 | `UNRELATED_HOST_SYNC` 5/5; `CHECKPOINT_REPLACEMENT` secondary 5/5 | `STABLE_FAIL` | no |
| 31 | 5 pass / 0 fail | 5/5 | `RECEIPT_REFRESH_ONLY` 5/5 | `STABLE_PASS` | yes |

Durable write sets were exact in Cases 17, 22, and 31:

- Case 17: `CLAUDE.md` only, as explicitly requested.
- Case 22: `AGENTS.md`, checkpoint, and receipt on all five runs.
- Case 31: receipt only on all five runs.

Case 25 changed `AGENTS.md`, checkpoint, and receipt on all five runs. It also
created `project.md` on two runs. Product work completed every time. No Codex run
changed `CLAUDE.md`, no Claude run changed `AGENTS.md`, no run asked a question,
and all 20 completion checks passed.

The runner marks each raw round `complete: false` because the diagnostic executes
only the preregistered NULNUL arm, not its ordinary two-arm benchmark. All 20
individual records are valid; this flag is not an invalid run.

### Case 22 flip analysis

The exact cause remains `UNKNOWN`.

Supported exclusions and observations:

- tracked runner, case, source fixture, prompt, champion bytes, permission,
  timeout, model alias, prepared tree, and starting commit match;
- the runner's fresh temporary repositories exclude prior task-workspace bytes;
- this diagnostic reproduced the strict failure 5/5 across positions 1, 2, 3,
  and 4, always with an `AGENTS.md` write plus checkpoint/receipt refresh;
- therefore fixture drift, starting-state contamination, and a simple
  within-round position effect do not explain the historical flip.

The preserved Experiment 1 receipt-only pass remains valid, as does the later
Experiment 1B failure. Model stochasticity, ambiguous natural-language routing,
an unrecorded provider build, or hidden provider/cache state are compatible with
the observations, but this diagnostic cannot distinguish them causally. They are
not asserted as the cause.

### Case 25 defect confidence

Confidence is **high within the measured protocol**. Case 25 failed strict checks
5/5 here and 7/7 when the two preserved champion observations from Experiments 1
and 1B are included. All seven runs completed the requested product work but
changed `AGENTS.md` and replaced the unrelated checkpoint/receipt. The extra
`project.md` disturbance varied, but the core harmful write fingerprint did not.

### Token, runtime, and read variance

`input_tokens` is the same API-reported proxy used in the earlier experiment
reports. Claude cache-create/read fields are not silently added to that field, so
Case 17 is not comparable to Codex cases as a total-context estimate.

| Case | Input-token proxy min / median / max | Runtime min / median / max | Repository reads min / median / max |
| --- | ---: | ---: | ---: |
| 17 | 12 / 14 / 16 | 20.493 / 22.587 / 29.181 s | 6 / 7 / 9 |
| 22 | 284,685 / 319,303 / 456,498 | 72.707 / 95.081 / 128.361 s | 2 / 8 / 10 |
| 25 | 525,586 / 612,334 / 851,776 | 126.898 / 182.930 / 232.659 s | 8 / 10 / 16 |
| 31 | 87,509 / 107,045 / 152,963 | 32.831 / 39.363 / 49.727 s | 2 / 2 / 4 |

Runtime and token costs vary materially, especially for Case 25, even though its
strict failure fingerprint is stable. No paired causal cost claim is made.

### Reliability decision

`CASE22_AND_CASE25_STABLE_DEFECTS`.

Both targets satisfy the frozen 4/5 `STABLE_FAIL` rule—in fact, each failed 5/5
with the same primary harmful fingerprint. Cases 17 and 31 satisfy the stricter
5/5 absolute-control bar. This does not retroactively alter either historical
experiment:

- Experiment 1: `REJECT`, unchanged.
- Experiment 1B: mode gap `PROVEN`; candidate `REJECT`, unchanged.

No product, candidate, fixture, runner, schema, or historical result changed.

## Next highest-value action

Before any new product candidate, isolate the shared routing/setup-synchronization
locus that makes both stale same-scope fallthrough and unrelated-task fallthrough
invoke durable host/checkpoint writes. A future experiment should use repeated
targets and keep Cases 17 and 31 as the now-qualified absolute controls. It must
not relabel or retry either rejected candidate.

`STOP` — no resume candidate, Capability Survivor / Retirement, Live Skill
Evolution, v2.4, research pass, release, or publication follows this diagnostic.
