# NULNUL POST-9 POSITIVE ACTIVATION ARCHITECTURE REVIEW

Date: 2026-08-28

Scope: architecture review only

Product changes: 0

Model benchmarks run: 0

## Experiment 10 execution outcome

Experiment 10 was separately authorized and frozen on 2026-08-30. Its
deterministic infrastructure and one structurally new Candidate passed
pre-generation controls, but the first official Champion arm exited before
model usage evidence existed. The incremental evaluator then failed to make
that missing-usage record immediately terminal. The frozen evidence-failure
rule stopped the experiment as `INFRASTRUCTURE_INVALID`; no Candidate arm or
holdout ran, no Candidate 2 exists, and no product bytes changed.

This result does not revise the review below or the Experiment 9 verdict.
`POSITIVE ACTIVATION + DETERMINISTIC COMMIT` remains `UNPROVEN`. See
`docs/experiments/experiment-10-positive-activation-commit-boundary.md` for the
complete boundary report.

## Experiment 10B execution outcome

Experiment 10B repaired and live-smoked record-level evidence admission, then
froze the exact Experiment 10 Candidate with fresh holdouts. Its first official
Champion arm produced valid usage and passed. The following Candidate wrapper
failed before arm-record creation because the frozen Candidate source was
inside the durable evidence root, which the runner's containment guard rejects.
The official evidence-failure rule stopped all later arms as
`INFRASTRUCTURE_INVALID`; no Candidate model arm or holdout ran.

This is additional infrastructure evidence, not architecture evidence. It does
not repair, relabel, or supersede Experiment 10, and it does not test the
Candidate. `POSITIVE ACTIVATION + DETERMINISTIC COMMIT` remains `UNPROVEN`. See
`docs/experiments/experiment-10b-infrastructure-repair-clean-live-proof.md`.

## Experiment 10C execution outcome

Experiment 10C repaired the proven later-arm path-preflight omission and passed
canonical positive/negative controls plus the exact 22-arm dry-resolved
schedule. Read-only byte-identical Champion and Candidate execution sources,
fresh holdouts, preregistration, and benchmark revision were frozen before arm
1. The first Champion model process exited zero, produced valid usage, solved
and verified the disposable fixture, and wrote complete evidence. Cleanup then
failed because read-only source modes had propagated into the disposable
installed harness while `shutil.rmtree` assumed removable directories.

Evidence admission correctly made `cleanup_invalid` terminal
`INFRASTRUCTURE_INVALID`. No Candidate or holdout model arm ran. This third
failure is benchmark-infrastructure evidence only; it does not test or modify
the Candidate and does not support an architecture conclusion. The benchmark
system is now the dominant failure source, so another repair cycle or
Diagnostic 10D is not automatic. `POSITIVE ACTIVATION + DETERMINISTIC COMMIT`
remains `UNPROVEN`. See
`docs/experiments/experiment-10c-full-schedule-path-preflight-clean-live-proof.md`.

## Claim discipline

| Label | Meaning in this review |
| --- | --- |
| **PROVEN** | Directly observed in valid Experiment 9 evidence. |
| **PARTIAL** | Observed on the single stopped FP-A pair, not the frozen workload. |
| **UNPROVEN** | Required live evidence does not exist. |
| **ARCHITECTURAL HYPOTHESIS** | Proposed boundary requiring a new frozen experiment. |

Experiment 9 keeps its frozen verdict. This review changes neither that result
nor Candidate 1; it asks whether the benchmark-required Direct ceremony was a
necessary product transition.

## EXPERIMENT 9 HISTORICAL VERDICT

Historical verdict: **`FALSE_POSITIVE_PROJECT_FIT`**

Candidate 1: **`REJECTED / NOT PROMOTED`**

The frozen evaluator required FP-A to produce an observable `ORDINARY` stage,
no-match decision, and `DIRECT` commitment. Their absence triggered the frozen
false-positive terminal class. The verdict is immutable.

## ACTUAL FP-A RUNTIME BEHAVIOR

| Observation | Candidate FP-A |
| --- | --- |
| Stage-1 event | none |
| Match / no-match event | none / none |
| Final lane commitment | none |
| Bounded capability view | read once; 619 bytes |
| Accepted identities visible | `project-api-validation`, `project-release-docs` |
| Capability identity selected | none |
| Capability body loaded | none |
| Affirmative Project-Fit / Governed activation | 0 / 0 |
| Full NULNUL / live-state / evolution reads | 0 / 0 / 0 |
| Durable NULNUL writes | 0 |
| Product result | strict PASS; completion PASS |
| Candidate / Champion input | 0.9998x |
| Candidate / Champion output | 1.2002x |
| Candidate / Champion runtime | 1.1383x |
| Candidate / Champion reads | 0.8333x |

The tool trace establishes this order:

```text
host entry available
  -> bounded capability-view helper invoked
  -> product files read
  -> product write
  -> project verification PASS
```

The Candidate did not skip the entire applicability surface: it invoked the
helper and received both accepted identities. It also did not invoke only a
different helper path; the intended helper was used. It then followed an
operationally Direct-like path without the requested model-authored events.

From observable evidence, the best classification is:

- **B, partially:** it began the applicability procedure but omitted its
  prescribed events;
- **D, behaviorally:** it used a cheaper no-activation execution path; and
- **E, semantically:** the trace cannot determine whether the model made a
  reasoned no-match judgment or ignored the rest of the contract.

No private reasoning is needed or claimed.

## VERDICT VS OBSERVED BEHAVIOR DISTINCTION

`FALSE_POSITIVE_PROJECT_FIT` is the correct historical verdict under the
frozen Experiment 9 contract. It is not evidence that Project-Fit activated:
affirmative Project-Fit events, selected identities, and body loads were all
zero.

The result exposes two different questions:

1. Did the Candidate satisfy the preregistered explicit-Direct trace? **No.**
2. Did it overactivate a capability or governed state in FP-A? **No.**

The first rejected Candidate 1. The second is the runtime fact this
architecture review must preserve.

## WHAT EXPERIMENT 9 PROVED

- **PROVEN:** a bounded accepted-capability view can be read without loading a
  Skill body, full NULNUL, live state, or evolution history.
- **PROVEN:** FP-A can complete and pass strict verification with no positive
  NULNUL activation and no durable NULNUL write.
- **PROVEN:** model-authored Stage-1, no-match, and Direct events are not
  reliably produced merely because the host contract requires them.
- **PARTIAL:** the one observed no-activation execution stayed near Champion
  input and below Champion repository reads.
- **PROVEN:** the absence of an explicit Direct marker did not itself prevent
  correct product execution or verification.

## WHAT IT DID NOT PROVE

- That the model semantically considered every accepted capability.
- That every false positive stays capability-free.
- That a true positive activates the correct capability.
- That one-anchor ambiguity resolution works live.
- That Project-Fit produces outcome advantage or attributable evidence.
- That Governed activation and authority remain correct.
- That aggregate Direct or overall cost gates pass.
- That the positive-material-fit hypothesis is superior.

## SHOULD DIRECT BE EXPLICIT?

**No. Direct execution should not be a positive activation lane.**

The previous explicit event served several intended purposes, but none needs a
model-generated Direct commitment:

| Intended purpose | Does Direct need a positive event? | Smaller credible evidence |
| --- | --- | --- |
| Classification observability | No | bounded-view opportunity plus absence of successful positive activation |
| Proof fit was considered | No marker can prove attention | deterministic view-read/exposure event and contrastive true-positive controls |
| Prevent Skill underactivation | No | every ordinary task receives the view; true-positive activation is independently tested |
| Benchmark measurement | No | infer normal execution from view, activation, body, state, work, and check traces |
| Execution attribution | No | Direct has no capability owner; retain task outcome and verification only |
| User explainability | No | report from trace that no capability or governed mechanism activated |

An explicit Direct marker is therefore measurement ceremony, not an execution
transition. It adds instruction and failure surface without loading a
capability, granting authority, or enabling attribution.

## JUSTIFIED DIRECT

Under the revised hypothesis, **Justified Direct** means:

1. the request produced no positive Governed commit;
2. the current bounded accepted-capability view was made observable to the
   model before the first product write;
3. the positive capability-activation mechanism was available;
4. no Project-Fit commit succeeded and no capability body loaded;
5. no governed state or authority was entered; and
6. ordinary product work and an appropriate repository check completed.

No `DIRECT` event is required. An optional concise `NO_MATERIAL_MATCH` may be
useful diagnostically, but it is not an activation, authority grant, or
precondition for product work.

This is operational justification, not proof that no imaginable capability
could help. True-positive controls remain necessary to measure underactivation.

## UNEXAMINED DIRECT

An execution is **Unexamined Direct** when ordinary work proceeds but one of
these is missing before the first product write:

- the bounded accepted-capability view was not available or not read/exposed;
- the positive activation boundary was unavailable; or
- trace evidence cannot establish that the capability opportunity preceded
  the work.

The product task may still be completed outcome-first, but the run cannot be
credited as justified Direct or used as evidence that no project capability
applied. It must not trigger setup repair or acquire durable write authority.
In an architecture experiment, missing required opportunity evidence is an
infrastructure or underactivation failure, not a successful Direct result.

## UNDERACTIVATION RISK

Experiment 4C proves that useful local capabilities can remain available but
inactive. Removing the Direct marker does not solve or worsen that risk by
itself; the marker never caused a capability load.

The smallest mitigation is:

- show every ordinary request the current bounded accepted-capability view;
- make one narrow positive activation operation available;
- require true-positive tasks to invoke it with the exact identity; and
- measure missed positive activation directly.

No architecture can deterministically prove semantic fit without turning
project meaning into a brittle rules engine. Underactivation remains a model
quality risk measured by contrastive true positives, while identity, loading,
authority, and attribution become deterministic after the model elects to
activate.

## SHOULD EVERY ORDINARY TASK READ THE BOUNDED VIEW?

**A. Always read the bounded view.**

This is the recommended current boundary.

- A zero-view path has the lowest tax but recreates Experiment 4C's
  availability-without-opportunity failure.
- A conditional view requires a cheaper pre-classifier to decide whether a
  capability might matter. That is the request-only guessing problem exposed
  by Experiment 7D.
- Automatic host metadata injection could eventually remove the explicit
  read, but current host semantics have not proven such a surface. Embedding a
  durable snapshot in root guidance would add staleness and writer concerns.
- Experiment 9 showed that a 619-byte view and one read can coexist with
  near-Champion input on FP-A. This is only one-pair evidence, but it supports
  testing the fixed view tax rather than adding another pre-router.

The view must stay read-only, project.md-derived, body-free, state-free, and
small. If unavailable, ordinary work does not escalate; it simply loses
justified-Direct and capability-selection credit.

## PROJECT-FIT POSITIVE ACTIVATION

Project-Fit remains positive-only:

```text
request + accepted view + optional one anchor
  -> model asserts positive material fit with exact ID and evidence
  -> deterministic activation boundary validates accepted/current ID
  -> validates contained ID/path correspondence
  -> loads exactly that body and binds its digest
  -> emits successful PROJECT_FIT activation
  -> product work
  -> relevant project check
  -> deterministic attribution eligibility
```

Uncertainty, availability, repository adjacency, or possible usefulness do
not invoke the boundary. A failed validation produces no activation and no
body load.

The deterministic boundary may return the selected body and activation
receipt in one atomic tool response. Separate model-authored prose markers are
unnecessary as long as the trace proves that the validated body entered
context before the first governed product write.

## GOVERNED POSITIVE ACTIVATION

Governed also becomes positive-only. The model identifies a concrete
structural stage such as New Setup, Adopt/Upgrade, host repair, continuity,
permission transition, or governed evolution and invokes the bounded Governed
entry operation.

The operation validates host ownership and the named stage, loads only that
stage's required contract/state, and records the positive activation. Actual
writes remain restricted to existing stage-owned deterministic writers.

State existence, staleness, uncertainty, or NULNUL availability alone produce
no Governed activation. Ordinary work therefore does not pay setup,
continuity, checkpoint, receipt, or evolution cost.

## NATURAL-LANGUAGE COMMITMENT REVIEW

Experiment 9's host contract explicitly required Stage-1, no-match, Direct,
match, load, Project-Fit, and attribution markers. The model invoked the view
helper but emitted none of the routing markers. Those clauses described an
intended sequence; they did not govern a transition.

For Direct this was mostly harmless ceremony: no context or authority had to
change. For Project-Fit and Governed it is unsafe because a real capability or
stateful contract must enter context and authority must remain bounded.

The architecture should therefore remove negative/direct choreography from
the host prompt and stop treating model prose as the authoritative positive
commit.

## DETERMINISTIC COMMIT REVIEW

**A tiny deterministic positive commit is the recommended execution boundary.**

Semantic fit and structural intent remain model judgment. After that judgment,
deterministic code may only:

- validate accepted/current capability identity;
- validate identity/path containment;
- enforce zero or one task anchor;
- load only the selected body and bind its digest;
- emit the positive activation record;
- enforce activation before product write;
- validate the named Governed stage and host ownership;
- preserve stage-specific write authority; and
- determine attribution eligibility from activation, work, check, and outcome
  order.

It must not classify requests, score capabilities, infer job meaning, or choose
the capability. This is a commit boundary, not a routing engine.

## ATTRIBUTION PRIORITY

NULNUL 3.0 needs strong positive capability evidence, not symmetric lane
records. A credited Project-Fit run must yield:

```text
TASK / JOB
CAPABILITY ID
POSITIVE MATCH EVIDENCE
OPTIONAL ANCHOR EVIDENCE
VALIDATED BODY LOAD BEFORE WORK
PRODUCT OUTCOME
PROJECT CHECK + RESULT
SUCCESS / FAILURE
```

Direct has no capability owner and needs only the verified product outcome,
the pre-work capability opportunity, and absence of positive activation. This
focus keeps the architecture aimed at Project-Fit Evolution rather than
producing routing labels.

## PERFORMANCE MODEL

| Execution | Root/view tax | Capability body | Harness/state/evolution | Expected tier |
| --- | --- | --- | --- | --- |
| Direct | concise positive-activation guidance plus one bounded accepted view; optional unavoidable task anchor | 0 | 0 | near Champion |
| Project-Fit | Direct evidence plus one deterministic positive commit | exactly one selected body | no setup/live/evolution state | moderate bounded overhead justified by outcome gain |
| Governed | concise positive-entry guidance | only if the governed task needs one | named stage contract and authorized state only | full justified overhead |

Explicit Direct markers add context and compliance surface but no product
capability. Experiment 9's stopped pair does not prove aggregate performance;
the 120% Direct and 130% overall ceilings remain hard gates.

## OPTION A — EXPLICIT DIRECT

Every task emits Direct, Project-Fit, or Governed.

- **Benefit:** symmetrical traces and simple lane-count reporting.
- **Cost:** extra host instructions and model events on every simple task.
- **Failure exposed by Experiment 9:** correct, capability-free work can be
  rejected solely because the Direct ceremony is absent.
- **Underactivation:** not prevented; a model can still emit Direct after
  overlooking a useful capability.
- **Decision:** reject as the target architecture.

## OPTION B — POSITIVE ACTIVATION ONLY

Only Project-Fit and Governed activate; Direct is ordinary fallthrough after
the bounded view.

- **Benefit:** cheapest Direct semantics and no negative-lane ceremony.
- **Risk:** if positive transitions remain natural-language events, relevant
  capability loads and authority entry can still be skipped or retrospectively
  claimed.
- **Attribution:** weak unless load and activation are executable facts.
- **Decision:** directionally correct but insufficient by itself.

## OPTION C — POSITIVE ACTIVATION + DETERMINISTIC COMMIT

The model judges semantic material fit or structural intent. A small
deterministic operation commits only positive Project-Fit or Governed
transitions. Direct remains uncommitted normal execution after the always-read
bounded view.

- **Benefit:** preserves the cheapest correct FP-A behavior while making the
  transitions that load capability/context or grant authority real and
  attributable.
- **Cost:** one narrow read-only view and a small positive commit surface; no
  database, service, Agent, or new durable state.
- **Underactivation:** every capability gets a bounded opportunity and missed
  true positives are directly measurable.
- **Attribution:** exact identity, body, ordering, check, and outcome can be
  deterministically linked.
- **Decision:** recommended.

## HISTORICAL COUNTERFACTUAL

These are hypotheses about unbuilt architectures, not retroactive results.

| Evidence | Option A: explicit Direct | Option B: positive only | Option C: positive + deterministic commit |
| --- | --- | --- | --- |
| Experiment 4C | A Direct marker does not make a Skill visible. | Always-read view gives a fair chance, but model-only activation may still be skipped. | Always-read view gives a fair chance; missed positive invocation is an explicit underactivation failure. |
| Experiment 5B relevant | Skill A can activate, but still through prose. | Skill A should activate on positive fit, without causal enforcement. | Exact Skill A ID/body activation becomes an executable pre-work fact. |
| Experiment 5B simple | Explicit Direct can avoid Governed only if obeyed. | No positive Governed event suppresses continuity overreach. | No successful Governed commit means setup/continuity contracts and writers remain inaccessible. |
| Experiment 7D | Three-way labeling can repeat speculative Project-Fit. | No positive evidence means ordinary execution. | No validated exact-ID commit means speculative Project-Fit cannot become active. |
| Experiment 8 | A permissive model match can still load Skill A. | Same semantic false-positive risk remains. | Semantic risk remains testable, but body load and activation require the explicit validated commit. |
| Experiment 9 FP-A | Fails because the Direct marker is missing. | Counts as operational Direct-like execution if the bounded-view opportunity is proven. | Counts as justified Direct if view-read and commit availability are deterministic; no positive activation is required. |
| Future Skill Evolution | Direct symmetry adds no causal credit. | Positive runs may still lack reliable ordering. | Successful positive runs can be attribution-eligible; Direct runs receive no capability credit. |

## RECOMMENDED ARCHITECTURE HYPOTHESIS

**`POSITIVE ACTIVATION + DETERMINISTIC COMMIT`**

Status: **`ARCHITECTURAL HYPOTHESIS — UNPROVEN`**

```text
USER REQUEST
  -> positive structural intent?
       -> yes: deterministic GOVERNED commit -> stage-scoped harness/authority
       -> no: expose one bounded accepted-capability view
            -> no positive material fit: normal product execution
            -> positive material fit:
                 model supplies exact ID + evidence
                 -> deterministic validation/body load/activation
                 -> product work -> check -> attribution eligibility
```

This keeps the two useful tiers—ordinary work and justified escalation—while
removing Direct as a pseudo-capability. Routing remains infrastructure for
capability use and evolution, not the product outcome.

## DIRECT SEMANTICS

Direct is ordinary product execution with no successful Project-Fit or
Governed activation. It receives the bounded capability opportunity, loads no
capability body or harness state, performs task work, and verifies the result.
It emits no mandatory positive lane commitment.

## PROJECT-FIT SEMANTICS

Project-Fit exists only after a successful deterministic commit has validated
the model-selected accepted identity/path and placed the exact body in context.
The activation precedes product work; the relevant project check and outcome
can then be attributed to that identity.

## GOVERNED SEMANTICS

Governed exists only after a positive named-stage entry succeeds. It loads only
the required setup, repair, continuity, permission, or evolution contract and
does not broaden the stage's existing write authority.

## MODEL JUDGMENT

The model owns:

- requested-job interpretation;
- positive material-fit evidence;
- whether one specific relation needs one bounded anchor;
- the decisive fact from that anchor; and
- whether the user request positively requires a named Governed stage.

No keyword score or deterministic semantic router is introduced.

## DETERMINISTIC ENFORCEMENT

Deterministic mechanisms own:

- bounded-view extraction and pre-work exposure evidence;
- accepted/current ID and contained-path validation;
- zero-or-one anchor budget;
- selected-body-only loading and digest;
- positive Project-Fit activation receipt before product write;
- positive Governed stage entry, host ownership, and stage authority;
- zero positive activation on Direct traces;
- attribution eligibility from ordered activation/work/check/outcome facts;
- write-set enforcement and evidence durability.

They do not decide semantic fit.

## EXPERIMENT 9 FAMILY

**`CLOSED`**

Reason: Candidate 1 made Direct, no-match, and positive activation primarily
model-authored marker sequences. The recommended hypothesis removes explicit
Direct activation and moves only positive commits into a deterministic
boundary. That is a different execution and enforcement model, not a wording
revision. Candidate 1 remains frozen rejection evidence; no Candidate 2 is
authorized.

## NEXT SINGLE EXPERIMENT

### Name

**NULNUL Experiment 10 — Positive Activation Commit Boundary**

### Hypothesis

An always-read bounded capability view plus a deterministic positive commit
can keep false-positive/simple work near Champion with zero positive
activation, activate the exact capability and produce attribution-eligible
evidence on true positives, and preserve positive stage-scoped Governed entry.

### Candidate concept

One structurally new Candidate removes mandatory Direct/Ordinary/no-match
markers. Ordinary work receives one deterministic bounded-view opportunity.
After model semantic judgment, one small transient commit boundary supports:

- positive capability activation: validate ID/path and optional one-anchor
  evidence, return exactly one body plus digest, and emit an activation receipt;
- positive Governed entry: validate the named stage and host, then expose only
  the stage contract/authority.

No new store, cache, Agent, service, schema, or semantic rules engine is added.

### Structural difference

Experiment 9 asked the model to narrate every lane transition. Experiment 10
makes Direct non-activated and makes successful positive transitions tool
facts. A tool response—not later prose—proves body/context entry before work.

### False positives

- FP-A: API-adjacent formatting/normalization with no capability-owned
  requirement.
- FP-B: release/doc-adjacent ordinary work that does not invoke the release
  capability's job or check.

Required: bounded-view opportunity present; Project-Fit activations 0;
Governed activations 0; body loads 0; strict/completion PASS.

### True positives

- TP-A: Skill A materially governs a project-specific validation requirement.
- TP-B: materially different wording, same Skill A responsibility.
- TP-C: Skill B materially governs a distinct release/documentation job.

Required: exact accepted identity, exact pre-work body load, positive
Project-Fit activation, relevant check, complete attribution record, and
strict/completion PASS.

### Governed

- G1: true New Setup.
- G2: explicit host repair or legitimate continuity transition.

Required: positive Governed stage activation, required behavior, host/state
ownership, and only task-authorized writes.

### Holdouts

Freeze before Candidate generation:

- `H-FALSE-POSITIVE`
- `H-TRUE-PROJECT-FIT`
- `H-DISTINCT-CAPABILITY`
- `H-GOVERNED`

### Direct evidence

Minimum credible evidence, with no model-generated Direct ceremony:

1. bounded accepted view was valid and entered context before first product
   write;
2. positive activation boundary was available;
3. successful Project-Fit and Governed activations were both 0;
4. capability bodies, full harness, and live/evolution state reads were 0;
5. ordinary product work occurred; and
6. the required repository verification passed.

If the view or activation boundary is absent, the run is unexamined and cannot
receive justified-Direct credit.

### Project-Fit activation

Required on every true positive:

- exact ID 100%;
- accepted/current/path validation 100%;
- selected body loaded before first product write 100%;
- positive activation receipt 100%;
- irrelevant body loads 0.

### Attribution

Every credited positive run must expose, in order:

```text
TASK / JOB
CAPABILITY ID
MATCH EVIDENCE
OPTIONAL ANCHOR EVIDENCE
BODY LOAD + DIGEST BEFORE WORK
PRODUCT OUTCOME
PROJECT CHECK + RESULT
SUCCESS / FAILURE
```

Attribution eligibility must be 100%.

### Strict

- every credited Candidate task strict/completion PASS;
- Project-Fit strict gain at least +1 versus Champion;
- paired strict regressions 0;
- paired completion regressions 0.

### Direct cost

False-positive/simple aggregate Candidate input: **at most 120% of Champion**.

Report input, output, runtime, repository reads, view reads, anchor reads, body
reads, harness reads, and state reads separately.

### Overall cost

Complete Candidate workload input: **less than 130% of Champion**.

Report Direct, Project-Fit, and Governed separately.

### State authority

- Direct and Project-Fit unrelated durable NULNUL writes: 0.
- Governed: exact task-owned writers and targets only.
- Positive activation never grants promotion or unrelated structural write
  authority.

### User burden

New harness-management questions: 0. The user never selects a route,
capability, stage, or activation mechanism.

### Kill

Stop on any false-positive positive activation, true-positive underactivation,
wrong identity, pre-commit/speculative body load, invalid attribution order,
Governed suppression, unauthorized write, paired strict/completion regression,
user routing question, impossible Direct/overall cost gate, holdout leakage,
or infrastructure/evidence invalidity. No generation 2.

### Promote

Promote only if all false positives complete with zero positive activation,
all true positives and holdouts produce exact activation and attribution, both
Governed controls preserve authority, all outcome/regression/cost/user/evidence
gates pass, and rollback remains available. No partial promotion.

### Rollback

Champion remains active. Candidate stays isolated until every gate and full
product validation pass. On any kill, preserve evidence, reject the Candidate,
and restore/discard only its isolated bytes.

## EVOLUTION READINESS

If Experiment 10 succeeds: **YES**, every credited Project-Fit run will expose
the task/job, exact capability identity, positive match evidence, body load
before work, product outcome, relevant project check and result, and
success/failure required for an attribution-grounded Skill Evolution proof.

Success would make that next experiment eligible; it would not itself prove or
begin Skill Evolution.

## PRODUCT CHANGES

`0`

No Candidate, benchmark run, evaluator modification, version bump, tag, or
publication occurred.

## VERSION

`v2.3 ARCHITECTURE REWORK REQUIRED`

## RELEASE

`NOT READY`

## NEXT

`STOP — do not implement Experiment 10.`
