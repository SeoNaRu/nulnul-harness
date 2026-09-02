# Experiment 1E — Existing-Setup Owner + Structural Sync Boundary

Status: `PREREGISTERED`
Preregistered at: `2026-08-26T18:06:12+09:00`
Generation budget: one candidate
Retry budget: zero

This experiment targets Diagnostic 1D's frozen causal decision,
`LOCUS_D — MODE_GAP_PLUS_SECONDARY_TRIGGER`. It does not reopen or relabel
Experiment 1 (`REJECT`), Experiment 1B (`MODE GAP PROVEN`, candidate `REJECT`),
Diagnostic 1C (`CASE22_AND_CASE25_STABLE_DEFECTS`), or Diagnostic 1D
(`LOCUS_D`). The protocol below is frozen before candidate generation.

## Frozen champion

| Field | Value |
| --- | --- |
| Source revision | `cee7b91e2a992adee1582702b7a4084c631443b6` |
| Archive SHA-256 | `48a819a3878c9611487a4a632d9a62d1c9bda403f5dbca224466082ada26136b` |
| Plugin tree SHA-256 | `7965cadc2aa55782194f3c1df31bacd403b4463b222fea3952731cabac350732` |
| `SKILL.md` SHA-256 | `133978c82c7f9cfaf638c711e206a597a828ff239b10da5f0a031aebbf32307f` |
| Benchmark revision | `a3599dcbba975e1696a5fd4ca68f6f822d86d572` |

The champion is extracted from that archive. Neither the mutable NULNUL
worktree nor either rejected candidate is an execution input.

## Frozen causal model and hypothesis

The defect is not fast-path fallthrough. It is the combination of:

1. no explicit ordinary full-work owner when an existing valid setup cannot use
   the bounded fast path; and
2. downstream wording that can turn existing-state observation or selection
   into authority to synchronize host guidance or replace continuity scope.

> If ordinary work on an already-valid NULNUL setup receives an explicit
> execution owner, and host-entry synchronization is limited to real
> setup/repair/state-pointer transitions rather than mere shared-state existence
> or selection, Cases 22 and 25 will stop producing unrelated durable-state
> mutations while Cases 17 and 31 and true setup/adoption behavior remain
> correct.

The hypothesis is falsified by any target durable-write failure, suppressed
receipt refresh, suppressed explicit repair, setup/adoption regression, or
failed aggregate cost guardrail.

## Frozen candidate boundary

One generation may change the frozen `skills/nulnul-harness/SKILL.md`. A nearby
reference may change only if leaving it untouched makes the same rule
contradictory. No deterministic writer, schema, state format, Gate, Agent,
dependency, topology, memory mechanism, or user question may be added. If the
distinction cannot be represented in that boundary, the terminal result is
`INSUFFICIENT_ARCHITECTURE_EVIDENCE`; scope does not expand.

The candidate must express one reusable rule:

- existing setup + failed fast path has an ordinary full-work owner;
- observing or selecting existing state is read-only;
- root entries are structural live-state pointers, not product-task notes;
- synchronization requires New Setup, explicit Adopt/Upgrade/Repair, active-host
  addition, or a real live-state target-path transition;
- changing content behind the same checkpoint path does not itself require sync;
- checkpoint semantic maintenance remains scoped to legitimate continuity work;
- runner-owned receipt refresh remains independent;
- ordinary work does not create or rewrite `project.md` merely because broad
  inspection occurred.

It must not implement “never write state,” case-specific exceptions, fixture
symbols, or a second generation of either rejected wording candidate.

## Frozen execution protocol

- Arms: exact frozen champion versus one candidate.
- Codex: `gpt-5.6-sol`, reasoning `medium`, ephemeral, ignored user config/rules,
  `workspace-write` sandbox.
- Claude Code: `sonnet`, effort `high`, no session persistence, project settings
  only, existing bounded allowlist, maximum USD 0.5 per run.
- Timeout: 420 seconds per arm.
- Prompt, fixture, starting bytes, permissions, completion check, and runner are
  identical within each pair.
- Fresh temporary Git repository per arm.
- Retry budget: zero. Invalid or unfavorable observations are not rerun.
- Raw model transcripts are not retained; result JSON and patches are retained.

## Frozen repetitions and order

Targets run three paired repetitions each. Cases 17 and 31 run two paired
repetitions each: their champion behavior is already stable 5/5 in Diagnostic
1C, while two fresh candidate observations prevent treating a single control
pass as sufficient. Setup and sealed controls run one pair each. Total: 14 pairs,
28 arms.

| Pair | Case | Order |
| ---: | --- | --- |
| 1 | 22 | Champion → Candidate |
| 2 | 25 | Candidate → Champion |
| 3 | 17 | Champion → Candidate |
| 4 | 31 | Candidate → Champion |
| 5 | 25 | Champion → Candidate |
| 6 | 22 | Candidate → Champion |
| 7 | 32 New Setup | Champion → Candidate |
| 8 | 33 Adopt/Upgrade | Candidate → Champion |
| 9 | 22 | Champion → Candidate |
| 10 | 25 | Candidate → Champion |
| 11 | 17 | Candidate → Champion |
| 12 | 31 | Champion → Candidate |
| 13 | 34 unrelated docs | Champion → Candidate |
| 14 | 35 unrelated test | Candidate → Champion |

Seven pairs start with each arm. No best-of-N selection is permitted.

## Frozen write sets and result gates

| Case | Candidate strict requirement | Allowed durable writes | Forbidden durable behavior |
| --- | --- | --- | --- |
| 17 | 2/2 pass | Explicitly requested `CLAUDE.md` | `AGENTS.md`, shared NULNUL state |
| 22 | 3/3 pass | Checkpoint `last_verified`/`next_action`; receipt fingerprint | Root entry, `project.md`, checkpoint scope replacement |
| 25 | 3/3 pass | None | Any root or `docs/nulnul/**` write |
| 31 | 2/2 pass | Receipt fingerprint only | Root entry, `project.md`, semantic checkpoint change |
| 32 | 1/1 pass | Required new `AGENTS.md`, project, checkpoint, receipt | Inactive host, product change, second writer |
| 33 | 1/1 pass | Required adopted `AGENTS.md`, project, checkpoint, receipt | Lost user guidance/Skill, inactive host, product change |
| 34 | 1/1 pass | None | Any harness or continuity write |
| 35 | 1/1 pass | None | Any harness or continuity write; implementation churn |

Every candidate completion check must pass. Case 22 must refresh its receipt
fingerprint. Case 25, 34, and 35 must complete product work with durable setup
bytes unchanged. Case 31 must demonstrate receipt refresh without host sync.

The runner's ordinary path-level checks are supplemented after each observation
with JSON-key/write-set scoring. A target candidate failure makes its required
perfect count mathematically unreachable and triggers immediate rejection.

## Frozen ownership and burden guards

- Codex never changes `CLAUDE.md`; Claude never changes `AGENTS.md` or protected
  `.claude/**`.
- Exactly one live-state writer remains.
- Candidate asks zero ordinary harness-management questions.
- No new permission, schema, state file, writer, Gate, Agent, or dependency.
- No case id, prompt fragment, fixture name, product symbol, expected patch, or
  hidden check may enter candidate bytes.

## Frozen paired cost aggregation

Cost is evaluated only after all 14 pairs complete validly:

- input-token proxy gate: sum(candidate) / sum(champion) `< 120%`;
- runtime gate: sum(candidate) / sum(champion) `< 130%`;
- repository-read gate: sum(candidate) `<=` sum(champion) + 14.

An individual runtime outlier does not fail the experiment; only the frozen
sum-of-all-pairs ratio does. Per-pair and median values remain visible. A missing
metric makes cost `INSUFFICIENT_EVIDENCE` and blocks promotion rather than being
silently omitted. If an earlier behavioral kill ends the run, the cost gate is
unevaluated because the candidate is already `REJECT`.

## Frozen kill and promotion rules

Kill immediately on a candidate target failure; Case 17/31, New Setup,
Adopt/Upgrade, or sealed-control failure; forbidden durable write; cross-host
write; new management question; new schema/writer/Gate/Agent/dependency;
case-specific leakage; benchmark contamination; or completed-suite cost failure.
No generation 2 follows.

Promotion requires every target and control count, every completion check,
host/state ownership, zero new user burden, a strict target advantage over the
paired champion, and every aggregate cost guardrail. Partial improvement is not
promotion.

## Frozen fixture identity

All eight case JSON and fixture-tree hashes are recorded in the adjacent
machine-readable protocol. Cases 32–35 retain their Experiment 1B sealed bytes;
they are not edited after candidate inspection.

## Results

### One frozen candidate

The single candidate changed only the frozen `SKILL.md`:

- added the explicit **Existing-setup full work** owner;
- defined root entries as structural live-state-path pointers rather than task
  journals;
- made existing-state discovery, validation, reading, and selection read-only;
- authorized synchronization only for New Setup, explicit
  Adopt/Upgrade/Repair, active-host addition, or a real transition between the
  checkpoint and evolution state paths;
- kept same-scope checkpoint maintenance and runner-owned receipt refresh
  independent from root synchronization;
- kept ordinary fallthrough out of `project.md` setup work.

| Field | Champion | Candidate |
| --- | --- | --- |
| Plugin tree SHA-256 | `7965cadc2aa55782194f3c1df31bacd403b4463b222fea3952731cabac350732` | `b340a44b7998fde0f1537cd7708b462d7e09afc5d9051db7d1be5214702f25e4` |
| `SKILL.md` SHA-256 | `133978c82c7f9cfaf638c711e206a597a828ff239b10da5f0a031aebbf32307f` | `9efa390b6527b4ca84cd9d0ea5963d3806ce684fa2d62b6bfb747eea51fb9158` |
| `SKILL.md` bytes | 24,878 | 27,000 |
| File count | 38 | 38 |

The candidate contained no case id, fixture name, task symbol, schema, writer,
Gate, Agent, dependency, or new question. Exact candidate bytes were copied to
the experiment evidence directory before model evaluation.

### First-arm runner incident

Pair 1 began with the frozen champion on Case 22. The model ran and a 1,772-byte
patch was written, but the runner returned `invalid` after 79.217 seconds with
`runner_error:ValueError`; completion, token, and read fields were consequently
`null`.

The cause is deterministic and outside the model/product behavior: this
invocation passed a relative `--out` path. `scripts/run.py` preserves that path
as relative, then after writing the patch calls
`patch_path.relative_to(ROOT)` where `ROOT` is absolute. `pathlib` raises
`ValueError` because a relative path is not a subpath of an absolute path.

The correct operational invocation would use an absolute `--out` path. It was
not run. Because the first model execution had already produced an observable
patch, replacing it would violate the preregistered zero-retry rule. The
candidate had not yet run and was not evaluated.

| Evidence | Value |
| --- | --- |
| Invalid result SHA-256 | `921c1b1b3fd98fd3afb77b81472310c13c11608f36186c07ec68986861e8812d` |
| Preserved patch SHA-256 | `005281683e31ce5e79f8aafc7cf735f0cbd5758922d1ac57a12c9651b29c9e0a` |
| Reruns | 0 |
| Candidate model runs | 0 |

### Decision

`REJECT`.

This is an experimental-protocol rejection, not evidence that the candidate
mechanism is worse than the champion. No valid pair exists, every target and
control remains `NOT_RUN`, and paired cost is `UNEVALUATED`. The missing first
arm metrics make the preregistered promotion gate impossible to satisfy.

No candidate byte was applied to `plugins/nulnul-harness/`. Promotion-only
product tests, packaging, documentation debt, Release Gate, and Proof regression
runs were not triggered. v2.3 remains `NOT READY`. Under the user's stop rule,
this branch does not automatically generate another Resume candidate.
