# NULNUL POST-8 CAPABILITY APPLICABILITY REVIEW

Date: 2026-08-28

Scope: architecture review only

Product changes: 0

Model benchmarks run: 0

## Claim discipline

| Label | Meaning in this review |
| --- | --- |
| **PROVEN** | Directly observed in valid Experiment 8 evidence. |
| **PARTIAL** | Observed on D1, but not across the stopped workload. |
| **UNPROVEN** | Required live evidence does not yet exist. |
| **ARCHITECTURAL HYPOTHESIS** | Proposed boundary requiring a new frozen experiment. |

Experiment 8 rejects its exact Candidate. It does not prove or disprove every
two-stage bounded-lane architecture.

## EXPERIMENT 8 RESULT

Verdict: **`DIRECT_PROJECT_FIT_MISCLASSIFICATION`**

Architecture: **`TWO-STAGE BOUNDED LANES — UNPROVEN`**

Candidate 1: **`REJECTED / NOT PROMOTED`**

| D1 observation | Result |
| --- | --- |
| Frozen Stage 1 / final lane | `ORDINARY` / `DIRECT` |
| Candidate Stage 1 / final lane | `ORDINARY` / `PROJECT_FIT` |
| Accepted view | 776 bytes from `docs/nulnul/project.md` |
| Accepted identities | `project-api-validation`, `project-release-docs` |
| Frozen expected matches | 0 |
| Candidate match and body | `project-api-validation`; loaded |
| Full-harness / live-state reads | 0 / 0 |
| Unauthorized durable writes | 0 |
| Strict / completion | Candidate fail / pass; Champion fail / pass |
| Candidate / Champion input | 1.3565x on the stopped pair |

The kill occurred on the first Candidate case. Project-Fit true positives,
Governed behavior, aggregate Direct cost, overall cost, and sealed holdouts
were not evaluated.

## WHAT WORKED

- **PROVEN:** Stage 1 emitted `ORDINARY` before the first repository read.
- **PROVEN:** one small project capability view was available without loading
  checkpoint, receipt, evolution state, or the full NULNUL harness.
- **PROVEN:** D1 activation did not acquire durable write authority.
- **PARTIAL:** the physical two-stage read boundary is feasible on the tested
  Codex host.
- **UNPROVEN:** the boundary can classify a contrastive ordinary workload,
  activate a true-positive capability, or stay within the Direct cost ceiling.

These are useful boundary signals, not promotion evidence.

## PRIMARY FAILURE

Candidate 1 converted broad semantic adjacency into a material-fit claim:

    username normalization
      + API-service context
      + a capability mentioning request validation
      -> possible relevance
      -> project-api-validation
      -> body load
      -> PROJECT_FIT

The accepted capability actually governed request-validation failures, the
`errors.problem(field, code)` envelope, and error-code catalog maintenance.
D1 changed an isolated string normalizer. The task neither changed request
acceptance/rejection nor required the error catalog.

The missing boundary was not capability availability. It was a positive proof
that the capability's verified job contract owned a requirement of this task.

## FAILURE LOCUS

**`MULTIPLE`**

| Locus | Finding |
| --- | --- |
| `MATCH_POLICY_TOO_PERMISSIVE` | **Primary.** The current row supplied enough job/trigger/check evidence to reject D1, yet the Candidate accepted weak API adjacency as a concrete match. |
| `COMMIT_ORDER_AMBIGUOUS` | **Proven secondary defect.** Match, body-read marker, and Project-Fit commitment appeared in one tool event, so load-before-commit was not provable. |
| `TASK_EVIDENCE_TOO_THIN` | **Boundary risk, not proven as D1's primary cause.** Request-only matching can remain ambiguous when a named behavior might sit inside or outside a capability-owned surface. One bounded anchor can resolve that class. |
| `CAPABILITY_CONTRACT_TOO_BROAD` | **Not established as the primary D1 cause.** The combined job, trigger, and check were sufficiently discriminating for a careful decision. |

Candidate 1 also said that possible usefulness or uncertainty was not a
concrete match. The live result shows that another instruction sentence does
not create an executable positive-proof threshold.

## CURRENT CAPABILITY CONTRACT AUDIT

The prepared D1 `project.md` stored two routing rows. The corresponding local
Skill bodies were frozen and consistent with those rows.

| Field | Current representation | Classification | Finding |
| --- | --- | --- | --- |
| Identity | `project-api-validation`, `project-release-docs` | **SUFFICIENT** | Stable IDs distinguish both accepted jobs. |
| Job | `api-error-code-maintenance`; `release-documentation` | **SUFFICIENT for D1** | Neither job names username normalization. The API job is terse but materially narrower than generic API work. |
| Activation trigger | Request-validation/error-code changes; documentation-only release communication | **AMBIGUOUS at boundaries** | The release trigger is narrow. “Validation behavior” can be overextended to normalization unless interpreted with job/check evidence or one task anchor. |
| Project check | Unit tests plus error-catalog verifier; docs verifier | **SUFFICIENT as corroboration** | D1 required the unit check, not an error-catalog or docs obligation. A check alone is not a match, but it exposes the capability-owned outcome. |
| Accepted / verified status | Aggregate Candidate-evidence row says project-local Skills are verified for declared jobs and reused only when relevant | **AMBIGUOUS** | It is not a per-ID current-status field. Candidate 1 converted the aggregate decision into `verified` for every routing row. This did not cause D1's semantic error but weakens general identity authority. |
| Path / load target | Not stored in the routing row; deterministically derived from ID under the host-local Skills root | **MISSING AS DATA; NOT NEEDED AS A NEW FIELD** | A validator can safely derive and containment-check the exact path. Duplicating it durably would create stale state. |
| Scope / behavioral ownership | No dedicated field; partly expressed by job, trigger, and check | **MISSING** | D1 does not yet justify a new field because the existing positive contract could reject it. Reconsider only after contrastive evidence shows repeated ambiguity. |
| Permission boundary | `local files` | **NOT NEEDED FOR FIT; SUFFICIENT FOR AUTHORITY** | It limits action, not semantic applicability. |
| Removal condition | Verified job disappears or a better survivor replaces it | **NOT NEEDED FOR TASK FIT** | It belongs to lifecycle management. |

The shipped setup validator currently validates headings and completed fields;
it does not validate per-row routing relationships, per-ID acceptance, or
applicability semantics. That is a deterministic integrity gap, not a reason
to make semantic matching deterministic.

### Could the current contract reject D1?

**Yes.** A careful bounded decision could combine:

1. task behavior: collapse whitespace/underscore runs in
   `normalize_username()`;
2. capability job: API error-code maintenance;
3. trigger: adding or changing request-validation behavior; and
4. capability check: the error-code catalog verifier.

No requested outcome requires the capability's error envelope, catalog, or
validation-failure procedure. Therefore the row has no positive material-fit
proof. The contract does not need a case-specific “does not govern
`normalize_username`” exception.

## D1 APPLICABILITY ANALYSIS

The Candidate saw the request, root Stage-1 contract, and then the 776-byte
accepted view. It did not see a product file before matching.

Observable signals that may have encouraged the wrong match were the API
working agreement, the function's username/input semantics, and the broad
phrase “validation behavior.” None establishes that D1 changes rejection,
error envelopes, or the catalog. The Candidate nevertheless emitted
`MATCHED(project-api-validation)`.

One bounded product anchor would have made the non-fit even clearer:
`username.py` contained only a pure string transformation, while `api.py`,
`errors.py`, and `contracts/error-codes.json` were outside D1's allowed product
surface. That anchor was available only after Candidate 1 had already matched,
loaded, and committed.

No private reasoning is needed for this diagnosis. It follows from the frozen
request, accepted rows, Skill body, allowed product surface, and ordered trace.

## MATERIAL-FIT DEFINITION

**ARCHITECTURAL HYPOTHESIS:** a capability materially governs an ordinary task
only when all three predicates hold:

1. **Accepted identity:** the exact capability is current and accepted for its
   declared job.
2. **Task-contract relation:** the requested behavior or output satisfies that
   job's activation trigger.
3. **Material consequence:** the capability contributes a task-required
   constraint, owned artifact, or project check that changes how the work must
   be implemented or verified.

This is not a keyword score and does not mechanically require every available
evidence type. The model must produce one concise positive claim supported by
the accepted row. A task anchor is additional evidence for predicates 2 or 3
only when the request and row do not settle them.

Name similarity, repository adjacency, general usefulness, capability
availability, and “might help” are insufficient.

## NO-MATCH DEFINITION

`NO_MATERIAL_MATCH` means:

> For every accepted/current capability row, the bounded evidence fails to
> establish either the task-contract relation or a material execution/check
> consequence; after the one permitted anchor where ambiguity exists, no row
> has positive proof.

Then Direct commits. No Skill body loads and no capability receives credit.

A missing or invalid capability view is different from a verified no-match.
Ordinary execution may still fail closed to Direct so it does not invent
Project-Fit or setup authority, but it must record `FIT_EVIDENCE_UNAVAILABLE`
and may not contribute “no capability applies” ecosystem evidence. In an
architecture experiment, unavailable required evidence is an infrastructure
failure, not a successful Direct classification.

## AMBIGUITY POLICY

Use a bounded three-result fit check:

    REQUEST + ACCEPTED VIEW
      -> CLEAR MATCH    -> continue exact-capability proof
      -> CLEAR NO MATCH -> DIRECT
      -> AMBIGUOUS      -> read at most one task anchor
                            -> MATCH or NO MATCH

Ambiguity exists only when a specific accepted row could own the requested
behavior but the request does not reveal the implementation boundary. It is
not a synonym for general model uncertainty.

The one anchor must be the smallest task surface that can settle ownership:

- an explicitly named target file;
- the current implementation file for an exact named symbol;
- one immediate framework/module manifest; or
- one directly relevant repository metadata surface.

It may not become directory-wide exploration, all tests, every Skill body,
checkpoint/state inspection, or full-harness activation. Prefer a product file
that implementation would need to read anyway; moving that unavoidable read
before lane commitment adds ordering, not necessarily another read.

If the one anchor still supplies no positive proof, commit Direct. This is the
cheapest justified action, not a claim that no future capability could help.

## CAPABILITY-BODY LOAD RULE

The accepted view and optional anchor decide applicability. A Skill body is
not a speculative search surface.

    POSITIVE MATERIAL MATCH
      -> select exact accepted ID
      -> validate exact load target
      -> load only that body

No match or unresolved ambiguity loads zero bodies. If the selected body
contradicts its accepted row, Project-Fit must not commit; the contract is
inconsistent and receives no attribution. Experiment 8 provides no evidence
that all bodies must be read to determine fit.

## PROJECT-FIT COMMIT ORDER

The following stages must be separately observable, even if the final runtime
implementation uses compact transient events:

| Order | Event | Required proof |
| ---: | --- | --- |
| 1 | `MATCHED(capability_id, evidence)` | Positive row evidence and optional anchor reference; no body read yet. |
| 2 | `SELECTED(capability_id)` | ID is accepted/current and resolves to one contained path. |
| 3 | Body read | Exact selected body bytes are actually read. |
| 4 | `LOADED(capability_id, body_digest)` | Identity/path/digest correspond to the read body. |
| 5 | `PROJECT_FIT_COMMITTED(capability_id)` | Occurs after load in a later observable event. |
| 6 | First governed product write | Occurs after commitment. |
| 7 | `VERIFIED(project_check, outcome)` | Relevant check actually ran and its result is recorded. |
| 8 | `ATTRIBUTED(capability_id, outcome)` | Eligibility guard succeeds after the observed result. |

Experiment 8 collapsed steps 1, 3/4, and 5 into one tool event. Even though the
body read preceded the first product write, the trace could not prove that load
preceded commitment. That ordering is architecturally invalid for attribution.

## ATTRIBUTION ELIGIBILITY

A Project-Fit execution is **attribution-eligible** only when:

- exact accepted/current identity is established;
- positive match evidence is recorded;
- the exact body is loaded and its digest is known;
- load and Project-Fit commitment precede governed product work;
- the capability-relevant project check executes; and
- a success or failure outcome is observed.

The minimal causal record is:

    TASK / JOB
    CAPABILITY ID
    MATCH EVIDENCE
    LOAD EVENT BEFORE FIRST GOVERNED WRITE
    PRODUCT OUTCOME
    PROJECT CHECK + RESULT
    SUCCESS / FAILURE

Eligibility does not prove that the capability is better than Champion or
that every failure is the capability's fault. It proves that the capability
actually governed the work, so a later evolution experiment may reproduce and
test the causal claim. D1 is ineligible because its match was wrong and its
load/commit order was ambiguous.

Direct executions can record a verified no-match and outcome for ecosystem
planning, but they produce no capability-specific performance evidence.

## PROJECT.MD REVIEW

Keep `docs/nulnul/project.md` as the durable source. Do not add a capability
database.

| Approach | Assessment | Decision |
| --- | --- | --- |
| A. Read the current bounded section directly | Reuses truth but exposes table/prose formatting and requires the model to parse acceptance relationships. | Viable fallback, not preferred runtime shape. |
| B. Deterministically extract a tiny read-only view | Experiment 8 proved a 776-byte view can be produced without live state or bodies. Identity/path/currentness checks can fail closed. | **Preferred hypothesis.** Extraction worked; semantic matching failed. |
| C. Strengthen existing routing rows | Could add positive ownership precision, but D1 does not prove new fields are necessary and duplicated scope can become stale. | Defer until contrastive evidence shows current job/trigger/check plus one anchor is insufficient. |

The exact Experiment 8 helper is part of a rejected Candidate and is not
promoted. Its successful extraction is evidence for the source/shape, not for
those bytes. A future boundary must also validate accepted/current identity at
per-ID granularity rather than blindly converting one aggregate candidate row
into status for every capability.

Negative exception fields such as `DOES NOT GOVERN` are not justified. Prefer
precise positive job, trigger, and check contracts. Add a general ownership or
scope field only after repeated contrastive failures show positive evidence
cannot express the boundary.

## MODEL VS DETERMINISTIC BOUNDARY

| Concern | Owner | Why |
| --- | --- | --- |
| Interpret requested job | Model judgment | Project meaning is semantic and open-ended. |
| Decide whether row evidence materially fits | Model judgment | Requires relating task outcome to capability contract, not keywords. |
| Decide whether one anchor is necessary | Model judgment within a deterministic one-anchor budget | Ambiguity is semantic; breadth must remain bounded. |
| Extract accepted-view fields | Deterministic | Data selection should not vary by phrasing. |
| Validate accepted/current ID | Deterministic | An unknown, stale, or rejected ID cannot gain authority. |
| Resolve ID to contained exact path | Deterministic | Prevents identity/path substitution. |
| Enforce at most one anchor | Deterministic | Preserves the Direct cost boundary. |
| Enforce zero body reads before match | Deterministic | Prevents speculative capability loading. |
| Enforce selected-body-only load | Deterministic | Prevents irrelevant context and false credit. |
| Enforce load -> commit -> first write order | Deterministic/observable | Causal ordering cannot depend on retrospective prose. |
| Enforce Direct/Project-Fit write sets | Deterministic | Activation does not grant durable authority. |
| Decide attribution eligibility | Deterministic from recorded facts | Identity, ordering, check, and outcome are observable. |
| Decide whether a failure generalizes or merits evolution | Model judgment under a later independent Gate | Attribution eligibility is not promotion evidence. |

This is the smallest reliable split: verified evidence plus semantic judgment,
with deterministic identity, ordering, and authority guards. It is not a
static trigger engine.

## DIRECT COST ANALYSIS

Experiment 8's stopped D1 pair is a warning, not an aggregate cost verdict.

| Candidate overhead source | Observable evidence |
| --- | --- |
| Stage-1/Stage-2 root contract | Candidate managed block was 1,501 bytes versus Champion's 501 bytes. |
| Accepted view | One 776-byte output and one repository read. |
| Wrong body | One irrelevant `project-api-validation` body read. |
| Wrong capability check | The error-catalog verifier ran even though D1 did not need it. |
| Product work | Candidate later read `username.py` and `test_username.py`, which the task required in some form. |

Removing the wrong body and its check removes observable context and tool work.
For an ambiguous task, reading the eventual target product file earlier can
serve as the one anchor rather than adding a new product read. Therefore the
architecture is plausibly capable of approaching the 120% Direct ceiling.

It is still **UNPROVEN**. The larger root contract and bounded-view turn remain
fixed taxes, Champion itself performed an irrelevant Skill/live-state read,
and input proxies compound prior context across turns. Exact savings cannot be
derived from the stopped pair.

Projected successful Direct context:

- host: one small Stage-1/applicability contract;
- stable project evidence: one extracted accepted view;
- anchor: zero for clear cases, at most one task file for ambiguous cases;
- capability bodies: 0;
- full harness: 0;
- live state/evolution: 0;
- product/verification: only task-required files and checks.

## OPTION A — STRONGER POSITIVE MATCH, REQUEST + CURRENT VIEW

The model receives the request and current accepted view. It must name a
trigger-satisfying task relation and material consequence; otherwise Direct.

| Dimension | Assessment |
| --- | --- |
| D1 | Should reject both rows from job/trigger/check evidence. |
| Direct cost | Lowest Stage-2 tax; no product anchor. |
| True-positive risk | Requests that omit implementation ownership can repeat 4C-style underactivation. |
| Implementation risk | Candidate 1 already contained a prose warning against possible usefulness; a policy-only revision risks becoming another wording patch. |
| Attribution | Strong only if event ordering is separately repaired. |

**Decision:** insufficient as the sole target.

## OPTION B — POSITIVE MATCH + ONE AMBIGUITY ANCHOR

The model receives request plus current accepted view. Clear matches and clear
no-matches commit without another read. Only a specific ambiguous row permits
one task anchor, followed by match/no-match. Identity, body load, commitment,
and attribution are separately enforced.

| Dimension | Assessment |
| --- | --- |
| D1 | Current row evidence yields no positive match; if treated as ambiguous, `username.py` confirms Direct. |
| Direct cost | One 776-byte-class view; zero body; anchor only when needed and preferably an unavoidable task read. |
| True-positive accuracy | Can confirm capability ownership when user wording omits the implementation boundary. |
| 4C risk | Every accepted row is considered; concrete matches must load exact bodies. |
| Complexity | One conditional read budget and ordered events; no new store, Agent, service, or rule engine. |
| Attribution | Strongest of the bounded options because proof, load, work, and check are ordered. |

**Decision:** recommended applicability hypothesis.

## OPTION C — RICHER ACCEPTED CAPABILITY CONTRACT

Add explicit positive ownership/scope data to every durable capability row,
then match request plus the richer view.

| Dimension | Assessment |
| --- | --- |
| Potential value | Can make recurring boundaries clearer and reduce anchor reads. |
| Current evidence | D1's existing job/trigger/check already supports rejection; necessity is unproven. |
| Cost | More setup, validation, maintenance, migration, and stale duplicated meaning. |
| Negative-scope risk | Accumulates benchmark- or symbol-specific exceptions instead of general positive contracts. |

**Decision:** defer. Reconsider only if Option B fails because diverse accepted
rows remain intrinsically ambiguous after one bounded anchor.

## HISTORICAL COUNTERFACTUAL

These are architecture hypotheses, not claims about an unbuilt Candidate.

| Evidence | Recommended boundary |
| --- | --- |
| Experiment 7D D1 | Stage 1 returns ordinary; accepted-view proof is required before Project-Fit, so request-only uncertainty cannot activate a capability. |
| Experiment 8 D1 | API error-code job/trigger/check has no material consequence for normalization; optional `username.py` anchor confirms Direct; no body loads. |
| Experiment 5B relevant API task | A real request-validation/error-code change satisfies Skill A's trigger and requires its error-catalog check, so it gets an exact pre-work load. |
| Experiment 4C | Accepted capabilities are always considered on ordinary work, and a positive fit must transition to an exact body load, reducing availability-only underactivation. |
| Future Skill B task | A release-documentation job/check or another distinct accepted contract identifies Skill B by exact ID rather than generic API similarity. |
| Simple work | A clear no-match avoids all bodies; an ambiguous task pays at most one task-anchor read, not full discovery. |
| Future Skill Evolution | Match evidence, exact identity, pre-work load, governed edits, check, and outcome form an attribution-eligible causal record. |

One principle explains the set:

> Project-Fit requires positive capability ownership evidence; uncertainty may
> buy one bounded task anchor, but it grants neither capability activation nor
> write authority.

## RECOMMENDED APPLICABILITY HYPOTHESIS

**POSITIVE MATERIAL FIT WITH ONE AMBIGUITY ANCHOR**

This refines **TWO-STAGE BOUNDED LANES**; it does not add another lane.

    STAGE 1: GOVERNED or ORDINARY
      -> ORDINARY reads accepted capability view
      -> clear no-match: DIRECT
      -> clear positive material match: SELECT
      -> ambiguous specific row: read at most one task anchor
           -> no positive proof: DIRECT
           -> positive proof: SELECT
      -> load selected body
      -> prove load
      -> PROJECT_FIT commit
      -> work -> check -> attributable outcome

It remains an **ARCHITECTURAL HYPOTHESIS — UNPROVEN**.

## WHAT MODEL SEES

1. the ordinary user request;
2. one deterministically extracted accepted capability view containing exact
   ID, job, trigger, check, accepted/current status, and derived load target;
3. only when one specific relation is ambiguous, at most one bounded task
   anchor; and
4. after positive fit is established, only the selected capability body.

The model does not see checkpoint, receipt, evolution history, full NULNUL,
all Skill bodies, rejected capabilities, or repository-wide discovery during
applicability classification.

## WHAT MODEL MUST PROVE

Before selection, the model must emit a compact, inspectable fit result:

- which exact accepted capability ID, if any;
- which requested behavior/output satisfies its recorded job and trigger;
- which capability-owned constraint, artifact, or project check is material;
- whether a task anchor was needed and which single anchor supplied the
  decisive fact; or
- `NO_MATERIAL_MATCH` when no row has positive proof.

This is a decision record, not private chain-of-thought.

## WHAT IS DETERMINISTIC

- accepted/current roster membership;
- bounded-view extraction and field integrity;
- identity-to-path containment and body digest;
- the one-anchor maximum;
- zero body reads before positive match;
- selected-body-only loading;
- separate match, load, commitment, first-write, check, and attribution order;
- Direct and Project-Fit durable write sets;
- attribution eligibility from the ordered evidence record; and
- evidence durability, candidate freeze, evaluation, and rollback.

Semantic job interpretation remains model judgment.

## EXPERIMENT 8 CANDIDATE FAMILY

**CLOSED**

Candidate 1 reached its intended live Stage-2 boundary and exposed two central
defects: permissive applicability and unprovable commit ordering. Its one
generation is exhausted. Rewording “concrete match” would tune the rejected
decision surface rather than instantiate the one-anchor and attribution
boundaries.

The exact Candidate remains frozen rejection evidence. No Candidate 2 is
authorized.

## NEXT SINGLE EXPERIMENT

### Name

**NULNUL Experiment 9 — Contrastive Applicability + Attribution Boundary**

### Hypothesis

Request plus the current accepted capability view can settle clear cases; one
bounded task anchor can settle genuinely ambiguous cases. Positive material-fit
proof followed by separate exact-body load and Project-Fit commitment will
classify contrastive false/true positives correctly, make every credited
Project-Fit run attribution-eligible, and keep aggregate Direct input at or
below 120% of Champion.

### Candidate concept

Generate exactly one structurally new Candidate after deterministic benchmark
preflight and task/holdout freeze:

- retain the tiny positive-intent Stage-1 boundary;
- expose a deterministic read-only view from existing `project.md` evidence;
- require an observable `MATCH`, `NO_MATCH`, or one-budget `AMBIGUOUS` result;
- allow at most one task anchor before the final match/no-match decision;
- deterministically validate selected identity/path;
- separate actual body read, load proof, Project-Fit commitment, first product
  write, relevant check, and attribution events; and
- add no durable state, cache, routing database, service, Agent, or external
  dependency.

### Structural difference

Experiment 8 left “concrete match” as an unconstrained semantic jump and
combined match/load/commit in one tool event. Experiment 9 must instantiate a
conditional one-anchor applicability boundary and an ordered identity/load/
commit/attribution boundary. It may reuse `project.md` as evidence; it may not
reuse Candidate 1 as a wording base.

Likely surfaces are the small host Stage-1 entry, one read-only `project.md`
view/identity validator, exact local Skill loading, and experiment-only trace
guards. Exact product files must be justified and frozen before generation.

### Contrastive development tasks

| Class | Frozen design |
| --- | --- |
| False positive A | API/validation-adjacent normalization or formatting where no accepted validation/error capability owns the behavior. Expected Direct. |
| False positive B | Different superficial similarity, such as release-named product formatting with no release-documentation obligation. Expected Direct. |
| True positive A | Skill A's request-validation/error-code contract and specific check are genuinely required. Expected Project-Fit + exact Skill A. |
| True positive B | Different wording for the same Skill A job, still requiring its owned constraint/check. Expected Project-Fit + exact Skill A. |
| Distinct true positive | Skill B's distinct accepted job and check genuinely govern the task. Expected Project-Fit + exact Skill B. |
| Ambiguous development control | Request/view alone leave one specific row plausible; one frozen target anchor resolves the expected lane. |
| Governed control | One explicit host repair or setup request must select Governed and bypass Stage 2; one deterministic reachability control is sufficient beyond it. |

Do not reuse D1 wording as a routing rule or embed fixture answers in the
Candidate.

### Holdouts

Freeze before Candidate generation:

- `H-FALSE-POSITIVE`;
- `H-TRUE-PROJECT-FIT`;
- `H-DISTINCT-CAPABILITY`; and
- `H-AMBIGUOUS`, because the conditional anchor is the highest-risk new
  boundary.

Holdouts remain sealed until all development gates pass and are retired after
one use.

### Metrics

| Metric | Promotion gate |
| --- | --- |
| Applicability | False-positive Direct 100%; true-positive Project-Fit 100%; ambiguous branch correct 100%. |
| Capability identity | Exact expected ID 100%; irrelevant identities/bodies 0; Direct identities/bodies 0. |
| Load/commit | Body loads before Project-Fit commitment and first governed write on 100% of Project-Fit cases; bare Project-Fit 0. |
| Attribution | 100% of credited Project-Fit cases produce the complete task/job, ID, match, pre-work load, check, outcome record. |
| Strict outcome | Every credited Candidate task passes frozen strict/completion checks; Project-Fit strict gain >= +1 versus Champion; paired strict regressions 0; completion regressions 0. |
| Stage 1 | All ordinary contrastive tasks `ORDINARY`; explicit Governed control `GOVERNED` and bypasses Stage 2. |
| State authority | Direct/Project-Fit unrelated durable writes 0; Governed writes exactly task-authorized. |
| Direct cost | Aggregate Candidate input <=120% Champion; no full harness/live-state/evolution/body reads. |
| Overall cost | Complete Candidate input <130% Champion. |
| User burden | New harness-management questions 0. |
| External operations | 0. |

### Kill

Stop on any false-positive Project-Fit, true-positive Direct, wrong identity,
body load before justified match, bare Project-Fit, Direct body load,
Project-Fit state/setup/evolution overreach, attribution-order failure,
unauthorized write, Governed suppression, paired strict/completion regression,
user route question, holdout/evidence/infrastructure invalidity, or
mathematically impossible Direct/overall cost gate.

No generation 2 and no case-specific tuning.

### Promote

Promote only if all development and sealed contrastive cases pass every
applicability, identity, ordering, outcome, state, cost, burden, and durability
gate; Project-Fit gains at least one strict pass with no regression; Governed
reachability remains intact; rollback is available; and later independent full
product validation passes. No partial promotion.

### Rollback

Champion remains active. Discard the isolated Candidate on any kill, invalid
evidence, no advantage, cost failure, or later validation failure. Preserve
the Candidate and ordered traces as rejection evidence; do not tune it.

## EVOLUTION READINESS

If Experiment 9 succeeds, **yes**: each credited Project-Fit execution can
produce a causal record usable as input to the next Skill Evolution
experiment:

    TASK / JOB
      -> CAPABILITY ID
      -> POSITIVE MATCH EVIDENCE
      -> BODY LOAD BEFORE WORK
      -> PRODUCT OUTCOME
      -> PROJECT CHECK
      -> SUCCESS / FAILURE

That would establish attribution eligibility, not successful Skill Evolution.
The next experiment would still need to reproduce a capability-governed
failure, freeze one Skill revision, compare it against the accepted version,
use sealed holdouts, check regressions, and independently upgrade or roll back.

Routing accuracy without this record is insufficient for promotion.

## PRODUCT CHANGES

**0**

No Candidate, benchmark run, version change, tag, or publication was produced.

## VERSION

**v2.3 ARCHITECTURE REWORK REQUIRED**

## RELEASE

**NOT READY**

## NEXT

**STOP — do not implement Experiment 9.**
