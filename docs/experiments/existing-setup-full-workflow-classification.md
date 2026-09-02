# Experiment 1B — Existing-Setup Full-Workflow Classification

Status: `PREREGISTERED`
Preregistered at: `2026-08-26T07:29:05Z`
Generation budget: one bounded candidate
Retry budget: zero
Product candidate generated: no

The diagnosis, fixtures, schedule, success criteria, cost limits, and kill
conditions below were frozen before candidate generation. Results may only be
appended after this section.

## Preserved Experiment 1 evidence

Experiment 1 remains `REJECT`. Its preregistration, invalid runner incident,
champion/candidate results, candidate bytes, write-set observations, and decision
remain immutable. In particular, this experiment does not reuse candidate
`211abf63c638e291a381b704e7ccff78579fce8de46c872a51e517acc6474c8c`.

The champion remains the exact Project-Fit Proof archive:

| Field | Frozen value |
| --- | --- |
| Candidate id | `outcome-first-project-fit-proof-2026-08-26` |
| Source revision | `cee7b91e2a992adee1582702b7a4084c631443b6` with its recorded dirty tree |
| Archive SHA-256 | `48a819a3878c9611487a4a632d9a62d1c9bda403f5dbca224466082ada26136b` |
| `SKILL.md` SHA-256 | `133978c82c7f9cfaf638c711e206a597a828ff239b10da5f0a031aebbf32307f` |
| Files | 38 |
| Benchmark revision | `a3599dcbba975e1696a5fd4ca68f6f822d86d572` |

## Preregistered hypothesis

> Case 25 occurs because a task that cannot use the bounded Fast Path, but
> already has a valid durable NULNUL setup, lacks an explicit ordinary
> full-workflow classification. As a result, setup-completeness and host-entry
> synchronization behavior can become active during unrelated product work.
> Completing the existing mode partition will allow full task inspection and
> execution without treating fallthrough as adoption, bootstrap, or continuity
> replacement.

This tests mode classification, not a second generation of the rejected generic
state-write-authorization wording.

## Frozen mode-partition diagnosis

The champion says to take exactly one of three workflow modes: `Fast path`,
`Adopt and upgrade`, or `New setup`. The earlier Resume Fast Path separately
requires fallthrough when verification, scope, files, or permissions do not
match. The two uses of “Fast path” do not identify an ordinary existing-setup
full-work owner after that fallthrough.

| State | Fast path? | Adopt/upgrade? | New setup? | Current actual path | Unambiguous? | Setup mutation? | Continuity mutation? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A. Fresh project, no durable setup | No | No | Yes | New setup | Yes | Yes, create justified setup | Yes, create its single checkpoint when durable continuity is needed |
| B. Existing project, explicit adoption request | No | Yes | No | Adopt and upgrade | Yes | Yes, requested outcome | Only the continuity fields created or materially upgraded by adoption |
| C. Valid setup, task inside checkpoint milestone | Yes | No | No | Bounded Resume Fast Path | Yes | No | Refresh owned receipt/state after the task invalidates it |
| D. Valid setup, stale checkpoint for same relevant task | No | No | No | Resume fallthrough, then overloaded workflow `Fast path` or setup steps | No | No | Refresh owned verification; Case 22's fresh champion did this correctly |
| E. Valid setup, unrelated ordinary product task | No | No | No | Resume fallthrough with no named owner; Case 25 entered setup synchronization and replacement | **No** | No | No |
| F. Existing setup, explicit host-guidance repair | No | Yes, because setup repair is the requested outcome | No | Explicit repair/adopt-upgrade path | Yes | Yes, only requested guidance | Only when explicitly included in the repair |
| G. Existing setup, permission change | No | No | No | Permission-triggered fallthrough with downstream permission rules | Partially; reason is clear but the full-work mode is unnamed | No | Yes, only relevant permission/check evidence |
| H. Evolution feedback requiring governed update | No | No | No | Explicit workflow step 10 evolution route | Yes | No bootstrap | Yes, governed evolution state only after reproduced feedback |

State E is outside the stated three-way partition. The wording could be stretched
to call repository-wide ordinary work the workflow `Fast path`, but that conflicts
with the earlier explicit bounded-fast-path rejection. Case 25 demonstrates that
this ambiguity is behavioral rather than terminological: product completion
passed while unrelated `AGENTS.md`, checkpoint, and receipt were rewritten.

**Mode gap: PROVEN.**

## Frozen cases and controls

### Existing immutable cases

- Target: `25-resume-required-fallthrough`.
- Positive controls: `17-stale-claude-instruction`, `22-resume-stale-files`, and
  corrected `31-resume-named-file-fast-path-v2`.

### Sealed Experiment 1B controls

Four small controlled fixtures were frozen before candidate generation:

| Case | Purpose | Case SHA-256 | Fixture tree SHA-256 |
| --- | --- | --- | --- |
| `32-new-setup-control` | True new setup creates valid project, entry, checkpoint, and receipt without product change | `8d4f434d221bdc90f511b7c947510a723732f3beffea7204e756b8c77eda5501` | `be09e59423466bdd71c8da5d2333ea513112553a0c3d09318ed2c826e0e574c7` |
| `33-explicit-adopt-upgrade-control` | Explicit adoption preserves existing guidance and project-test Skill while creating validated shared setup | `2ebd606b309c7db6c335647440a35a358b24eb5637e356391fbd40a1a8977845` | `c714b2ad25a1f828b086e58eb01e0204907d879e6a5e62b08de0317883822ca6` |
| `34-existing-setup-unrelated-doc` | Valid verified setup plus unrelated documentation work | `cfcd1abe18d396dfc693634a230d6bd3f7cf142773ba8f66b8efcc03cdb1b335` | `54dcc82092c811f5c3e50b1eefa4b56fec11f178c02eb8ced0e67aad22906291` |
| `35-existing-setup-unrelated-test` | Valid verified setup plus unrelated product-test addition | `040b12f648895fa365c8fd6435b318a43e3810b9bbaa4fafdea169f8cef60638` | `7f9cb0255781d2d4bef51ff3a623b06073783bf77026db613de3a579d1c215cb` |

Combined case tree SHA-256:
`7205528ce2f1bc96d4b9eecc536a4316a69e33814251e01bd7f688af320552e0`.
Combined fixture tree SHA-256:
`bfd2ce93775f4bb041687bf51bc889b4cfff38ba8708dda8bf5a223b2332eb75`.

Each setup control was tested against a constructed valid end state: the product
check, project validator, checkpoint validator, host-entry preservation, and
receipt checks passed. Each fresh control was tested negative before its requested
change and positive afterward while the unrelated checkpoint stayed fresh.

## Frozen protocol

| Field | Value |
| --- | --- |
| Arms | exact frozen champion vs one candidate |
| Host/model | case host; Codex `gpt-5.6-sol` medium, Claude `sonnet` high |
| Timeout | 420 seconds |
| Permission | existing local-write benchmark boundary |
| Retry | 0 |
| Raw transcript | not retained |
| Workspace | fresh deterministic Git repository per arm |

Case 25 has two counterbalanced pairs and must pass twice. Every control has one
paired observation. Order is frozen:

1. Case 25: champion then candidate.
2. Case 17: candidate then champion.
3. Case 22: champion then candidate.
4. Case 31: candidate then champion.
5. Case 32: champion then candidate.
6. Case 33: candidate then champion.
7. Case 34: champion then candidate.
8. Case 35: candidate then champion.
9. Case 25: candidate then champion.

No failed or invalid stochastic run is retried. A runner/instrumentation failure is
preserved and may be replaced only before its result is observable, with the same
arm and no selective scoring.

## Frozen success criteria

### Primary target

- Candidate Case 25 strict result: 2/2 pass.
- Candidate Case 25 completion: 2/2 pass.
- Candidate target strict passes must exceed paired champion target strict passes;
  otherwise the verdict is `NO_ADVANTAGE`.
- Both candidate target runs leave `AGENTS.md`, `CLAUDE.md`, checkpoint, receipt,
  project contract, and evolution state unchanged.

### Positive and setup controls

- Candidate Cases 17, 22, and 31: strict pass.
- Case 17 still permits its explicitly requested `CLAUDE.md` repair.
- Case 22 refreshes stale same-scope verification without an `AGENTS.md` write.
- Case 31 refreshes its same-milestone receipt.
- Candidate Case 32 creates and validates the true new setup.
- Candidate Case 33 performs explicit adoption, preserving user guidance and the
  existing project-test Skill.
- Candidate Cases 34 and 35 complete only their requested file change and preserve
  all existing setup/continuity bytes.
- Every observed candidate completion check passes.

### Architecture, ownership, and burden

- No state schema, state file type, writer, Gate, Agent, dependency, or persistent
  instrumentation is added.
- Codex never changes `CLAUDE.md`; Claude never changes `AGENTS.md` or protected
  `.claude/**`.
- Exactly one live-state writer remains.
- Candidate asks zero ordinary harness-management questions.
- No case id, fixture name, product symbol, expected patch, or hidden check enters
  candidate product bytes.

## Frozen cost guardrail

The candidate may change only the already loaded `SKILL.md`; it may add no
always-loaded file. Existing evidence used to set the limits:

- the established setup benchmark treats +20% input as regression;
- the Project-Fit warning was +19.7% input and +8.1% runtime;
- three existing Case 25 champion observations have a 19.87% runtime median
  absolute deviation, while Experiment 1's rejected observed subset was +158.86%
  input and +61.32% runtime.

Across the nine completed pairs:

- candidate input-token proxy must be less than 120% of champion;
- candidate runtime must be less than 130% of champion;
- candidate repository reads must not exceed champion by more than nine total
  reads, one per pair;
- per-case values, tool calls, and loaded `SKILL.md` byte delta remain visible.

These are ceilings, not evidence of improvement. Missing measurements remain
`null`; they are not invented or silently excluded.

## Frozen kill conditions

Immediately reject and stop generation if the candidate:

- fails either Case 25 run or rewrites its unrelated durable state;
- regresses Case 17, 22, or 31;
- fails New Setup, Adopt/Upgrade, or either fresh classification control;
- introduces a new ordinary user question, schema, writer, Gate, Agent,
  dependency, permission expansion, case string, or fixture leakage;
- contaminates the benchmark or crosses a frozen cost ceiling.

No generation 2 follows a kill. Allowed terminal verdicts are `PROMOTE`, `REJECT`,
`NO_ADVANTAGE`, `HYPOTHESIS_REJECTED`, or `INSUFFICIENT_EVIDENCE`.

## Candidate and results

### One bounded candidate

The single candidate changed only `skills/nulnul-harness/SKILL.md`:

- completed the stated three-mode partition with an explicit
  **Existing-setup full workflow** mode;
- bound host-entry synchronization to **New setup** or **Adopt and upgrade**;
- made step 9 checkpointing conditional on the selected mode's continuity scope.

It did not reuse Experiment 1's rejected write-authorization wording and added no
file, schema, writer, Gate, Agent, dependency, or deterministic behavior.

| Field | Value |
| --- | --- |
| Champion tree SHA-256 | `7965cadc2aa55782194f3c1df31bacd403b4463b222fea3952731cabac350732` |
| Candidate tree SHA-256 | `952db137abd358201782753c7a35dec04be15244ea1f5574d541024a179e5e2c` |
| Candidate `SKILL.md` SHA-256 | `e8367db6292c89c78d013da8a3cb7d4da57ab3c316cfb24fd32a866e59099dc8` |
| File count | 38 to 38 |
| Loaded `SKILL.md` bytes | 24,878 to 25,773 (+895) |

### Paired observations before kill

| Pair | Champion | Candidate | Candidate durable writes | Completion |
| --- | --- | --- | --- | --- |
| Case 25, first target | fail | **pass** | none | both pass |
| Case 17 | pass | pass | requested `CLAUDE.md` repair | both pass |
| Case 22 | fail | **fail** | `AGENTS.md`, checkpoint, receipt | both pass |

In Case 25, the candidate changed only `cli.py` and `test_cli.py`; it made no
root-entry or `docs/nulnul/**` change. The champion again changed `AGENTS.md`, the
unrelated checkpoint, and its receipt. This is one direct observation supporting
the mode-classification hypothesis.

In Case 22, however, the candidate changed the existing `AGENTS.md` sentence to
add post-change runner advice, then updated same-scope checkpoint fields and the
required receipt. The receipt refresh and product fix were correct, but the host
guidance change violated the frozen strict boundary. The paired champion also
failed this stochastic observation, but the positive control required an absolute
candidate pass because Experiment 1's fresh champion had already demonstrated the
receipt-only correct behavior.

The Case 22 failure triggered the immediate kill condition. Case 31, both setup
controls, both sealed fresh controls, and the second Case 25 pair were not run.
There is no result-selected retry and no generation 2.

### State and completion

- Candidate Case 25: expected no durable write; observed no durable write.
- Candidate Case 17: expected explicit `CLAUDE.md` write; observed that write only.
- Candidate Case 22: expected no `AGENTS.md` write; observed one.
- Observed completion: champion 3/3, candidate 3/3.
- Observed candidate questions: 0.
- No cross-host write, permission expansion, new writer, or new schema was
  observed.

### Partial cost observation

Only three of nine planned pairs completed, so the preregistered aggregate cost
gate was not evaluated.

| Completed pairs | Champion | Candidate | Candidate / champion |
| --- | ---: | ---: | ---: |
| Input-token proxy | 746,694 | 581,521 | 77.88% |
| Runtime | 248.045 s | 190.770 s | 76.91% |
| Repository reads | 12 | 13 | +1 read |

These partial values show no recurrence of Experiment 1's severe cost warning,
but they cannot establish a full-suite efficiency improvement.

### Instrumentation limitation

The two arms wrote into one result directory per pair. The existing runner gives
both arms the same patch filename, so the second arm overwrote the first arm's
patch file. Arm-specific JSON results and scoring fields remain distinct, and the
surviving candidate patches cover both the Case 25 target and Case 22 kill
observation. No run was repeated. Future paired invocations should use one patch
directory per arm; this did not affect the observed workspaces or strict scoring.

### Decision

`REJECT`.

The mode gap is proven and the candidate corrected one Case 25 observation, but a
bounded improvement that fails the Case 22 positive control cannot be promoted.
The exact candidate and decision remain under
`../nulnul-benchmarks/challengers/existing-setup-full-workflow-classification-v1/`.

No candidate byte was applied to the shipped plugin. Promotion-only product pack,
full deterministic tests, documentation debt, Release Gate, and Proof regression
runs were not triggered. v2.3 remains `NOT READY`.
