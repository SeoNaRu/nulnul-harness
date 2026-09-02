# NULNUL POST-7D ARCHITECTURE HYPOTHESIS REVIEW

Date: 2026-08-28

Scope: architecture-hypothesis review only

Product changes: 0

Model benchmarks run: 0

## Claim discipline

| Label | Meaning in this review |
| --- | --- |
| **PROVEN** | Directly observed in valid Experiment 7D evidence. |
| **PARTIAL** | Observed on D1, but not across the frozen mixed workload. |
| **UNPROVEN** | Required live evidence does not yet exist. |
| **ARCHITECTURAL HYPOTHESIS** | A proposed boundary that needs a future experiment. |

Experiment 7D is the first valid live test of the exact Experiment 7
candidate. It rejects that implementation; it does not prove or disprove every
bounded-lane architecture.

## LIVE EVIDENCE

| Fact | Result |
| --- | --- |
| D1 frozen lane | `DIRECT` |
| D1 Candidate lane | `PROJECT_FIT` |
| Decision timing | Before any observable repository read or broader context |
| Pre-decision repository-tool file reads | 0 |
| Relevant project capability loaded | No |
| Durable state read | No |
| Unauthorized durable write | No |
| Strict | Champion fail; Candidate fail |
| Completion | Champion pass; Candidate pass |
| Candidate / Champion input | 130.017% |
| Candidate / Champion runtime | 124.0% |
| Candidate / Champion repository reads | 100% |

The aggregate Direct cost gate was not reached. The D1 ratio is a warning, not
an aggregate performance verdict.

## WHAT 7D PROVED

1. **PROVEN:** the host-loaded managed entry can cause an observable lane event
   before broader repository context.
2. **PROVEN:** the exact Candidate selected `PROJECT_FIT` for D1 even though the
   frozen expectation was `DIRECT`.
3. **PROVEN:** a lane label did not imply capability activation. The Candidate
   loaded no concrete project Skill before or after its `PROJECT_FIT` event.
4. **PROVEN:** the observed misclassification did not grant durable write
   authority; D1 produced no durable NULNUL write.
5. **PROVEN:** the Candidate paid more input and runtime on the stopped D1 pair
   without a strict advantage.
6. **PARTIAL:** early physical ordering is feasible on the tested Codex host.
   Its semantic accuracy and mixed-workload cost remain unproven.

## WHAT 7D DID NOT PROVE

- Bounded Lane Architecture is better or worse than Champion.
- A one-shot three-way classifier can work with different evidence.
- A router can establish Project-Fit from request semantics alone.
- The Project-Fit path can identify, load, use, and attribute a capability.
- Governed setup, repair, continuity, or evolution remains reachable under the
  Candidate.
- The Direct or overall aggregate cost guardrail passes or fails.
- A future two-stage boundary is superior.

## D1 MISCLASSIFICATION ANALYSIS

### Observable input at the decision

The Candidate was instructed to decide from only:

1. the user request; and
2. the automatically loaded `AGENTS.md`, including user-owned guidance and the
   generated managed block.

D1 asked:

> Fix `normalize_username()` so runs of whitespace and underscores become one
> dash. Preserve lowercase and trimming behavior, and verify it.

The user-owned root guidance said that this was an API service, named its unit
check, and said reusable project procedures lived under `.agents/skills/`.
The managed block defined Direct and Project-Fit, then added:

> When project-specific fit is semantically uncertain, use `PROJECT_FIT`.

The observable trace proves no repository file was read before the lane event.
It does not prove that any host-generated Skill catalog or description was in
pre-lane model context. Evaluator fixture metadata listing available Skills is
not activation evidence and is not proof that the router saw their jobs.

### Signals favoring the wrong lane

| Observable signal | Why it could bias Project-Fit |
| --- | --- |
| Named project function and preserved behavior | Looks project-specific without identifying a capability job. |
| Root says reusable procedures exist | Establishes availability in general, not relevance. |
| Project-Fit is defined by a project-specific convention or procedure | D1 can be described as a convention if no job boundary is known. |
| Uncertainty defaults to Project-Fit | Converts missing evidence into positive activation. |

The rule therefore treated “a capability might help” as equivalent to “a
known capability materially fits.” Those are not the same claim.

### Evidence that would have justified Direct

The prepared repository already contained the decisive evidence in
`docs/nulnul/project.md`:

| Capability | Recorded job / trigger | D1 relation |
| --- | --- | --- |
| `project-api-validation` | API error-code maintenance; activate when validation behavior changes | No match: username normalization does not change request acceptance, rejection, or an error catalog. |
| `project-release-docs` | Release documentation; activate for release-note work | No match. |

The two Skill descriptions agree with those boundaries. Neither body governed
username formatting. The task files would also have shown an isolated string
normalizer, but that read was not necessary once the active capability triggers
were known.

This evidence existed before the model call, but the Candidate architecture
required a final three-way decision before reading it. The one-shot input was
therefore insufficient to *justify* Project-Fit or to establish the negative
Direct condition. It could only guess.

## MINIMUM EVIDENCE FOR GOVERNED

Governed is a positive structural-authority decision. It usually needs less
project-specific evidence than Direct versus Project-Fit.

Minimum evidence:

1. the user request;
2. host ownership and the existence of the host-managed entry already in root
   guidance; and
3. a positive structural intent or prerequisite: explicit setup/adoption,
   host-entry repair, continuity/resume, permission transition, or evolution.

The frozen setup and repair controls state this intent directly. Only after
that positive decision should NULNUL read the relevant checkpoint, evolution
state, setup contract, or repair target.

The mere existence, staleness, or invalidity of durable state must not turn an
ordinary product task into Governed work. Cases 22/25 and Experiment 5B's
simple failure show why state health is not sufficient authority.

**ARCHITECTURAL HYPOTHESIS:** `GOVERNED` versus `ORDINARY` can be selected from
the request and root structural contract before live-state or capability reads.
Semantic interpretation remains model judgment; host ownership, allowed
writers, and the selected stage write set remain deterministic.

## MINIMUM EVIDENCE FOR DIRECT VS PROJECT-FIT

Request semantics alone cannot establish a relation to a project-specific
capability whose identity and job are not in that input.

The minimum reliable ordinary-work evidence is:

1. **Task job:** a bounded semantic description derived from the user request.
2. **Accepted capability view:** each active capability's identity, job,
   activation trigger, project check, and accepted/verified status.
3. **Concrete match:** one accepted row materially applies to the requested
   job. Name similarity, availability, or possible usefulness is insufficient.
4. **Exact body confirmation:** only the matched capability body is loaded to
   confirm its contract before Project-Fit commits.
5. **Optional task anchor:** only when request semantics cannot disambiguate the
   match, inspect one explicitly named file, manifest, or framework anchor
   before any product write. Do not perform repository-wide discovery.

No external search, live checkpoint, evolution state, full NULNUL Skill, or all
capability bodies are required for this decision.

## BOUNDED PROJECT CAPABILITY SURFACE

Do not add a capability database.

The existing `docs/nulnul/project.md` already has an **Inspected roster**,
**Candidate evidence**, and **Capability routing** table. The routing table
contains exactly the useful fields: capability, source, job, activation
trigger, check, permission boundary, and removal condition. The D1 fixture's
bounded routing section was much smaller than the whole project contract and
both Skill bodies.

Recommended use:

- keep `project.md` as the durable source of truth;
- expose only the accepted capability/routing view during the ordinary fit
  check;
- read no Skill body until one row matches;
- load exactly that body before Project-Fit commits; and
- keep checkpoint/evolution files out of this path.

Current deterministic validation proves required headings and completed setup
fields, but does not fully validate the routing-table row relationships. A
future experiment may need one minimal read-only extraction/validation
boundary. That is not a new state schema or routing framework.

## PROJECT-FIT COMMITMENT RULE

Project-Fit is not a speculative label. It is an execution commitment bound to
a concrete capability.

The derived rule is:

> `PROJECT_FIT` is valid only when one accepted project capability has been
> identified by job and trigger, its exact body has been loaded, and that load
> occurred before the product work it governs.

The observable event should therefore carry the capability identity. A bare
`PROJECT_FIT` followed by zero capability loads is invalid by construction.

The lifecycle remains distinct:

    AVAILABLE IN ACCEPTED PROJECT VIEW
      -> MATCHED TO TASK JOB
      -> SELECTED BY IDENTITY
      -> EXACT BODY LOADED
      -> PROJECT_FIT COMMITTED
      -> USED IN PRODUCT WORK
      -> REAL CHECK RUN
      -> OUTCOME ATTRIBUTED

Semantic job matching is model judgment. Identity, exact-body read ordering,
first product write, check execution, and attribution eligibility are
observable/deterministic evaluation facts.

## DIRECT DEFAULT ANALYSIS

For ordinary work, Direct should be the default **after a bounded accepted
capability check finds no concrete match**.

It should not be a blind request-only default:

- Experiment 4C shows relevant Skills can remain underactivated when automatic
  activation has no project evidence path.
- Experiment 5B target shows a correct project Skill can materially govern
  relevant work.

It should not default uncertainty to Project-Fit:

- Experiment 5A shows the cost of broad activation without advantage.
- Experiment 5B simple shows continuity/state overreach on no-Skill work.
- Experiment 7D shows the exact uncertainty fallback misclassified D1.

The balanced rule is positive-evidence activation:

> Ordinary work remains Direct unless the accepted project capability view
> identifies a concrete material fit.

If that view is missing or invalid, Project-Fit is not justified. Ordinary
product work must not repair setup or enter Governed automatically. It may run
Direct with an observable “fit evidence unavailable” condition; repairing the
project contract requires a separately authorized Governed request.

## ACTIVATION VS CLASSIFICATION

Experiment 7D conflated a speculative class label with entry into the
Project-Fit path. The label appeared first; the roster was enumerated later;
no concrete capability was loaded.

The revised boundary separates four events:

| Event | Meaning | What it authorizes |
| --- | --- | --- |
| Structural classification | Governed or ordinary | Only the next bounded read graph |
| Capability-fit check | Zero or one concrete accepted candidate | No durable write and no harness activation |
| Lane commitment | Direct, or Project-Fit bound to a loaded capability | Product execution and verification only |
| Governed activation | One named structural stage contract loaded | Only that stage's deterministic write set |

Classification chooses what may be read next. Activation means a controlling
contract is actually loaded. Neither grants unrelated write authority.

## TARGET FLOWS

### Simple Direct task

    USER REQUEST
      -> host already loaded its small structural root entry
      -> Stage 1: no positive Governed intent -> ORDINARY
      -> read only accepted capability-routing view from project.md
      -> no job/trigger match -> DIRECT
      -> read target product file and directly relevant test
      -> implement
      -> run smallest real project check

| Context class | Loaded | Not loaded |
| --- | --- | --- |
| Harness | Host structural entry only | Primary NULNUL `SKILL.md`; setup/continuity/evolution references |
| Capability | Bounded accepted routing rows | Every project Skill body |
| Stable project evidence | Capability view from `project.md` | Other setup/history sections unless task needs them |
| Live state | None | checkpoint, receipt, evolution, archive |
| Product | Target file and directly relevant check | Repository-wide discovery |

Direct is justified relative to the project's accepted active ecosystem: no
known verified job contract matches. It is not a claim that no capability in
the world could ever help.

### Project-Fit task

    USER REQUEST
      -> Stage 1: no positive Governed intent -> ORDINARY
      -> read accepted capability-routing view
      -> one job/trigger match identifies capability ID
      -> load that exact capability body
      -> confirm body applies and emit PROJECT_FIT + capability ID
      -> product work under that contract
      -> run normal check plus capability-specific check
      -> retain ordered use/outcome evidence for future evolution

Loaded: host structural entry, bounded accepted capability view, one selected
Skill body, task files, and real checks.

Not loaded: irrelevant Skill bodies, full NULNUL workflow, checkpoint/receipt,
setup, continuity, evolution, rejected history, or archive.

### Governed task

    USER REQUEST
      -> Stage 1 detects positive setup / repair / continuity / permission /
         evolution intent
      -> GOVERNED + named stage
      -> only then load primary NULNUL contract, exact stage reference,
         necessary live state, and its deterministic writer/validator
      -> perform authorized structural work
      -> verify exact state and product outcome

The capability-fit view is unnecessary unless the selected Governed stage is
setup/adoption and explicitly owns roster work.

## OPTION A — ONE-SHOT THREE-WAY ROUTER

    request + root guidance -> DIRECT / PROJECT_FIT / GOVERNED

| Dimension | Assessment |
| --- | --- |
| Minimum cost | Lowest possible pre-decision context. |
| Evidence | Sufficient for explicit structural intent; insufficient for project-specific fit unless capability metadata is also preloaded. |
| D1 | The uncertainty fallback selected Project-Fit without a capability. |
| Simplicity | One event and one root surface. |
| Direct risk | If uncertainty favors Project-Fit, simple work overactivates. |
| Project-Fit risk | If uncertainty favors Direct, relevant capabilities repeat 4C underactivation. |
| Attribution | Weak: the label need not identify or load a capability. |

Keeping the decision one-shot would require embedding or automatically loading
project capability metadata into the root context. That either increases every
task's root tax, becomes stale duplicated state, or silently turns the
one-stage design into a two-stage evidence load.

**Decision:** reject the one-shot three-way mechanism as the target hypothesis.

## OPTION B — TWO-STAGE BOUNDED LANES

    USER REQUEST
      -> Stage 1: GOVERNED or ORDINARY
      -> if ORDINARY, bounded accepted capability-fit view
      -> concrete capability fit? PROJECT_FIT : DIRECT

| Dimension | Assessment |
| --- | --- |
| Additional tax | One bounded stable project-capability read on ordinary tasks. |
| Evidence | Uses actual accepted project jobs/triggers rather than guessing. |
| Direct performance | Near-Champion target: root plus one small read; no Skill body or live state. |
| Project-Fit | Exactly one selected body, then product files and checks. |
| Governed | Skips the fit view and loads full machinery only after positive structural intent. |
| Attribution | Stronger: final Project-Fit commitment is bound to capability identity and pre-write load. |
| Host compatibility | Uses existing root entries, `project.md`, local Skills, and ordinary read tools; no service, hook, or new state store. |

**Decision:** select as the revised architecture hypothesis. It remains
unproven until a new structurally distinct candidate is evaluated.

## OPTION C — NOT ADVANCED

No third option has stronger evidence.

- Always-active NULNUL repeats the 5A/5B fixed-tax and context-interference
  risk.
- Pointer-only or blind Direct-first routing repeats 4C underactivation.
- Reading task files and then deciding before the first write is an optional
  evidence refinement inside Stage 2, not a distinct architecture.

Adding a third framework would not improve the causal boundary.

## PERFORMANCE MODEL

No performance benchmark was run. These are projected read/context tiers.

### Option A

| Lane | Expected reads/context | Relative expectation |
| --- | --- | --- |
| Direct | Root only when correct; roster/harness after a false Project-Fit | Near-Champion only when classification guesses correctly |
| Project-Fit | Root, roster enumeration, one or more candidate bodies | Moderate but weakly bounded |
| Governed | Root, full harness, selected state/stage | Full justified overhead |

### Option B

| Lane | Expected reads/context | Relative expectation |
| --- | --- | --- |
| Direct | Root; one bounded `project.md` capability view; target file/test | Near-Champion plus one bounded fit read |
| Project-Fit | Direct routing cost plus one exact Skill body and capability-specific check | Moderate bounded overhead tied to verified value |
| Governed | Root; exact NULNUL/stage contract; necessary state, writer, validator | Full justified overhead |

For Direct, the projected budget is:

- harness files: 0 after the root entry;
- capability bodies: 0;
- stable project evidence: one bounded accepted capability view;
- live-state files: 0;
- evolution files: 0; and
- ordinary task files/checks: only those needed for the result.

Stage 2 fails the performance hypothesis if it needs the full `project.md`,
full roster bodies, primary NULNUL Skill, live-state validation, or broad
repository discovery merely to return Direct.

## HISTORICAL COUNTERFACTUAL

These are architecture counterfactuals, not claims that an unbuilt option
would have passed.

| Evidence | Option A: one-shot | Option B: two-stage bounded |
| --- | --- | --- |
| Experiment 4C | A Direct-biased guess can still miss a relevant Skill. | Valid accepted row identifies the Skill; exact body load is required before Project-Fit. |
| Experiment 5A | Can route relevant work but has no evidence boundary preventing broad NULNUL context. | Ordinary fit check loads no core/state; only one selected body follows a match. |
| Experiment 5B target | Could preserve activation when task wording happens to signal fit. | API-validation trigger identifies Skill A and preserves pre-work load. |
| Experiment 5B simple | Uncertainty can enter capability/continuity machinery. | No accepted job match yields Direct; Stage 1 keeps continuity behind positive Governed intent. |
| Experiment 7D D1 | Actually selected Project-Fit without a body. | Existing routing rows produce zero matches, so the hypothesized result is Direct. |
| Future Skill evolution | Bare labels provide no causal unit. | Capability ID, exact load, governed write, specific check, and outcome form an attribution chain. |

One principle explains the set:

> Ordinary capability activation requires positive evidence from the accepted
> project capability contract; structural state activation requires positive
> Governed intent. Absence or uncertainty grants neither.

## RECOMMENDED ARCHITECTURE HYPOTHESIS

**TWO-STAGE BOUNDED LANES**

This is an **ARCHITECTURAL HYPOTHESIS**, not a promoted architecture.

### Why

7D showed that early ordering and correct semantic classification are separate
problems. The request/root pair can cheaply recognize explicit structural work,
but cannot justify project-specific fit without project-specific evidence.
One conditional bounded read supplies that missing evidence without loading the
full harness, every Skill, or live state.

### What changes

1. Replace the one-shot three-way choice with `GOVERNED` versus `ORDINARY`.
2. For ordinary work, read a bounded accepted capability view from the existing
   `project.md` before choosing Direct versus Project-Fit.
3. Remove “uncertainty means Project-Fit.” Positive fit evidence is required.
4. Bind Project-Fit to a concrete capability identity and exact body load.
5. Permit Direct to pay one bounded stable project-evidence read; continue to
   forbid Skill bodies, live state, evolution, and full harness context.
6. Treat missing fit evidence as no Project-Fit authority, not as automatic
   setup repair or Governed entry.

### What stays

- Direct, Project-Fit, and Governed remain the three execution outcomes.
- The host root remains tiny, read-only, first, host-owned, and user-invisible.
- Product execution remains with Codex or Claude and ends in real checks.
- Activation remains separate from authority.
- Direct and Project-Fit have no durable harness write authority.
- Governed stages retain exact writers, validators, one live-state target, and
  independent promotion/rollback rules.
- No MCP server, hook, app, service, daemon, Agent team, capability database,
  or new state schema is added.

## PROJECT-FIT EVOLUTION ALIGNMENT

The two-stage boundary exists to improve causal experience, not to make route
labels cleaner:

    low-cost structural decision
      -> accepted project job/trigger match
      -> concrete capability identity
      -> exact pre-work load
      -> verified product outcome
      -> attributable capability experience
      -> later governed upgrade/competition
      -> KEEP / UPGRADE / REPLACE / MERGE / RETIRE / CREATE
      -> project-fit survivor ecosystem

Direct also produces useful ecosystem evidence: no accepted capability matched
the job, and direct execution produced the verified result. That is stronger
than saying no capability was loaded accidentally.

## EXPERIMENT 7 IMPLEMENTATION FAMILY

**CLOSED — EXPERIMENT 7 IMPLEMENTATION FAMILY CLOSED**

The exact managed-block one-shot classifier must not receive another
generation. It had valid live execution, made the decision at the intended
early point, and exposed the architectural information deficit: it guessed
Project-Fit before project-fit evidence was available. Another wording change
would tune the same unsupported decision surface.

Candidate 1 remains frozen and rejected. No Candidate 2 is created. The
higher-level bounded-lane objective continues only through a structurally
distinct two-stage experiment.

## NEXT SINGLE EXPERIMENT

### Name

**NULNUL Experiment 8 — Two-Stage Capability-Fit Boundary**

### Highest-risk assumption

A bounded accepted capability view contains enough project evidence to
distinguish Direct from Project-Fit and identify the exact useful capability,
while Direct remains within its cost ceiling.

### Hypothesis

For ordinary work, one bounded read of accepted capability jobs/triggers can
produce correct no-match or one-capability-match decisions. Direct will avoid
all Skill bodies and live state; Project-Fit will load exactly the matched body
before work; explicit structural controls will bypass the fit check and retain
Governed behavior.

### Champion

The exact shipped Champion used by Experiment 7D.

### Candidate concept

- Stage 1 emits `GOVERNED + stage` or `ORDINARY` from request/root evidence.
- Ordinary work invokes a deterministic read-only view of the existing
  accepted `project.md` capability routing evidence.
- Zero matches commits Direct.
- One concrete match identifies the capability, loads its exact body, and only
  then commits Project-Fit with that identity.
- The evaluator rejects a bare Project-Fit event, a missing body load, an
  irrelevant body, or any live-state read on ordinary work.

### What is structurally new

Two ordered decision boundaries have a real project-evidence read between
them. Final Project-Fit is identity-bearing and invalid without an exact
pre-work capability load. This is not another one-shot managed-block wording
variant.

### Likely surfaces

- managed host-entry generation for Stage 1 only;
- the existing `project.md` Capability routing/Candidate evidence surface;
- the existing project-contract validator, or one minimal read-only extractor
  only if its current output cannot bound that surface;
- exact local Skill body loading; and
- experiment-only ordered trace and negative controls.

No new durable capability file or schema is justified.

### Workload

- **Direct development:** at least two isolated product changes with zero
  accepted capability matches, including an API-named false positive.
- **Project-Fit development:** at least two tasks whose accepted rows add a
  required project convention/check, using distinct job wording.
- **Governed controls:** true New Setup and explicit host-entry repair or
  continuity; each must bypass the ordinary fit view.
- **Near-boundary controls:** a small-looking task that genuinely needs a
  capability and a capability-sounding task that does not.
- **Sealed holdouts:** one fresh Direct, one Project-Fit, and one Governed case,
  frozen before candidate generation.

### Metrics and guardrails

| Requirement | Gate |
| --- | --- |
| Classification | Correct Stage 1 and final lane on every credited case; zero bare Project-Fit events. |
| Capability identification | Exact required capability ID on every Project-Fit case; zero ID on Direct; irrelevant IDs/loads = 0. |
| Activation | Exact body loaded before Project-Fit commitment and first governed product write. |
| Strict outcome | Project-Fit strict gain at least +1 versus Champion; paired strict regressions 0; completion regressions 0. |
| State authority | Direct/Project-Fit live-state and unrelated durable writes 0; Governed writes exactly match the task-owned set. |
| Direct input | Aggregate Candidate input <=120% Champion; no full harness, Skill body, checkpoint, or evolution read. |
| Overall input | Complete Candidate workload <130% Champion. |
| User burden | New harness-management questions 0. |
| External operations | 0. |

### Kill

Stop on any wrong Stage 1/final lane, Project-Fit without a concrete ID and
pre-work body load, Direct capability/harness/live-state read, Project-Fit
setup/evolution overreach, Governed suppression, unauthorized write, paired
strict/completion regression, user lane choice, evidence failure, holdout leak,
or mathematically impossible cost gate.

No generation 2 in the same experiment.

### Promote

Promote only the two-stage boundary if all development, validation, and sealed
holdout cases pass; exact capability identification/load/use attribution is
complete; Project-Fit gains at least one strict pass without regression;
Direct and overall cost gates pass; authority/user/external-operation guards
hold; evidence is durable; and independent full product validation later
passes. No partial promotion.

### Rollback

Champion remains active. The isolated candidate is discarded on any kill,
invalid evidence, no advantage, or later product-validation failure.

## PRODUCT CHANGES

**0**

No candidate, benchmark run, version bump, tag, or publication was produced.

## VERSION

**v2.3 ARCHITECTURE REWORK REQUIRED**

## RELEASE

**NOT READY**

## NEXT

**STOP — do not implement the revised architecture.**

## POST-EXPERIMENT 8 EVIDENCE

Experiment 8 instantiated the proposed two-stage boundary at frozen benchmark
revision `352ef9b0737fed48ec873a817f0deced76d40703`. Its one Candidate passed all
deterministic infrastructure gates, then stopped on the first live Candidate
case with `DIRECT_PROJECT_FIT_MISCLASSIFICATION`.

D1 reached `ORDINARY` before repository reads and loaded one 776-byte accepted
capability view with no live-state or full-harness read. It then incorrectly
matched `project-api-validation`, loaded that irrelevant body, and selected
`PROJECT_FIT` instead of frozen `DIRECT`. Candidate/Champion input on this
stopped pair was `1.3565x`; both arms failed strict, passed completion, and made
no durable NULNUL write.

This evidence leaves the two-stage topology unproven and rejects Candidate 1.
The physical Stage-1/view boundary is supported on one case; the bounded
capability-view/model-match boundary is insufficient in this implementation.
Project-Fit, Governed, aggregate cost, evolution reachability, and all holdouts
were not reached. No Candidate 2 is authorized. See
[Experiment 8](../experiments/experiment-8-two-stage-capability-fit-boundary.md).
