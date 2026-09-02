# Diagnostic 1D — Shared Setup-Synchronization Locus

Status: `COMPLETE`
Completed at: `2026-08-26T17:51:09+09:00`
Product-change budget: zero
Candidate-generation budget: zero

This diagnostic isolates the instruction/routing locus behind the stable
`UNRELATED_HOST_SYNC` fingerprint in Cases 22 and 25. It preserves Experiment
1 (`REJECT`), Experiment 1B (`MODE GAP PROVEN`, candidate `REJECT`), and
Diagnostic 1C (`CASE22_AND_CASE25_STABLE_DEFECTS`) without reinterpretation.

## Frozen champion and evidence boundary

| Field | Frozen value |
| --- | --- |
| Source revision | `cee7b91e2a992adee1582702b7a4084c631443b6` |
| Archive SHA-256 | `48a819a3878c9611487a4a632d9a62d1c9bda403f5dbca224466082ada26136b` |
| Frozen `SKILL.md` SHA-256 | `133978c82c7f9cfaf638c711e206a597a828ff239b10da5f0a031aebbf32307f` |
| Benchmark revision | `a3599dcbba975e1696a5fd4ca68f6f822d86d572` |
| Diagnostic 1C repetitions | 5 fresh champion runs per case; 20 total |

The champion was inspected from a fresh extraction of the frozen archive, not
from the mutable product worktree. Case traces below use the immutable
Diagnostic 1C results and patches.

Diagnostic 1C deliberately did not retain raw model transcripts, command event
streams, or ordered file-read paths. Therefore the exact first durable action,
the immediately preceding read, and literal script invocation are `UNKNOWN`.
This report does not reconstruct private reasoning. It attributes behavior from
contracts, scripts, prepared bytes, patches, changed JSON keys, and final output
signatures. In particular, a byte-exact writer output is strong execution-path
evidence but not a retained command event.

## Instruction graph

The relevant frozen contract forms this graph:

```text
USER TASK
  |
  | SKILL.md:36 — validate checkpoint before broad inspection
  v
RESUME CHECK
  |
  +-- eligible + same scope/files/permissions
  |      |
  |      | SKILL.md:36 — bounded reads; runner once; stop
  |      v
  |   FAST PATH -------------------------------------+
  |                                                  |
  +-- stale / outside scope / missing / changed      |
         | SKILL.md:36 — fall through                |
         v                                           |
FULL WORKFLOW                                        |
  | SKILL.md:43-46 — exactly one of Fast, Adopt, New |
  | (no named ordinary existing-setup full-work owner)
  v
SETUP SUFFICIENCY
  | SKILL.md:53 — Step 8 only when setup is missing or
  | materially insufficient; adapt user guidance
  | project-files.md:35,65-83 — day-one/state ownership
  v
SHARED STATE OBSERVED / SELECTED
  | SKILL.md:24 — after shared state exists, sync
  | SKILL.md:54 — after creating or selecting state, sync
  v
HOST ENTRY SYNC / GUIDANCE ADAPTATION
  | sync_host_entry.py:113-153 — structural preconditions,
  | active-host managed-block merge
  v
CONTINUE PRODUCT WORK
  | SKILL.md:56 — runner owns receipt
  | SKILL.md:57 — checkpoint before boundary/transition
  v
CHECKPOINT INTENT UPDATE? -----> RECEIPT REFRESH
                               run_checkpoint_check.py:25-74
```

The arrows and their permitting conditions are:

| Transition | Exact contract locus | What it permits |
| --- | --- | --- |
| Task → resume check | `SKILL.md:36` | Validate pointed checkpoint before broad inspection. |
| Resume check → full workflow | `SKILL.md:36` | Fall through for stale evidence, outside scope, missing files, permission change, or evolution feedback. |
| Full workflow → mode | `SKILL.md:43-46` | Choose exactly one of three modes; no mode owns valid-setup ordinary fallthrough. |
| Mode → setup sufficiency | `SKILL.md:53` | Apply project files if setup is missing or “materially insufficient”; adapt user-owned guidance. |
| Existing state → host synchronization | `SKILL.md:24,54` | State existence or selection is sufficient textual trigger; neither clause requires creation, pointer change, explicit repair, or adoption. |
| Synchronization → root write | `sync_host_entry.py:113-153` | Given one state and a valid active-host entry, merge/update the managed block. The script has no task-scope input. |
| Product work → checkpoint intent | `SKILL.md:57`; `baseline-kernel.md:6` | Record/checkpoint live continuation, without a closed ordinary-fallthrough ownership boundary. |
| Checkpoint check → receipt | `SKILL.md:56`; `project-files.md:83`; `run_checkpoint_check.py:25-74` | Execute the checkpoint's exact command and atomically refresh verification status/receipt. |

## Passing/failing divergence

| Stage | Case 17 | Case 22 | Case 25 | Case 31 |
| --- | --- | --- | --- | --- |
| Explicit setup/guidance outcome | Yes: repair `CLAUDE.md` | No | No | No |
| Checkpoint initially present | No | Yes, stale receipt after sealed file overlay | Yes, fresh arithmetic state | Yes, fresh matching state |
| Fast path eligible for requested task | N/A | No: stale files | No: outside milestone | Yes initially; product change then stales receipt |
| Full workflow entered | Direct ordinary repair, no NULNUL activation detected | Yes, 5/5 | Yes, 5/5 | No broad setup path required |
| Existing setup treated read-only | N/A | No: root guidance changed 5/5 | No: root and continuity changed 5/5 | Yes |
| `project.md` touched | No | No | Created 2/5 | No |
| Checkpoint selected/relied upon | No | Yes | Yes before replacement | Yes |
| Checkpoint semantic fields replaced | No | No; only `last_verified` and `next_action` changed | Yes, goal/milestone/check/files/last/next 5/5 | No |
| Receipt refreshed | No | Yes, fingerprint only 5/5 | Yes, files and fingerprint 5/5 | Yes, fingerprint only 5/5 |
| Host entry changed | Requested `CLAUDE.md` repair 5/5 | Unrequested manual `AGENTS.md` variant 5/5 | Unrequested `AGENTS.md` 5/5 | No, 5/5 |
| Exact deterministic sync output | No | No, 0/5 | Yes, 4/5 | No |
| Strict / completion | 5/5 / 5/5 | 0/5 / 5/5 | 0/5 / 5/5 | 5/5 / 5/5 |

The earliest **shared harmful** divergence is after fallthrough but before a
writer: the workflow has no read-only ordinary existing-setup owner, then
allows existing state selection/setup-sufficiency interpretation to activate
root-guidance and continuity maintenance. This is more specific than “Fast Path
failed.” The final executors diverge—Case 22 hand-adapts guidance while Case 25
usually emits the deterministic managed block—but both are permitted by the
same incomplete mode partition plus broad downstream mutation trigger.

## Observable case traces

### Case 17 — explicit guidance repair

- Task explicitly requested replacing the stale `nose` command in `CLAUDE.md`.
- No NULNUL state existed and NULNUL activation was not detected in any run.
- First durable action and command order: `UNKNOWN` (not retained).
- Final durable write: requested `CLAUDE.md` only, 5/5.
- No checkpoint runner, host synchronizer output, project contract, or shared
  state was present.
- Classification: legitimate product/guidance ownership, not the faulty route.

### Case 22 — stale same-scope fallthrough

- The prepared receipt was stale because the sealed overlay changed the named
  totals files; fast path correctly had to fall through.
- NULNUL activation was detected 5/5.
- First durable action, immediately prior instruction read, and exact script
  command invocations: `UNKNOWN`.
- Product fix completed 5/5.
- Checkpoint changes were limited to `last_verified` and `next_action`; receipt
  changes were limited to its fingerprint. Those are compatible with the task's
  explicit request to refresh same-scope verified state.
- `AGENTS.md` changed 5/5, always as a hand-authored one-line clarification or
  task fact. None had managed-block markers or matched `sync_host_entry.py`.
- `project.md` was not created.
- Attribution: setup/host-guidance maintenance became active even though no root
  guidance repair or state-pointer transition was requested.

### Case 25 — unrelated product-task fallthrough

- The fresh arithmetic checkpoint was valid but outside the requested CLI task,
  so fast path correctly had to fall through.
- NULNUL activation was detected 5/5.
- First durable action, immediately prior instruction read, and literal command
  invocation: `UNKNOWN`.
- Product work completed 5/5.
- `AGENTS.md`, checkpoint, and receipt changed 5/5; `project.md` was created 2/5.
- Checkpoint goal, milestone, completion command, verification files,
  `last_verified`, and `next_action` were replaced 5/5 with CLI scope.
- Four of five final `AGENTS.md` files exactly equal the frozen
  `sync_host_entry.py` merge result, including its managed block. This is strong
  evidence for the instructed synchronization path (or byte-identical
  reproduction), while the absent command stream prevents claiming the literal
  invocation as observed.
- Attribution: the proven mode gap admits setup re-entry; state existence or
  selection then activates the broad synchronization trigger, and broad
  checkpointing replaces unrelated continuity intent.

### Case 31 — bounded same-milestone refresh

- The fresh checkpoint matched the task and declared files.
- NULNUL activation was detected in 3/5 runs; all five followed the correct
  bounded write behavior.
- First durable action and literal runner command: `UNKNOWN`.
- Product files changed and only the receipt fingerprint changed durably, 5/5.
- Checkpoint semantic keys, host entry, and `project.md` stayed byte-identical.
- Attribution: runner-owned verification refresh already operates independently
  of host synchronization and checkpoint-intent replacement.

## Executor analysis

### Host synchronization

**Documented invocation conditions:** the frozen top-level contract says “after
shared state exists”; Step 8 says “after creating or selecting” the shared state.
The deterministic script itself checks only host identity, root shape, exactly
one regular shared state, a non-symlink target, and an unambiguous managed block.

**Writer decision:** `VALID_EXECUTOR / INVALID_INVOCATION` for harmful runs.
Given its documented structural inputs, `sync_host_entry.py` correctly preserves
user text, touches only the active host, fails closed on invalid state topology,
and is idempotent. It cannot decide whether the task authorizes synchronization
because task relevance, workflow mode, and pointer transition are not inputs.

Case 25 matches the writer's exact output 4/5. Case 22 does not match it 5/5,
so the shared defect is broader than a script call: active-host guidance
maintenance itself is being activated without an authorizing setup transition.

### Checkpoint write

`checkpoint.json` is Navigator-owned intent state. In the frozen contract it
owns goal, milestone, exact completion check, bounded files, status, last result,
next action, permissions, and blockers. The Case 22 same-scope updates touch only
the last-result/next-action fields and are compatible with the explicit refresh
request. Case 25 replaces every scope-defining field despite the task being
outside that checkpoint; that is an invalid upstream routing/ownership decision.

`run_checkpoint_check.py` does not choose a goal, milestone, command, file set,
or next action. It executes whatever checkpoint the upstream route supplied and
updates verification status plus the receipt. Therefore it is also a valid
executor whose Case 25 input scope was invalid upstream.

### Receipt refresh

The receipt is owned solely by `run_checkpoint_check.py`. Cases 22 and 31 show a
legitimate fingerprint-only refresh, and Case 31 proves this can occur without a
host-entry write or semantic checkpoint replacement. Case 25's receipt changes
are downstream of the unauthorized checkpoint replacement, not evidence that
receipt refresh inherently requires synchronization.

### `project.md`

The contract assigns `project.md` stable setup evidence, not live task intent.
It belongs to New Setup, explicit Adopt/Upgrade, or a material change in durable
setup/capability topology. Its absence alone during ordinary product fallthrough
does not establish adoption authority. Case 25's 2/5 creation rate supports
unnecessary setup-completeness re-evaluation, but because Case 22 never created
it, `project.md` is not the shared executor-level cause.

## “Create or select” analysis

The exact broad triggers are present twice:

- `SKILL.md:24`: after shared state **exists**, run host sync.
- `SKILL.md:54`: after **creating or selecting** the state, run host sync.

1. Yes. Ordinary fallthrough must inspect/select an existing checkpoint to
   reject or delimit it, and the text makes that read/routing operation satisfy
   the same trigger as creation.
2. Selection is observational. Synchronization is a durable write and needs a
   structural setup transition: creation, explicit adoption/repair, host-entry
   addition, or a real change to the selected live-state pointer.
3. Case 25 strongly matches this interpretation: 4/5 entries are exact writer
   outputs after an existing checkpoint was selected and replaced. Case 22
   matches the broader behavioral permission but not the deterministic executor:
   it hand-adapted the existing entry 5/5.
4. Cases 17 and 31 do not contradict it. Case 17 explicitly owns guidance repair
   and has no shared state. Case 31 never enters the full setup-selection route
   and refreshes only runner-owned evidence.

H1 is therefore **supported but incomplete**: it explains the synchronization
trigger, especially Case 25, but not the full mode/continuity replacement path or
Case 22's hand-authored edits by itself.

## Step-8 activation analysis

Textually, entering the full workflow does not automatically activate Step 8;
`SKILL.md:53` conditions it on setup being “missing or materially insufficient.”
Structurally, however, the contract is ambiguous:

- the three-mode partition has no owner for valid-setup full fallthrough;
- “materially insufficient” has no closed boundary for an existing checkpoint
  and usable root instruction when `project.md` is absent;
- the same paragraph says to adapt user-owned guidance;
- its nested state-selection clause activates sync even for an existing state;
- top-level `SKILL.md:24` independently repeats an existence-based trigger.

The behavior is accordingly conditional in prose but effectively re-openable in
ordinary fallthrough. Case 25's `project.md` creation 2/5 and exact managed-block
sync 4/5 show Step-8/setup behavior becoming active. Case 22's no-project,
manual-root-edit path shows that completing the mode partition alone is not
sufficient to close every downstream host-guidance trigger.

Experiment 1B is direct bounded evidence: its explicit existing-setup mode made
one Case 25 observation clean, but Case 22 still changed `AGENTS.md` and killed
the candidate. The candidate also narrowed the top-level trigger but left the
nested “creating or selecting” clause in place. Experiment 1's generic relevance
wording narrowed both clauses yet still allowed the resume-themed Case 22 task to
be interpreted as guidance relevance. Those candidates remain rejected; this
diagnostic does not promote or retry them.

## Durable write ownership model

| Durable file | Existing legitimate mutation owner | Not sufficient authorization |
| --- | --- | --- |
| `AGENTS.md` / `CLAUDE.md` | Initial setup; explicit adoption/upgrade; explicit guidance repair; new active-host entry; real shared-state pointer transition, active host only | Fast-path failure; state existence/selection; product or receipt change; active-host ownership alone |
| `checkpoint.json` | Single Navigator writer on a real goal/milestone, exact check/files, next action, permission, blocker, or verified-status transition inside that continuity scope | Unrelated product completion; repository-wide inspection; checkpoint presence |
| `checkpoint.verification.json` | Completion runner when the recorded check/files need verified, failed, or refreshed evidence | Setup completeness; host synchronization; an unrelated newly chosen task scope |
| `docs/nulnul/project.md` | New Setup, explicit Adopt/Upgrade, or a material durable setup/capability-topology change | Its absence during ordinary work; stale receipt; unrelated product task |
| `evolution.json` | Its one governed writer after reproduced feedback and the existing Gate lifecycle | Ordinary fallthrough or state discovery |

Host ownership answers **which host may write a root file**. It does not answer
**whether this task authorizes a root write**. Checkpoint selection answers
**which state was inspected**. It does not itself create a state transition.

## Competing hypotheses and causal decision

| Hypothesis | Evidence for | Evidence against / limit | Decision |
| --- | --- | --- | --- |
| H1 — Step-8/create-or-select scope ambiguity | Exact broad clauses; Case 25 writer signature 4/5 | Case 22 never matches the writer output; mode/relevance candidates did not solve it | Partial contributor |
| H2 — setup completeness re-evaluated | No named existing-setup mode; Case 25 creates `project.md` 2/5 | Case 22 creates no project contract | Partial contributor |
| H3 — verification and sync coupled | Failures include receipt and root writes | Case 31 receipt-only 5/5; Case 22 historically achieved receipt-only; scripts are separate | Rejected as primary locus |
| H4 — mode gap plus secondary trigger | Experiment 1B proves gap and fixes one Case 25; Case 22 survives via downstream root-guidance path; duplicated broad triggers remain | Ordered command traces unavailable, so exact clause attribution is contract-level rather than event-level | Best supported |
| H5 — deterministic writer defect | Harmful Case 25 entries often equal writer output | Script satisfies its structural contract and lacks relevance input; Case 22 bypasses its output | Rejected |

**Causal locus: `LOCUS_D — MODE_GAP_PLUS_SECONDARY_TRIGGER`.**

The mode gap makes unrelated existing-setup work susceptible to setup re-entry.
The secondary trigger is a non-closed host/continuity mutation boundary:
existing shared-state existence or selection can activate synchronization, and
host ownership/guidance adaptation can be mistaken for task-level write
authorization. A stale same-scope task can reach that secondary boundary even
when explicit mode classification protects an unrelated task. This is the
smallest locus that explains both stable failures and both passing controls
without treating the deterministic writers as causal.

Confidence is **high for the contract/routing locus** and **limited for exact
event ordering**, because command and ordered-read events were not retained.

## Counterfactual explanation

- **Case 17:** an explicit user request owns the `CLAUDE.md` repair. Closing
  ordinary state-selection triggers does not prohibit that requested guidance
  mutation.
- **Case 22:** stale same-scope evidence requires full product inspection and a
  receipt refresh; it may also update checkpoint-owned last/next fields. Merely
  selecting that checkpoint must not turn its already-usable `AGENTS.md` into a
  setup or task-note output. The current secondary trigger permits exactly that
  harmful transition.
- **Case 25:** the task is outside the checkpoint. The missing full-work owner
  exposes it to setup re-entry; broad state-selection/synchronization and broad
  end-of-work checkpointing then rewrite the root entry and continuity scope.
- **Case 31:** the task is inside the verified milestone. It remains on the
  bounded path, changes named product files, and independently refreshes the
  runner-owned receipt. No setup or host-pointer transition occurs.

## Next experiment preregistration draft — do not implement

### Hypothesis

> If ordinary existing-setup fallthrough has an explicit owner **and** root-entry
> synchronization is a single structural setup transition rather than an effect
> of existing-state selection or task-themed guidance relevance, Cases 22 and 25
> will preserve their root entries while completing product work; Case 22 and
> Case 31 will still refresh owned verification, and explicit repair/New
> Setup/Adopt-host transitions will still synchronize correctly.

This is not a retry of Experiment 1's generic state-write relevance wording or
Experiment 1B's mode-only candidate. It tests the measured combination: complete
the mode owner and eliminate the duplicated downstream “exists/selects” root
trigger in favor of one structural host-entry transition.

### Frozen inputs and budget

- Champion: archive
  `48a819a3878c9611487a4a632d9a62d1c9bda403f5dbca224466082ada26136b`,
  revision `cee7b91e2a992adee1582702b7a4084c631443b6`.
- One candidate generation; retry budget zero.
- Same model, host, permissions, timeout, runner revision, and fresh prepared
  bytes as Diagnostic 1C; counterbalanced paired order.

### Targets

- Cases 22 and 25: three independent paired champion/candidate repetitions each.
- Candidate target completion: 6/6.
- Case 22: no `AGENTS.md` or `project.md`; receipt fingerprint refresh required;
  checkpoint changes, if any, restricted to `last_verified` and `next_action`.
- Case 25: product files only; every durable state byte unchanged.

### Positive controls

- Case 17: one paired run; requested `CLAUDE.md` repair remains allowed.
- Case 31: one paired run; receipt-only refresh remains required.
- Existing true New Setup control 32 and explicit Adopt/Upgrade control 33: one
  paired run each; their required setup synchronization remains allowed.

### Sealed controls

Freeze before candidate generation:

1. Existing canonical setup + same-scope product change that stales only the
   receipt: expected product + receipt, no host-entry/setup write.
2. Existing shared state + explicit second-host adoption: expected new active
   host entry only; inactive entry and checkpoint semantics byte-identical.

These are structural controls, not Case 22/25 wording variants.

### Candidate concept and likely file

- Start from the frozen champion, never either rejected candidate.
- Give ordinary valid-setup fallthrough a reusable full-work owner.
- Treat shared-state observation/selection as read-only.
- Make host synchronization one structural action owned only by New Setup,
  explicit Adopt/Upgrade or guidance repair, adding the active host, or a real
  shared-state pointer change. A product/receipt/checkpoint-content change does
  not alter that pointer.
- Keep runner-owned receipt refresh independent.
- Keep checkpoint intent updates scoped by the workflow owner.
- Likely change: frozen `SKILL.md` only. No script, schema, reference, writer,
  Gate, Agent, or persistent instrumentation unless diagnosis is disproved
  before candidate generation.

### Cost guardrail

Across all 12 completed pairs, candidate input-token proxy must be below 120% of
champion, runtime below 130%, and repository reads no more than champion plus one
per pair. Add no always-loaded file. Report per-case values; missing values stay
`null`. These reuse the preregistered Experiment 1B ceilings and are not tuned to
future results.

### Kill and promotion conditions

Kill on any target completion failure; any candidate host write in Case 22 or
durable write in Case 25; any Case 17/31/setup/sealed control regression;
inactive-host mutation; new user harness-management question; new schema/writer/
Gate/Agent/dependency; case-specific string; fixture leakage; contamination; or
cost-bound violation. No generation 2 follows.

Promote only if all six target repetitions pass strict and completion checks,
the candidate exceeds its paired champion on the declared strict failure
dimension, every positive and sealed control passes, ownership remains intact,
and all cost ceilings pass. Partial improvement is `REJECT` or `NO_ADVANTAGE`,
not promotion.

## Final decision

- Product changes: `0`.
- Candidate bytes generated: `0`.
- Deterministic scripts executed on product: `0`.
- Historical evidence rewritten: `0`.
- Experiment 1: `REJECT`, unchanged.
- Experiment 1B: `MODE GAP PROVEN`; candidate `REJECT`, unchanged.
- Diagnostic 1C: `CASE22_AND_CASE25_STABLE_DEFECTS`, unchanged.

`STOP` — no candidate, Capability Survivor / Retirement, Live Skill Evolution,
v2.4, research pass, release, or publication follows this diagnostic.
