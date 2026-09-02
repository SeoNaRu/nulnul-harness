# NULNUL Experiment 7 — Bounded Lane Boundary

## Architecture decision

- Recommended architecture: Bounded Lane Architecture
- Status before experiment: architectural hypothesis, not proven
- Architecture contribution: **FAIL — infrastructure invalid before live evaluation**

The architecture hypothesis remains untested. This result does not contradict
or validate the Post-6C architecture decision.

## Champion

- Revision: `cee7b91e2a992adee1582702b7a4084c631443b6`
- Artifact SHA-256:
  `48a819a3878c9611487a4a632d9a62d1c9bda403f5dbca224466082ada26136b`
- Plugin tree SHA-256:
  `7965cadc2aa55782194f3c1df31bacd403b4463b222fea3952731cabac350732`

## Benchmark

- Predecessor durable lineage:
  `3cb512de515fc0003c285a9a7842996014207715`
- Frozen Experiment 7 revision:
  `116c5ce6347b82afe851c8f13210571f4575f12e`
- Durability: external atomic JSON/patch/report writes, SHA receipts, readback,
  lifecycle fixture gate, source/prepared fixture hashes, and zero-retry frozen
  schedule
- Deterministic pre-candidate checks: 34 pass, 0 fail
- Fresh fixture initial-state checks: 5 pass, 0 fail
- Sealed holdouts: frozen, not exposed

The frozen benchmark branch is `experiment-7-bounded-lane` in the durable
benchmark repository. External evidence is under
`/mnt/c/Users/seonaru/Desktop/nulnul-benchmark-evidence/experiment-7-bounded-lane-boundary/`.

## Hypothesis

A tiny host-visible boundary can choose `DIRECT`, `PROJECT_FIT`, or `GOVERNED`
before broader harness context loads. Direct work avoids the full harness;
Project-Fit work loads exactly the relevant project capability before governed
work; Governed work retains legitimate structural mechanisms; activation does
not grant write authority.

Status: **UNPROVEN**. No live arm ran.

## Candidate

- Generations: exactly 1
- Tree SHA-256:
  `1305587c574405991e9cb2223509245baf853b414d7c427b2a98613db5c1179e`
- Changed file:
  `skills/nulnul-harness/scripts/sync_host_entry.py`
- Champion file SHA-256:
  `849c206b2f2b0a5fe3ad2a97c8d7f6fb72407d9d7902c97f1bb9884079ffdb50`
- Candidate file SHA-256:
  `d5ea23fc890e48663f7106169da0d686a6f8397ff1846a149cdb8bcac101f3f4`
- Byte delta: `+1104`
- Structural boundary: the managed root entry commits to one downstream load
  graph before repository tools
- Migration surface: managed host-entry generation only
- Leakage scan: no benchmark ID, task prompt, literal fixture answer, or hidden
  patch embedded

This is architectural rather than wording-only because the earliest guaranteed
host surface defines three mutually exclusive post-decision context graphs:
no harness/capability load, one selected project capability load, or the full
governed harness load. A no-write marker makes the commitment observable before
the first repository tool.

The candidate was preserved but never admitted to model evaluation.

## Lane model

- `DIRECT`: product work, bounded task-file reads, real task verification, no
  NULNUL/capability/state/evolution context
- `PROJECT_FIT`: bounded roster discovery, exactly one relevant project Skill
  loaded before its governed product write, then real project verification;
  no setup/continuity/evolution context
- `GOVERNED`: explicit setup/adoption, host repair, continuity/permission
  transition, or governed evolution; load the full installed NULNUL contract
  and retain its exact writers

## Frozen preflight failure

The candidate checker returned:

> code outside managed_block changed

That result is caused by a frozen evaluator defect, not by the candidate diff.
`ast_without_boundary()` retains `managed_block` and removes every other
function before comparison. A valid candidate that changes only
`managed_block` therefore always differs. Independent byte comparison confirms
one changed file, and the patch is confined to `managed_block`.

The benchmark and evaluator were frozen before candidate generation. Fixing
the AST filter afterward would alter evaluator semantics during the experiment,
so the preregistered infrastructure kill condition applies.

## Lane decision observability

- Decision point: designed in the managed root block
- Files/context before decision: designed as the user request plus the
  automatically loaded root entry only
- Static proof: candidate block contains the three lane commitments, ordered
  no-write marker, separate project-capability/full-harness targets, authority
  separation, and governed evolution reachability
- Live proof: **not collected**

## Results

### Direct

`D1`, `D2`, `H-Direct`, and the near-boundary case: **not run**.

Strict, completion, capability loads, state writes, input, runtime, and reads:
not measured.

### Project-Fit

`P1`, `P2`, and `H-Project-Fit`: **not run**.

Relevant capability load, pre-write ordering, irrelevant capability exclusion,
strict outcome, completion, state writes, input, runtime, and reads: not
measured.

### Governed

`G1`, `G2`, and `H-Governed`: **not run**.

Structural behavior, exact authorized writes, strict outcome, and completion:
not measured.

### Evolution reachability

The static candidate preflight found the Governed-to-NULNUL evolution path
present. This proves text reachability only, not live evolution activation.

## Classification, attribution, authority, and performance

- Classification accuracy: not measured
- Capability `AVAILABLE -> DISCOVERED -> SELECTED -> LOADED -> USED ->
  ATTRIBUTED`: not measured
- Live state-authority behavior: not measured
- Champion strict/completion: not run
- Candidate strict/completion: not run
- Paired gains/regressions: not measured
- Direct/Project-Fit/Governed input, runtime, reads: not measured
- Overall ratio, tokens per strict solve, runtime per strict solve: not
  mathematically meaningful
- User burden: not measured in live work
- External capability operations: 0
- Model-performance runs: 0

## Verdict

**INFRASTRUCTURE_INVALID**

### Valid claim

**PROVEN:** the frozen Experiment 7 evaluator cannot validly admit or reject
the sole structural candidate because its AST scope check is inverted.

### Unsupported claims

- The Bounded Lane Architecture is superior.
- The candidate reliably classifies Direct, Project-Fit, or Governed work.
- Direct input is at most 120% of Champion.
- Mixed-workload input is below 130% of Champion.
- Project-Fit capability activation produces a strict gain.
- Governed behavior and exact live write authority are preserved.

## Full product validation

Not run: promotion eligibility was never reached.

## Architecture product state

**BLOCKED**

The exact candidate was not applied to
`plugins/nulnul-harness/`. The shipped product boundary remains byte-identical
to the frozen Champion used for this experiment.

## Product changes

**0**

Only benchmark/evidence documentation was added. No candidate byte, version,
tag, publication, Skill evolution, Agent evolution, external capability, or
release change entered the product.

## Rollback

No product rollback is required. The Champion remained active. The isolated
candidate and patch are retained as inactive rejected/invalid evidence.

## Version status

**v2.3 ARCHITECTURE REWORK REQUIRED**

## Release

**NOT READY**

## Next roadmap area

Repair the experiment checker and preregister a fresh sealed architecture
experiment before any live arm. Do not reuse the sealed holdouts or candidate
without an explicit new exposure decision. The architecture hypothesis itself
does not yet need revision because this failure supplied no live architectural
evidence.

## Stop

Do not implement architecture changes or start the next roadmap experiment.
