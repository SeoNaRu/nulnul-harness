# POST-6C ARCHITECTURE DECISION

Date: 2026-08-28

Decision type: product architecture only

Product changes: 0

The full analysis is
[NULNUL Post-6C Product Architecture Review](../architecture/post-6c-product-architecture-review.md).
The live D1 revision is
[NULNUL Post-7D Architecture Hypothesis Review](../architecture/post-7d-bounded-lane-hypothesis-review.md).
The current applicability decision is
[NULNUL Post-8 Capability Applicability Review](../architecture/post-8-capability-applicability-review.md).

## Decision

Adopt **Bounded Lane Architecture** as the single target hypothesis, revised
after Experiment 8 to use two bounded stages plus a positive applicability
proof:

> A tiny host-loaded, read-only Stage 1 selects Governed or ordinary work
> before live-state or capability-body context. Ordinary work then reads one
> bounded accepted capability view from the existing project contract. A
> capability may match only when its accepted job/trigger has a material
> task consequence; one task anchor may be read when that relationship is
> genuinely ambiguous. No positive proof commits Direct. Positive proof
> selects and loads one exact capability before a separately observable
> Project-Fit commitment. Durable harness writes belong only to a named
> Governed stage.

This is an **ARCHITECTURAL HYPOTHESIS**. It is not an implemented or proven
advantage.

## Product identity

The 3.0 North Star remains frozen:

- Outcome First
- Project-Fit First
- Beginner / Calm Surface
- No AI FOMO
- Continuity
- Adaptation / Evolution
- Inspectability / Learnability
- Waste Awareness

NULNUL is intended to evolve the best capability ecosystem for a project. It
is not intended to maximize routing sophistication, capability count, or
harness activation.

The added performance principle is:

> Simple work should pay only the cost required to know that it is simple.

NULNUL is always available, not always fully active.

## Evidence basis

| Evidence | Decision-relevant result |
| --- | --- |
| Post-v2.2.1 proof | Vanilla, exact v2.2.1, and Project-Fit candidate tied at 21/25 strict. Candidate verdict: NO_ADVANTAGE. |
| Resume Cases 22/25/31 | Ordinary fallthrough can invoke valid continuity writers for the wrong task; Case 31 proves some receipt refresh is legitimate. LOCUS_D remains a KNOWN LIMITATION. |
| Experiment 2 | Harness activation did not produce a lifecycle survivor action. |
| Experiments 3A/3B | Live Skill evolution remains UNEVALUATED because governing Skill activation was not validly observed. |
| Experiment 4C | Capability availability did not become live activation. |
| Experiment 5A | Root routing made NULNUL and a relevant Skill observable, but target input/runtime/reads rose to about 161%/193%/200% of Champion without strict advantage. |
| Experiment 5B target | Bounded relevant work activated NULNUL and Skill A 6/6, passed strict 6/6, and made no setup writes. |
| Experiment 5B simple | A no-Skill task performed continuity work, made a forbidden mutation, and used about 231% of Champion input. |
| Experiment 6C | Meta contract and rejected history were reachable, but frozen attribution said NULNUL was not loaded; an archive write also escaped the fixed write set. Verdict: SELF_EVOLUTION_NOT_ACTIVATED. |
| Experiment 7D | The exact one-shot Candidate emitted an early lane event but chose Project-Fit for frozen Direct D1, loaded no project capability, and used 130.017% of Champion input on the stopped pair. Verdict: MISCLASSIFICATION. |
| Experiment 8 | The two-stage Candidate emitted `ORDINARY`, read a 776-byte accepted capability view, then incorrectly matched and loaded `project-api-validation` for frozen Direct D1. Candidate/Champion input was 135.65% on the stopped pair; both failed strict, passed completion, and made no durable NULNUL write. Verdict: DIRECT_PROJECT_FIT_MISCLASSIFICATION. |

The common diagnosis is:

> Contract correctness does not establish an ordered activation transition or
> grant task-appropriate write authority.

More routing wording is therefore not the next step.

Experiment 8 leaves the two-stage topology **UNPROVEN**. It supports the
physical Stage-1 and bounded-view ordering on one live case, but rejects the
first accepted-view/model-match implementation. The Post-8 review identifies
permissive matching and collapsed match/load/commit ordering as the causal
boundary defects. Candidate 1 is closed. Exactly one future Experiment 9 may
test the structurally different positive-fit/one-anchor boundary; it is not
implemented here.

## Target lanes

    HOST STAGE 1
       |
       +-- GOVERNED
       |     positive setup / repair / continuity / permission / evolution intent
       |     named stage owner
       |     fixed allowed writes
       |     deterministic writer and validator
       |
       +-- ORDINARY
             |
             v
       BOUNDED ACCEPTED CAPABILITY VIEW
             |
             +-- clear no positive match -> DIRECT
             |     no NULNUL core or capability body
             |     no durable harness state
             |     direct work + smallest real check
             |
             +-- one ambiguous relation -> one bounded task anchor
             |     +-- no positive proof -> DIRECT
             |     +-- positive proof -> select exact ID
             |
             +-- positive material fit -> select exact ID
                   -> load exact body -> prove load -> PROJECT-FIT
                   -> use -> verify -> attribute
                   product writes only

Direct is a successful NULNUL product decision even though NULNUL's full
harness is not active.

## Activation and authority decisions

| State | Required proof |
| --- | --- |
| Host routed | Host automatically loaded the managed root micro-router before work. |
| Harness active | Project-Fit or a Governed lane was selected and its controlling contract loaded before governed work. |
| Capability active | Exact named/versioned capability body or tool binding loaded before its assigned job. |
| Evolution active | One bounded episode opened with feedback, target, WHERE, WHY, budget, permissions, and write set before candidate generation. |
| Self-evolution active | Evolution is active on a frozen NULNUL target and NULNUL's pre-candidate contribution is attributable. |

None of these states grants the next authority automatically. In particular:

- harness activation does not authorize setup or continuity writes;
- capability activation does not authorize harness restructuring;
- evolution activation does not authorize promotion; and
- self-evolution activation does not authorize publication or release.

## What stays

Keep the Product North Star, outcome-first evaluation, real repository checks,
frozen Champion/candidate identity, independent Gate, rollback, rejected
history, one live-state target, host ownership, exact checkpoint command and
sole receipt writer, evidence durability, preregistered and retired holdouts,
and no partial promotion.

Navigator, Coach, and Gate remain logical responsibilities; they do not imply a
required Agent count.

## What moves

- Move Governed-versus-ordinary classification before checkpoint/evolution
  validation.
- For ordinary work, conditionally read only the accepted capability-routing
  view from `project.md`; do not load primary SKILL.md or live state during the
  fit check.
- Require positive evidence that the accepted job/trigger contributes a
  task-required constraint, owned artifact, or project check. Permit at most
  one bounded task anchor only when one specific relation remains ambiguous.
- Keep any Project-Fit execution/attribution kernel smaller than the full
  primary Skill and add it only if the next experiment proves it necessary.
- Move setup/adoption, continuity, evolution, meta-evolution, personal
  adaptation, and generalization behind explicit Governed entry.
- Require separately observable match, identity selection, exact body load,
  Project-Fit commitment, first governed write, project check, and attribution
  before capability-performance evolution.
- Route each durable state target through one stage-owned writer.
- Reuse self-evolution as target_kind=harness in the normal evolution
  transaction.
- Keep observability ordered and bounded; do not add an always-on durable task
  transcript.

Do not add a router service, MCP server, hook, app, mandatory Agent, or new
state schema unless a bounded skills-only experiment proves the necessary
boundary cannot hold.

## Rejected target options

### Pointer-only root

Rejected as the target because it is cheap but leaves the user/base model to
know when NULNUL should engage. It naturally repeats the 3A/4C activation gap.

### Always-active harness

Rejected because it makes nominal activation easy while retaining a fixed
harness tax and an accumulation surface for continuity/setup clauses. The
5A/5B cost and side-effect evidence points away from this choice.

## Version decision

**v2.3 ARCHITECTURE REWORK REQUIRED**

The bounded activation/authority milestone must precede a v2.3 release claim.
No version is bumped and no release work begins here.

## Historical Experiment 7 design — closed

### Experiment 7 — Bounded Lane Boundary

**Highest-risk assumption:** the guaranteed host-loaded surface can cheaply
choose and physically isolate Direct, Project-Fit, and Governed context while
preserving relevant pre-work capability activation.

**Candidate concept:** change the load topology so the managed root block is
only a three-lane micro-router; Direct has no harness entry, Project-Fit loads a
thin core and exact selected capability before work, and Governed loads one
stage contract. Ordered reads and a protected-state diff make the boundary
observable. This is not another prohibition sentence.

**Primary metric:** paired strict verified-result count on a mixed workload,
with completion as a required control and input/runtime per strict result as
the efficiency tie-breaker.

**Required activation:**

- Direct: no NULNUL core, capability, or governed state contract;
- Project-Fit: exact core and selected capability before first governed action;
- Governed: exact selected stage contract before transition; and
- every unselected contract/capability remains unloaded.

**Required authority:**

- zero unauthorized durable harness writes;
- exact required structural/continuity writes;
- empty protected-state diff for Direct and Project-Fit; and
- no candidate/archive bytes during evolution-entry preflight.

**Simple guardrail:** every Direct pair stays at or below 115% of Champion
input and runtime, adds no more than one root-entry read, and touches no durable
harness state.

**Project-Fit guardrail:** no strict/completion regression; all relevant tasks
pass real checks; raw input at or below 135% of Champion; total input per
strict result at or below 110% of Champion.

**User burden:** zero harness-specific questions when the repository contains
the answer.

**Kill:** any wrong-lane load, unauthorized/missing state write, Champion-pass
regression, guardrail breach, invalid negative control, holdout leak, or need
for a new service/hook/state system in this bounded candidate.

**Promote:** only an independent Gate, only after exact activation/authority,
all development/validation/sealed-holdout checks, at least one paired strict
gain without regression, cost/user guardrails, frozen evidence, and a later
observed live cycle. Promotion is provisional and covers only the lane
mechanism.

**Rollback:** Champion remains active; discard the isolated candidate on any
kill, invalid evidence, no advantage, or live-cycle failure.

If the experiment succeeds, it enables:

    low-cost activation
      -> reliable capability use
      -> causal attribution
      -> later Skill / Agent / Harness evolution
      -> verified competition
      -> project-fit survivor ecosystem

Cleaner route labels alone are a failure.

## Frozen stop

- No product candidate
- No wording candidate
- No routing patch
- No self-evolution candidate
- No External Capability Competition
- No Skill Evolution 3C
- No Agent Evolution
- No Generalization
- No v2.4 implementation
- No v2.3 release work
- No new model-performance benchmark

## Product changes

**0**

## Release

**v2.3 NOT READY**

## Next

**STOP — do not implement architecture changes.**

## Experiment 7 status — 2026-08-28

Experiment 7 froze benchmark revision
`116c5ce6347b82afe851c8f13210571f4575f12e` and generated exactly one isolated
managed-entry boundary candidate. The frozen structural checker contained an
inverted AST scope comparison and rejected every valid `managed_block` change.
No model arm or sealed holdout ran.

Verdict: **INFRASTRUCTURE_INVALID**.

This does not validate or contradict the Bounded Lane Architecture. Product
changes remain 0, v2.3 still requires architecture rework, and the next allowed
work is a fresh preregistration after evaluator repair—not candidate tuning or
generation 2. See
[`experiment-7-bounded-lane-boundary.md`](../experiments/experiment-7-bounded-lane-boundary.md).

## Experiment 7D status — 2026-08-28

After two further infrastructure-only stops, Experiment 7D repaired the
fixture-integration preflight so each arm is checked against its own
deterministic managed-entry output. The repair passed 48/48 deterministic tests,
14/14 development fixture integrations, eight negative controls, exact
Champion/Candidate integrity, and sealed-holdout hash checks.

The first live pair then produced valid architecture evidence. D1 Candidate
made an early observable decision but selected `PROJECT_FIT` for the frozen
`DIRECT` task. The preregistered kill rule stopped the other 18 arms and all
holdouts.

Verdict: **MISCLASSIFICATION**.

This rejects the exact frozen implementation without disproving the Bounded
Lane Architecture. Product changes remain 0, the architecture remains
unproven, and v2.3 still requires architecture rework. No Candidate 2 was
created. The next roadmap action is architecture hypothesis review. See
[`experiment-7d-bounded-lane-boundary.md`](../experiments/experiment-7d-bounded-lane-boundary.md).

## Post-7D hypothesis revision

Experiment 7D separates two assumptions that Post-6C had combined:

1. an early host-visible decision can execute; and
2. request/root semantics alone can distinguish Direct from Project-Fit.

The first was observed on D1. The second was not supported. Before the lane
event, the Candidate had the request and root guidance but no observable
project capability job, trigger, or body. Its uncertainty rule therefore
turned missing evidence into `PROJECT_FIT`. The prepared repository's existing
`project.md` capability-routing table would have shown that neither active
Skill governed username normalization, but the one-shot design prohibited that
read until after the final lane decision.

Current architecture hypothesis: **TWO-STAGE BOUNDED LANES**.

- Stage 1 uses positive structural intent to select one Governed stage or
  ordinary work before live-state/capability-body reads.
- Ordinary work reads one bounded accepted capability view from the existing
  `project.md`.
- Zero concrete matches commits Direct.
- One concrete match identifies and loads the exact capability body before
  Project-Fit commits.
- Uncertainty, availability, or name similarity alone grants neither
  Project-Fit activation nor durable authority.

The existing project contract is reused; no capability database, service,
hook, app, Agent team, or new state schema is proposed.

## Experiment 7 implementation family

**CLOSED — EXPERIMENT 7 IMPLEMENTATION FAMILY CLOSED**

The exact one-shot managed-block approach receives no Candidate 2 and no
wording generation. It reached the intended live decision point and exposed a
missing-information boundary. The higher-level bounded-lane goal continues
only through a structurally distinct experiment.

## Historical Post-7D next experiment

### Experiment 8 — Two-Stage Capability-Fit Boundary

Test whether one bounded accepted capability view can correctly distinguish
Direct from Project-Fit, identify and load the exact useful capability, keep
Direct aggregate input at or below 120% of Champion, keep total input below
130%, preserve explicit Governed controls, produce at least one Project-Fit
strict gain with no paired strict/completion regression, make no unauthorized
state write, ask no harness-management question, and pass one sealed holdout
per lane.

The candidate must be structurally different from Experiment 7: two ordered
decision events with a deterministic bounded project-evidence read between
them, and a final Project-Fit event that is invalid without a concrete
capability identity and exact pre-work body load. Champion remains active and
the isolated candidate rolls back on any wrong lane, missing/irrelevant load,
authority failure, outcome regression, cost failure, evidence defect, or
holdout leak.

Do not implement this experiment from the architecture review.

## Post-7D stop

- Product changes: **0**
- Model benchmark runs in the Post-7D review: **0**
- Version: **v2.3 ARCHITECTURE REWORK REQUIRED**
- Release: **NOT READY**
- Next: **STOP — do not implement the revised architecture.**

## Experiment 8 status — 2026-08-28

The first two-stage Candidate reached `ORDINARY` before repository reads and
read one 776-byte accepted capability view without live state or the full
harness. It then incorrectly matched and loaded `project-api-validation` for
frozen Direct D1. Match, body-load marker, and Project-Fit commitment also
occurred in one event. The kill stopped the rest of development and all sealed
holdouts.

Verdict: **DIRECT_PROJECT_FIT_MISCLASSIFICATION**.

This rejects Candidate 1 without proving or disproving every two-stage
boundary. Candidate 1 is closed and receives no generation 2.

## Post-Experiment 8 applicability revision

The D1 accepted contract was sufficiently discriminating when its fields were
considered together:

- job: `api-error-code-maintenance`;
- trigger: request-validation/error-code behavior;
- check: unit tests plus the error-catalog verifier; and
- requested work: isolated username normalization.

The primary defect was therefore a permissive semantic jump from API adjacency
to material fit. A second proven defect was causal ordering: match, body-load
marker, and Project-Fit commitment were not separate observable events.

Current applicability hypothesis:

**POSITIVE MATERIAL FIT WITH ONE AMBIGUITY ANCHOR**

- A capability must be accepted/current by exact identity.
- Its job/trigger must govern a requested behavior or output.
- Its contract must contribute a task-required constraint, owned artifact, or
  project check.
- Clear no-match commits Direct without a body read.
- Only one specific ambiguous relation may inspect one bounded task anchor.
- Positive proof selects an exact ID; only then may its exact body load.
- Match, load, Project-Fit commitment, first governed write, check, and
  attribution must be separately observable in that order.
- Attribution eligibility requires the ordered task/job, identity, match,
  load, outcome, and check record; it does not prove advantage or authorize
  evolution.

Keep `docs/nulnul/project.md` as the durable capability source. Prefer one
deterministically extracted read-only view and per-ID/path validation. Do not
add a capability database, negative exception list, cache, service, hook, MCP,
Agent, or new state schema. Strengthen positive routing rows only if
contrastive evidence later proves the current job/trigger/check contract plus
one anchor insufficient.

## Experiment 8 Candidate family

**CLOSED**

Candidate 1 receives no second generation and no wording tune. Its exact bytes
remain rejection evidence.

## Exactly one current next experiment — revised

### Experiment 9 — Contrastive Applicability + Attribution Boundary

Test one structurally new Candidate on deliberately contrastive ordinary work:

- two false positives whose wording resembles accepted capability jobs but
  whose required behavior/check does not;
- two differently worded true positives for Skill A;
- one true positive for distinct Skill B;
- one development ambiguity control that must use exactly one frozen task
  anchor;
- one explicit Governed control plus bounded deterministic reachability; and
- sealed false-positive, true-positive, distinct-capability, and ambiguous
  holdouts frozen before Candidate generation.

The Candidate must implement positive fit evidence, a conditional one-anchor
budget, deterministic accepted-ID/path validation, and separate match, body
load, Project-Fit commit, work, check, and attribution events. It may reuse the
existing project contract but may not reuse Candidate 1 as a wording base or
add durable routing infrastructure.

Required promotion gates:

- false-positive Direct and true-positive Project-Fit accuracy 100%;
- exact expected capability identity 100%;
- irrelevant or Direct capability bodies 0;
- bare Project-Fit events 0;
- pre-commit and pre-write selected-body load 100%;
- attribution-eligible causal records for 100% of credited Project-Fit tasks;
- every credited Candidate task passes strict/completion;
- Project-Fit strict gain at least +1 with zero paired strict/completion
  regressions;
- Direct aggregate input at most 120% of Champion and complete input below
  130%;
- Direct/Project-Fit unrelated durable writes 0;
- new harness-management questions and external operations 0; and
- all sealed holdouts and evidence-durability checks pass.

Champion remains active. Any false/true-positive error, wrong identity,
premature/speculative body load, bare Project-Fit, attribution-order failure,
authority/outcome/cost regression, Governed suppression, user routing burden,
or evidence defect kills the Candidate with no generation 2.

If successful, Experiment 9 establishes only applicability/attribution
boundary evidence. It may supply a later Skill Evolution experiment with a
task/job, exact capability ID, match evidence, pre-work body load, product
outcome, project check, and success/failure record. It does not run or prove
Skill Evolution.

See the full
[Post-8 Capability Applicability Review](../architecture/post-8-capability-applicability-review.md).

## Current Post-8 stop

- Product changes: **0**
- Model benchmark runs in this review: **0**
- Version: **v2.3 ARCHITECTURE REWORK REQUIRED**
- Release: **NOT READY**
- Next: **STOP — do not implement Experiment 9.**

## Experiment 9 status — 2026-08-28

Experiment 9 froze a structurally new positive-material-fit Candidate and a
contrastive workload only after the complete model-free infrastructure
preflight passed. The first frozen pair, FP-A, completed in Champion then
Candidate order.

Both arms passed strict and completion with the same product patch. Candidate
read the 619-byte accepted capability view, loaded no Skill body, loaded no
full harness or live state, made no durable NULNUL write, and used 99.98% of
Champion input on that stopped pair. It did not, however, emit an observable
Stage-1 decision, evidenced no-match, or Direct commitment.

Frozen verdict: **FALSE_POSITIVE_PROJECT_FIT**.

The frozen reason is that FP-A did not remain an observable ordinary Direct
chain. Claim discipline matters: the Candidate emitted zero affirmative
Project-Fit events and loaded zero capabilities. The terminal class records
the preregistered false-positive fixture failure; the measured locus is a
missing executable commitment boundary, not the semantic false-positive body
load seen in Experiment 8.

The kill stopped TP-A and every later development/holdout arm. Therefore:

- positive material fit remains **UNPROVEN**;
- the one-anchor policy has deterministic controls but no live evidence;
- the bounded `project.md` view remains a partial low-cost signal;
- attribution eligibility and Project-Fit outcome advantage were not tested;
- Candidate 1 is rejected and receives no generation 2; and
- Live Skill Evolution remains closed.

See [Experiment 9](../experiments/experiment-9-positive-material-fit-boundary.md).

## Current Post-Experiment-9 stop

- Product changes: **0**
- Model arms: **2**, then frozen kill
- Holdout model calls/live exposure: **0**
- Version: **v2.3 ARCHITECTURE REWORK REQUIRED**
- Release: **NOT READY**
- Next: **ARCHITECTURE REVIEW**

Do not tune Candidate 1, create Candidate 2, or begin Skill Evolution.

## Post-Experiment-9 positive-activation decision — 2026-08-28

The architecture review preserves Experiment 9's frozen
`FALSE_POSITIVE_PROJECT_FIT` verdict while separating it from the actual FP-A
trace. Candidate 1 invoked the 619-byte accepted-capability view, selected and
loaded no capability, entered no Governed mechanism, changed no durable NULNUL
state, and passed strict/completion near Champion input. It failed the frozen
contract because it emitted no Stage-1, no-match, or Direct commitment.

Explicit Direct is no longer the target architecture. A Direct marker does not
load context, grant authority, prevent underactivation, or create capability
attribution. Ordinary execution is instead the absence of a successful
positive escalation after one bounded capability opportunity. Every ordinary
task should receive the small project.md-derived accepted view; otherwise the
run is unexamined and cannot support a justified-Direct claim.

Recommended hypothesis: **POSITIVE ACTIVATION + DETERMINISTIC COMMIT**.

The model continues to judge job meaning, positive material fit, optional
one-anchor evidence, and positive structural intent. A tiny deterministic
boundary validates accepted ID/path, loads only the selected body, records
positive Project-Fit activation before work, constrains one-anchor use, enters
only the named Governed stage, preserves writer authority, and determines
attribution eligibility. It does not classify semantics.

Experiment 9 Candidate family is **CLOSED**. The next single experiment is
Experiment 10, a structurally new positive-activation commit proof with
false-positive, true-capability, distinct-capability, and Governed controls.
It is designed only; no Candidate or benchmark run exists.

See the full
[Post-9 Positive Activation Review](../architecture/post-9-positive-activation-review.md).

## Current Post-Experiment-9 architecture stop

- Product changes: **0**
- Model benchmark runs in this review: **0**
- Recommended architecture: **POSITIVE ACTIVATION + DETERMINISTIC COMMIT**
- Architecture status: **UNPROVEN**
- Version: **v2.3 ARCHITECTURE REWORK REQUIRED**
- Release: **NOT READY**
- Next: **STOP — do not implement Experiment 10**
