# Experiment 1 — Resume Fallthrough State Preservation

Status: `PREREGISTERED`
Preregistered at: `2026-08-26T06:49:49Z`
Generation budget: one bounded first-generation candidate
Retry budget: zero
Scope: Cases 17, 22, 25, and corrected Case 31 only

The hypothesis, target/guardrail checks, cost boundary, arm order, and initial
failure-locus diagnosis below were frozen before candidate generation. Later
sections may append immutable run results and the final decision; the
preregistration itself must not be rewritten after exposure.

## Frozen champion and historical evidence

The champion is the exact Project-Fit Proof archive, not the mutable worktree.

| Field | Frozen value |
| --- | --- |
| Candidate id | `outcome-first-project-fit-proof-2026-08-26` |
| Source revision | `cee7b91e2a992adee1582702b7a4084c631443b6` with the recorded dirty candidate tree |
| Archive | `../nulnul-benchmarks/candidates/project-fit-proof-frozen/nulnul-harness-2.2.1.zip` |
| Archive SHA-256 | `48a819a3878c9611487a4a632d9a62d1c9bda403f5dbca224466082ada26136b` |
| Archive files | 38 |
| Frozen `SKILL.md` SHA-256 | `133978c82c7f9cfaf638c711e206a597a828ff239b10da5f0a031aebbf32307f` |
| Benchmark revision | `a3599dcbba975e1696a5fd4ca68f6f822d86d572` |
| Benchmark amendment manifest | `e2f8b0a45a66417f5240571ef7e811ca35427c7331153c4ec9ffe3b7b2c95967` |

The exact v2.2.1 and Vanilla results remain historical context and are not tuning
arms. Original invalid cases remain preserved. These rejected candidates remain
immutable inputs to the diagnosis:

- `resume-state-preservation-v1` — `REJECT`, target 0/4.
- `resume-state-preservation-v2` — `NARROWER_SCOPE`, Case 25 improved 2/2 but the
  full family criterion failed.
- `different-task-state-preservation-v1` — `REJECT`, Case 25 improved 2/2 but the
  Case 22 guardrail fell from 1/2 to 0/2.

## Preregistered hypothesis

> Separating fast-path validity from durable continuity-state write authorization
> will allow NULNUL to fall through safely when the checkpoint cannot be used
> directly, while mutating `AGENTS.md` / `CLAUDE.md` / checkpoint / verification
> state only when the current task materially invalidates or advances that durable
> state.

Expected result:

- Cases 22 and 25 pass their strict boundaries in both candidate rounds.
- Cases 17 and 31 remain correct in both candidate rounds.
- Completion remains 8/8 across the candidate's two four-case rounds.
- No state, schema, writer, role, dependency, or user question is added.
- Candidate context/runtime remains below the frozen cost boundary.

This is not a general “write less state” rule. Fast-path eligibility controls how
much old state can be trusted and read. State-write relevance controls whether the
current task may change durable continuity state.

## Two decisions under test

### A. Resume eligibility

The current state may be used as the bounded fast path only when its validation,
task scope, named files, and permission boundary match. A `NO` answer falls through
to the full workflow; it grants no write authority by itself.

### B. State-write relevance

After fallthrough, a durable write is relevant only when the current task
materially changes an owned goal/milestone, owned verification file or exact check,
permission boundary, or verified next action. A truthful host pointer is changed
only when it is false or the task explicitly requires that host guidance change.

These are decision criteria, not a new permission engine or exception table.

## Pre-candidate trace and expected write sets

The first trace uses the preserved exact-champion Proof records and patches. Round
1 champion runs will reproduce these paths freshly before the candidate bytes are
generated.

### Case 17 — stale Claude instruction

| Field | Trace |
| --- | --- |
| Current task | Fix `split_words()` and explicitly replace stale `CLAUDE.md` test guidance. |
| Checkpoint status | No checkpoint/evolution state. |
| Fast path eligible? | Not applicable. |
| Why? | This is a direct product plus host-guidance task, not resume. |
| Durable files actually touched | `CLAUDE.md`. |
| Durable files that should be touched | `CLAUDE.md`, because the user explicitly requested its repair. |
| Product files changed | `words.py`. |
| Verification files changed | None. |
| Expected state-write set | `CLAUDE.md`: `EXPECTED WRITE`; every Codex-owned entry and `docs/nulnul/**`: `EXPECTED NO-WRITE`. |
| Actual state-write set | `CLAUDE.md`. |
| Failure locus | None; positive host-ownership/direct-request control. |

### Case 22 — stale verification files, same goal

| Field | Trace |
| --- | --- |
| Current task | Reject stale evidence, fix `total([])`, run the full check, refresh verified state. |
| Checkpoint status | Schema 3 and previously verified, but the prepared receipt fingerprint is stale after `totals.py` and `test_totals.py` change. |
| Fast path eligible? | No. |
| Why? | Owned verification files no longer match the receipt. |
| Durable files actually touched | `AGENTS.md`, `checkpoint.json`, `checkpoint.verification.json`. |
| Durable files that should be touched | `checkpoint.verification.json`; `checkpoint.json` only if an owned field genuinely changes, not merely to narrate the fix. |
| Product files changed | `totals.py`. |
| Verification files changed | `totals.py`; `test_totals.py` was already the prepared regression check. |
| Expected state-write set | Receipt: `EXPECTED RECEIPT REFRESH`; checkpoint: conditional owned-field write; `AGENTS.md`, `CLAUDE.md`, `project.md`, `evolution.json`: `EXPECTED NO-WRITE`. |
| Actual state-write set | `AGENTS.md`, semantic checkpoint rewrite, receipt refresh. |
| Failure locus | `SKILL routing`; full-workflow state actions lack a relevance boundary. `project-files` wording contributes, but deterministic writers behaved as invoked. |

### Case 25 — different task outside checkpoint scope

| Field | Trace |
| --- | --- |
| Current task | Add CLI JSON output; the checkpoint owns only the arithmetic helper. |
| Checkpoint status | Valid, verified, and fresh for `app.py` / `test_app.py`. |
| Fast path eligible? | No. |
| Why? | The CLI task is outside the checkpoint goal and milestone. |
| Durable files actually touched | `AGENTS.md`, `checkpoint.json`, `checkpoint.verification.json`. |
| Durable files that should be touched | None. |
| Product files changed | `cli.py`, `test_cli.py`. |
| Verification files changed | `test_cli.py`, but it is not owned by the existing checkpoint. |
| Expected state-write set | All root entries and `docs/nulnul/**`: `EXPECTED NO-WRITE`. |
| Actual state-write set | Managed `AGENTS.md` block plus expanded checkpoint and receipt. |
| Failure locus | `SKILL routing`; task mismatch correctly causes fallthrough, but fallthrough is then treated as authority to synchronize and replace unrelated continuity state. The sync and checkpoint writers produce valid output for a wrongly routed invocation. |

### Case 31 — same named milestone

| Field | Trace |
| --- | --- |
| Current task | Change `slug()` and its focused test inside the recorded whitespace milestone. |
| Checkpoint status | Valid, verified, fresh, schema 3, matching named files and permissions before the edit. |
| Fast path eligible? | Yes. |
| Why? | Goal, milestone, files, check, and permissions match. |
| Durable files actually touched | `checkpoint.verification.json`. |
| Durable files that should be touched | `checkpoint.verification.json`. |
| Product files changed | `slug.py`, `test_slug.py`. |
| Verification files changed | Both owned verification files. |
| Expected state-write set | Receipt: `EXPECTED RECEIPT REFRESH`; all root guidance, `project.md`, checkpoint semantics, and evolution state: `EXPECTED NO-WRITE`. |
| Actual state-write set | Receipt refresh only. |
| Failure locus | None; positive same-milestone refresh control. |

## Diagnosed candidate locus

Primary locus: `SKILL routing`.

Evidence against other loci:

- `sync_host_entry.py` deterministically writes the managed block when invoked; it
  does not decide whether the current task made invocation relevant.
- the checkpoint runner correctly refreshes the declared receipt; it does not
  choose whether an unrelated checkpoint should be expanded.
- one live writer and host ownership already exist; neither failure introduced a
  second writer.
- previous early resume-paragraph sentences could be copied into host guidance or
  be bypassed by later unconditional workflow actions. The next candidate must
  change the existing action boundary, not add another case-specific exception.

The first-generation candidate may change only the frozen `SKILL.md` decision
contract. A deterministic Python edit is forbidden unless the fresh champion
reproduction contradicts this diagnosis; such a contradiction ends this
generation as `INSUFFICIENT_EVIDENCE` rather than expanding scope.

## Evaluation-only state-write instrumentation

Every run records whether these paths changed:

- `AGENTS.md`
- `CLAUDE.md`
- `docs/nulnul/project.md`
- `docs/nulnul/checkpoint.json`
- `docs/nulnul/checkpoint.verification.json`
- `docs/nulnul/evolution.json`
- any other `docs/nulnul/**` live-state file

This is derived from existing patches and changed-file lists. No persistent product
instrumentation is added.

## Frozen protocol

| Field | Value |
| --- | --- |
| Arms | exact frozen champion vs one candidate |
| Model/host | Existing case host; Codex `gpt-5.6-sol` medium, Claude `sonnet` high |
| Timeout | 420 seconds per run |
| Permission | Existing benchmark local-write boundary |
| Retry budget | 0 |
| Rounds | 2 |
| Round 1 order | champion → candidate |
| Round 2 order | candidate → champion |
| Fixture | Existing immutable fixture copied to a fresh deterministic Git repository per run |
| Prompt | Existing case task string, identical between arms |
| Raw transcript | Not retained |

The Round 1 champion arm doubles as the required fresh pre-candidate reproduction.
Candidate bytes are generated only after all four Round 1 champion results are
recorded. Candidate generation may use those known development results, but not
candidate or Round 2 outcomes.

## Frozen success and kill criteria

### Target

- Case 22 candidate strict pass: 2/2.
- Case 25 candidate strict pass: 2/2.
- Combined target: 4/4.
- Candidate combined target passes must be strictly greater than the paired
  champion target passes; otherwise the verdict is `NO_ADVANTAGE` even when the
  candidate reaches 4/4.

### Positive controls

- Case 17 candidate strict pass: 2/2.
- Case 31 candidate strict pass: 2/2.
- Combined controls: 4/4.

### Completion and ownership

- Candidate completion: 8/8.
- Claude never changes `AGENTS.md`; Codex never changes `CLAUDE.md`.
- Existing protected `.claude/**` behavior remains unchanged.
- Exactly one live-state writer remains.
- No state/schema/writer/role/dependency is added.
- Candidate questions asked: 0.
- No hard-coded case id, fixture path, product symbol, expected patch, or hidden
  check content enters product bytes.

### Context and runtime boundary

The Research Pass preregistered the measured Project-Fit warning levels as
conservative stop boundaries. Across all eight runs per arm:

- candidate total `input_tokens` proxy must be **less than 119.7%** of its paired
  champion total;
- candidate total wall-clock runtime must be **less than 108.1%** of its paired
  champion total;
- changed frozen `SKILL.md` byte delta, repository reads, tool calls, loaded
  capability count, and runtime distribution remain visible;
- no new always-loaded file is permitted.

These thresholds are rejection ceilings derived before generation, not expected
improvements or causal claims. Passing them does not establish efficiency.

### Immediate kill conditions

Any of the following rejects the candidate:

- a Case 17 or Case 31 strict regression;
- Case 25 mutates existing root/checkpoint/receipt state;
- Case 22 fails to refresh legitimately stale owned verification;
- protected host/config mutation, permission expansion, or a new writer/schema;
- a new ordinary harness-management question;
- case-specific strings, fixture leakage, contamination, or selective retry;
- either cost ceiling is reached without the complete 4/4 target improvement;
- partial target improvement below 4/4.

Allowed terminal verdicts are `PROMOTE`, `REJECT`, `NO_ADVANTAGE`,
`NARROWER_SCOPE`, or `INSUFFICIENT_EVIDENCE`. No generation 2 follows this run.

## Candidate and results

### Runner incident

The first champion invocation passed a relative `--out` path to the existing
runner. Each agent process ran, but `run_one()` raised `ValueError` while making
the relative patch path relative to the absolute benchmark root. All four records
were therefore invalid. They are preserved as
`results/round-1-champion/invalid-invocation-relative-out.json`; none contributed
to diagnosis, generation, or scoring. Before candidate generation, the complete
champion arm was run once with an absolute output path. This was instrumentation
recovery, not a stochastic or result-selected retry.

### Fresh champion reproduction

| Case | Strict | Completion | Durable write set |
| --- | --- | --- | --- |
| 17 | pass | pass | `CLAUDE.md` |
| 22 | pass | pass | `checkpoint.verification.json` |
| 25 | fail | pass | `AGENTS.md`, checkpoint, receipt |
| 31 | pass | pass | `checkpoint.verification.json` |

Case 25 reproduced the measured task-mismatch fallthrough defect. Case 22 did not
repeat its earlier failure in this sample: the frozen champion made the expected
receipt-only refresh. This narrows the live reproduction without rewriting the
historical Proof result.

### One bounded candidate

The candidate changed only `skills/nulnul-harness/SKILL.md`:

- champion tree SHA-256:
  `7965cadc2aa55782194f3c1df31bacd403b4463b222fea3952731cabac350732`;
- candidate tree SHA-256:
  `f2ee23535b51b5553ef497756038658802de613c8e803e59e14ee9280c79a6a2`;
- candidate `SKILL.md` SHA-256:
  `211abf63c638e291a381b704e7ccff78579fce8de46c872a51e517acc6474c8c`;
- file count: unchanged at 38;
- loaded `SKILL.md` size: 24,878 to 25,641 bytes (+763 bytes).

It separated resume eligibility from write relevance in the existing host/state
action boundary, removed “selecting state” alone as a synchronization trigger, and
made step 9 apply the same relevance rule before checkpointing. It added no script,
schema, state file, writer, role, dependency, or question.

### Candidate observation and frozen stop

| Case | Champion R1 | Candidate R1 | Candidate write set | Decision |
| --- | --- | --- | --- | --- |
| 17 | pass | pass | `CLAUDE.md` | direct-request control preserved |
| 22 | pass | **fail** | `AGENTS.md`, checkpoint, receipt | unauthorized host-entry write |
| 25 | fail | not run | not observed | stopped after kill |
| 31 | pass | not run | not observed | stopped after kill |

The candidate refreshed the required Case 22 receipt and completed the product
fix, but it also inserted the deterministic managed block into `AGENTS.md`. The
first Case 22 candidate failure made its preregistered 2/2 result and the combined
4/4 target impossible. The runner was interrupted during the next case; no partial
Case 25 workspace or result was scored. Round 2 was not run.

This is evidence that the proposed natural-language boundary was not decisive
enough against the existing setup-completeness/synchronization route. Because raw
transcripts are intentionally not retained, attributing the invocation to one
specific sentence would exceed the evidence. The deterministic sync writer still
did exactly what an invocation requests; it remains outside this generation's
proven defect locus.

### Cost observation

Only the two completed paired Round 1 cases are comparable; the stopped arm cannot
produce the preregistered eight-run aggregate.

| Completed pair (Cases 17/22) | Champion | Candidate | Candidate / champion |
| --- | ---: | ---: | ---: |
| Input-token proxy | 145,940 | 377,787 | 258.86% |
| Runtime | 70.410 s | 113.584 s | 161.32% |

This single incomplete round is a warning, not a full causal cost estimate. It
does not rescue a candidate that already failed the primary target.

### Decision

`REJECT`.

The candidate produced no measured target win and regressed the only target pair
observed candidate-versus-champion. Exact candidate bytes, patch, state-write
observations, partial run, and decision are preserved under
`../nulnul-benchmarks/challengers/resume-fallthrough-state-write-authorization-v1/`.
There is no generation 2.

No candidate byte was applied to the product. The current product `SKILL.md`
remains byte-identical to the frozen champion with SHA-256
`133978c82c7f9cfaf638c711e206a597a828ff239b10da5f0a031aebbf32307f`.
Consequently the promotion-only pack, full deterministic suite, documentation-debt
check, Release Gate, and Proof regression rerun were not triggered. Artifact JSON,
hashes, and repository diff hygiene are the applicable validation for this
rejected experiment. v2.3 remains `NOT READY`.

Pending the frozen Round 1 champion reproduction.
