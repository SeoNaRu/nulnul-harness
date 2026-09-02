# NULNUL POST-6C PRODUCT ARCHITECTURE REVIEW

Date: 2026-08-28

Scope: product architecture review only

Product changes: 0

Model-performance benchmarks run in this review: 0

New broad research passes run in this review: 0

## Claim discipline

This report uses five claim classes.

| Label | Meaning |
| --- | --- |
| **PROVEN** | Directly established within the stated frozen experiment or deterministic check. It is not a claim beyond that scope. |
| **PARTIAL** | Some required behavior was observed, but coverage, causality, or a control remains incomplete. |
| **UNPROVEN** | Required live evidence does not yet exist. |
| **KNOWN LIMITATION** | A reproduced defect was deliberately closed without a passing replacement. |
| **ARCHITECTURAL HYPOTHESIS** | A proposed explanation or design that still requires the next experiment. |

Paper evidence is used only to interpret the architecture. It is not NULNUL
performance proof.

Primary repository records used here:

- [Product North Star](../product-north-star.md)
- [Post-v2.2.1 proof decision](../roadmap/post-2.2.1-proof-decision.md)
- [Post-v2.2.1 baseline findings](../roadmap/post-2.2.1-baseline-findings.md)
- [Research decisions](../research/post-v2.3-research-decisions.md) and
  [research map](../research/post-v2.3-project-fit-research-map.md)
- [Resume fallthrough](../experiments/resume-fallthrough-state-preservation.md),
  [benchmark stability](../experiments/resume-benchmark-stability.md),
  [synchronization locus](../experiments/shared-setup-synchronization-locus.md),
  [full-workflow classification](../experiments/existing-setup-full-workflow-classification.md),
  and
  [structural-sync boundary](../experiments/existing-setup-owner-structural-sync-boundary.md)

The frozen external Experiment 2–6C reports and artifacts were inspected as
evidence inputs; this review does not rewrite or re-score them.

## CURRENT PRODUCT STATUS

North Star: **FROZEN — unchanged**

Champion: **exact NULNUL v2.2.1 frozen champion**

Release: **v2.3 NOT READY**

| Item | Status |
| --- | --- |
| North Star | **FROZEN.** Outcome First, Project-Fit First, Beginner / Calm Surface, No AI FOMO, Continuity, Adaptation / Evolution, Inspectability / Learnability, and Waste Awareness remain authoritative. |
| Champion | **PROVEN identity:** exact NULNUL v2.2.1 frozen from source revision cee7b91e2a992adee1582702b7a4084c631443b6. Frozen plugin-tree SHA-256: 7965cadc2aa55782194f3c1df31bacd403b4463b222fea3952731cabac350732. Frozen artifact SHA-256: 48a819a3878c9611487a4a632d9a62d1c9bda403f5dbca224466082ada26136b. |
| Post-v2.2.1 proof | **PROVEN:** Vanilla, exact v2.2.1, and the Project-Fit candidate each scored 21/25 strict. The candidate verdict was NO_ADVANTAGE. |
| Resume branch | **KNOWN LIMITATION:** LOCUS_D, MODE_GAP_PLUS_SECONDARY_TRIGGER. |
| Capability survivor action | **UNPROVEN:** Experiment 2 ended REJECT with ACTIVATED_NO_SURVIVOR_ACTION. |
| Live Skill evolution | **UNPROVEN:** Experiment 3A was CONFOUNDED and 3B was CONTROLLED_ACTIVATION_INVALID. |
| Ordinary local capability activation | **PARTIAL:** absent in 4C, present for all six 5B capability-relevant child runs, not reliable across ordinary work. |
| Harness self-evolution | **UNPROVEN:** Experiment 6C ended SELF_EVOLUTION_NOT_ACTIVATED. |
| Release | **v2.3 NOT READY.** No version, tag, publication, or release work is authorized by this review. |

## 3.0 PRODUCT DEFINITION

NULNUL 3.0 is a project-fit capability ecosystem, not a routing product with
evolution attached.

    USER asks for a result
      -> the project is understood
      -> an existing capability is used when it materially helps
      -> direct execution is used when no capability materially helps
      -> Codex or Claude implements
      -> the real repository verifies the result
      -> project experience becomes bounded evidence
      -> KEEP / UPGRADE / REPLACE / MERGE / RETIRE / CREATE
      -> Skills, Agents, tools, or routing may evolve
      -> the active ecosystem becomes more project-fit

The user does not design this system, choose an agent count, or operate an
evolution harness. The product remains:

> Simple outside. Inspectable inside.

The architecture therefore has two duties:

1. produce the strongest verified task outcome available for this project; and
2. preserve enough causal evidence to improve the ecosystem without making
   every request pay evolution cost.

Routing is an enabling boundary. Routing cleanliness by itself is not a product
outcome.

## PERFORMANCE NORTH STAR

The added performance principle is:

> Simple work should pay only the cost required to know that it is simple.

And:

> NULNUL should be always available, not always fully active.

The optimization unit is a verified result, not a raw completion:

- verified outcome per solved task;
- total input per verified result;
- total runtime per verified result;
- simple-task routing overhead;
- unnecessary repository reads; and
- irrelevant capability loading.

Verified outcome remains dominant. Among materially equivalent outcome paths,
the lower-context, lower-runtime, lower-read, lower-coordination path wins.

## MEASURED STRENGTHS

1. **PROVEN — the product evaluates outcomes rather than capability count.**
   The post-v2.2.1 proof preserved strict completion, completion, cost, reads,
   and disturbed-file evidence rather than treating activation as success.

2. **PARTIAL — exact v2.2.1 has selected completion and continuity advantages.**
   It completed 23/25 proof-view cases versus Vanilla's 21/25, including useful
   behavior in Cases 17 and 31. Aggregate strict success remained tied at
   21/25, so this is not proof of overall superiority.

3. **PROVEN — the root host entry can make NULNUL reachable before work.**
   Experiment 5A established the managed root entry as the earliest guaranteed
   host-loaded surface on the tested host.

4. **PROVEN within 5B's target fixtures — project-fit capability use is
   possible.** The child arm activated NULNUL 6/6, loaded the relevant Skill A
   6/6, avoided Skill B 6/6, passed strict 6/6, and made no setup writes on
   those capability-relevant tasks.

5. **PROVEN as deterministic mechanisms — state validation is stronger than
   semantic invocation.** Checkpoint fingerprints, the sole verification
   receipt writer, evolution schema validation, candidate count controls,
   independent-role checks, active/archive reconstruction, and rollback
   decisions have executable checks.

6. **PROVEN — evidence discipline is already valuable.** Frozen champions and
   candidates, preregistered cases, retired holdouts, rejected-history
   preservation, no-partial-promotion rules, and real repository checks
   prevented invalid runs from becoming product claims.

7. **PARTIAL — evolution primitives exist.** Experiment 6C reached the
   meta-evolution contract and rejected history, produced WHERE and WHY, formed
   one Coach-shaped proposal, and generated exactly one candidate. It did not
   establish evolution activation or candidate quality.

## RESEARCH INTERPRETATION

No new Research Pass was performed. The completed research is used only to
interpret the observed NULNUL evidence.

| Completed source family | Architecture lesson carried forward | Claim boundary |
| --- | --- | --- |
| Agentic Harness Engineering | Treat harness/scaffold shape, context, and tools as part of the causal execution system rather than neutral prompt text. | Does not prove a NULNUL routing or outcome advantage. |
| EvoSkill | A capability under evolution must be an explicit mutable unit with task evidence attached to its use. | Does not prove NULNUL can evolve a live Skill. |
| EvoSkills / CoEvoSkills | Ecosystem learning needs selection, contribution evidence, and survivor actions across capabilities rather than generation alone. | Does not validate NULNUL's KEEP/MERGE/RETIRE execution. |
| CODESKILL | Modular reusable behavior is useful only when selection and downstream verification are observable. | Does not prove correct automatic Skill selection in NULNUL. |
| SkillFoundry | Generated capability artifacts need bounded construction and evaluation, not existence-based credit. | Does not validate the 6C candidate, which was not evaluated. |
| Scaffold Effect | Scaffold choices can change both outcomes and cost; a strong base-model control and paired accounting remain necessary. | Does not explain away NULNUL-specific execution failures. |
| Self-Evolving Coding Agents | Self-modification needs an explicit mutable target, frozen evidence, independent acceptance, and rollback. | Does not prove NULNUL self-evolves. |

The shared transferable lesson is to bind an explicit mutable component to
ordered activation, downstream evidence, bounded competition, and survivor
action. The papers do not justify a new service, always-on trace, reinforcement
learning system, or capability collection.

## MEASURED FAILURE PATTERNS

The frozen 25-case post-v2.2.1 proof view was:

| Variant | Strict pass | Completion pass | Runtime total | Input-token proxy | Repository reads |
| --- | ---: | ---: | ---: | ---: | ---: |
| Vanilla | 21/25 | 21/25 | 889.613 s | 2,123,954 | 122 |
| exact v2.2.1 | 21/25 | 23/25 | 1,154.986 s | 2,813,285 | 144 |
| frozen Project-Fit candidate | 21/25 | 23/25 | 1,248.134 s | 3,367,586 | 141 |

The Project-Fit cost comparison against exact v2.2.1 is descriptive rather
than a causal paired estimate because that arm ran later. It remains a cost
warning, not a performance proof.

| Evidence | Observed result | Architectural implication |
| --- | --- | --- |
| Post-v2.2.1 proof | Strict tie at 21/25; Project-Fit candidate input about 19.7% and runtime about 8.1% above exact v2.2.1 in descriptive non-paired totals | More contract and context did not create strict advantage. |
| Cases 22 and 25 | Ordinary completed work disturbed checkpoint, receipt, root entry, and sometimes project state | Fast-path fallthrough can enter structural maintenance without a structural task owner. |
| Case 31 | Receipt refresh was legitimate | A blanket ban on state refresh would break a valid continuity path. |
| Experiment 2 | NULNUL activated but no KEEP, MERGE, or RETIRE action occurred | A lifecycle word is not an executable lifecycle transaction. |
| Experiment 3A | Skill under evaluation was not observably loaded | Failures cannot be attributed to an available but inactive capability. |
| Experiment 3B | Controlled activation preflight failed | Live Skill evolution remains unevaluated. |
| Experiment 4C | Product work occurred without NULNUL, roster, selection, or Skill-body load | Availability and a correct capability contract do not cause activation. |
| Experiment 5A | NULNUL and Skill activation became observable, but no strict advantage; input about 161%, runtime about 193%, reads about 200% of Champion | Always steering through the full path can buy activation at excessive cost. |
| Experiment 5B target | Six relevant child runs activated the correct Skill, passed strict, and avoided setup writes | A bounded project-fit path can work. |
| Experiment 5B simple | Continuity work, a forbidden test mutation, and about 231% simple-task input occurred | The boundary deciding whether the project-fit machinery should engage is not reliable. |
| Experiment 6C | Contract and history were read; WHERE, WHY, proposal, and candidate existed; frozen attribution still said NULNUL not loaded and capability count zero | Reading an evolution contract is not evolution activation. |
| Experiment 6C | evolution.archive.json was created outside the frozen write set | A valid archive executor can still be invoked without stage authority. |

Experiment 6C's exact diagnosis was:

- WHERE: host_entry_routing
- WHY: continuity validation occurs before classifying whether ordinary work
  needs NULNUL or a local Skill
- frozen attribution: nulnul_loaded = false; loaded capability count = 0
- candidate evaluation: not run

## CORE ARCHITECTURAL DIAGNOSIS

**ARCHITECTURAL HYPOTHESIS:** the central defect is not an insufficiently
sophisticated router. It is the absence of one small, observable boundary
between:

1. semantic task classification;
2. the contract that governs the selected lane; and
3. the write authority granted to that lane.

The frozen champion contains comparatively strong deterministic executors and
validators after a state transition has been attempted. It does not have an
equally strong mechanism that establishes which transition has begun before
the model reads broad context or invokes those executors.

The repeated shape is:

    valid executor + invalid or ambiguous invocation
      -> structurally valid but task-irrelevant mutation

This explains multiple families with one cause:

- fast-path failure exposes setup and continuity clauses;
- capability availability is mistaken for use;
- a lifecycle decision is not bound to a filesystem action;
- evolution references can be read without an evolution episode;
- the archive writer can be correct while the archive write is unauthorized;
- broad context activates mutually relevant but task-incompatible clauses.

The minimum target is therefore not a new framework. It is a bounded lane
decision at the first host surface, lazy contract loading after that decision,
and stage-owned deterministic writes.

## CURRENT EXECUTION MODEL

This is the frozen champion's actual execution shape, not its marketing flow.

| Current shipped surface | Actual responsibility |
| --- | --- |
| Marketplace and plugin manifests | Register the v2.2.1 skills-only plugin and make the NULNUL Skill discoverable. They establish availability, not live activation. |
| Managed AGENTS.md / CLAUDE.md block | Earliest guaranteed host-loaded surface; points to one state target and orders validation. |
| Primary SKILL.md | Orchestrates Fast Path, setup/adoption, discovery, execution, continuity, and evolution references. |
| sync_host_entry.py | Deterministically renders one host-owned managed block and preserves the inactive host; it does not decide whether the task semantically authorizes sync. |
| Checkpoint runner and validator | Execute and bind an exact completion command, fingerprint, and receipt after invocation. |
| Evolution validators, compactor, and rollback helper | Validate records, compact reconstructable history, and apply recorded terminal state decisions after invocation. |

The plugin has no shipped MCP server, hook, app, or external runtime service.

    Host automatically loads the managed AGENTS.md or CLAUDE.md block
                              |
                              v
          block points at one checkpoint.json or evolution.json
                              |
                              v
          validate the pointed state before broad repository inspection
                    /                         \
        eligible verified checkpoint       invalid / stale / out of scope
                   |                                   |
                   v                                   v
        bounded Fast Path                    Full Workflow fallthrough
        - read checkpoint                    - choose exactly one named mode
        - read listed files                    Fast / Adopt-Upgrade / New Setup
        - perform task                       - no explicit ordinary-existing-
        - run exact command once               setup mode owns this branch
        - runner writes receipt                         |
                   |                                   v
                   |                         discovery / roster / setup clauses
                   |                                   |
                   +----------------------+------------+
                                          v
                            product work and verification
                                          |
                     +--------------------+--------------------+
                     v                    v                    v
                continuity state      capability work      evolution clauses
                may be refreshed      may be selected      may be entered
                by broad triggers      but not loaded       without one
                                       observably            authority event

The important ordering problem is that state validation precedes a cheap
classification of whether the request needs continuity, project-fit
capabilities, setup, or evolution.

### Current transition map

| Transition | Trigger | Current owner | Input | Allowed reads | Allowed writes | Output | Observable proof | Dominant failure mode | Definition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Host installation to managed root entry | Setup, adoption, host addition, or selected state target | sync_host_entry.py plus the active host | Plugin identity, host, one state target | Root entry and selected state path | Active host entry only | Managed bounded block | Deterministic marker, target, idempotence, inactive-host preservation | The semantic reason for invoking sync is outside the script | **EXPLICIT** executor, **PARTIAL** invocation |
| Managed root entry to state validation | Host automatically loads the root entry | Root managed block | State pointer and validation command | Pointed checkpoint or evolution state and validator | None during validation | Eligible fast path or fallthrough | Host-loaded entry plus validator result | Runs before task class is known | **EXPLICIT**, but ordering is **CONTRADICTORY** with cheap simple work |
| Eligible checkpoint to Fast Path | Schema-3 verified checkpoint and matching receipt | Primary SKILL.md Fast Path | Task, checkpoint scope, listed files, exact command | Checkpoint, receipt, listed files, directly needed task files | Task files; runner later owns receipt fields | Bounded implementation and check | Matching fingerprint, bounded reads, exact runner invocation | Scope ambiguity or task exceeds checkpoint | **EXPLICIT** |
| Fast-path rejection to ordinary full work | Invalid, stale, unrelated, or out-of-scope checkpoint | No named ordinary-existing-setup mode | Task plus failed validation | Full workflow references can become relevant | Setup, root, checkpoint, receipt can become reachable | Product result plus possible maintenance | Transcript and diff only | Cases 22/25: mode gap plus secondary structural trigger | **MISSING / CONTRADICTORY** |
| Full workflow to mode | Model selects Fast Path, Adopt/Upgrade, or New Setup | Primary SKILL.md | Repository state and task | Repository instructions, harness state, roster | Mode-dependent | Mode choice | Usually model narrative, not a canonical event | Existing setup needing ordinary work fits none cleanly | **PARTIAL** |
| Mode to repository and capability discovery | Full setup/adoption or model belief that discovery is needed | NULNUL orchestrator | Task, repository facts, installed/local roster | Relevant project files; potentially broad roster and capability bodies | Discovery should be read-only | Repository model and candidate jobs | Read trace and discovery summary | Discovery can be skipped on relevant work or overused on simple work | **PARTIAL** |
| Discovered capability to fit decision | A job appears capability-relevant | Model under capability-discovery.md | Task/job, capability profile, provenance | Candidate metadata and body as needed | None | FIT VERIFIED or rejected | Explicit comparison when recorded | Fit may be inferred from a path or description alone | **PARTIAL** |
| Fit decision to selection | Capability is expected to improve outcome | NULNUL orchestrator | Verified fit, overlap, cost | Selected capability and competing evidence | None | Selected capability identity | Selection statement | Selection can remain descriptive | **PARTIAL** |
| Selection to load | Selected capability must govern work | Host/model context loader | Exact capability identity/version | Capability body before governed work | None | Capability in active context | Ordered body-load event before first product write | 3A and 4C: no observable load | **IMPLICIT** executable commitment |
| Loaded capability to product use | Capability instructions apply to implementation | Product executor | Task, project files, loaded capability | Task-relevant files | Product files within task scope | Product change or answer | Ordered actions consistent with unique guidance | Presence can be mistaken for causal use | **PARTIAL** |
| Product work to repository verification | Implementation is ready | Product executor; project command produces result | Changed files and project check | Changed and check-required files | Check outputs; no durable harness state by default | Pass/fail evidence | Exit status and strict completion check | Verification may complete while requested cleanup does not | **EXPLICIT** intent, **PARTIAL** outcome binding |
| Structural decision to project/root state | New setup, adoption, repair, host addition, or broad secondary trigger | Model plus sync/template scripts | Project topology, host, state target | Project instructions, state, host entry | project.md, selected host entry, initial state | Durable contract | Diff plus deterministic validators | Ordinary work can satisfy a broad trigger accidentally | **CONTRADICTORY** |
| Continuity decision to checkpoint | Durable work has an authorized resume boundary | Navigator/model; runner owns verification fields | Stable scope, files, exact completion command | Task state and files in scope | checkpoint.json | Pending or verified checkpoint | Schema and fingerprint validation | Model can refresh an unrelated checkpoint | **PARTIAL** |
| Completion check to verification receipt | Exact recorded checkpoint command is executed | run_checkpoint_check.py | checkpoint.json and command result | Checkpoint and command-required files | checkpoint verification fields and checkpoint.verification.json | Machine-valid receipt | Sole writer, exact command, fingerprint, exit code | Correct executor can be invoked for wrong task scope | **EXPLICIT** executor, **PARTIAL** authority |
| Reproduced feedback to evolution entry | Reproducible nonpass or bounded requested evolution | Model interprets evolution.md | Feedback, project facts, budgets, permissions | Active state, relevant rejected history | evolution.json and isolated candidate area in principle | Governed episode | No single canonical entry record before side effects | Contract read or failure narrative can be treated as entry | **MISSING / IMPLICIT** |
| Evolution entry to WHERE / WHY / proposal | Governed episode is active | Navigator and Coach roles | One reproduced feedback item and pathology | Relevant current component and rejected lookup | Episode/proposal record | One bounded proposal | Validator fields and links | Roles can be described without being operationally bound | **PARTIAL** |
| Proposal to generated, frozen candidate | One proposal passes generation preconditions | Candidate author under autonomous-evolution budget | Proposal, target component, write set | Frozen champion, target, allowed history | Isolated candidate only | Candidate identity and frozen bytes | Candidate count, hash, budget, freeze evidence | 6C generated a candidate although activation attribution failed | **PARTIAL / CONTRADICTORY** |
| Candidate to Gate and terminal decision | Frozen candidate has valid evaluation evidence | Independent Gate | Champion/candidate evidence, holdout inventory, permissions | Frozen evidence only | Gate verdict and controlled promotion state | Promote, reject, narrower scope, rollback, or no advantage | Independence, evidence, no-self-approval validators | Semantic quality still depends on a valid experiment | **EXPLICIT** record guards, **PARTIAL** live execution |
| Terminal decision to archive compaction | Closed history exceeds active resume need | compact_evolution_state.py only | Valid active evolution state and closed records | evolution.json and adjacent archive | evolution.json and evolution.archive.json atomically | Compact active state plus reconstructable archive | Digest/count/reconstruction checks | 6C: archive writer was invoked outside the frozen episode write set | **EXPLICIT** executor, **MISSING** entry authority |
| Harness-target episode to self-evolution attribution | Active evolution targets NULNUL's own component | No authoritative current runtime owner | NULNUL load/use events, target, candidate | Harness component and bounded evidence | Attribution record, then isolated candidate if valid | Self-evolution-active proof | Frozen 6C fields said nulnul_loaded=false and loaded count zero | Meta contract reachability was mistaken for activation | **MISSING** |

## FAILURE MAP

    Missing early lane boundary
              |
              +--------------------+----------------------+------------------+
              |                    |                      |                  |
              v                    v                      v                  v
      broad state-first       capability contract     lifecycle words    evolution contract
      context                 remains optional        remain descriptive  becomes reachable
              |                    |                      |                  |
              v                    v                      v                  v
      Cases 22 / 25          Experiment 3A / 4C       Cases 28 / 29       Experiment 6C
      5B simple              no pre-work load          Experiment 2        contract read
      invalid invocation     no causal attribution     no survivor action  without activation
              |                    |                      |                  |
              +--------------------+-----------+----------+------------------+
                                               |
                                               v
                               activation and authority collapse
                                               |
                         +---------------------+----------------------+
                         |                                            |
                         v                                            v
              valid writer, wrong stage                    full context on simple work
              checkpoint / receipt / archive               5A and 5B cost expansion
              6C outside-write-set archive                 conflicting instructions

The map does not say one missing sentence caused every failure. It says the
same missing execution boundary lets several otherwise reasonable clauses
compete for control.

## ACTIVATION MODEL

Activation is an ordered runtime fact. Reachability, availability, a path
printed in context, or a file read without governing semantics is insufficient.

| Level | Precise definition | Required observable proof | What does not prove it | Authority granted |
| --- | --- | --- | --- | --- |
| **HOST ROUTED** | The host has automatically loaded its owned managed root entry, making NULNUL's lane decision reachable. | Host semantics establish automatic root loading; managed marker and content identity are present before task work. A read counts here only because the host guarantees this surface. | Plugin installation alone, a catalog listing, or a path printed by another file. | None beyond reading the micro-router. |
| **HARNESS ACTIVE** | The request was classified into a NULNUL-governed lane, and that lane's controlling contract was loaded before the first action it governs. | Ordered trace: lane decision, exact core/structural/evolution contract load, then governed read/write. | HOST ROUTED, a pointer to SKILL.md, or a later incidental read. | Only the reads and decisions declared by that lane; no durable write authority by implication. |
| **CAPABILITY ACTIVE** | A named, versioned project Skill, Agent profile, or tool was selected and its governing instructions/tool interface entered context before the work for its assigned job. | Ordered identity-specific load or tool-binding event before governed work, plus assigned job. | Available, discovered, fit-verified, selected, or mentioned capability without the load/bind event. | The assigned product job only; no setup, harness, or lifecycle authority. |
| **EVOLUTION ACTIVE** | An authorized evolution controller has opened one bounded episode for one reproduced feedback item with target, WHERE, WHY, budget, permissions, and write set fixed before generation. | Canonical episode-entry record or equivalent ordered trace validated before candidate bytes; one target and allowed writes; rejected-history lookup status recorded. | Reading evolution.md or meta-evolution.md, producing a suggestion, or observing a failure. | Candidate-workspace writes and episode-state writes within the fixed envelope; no promotion authority. |
| **SELF-EVOLUTION ACTIVE** | EVOLUTION ACTIVE is true, the target is a frozen NULNUL harness component, NULNUL's pre-candidate contribution is attributable, and the same governed evolution procedure is operating on that target. | Evolution-entry proof, frozen target/champion identity, NULNUL governing load before the diagnosed work, causal attribution record, and candidate writes confined to the isolated workspace. | Meta-evolution reachability, rejected-history reads, WHERE/WHY, a proposal, or candidate generation alone. | The isolated harness candidate only. The candidate cannot evaluate, promote, publish, or release itself. |

The direct lane intentionally stops at HOST ROUTED. A simple task can be
correctly handled without HARNESS ACTIVE.

## AUTHORITY MODEL

Activation and authority are orthogonal:

- NULNUL active does not authorize setup or continuity mutation.
- A capability active for an API job does not authorize changing the harness.
- Evolution active does not authorize promotion.
- Self-evolution active does not authorize publication or release.

Owner names below are stages. They do not require a permanent Agent. One root
executor may perform several stages serially, except where independent Gate
judgment is required.

### Write-authority table

| Durable target | Current writer / enforcement | Recommended write owner | Event that authorizes a write | What does not authorize a write | Target enforcement |
| --- | --- | --- | --- | --- | --- |
| AGENTS.md | sync_host_entry.py writes a bounded managed block; invocation reason is model judgment | Codex Host Entry Writer | New setup, explicit Codex adoption, explicit host repair/addition, or a validated live-state pointer transition | Ordinary product work, checkpoint failure, state existence, capability activation, or evolution contract read | Deterministic managed-block writer plus lane/event precondition |
| CLAUDE.md | sync_host_entry.py; same invocation gap | Claude Host Entry Writer | New setup, explicit Claude adoption, explicit host repair/addition, or validated live-state pointer transition | Same exclusions; adopting the other host | Deterministic writer; inactive entry preserved byte-for-byte |
| docs/nulnul/project.md | Model/template under setup or adoption clauses | Structural Setup Owner | New setup, explicit adoption/upgrade, or verified material topology change | Direct task, capability use, fast-path rejection, or receipt refresh | One structural writer and schema/diff validation |
| docs/nulnul/checkpoint.json | Model can create/update; run_checkpoint_check.py updates verification fields | Continuity Writer; runner is sole verification-field writer | Explicit durable checkpoint creation/replacement for the current task scope, or the runner recording its exact command result | Unrelated task completion, mere staleness, harness activation, or state discovery | Deterministic scoped transition plus existing schema/fingerprint checks |
| docs/nulnul/checkpoint.verification.json | run_checkpoint_check.py only | Verification Receipt Writer | Execution of the exact command stored in the authorized checkpoint | A model claim, another test command, or an unrelated completion | Already deterministic; add scope-entry precondition, keep sole writer |
| docs/nulnul/evolution.json | Model-maintained state checked by validators | Evolution State Writer | Valid EVOLUTION ACTIVE entry, then stage transitions inside that episode | Product failure alone, reading an evolution reference, or candidate existence | Deterministic state transition validation and one writer |
| docs/nulnul/evolution.archive.json | compact_evolution_state.py only | Evolution Compactor | An authorized terminal evolution transition whose closed history qualifies for compaction | Rejected-history lookup, ordinary resume, contract read, or candidate generation | Existing atomic digest/reconstruction writer plus explicit episode/write-set guard |
| Project-local Skill | Model may edit during setup/evolution; validators govern evidence | Isolated Capability Candidate Author; controlled promotion applier | Active Skill-evolution episode with reproduced attributed feedback, fixed target, permissions, and isolated write set | Availability, selection, use, or an unattributed failure | Candidate isolation, source/freeze hash, independent Gate, atomic promote/rollback |
| Agent definition | Model may create/update under assembly/evolution contracts | Isolated Agent Candidate Author; controlled promotion applier | Active Agent-evolution episode proving a distinct job and permission-safe target | Desire for more agents, capability count, or ordinary task complexity | Same isolation/Gate controls; protected host paths remain read-only absent approval |
| NULNUL harness source | Model candidate process plus release controls | Isolated Self-Evolution Candidate Author; independent Gate and user-authorized release owner | SELF-EVOLUTION ACTIVE with frozen champion, attributable failure, fixed harness target/write set, and sealed evaluation | Meta contract or history read, WHERE/WHY, proposal, candidate bytes, or candidate self-evaluation | Candidate sandbox, exact hashes/count, independent Gate, rollback; publication remains separately approved |

**UNPROVEN:** a skills-only host can prevent every unauthorized raw edit before
it happens. The target should first route state changes through the existing
deterministic writers and fail on any protected-state diff outside the lane.
If a bounded experiment proves that model-only invocation cannot hold this
boundary, that evidence, not architectural taste, would justify a hook or other
small enforcement surface.

### Concern ownership decision table

| Concern | Current owner | Current problem | Recommended owner | Model vs deterministic | Observable proof |
| --- | --- | --- | --- | --- | --- |
| host entry | Active host plus sync_host_entry.py | State-first instructions are correct structurally but over-broad operationally | Host Entry Writer | Deterministic render; model authorizes only named structural event | Managed marker, host identity, one target or router version, inactive entry unchanged |
| task classification | Distributed clauses in root entry and SKILL.md | Happens after state validation or remains implicit | Root Micro-Router | Model semantic judgment inside a tiny deterministic lane vocabulary | Lane decision before any lane-only read |
| harness activation | Model follows SKILL.md if it notices relevance | Reachability can be mistaken for control | Lane Controller | Deterministic ordering requirement; model chooses lane | Exact governing contract loaded before governed work |
| capability discovery | Setup/full workflow and capability-discovery.md | Can be absent on relevant work or expensive on simple work | Project-Fit Orchestrator | Model scopes jobs; roster enumeration/read events are observable | Bounded roster and candidate identities |
| capability selection | NULNUL model judgment | Selection can remain descriptive | Project-Fit Orchestrator | Model fit judgment with recorded comparison | Exact selected identity, job, fit reason, rejected overlap |
| capability load | Model/host context behavior | No executable commitment connects selection to load | Context Loader under Lane Controller | Observable ordered load is deterministic evidence | Body/tool binding before first governed action |
| product execution | Root Codex/Claude, sometimes assembled roles | Harness concerns can displace implementation | One Product Executor | Model work under project/capability instructions | In-scope diff or answer, one final synthesis owner |
| verification | Product executor plus project command | Completion can coexist with missed cleanup or state side effects | Product Executor runs; Verification Owner records | Model chooses relevant check where unspecified; exit/status/diff deterministic | Real command result, strict task check, protected-state diff |
| project setup | Full Workflow model plus templates/scripts | Broad triggers allow setup on ordinary work | Structural Setup Owner | Model detects topology; deterministic allowed-write set | Explicit structural lane, project contract, exact permitted setup diff |
| checkpoint | Navigator/model plus validator/runner | Fast-path rejection can trigger unrelated refresh | Continuity Writer | Model proposes scope; deterministic scope, schema, command, fingerprint | Authorized checkpoint transition and validation |
| receipt | run_checkpoint_check.py | Correct writer can be invoked in the wrong lane | Verification Receipt Writer | Deterministic, after authorized continuity event | Exact command, result, fingerprint, sole-writer identity |
| evolution entry | Evolution prose interpreted by model | No authoritative event separates reading from entering | Evolution Controller | Model diagnoses; deterministic entry envelope | Episode ID/trace, target, WHERE/WHY, budget, permissions, write set before generation |
| candidate generation | Coach/candidate-author expectations plus validators | Generation can occur before activation attribution is valid | Isolated Candidate Author | Model generates; deterministic count, target, budget, write set | One candidate identity and frozen bytes in isolated area |
| Gate | Logical Gate role plus validators | Strong records do not repair invalid input evidence | Independent Gate | Model semantic comparison; deterministic independence/evidence preconditions | Gate identity, frozen evidence, verdict, no self-approval |
| archive | compact_evolution_state.py | Writer is strong; invocation authority is missing | Evolution Compactor | Deterministic after terminal authorized event | Adjacent path, atomic write, digest/count/reconstruction, allowed-write proof |
| self-evolution attribution | No authoritative runtime owner | Contract/history reads and candidate generation can be mistaken for activation | Evolution Observer, then independent Gate | Ordered load/use evidence deterministic; causal credit judged independently | Frozen harness target, prework NULNUL load/use, downstream comparison |

## MODEL JUDGMENT VS DETERMINISTIC ENFORCEMENT

The smallest reliable boundary keeps semantic work with the model and makes
stage identity, ordering, and irreversible transitions mechanical.

| Model judgment remains appropriate | Deterministic enforcement is required |
| --- | --- |
| Whether the task is semantically direct, project-capability relevant, or structural/evolutionary | The lane decision occurs before any lane-only read or write |
| Whether a capability's unique behavior is project-fit | Exact capability identity is loaded before governed work |
| Whether two capabilities overlap or one has unique value | A KEEP/MERGE/RETIRE decision is not complete until its required file action and verification exist |
| Whether a failure is reproducible and plausibly generalizes | One episode, one target, bounded generation count, explicit permissions and write set |
| Whether external search could materially improve an uncovered job | No external access, credential use, installation, or publication without the applicable permission |
| How to implement the product task | One state target, one writer process, exact completion command, receipt fingerprint, protected-state diff |
| Whether observed behavior deserves causal credit | Evidence must show load before governed work; independent Gate decides promotion |
| Whether candidate quality is materially better | Champion/candidate freeze, holdout exposure, no self-approval, evidence-before-promotion, rollback |

The model may propose a transition. It may not make the transition true merely
by narrating it.

## WHY CONTRACT CORRECTNESS != EXECUTION CORRECTNESS

The structural reason is larger than model nondeterminism.

1. **Static tests validate descriptions and end states, not ordered runtime
   commitments.** A contract can contain KEEP, MERGE, and RETIRE while no
   transition binds one decision to one required filesystem action.

2. **Only the host entry is guaranteed to be loaded.** Downstream Skill and
   reference files are conditional model reads. Their correctness cannot govern
   work that begins before they enter context.

3. **Validators run after invocation.** They can prove that a receipt, archive,
   or evolution state is internally valid. They cannot infer that the current
   task authorized the writer. This is the VALID_EXECUTOR /
   INVALID_INVOCATION pattern.

4. **Several natural-language clauses compete in the same context.** Fast-path
   invalidation, state existence, setup synchronization, continuity, discovery,
   and evolution are each locally reasonable. With no prior lane boundary, a
   simple task can satisfy enough secondary language to activate the wrong work.

5. **Availability, selection, load, use, and attribution are collapsed in
   prose.** Experiment 3A and 4C show that a capability can exist without being
   loaded. Experiment 6C shows that evolution materials can be read without the
   harness being attributable.

6. **Proof is missing at the transition where it matters.** Later product
   success does not prove the Skill governed it; a candidate file does not prove
   evolution was active; a valid archive does not prove archive authority.

Contract tests remain necessary. They should be complemented by ordered
activation evidence and lane-specific write-set checks, not replaced by more
wording tests.

## ROOT ENTRY REVIEW

| Root-entry shape | Evidence fit | Main advantage | Main failure |
| --- | --- | --- | --- |
| Pointer only | Fits the performance concern and preserves a calm surface | Near-zero routine harness context | Repeats 3A/4C: nothing reliably converts availability into project-fit activation |
| Micro-router | Fits 4C's activation gap and 5A/5B's cost/side-effect evidence | Pays only for one early class decision; loads heavier contracts lazily | Semantic classification quality and host-observable ordering remain **UNPROVEN** |
| Always-active harness | Makes activation easiest to observe | Uniform governing contract | 5A/5B already show excessive simple and target cost plus conflicting state clauses |

**Recommendation:** the root entry should be a micro-router, not a state
validator and not a full harness.

Its complete job is:

1. classify the request as Direct, Project-Fit, or Governed;
2. load exactly the selected lane entry; and
3. grant no durable write authority itself.

It should not enumerate capabilities, validate a checkpoint, read project.md,
or load evolution history. If the task cannot be classified cheaply from the
request and the minimally necessary target context, it enters Project-Fit;
uncertainty is not permission to enter Structural/Evolution.

## SKILL.MD REVIEW

Primary SKILL.md is currently **B: a contract whose execution boundaries are
overloaded**.

The problem is not its line count or number of reference files. It currently
has operational responsibility for resume, setup, adoption, discovery,
capability routing, agent assembly, product execution, verification,
continuity, evolution, meta-evolution, personal adaptation, and
generalization. Some of those concerns require mutually exclusive authority.

Three consequences follow:

- a Fast Path fallthrough exposes setup clauses to ordinary work;
- loading the orchestrator can make continuity and evolution instructions
  relevant before task need is known; and
- adding another exception increases context without creating an executable
  boundary.

The target responsibility is narrower:

- SKILL.md remains the thin Project-Fit orchestration kernel;
- it owns bounded discovery, fit, selection, load-before-use, one executor, and
  real verification;
- setup/adoption, continuity, evolution, meta-evolution, personal adaptation,
  and generalization remain existing references loaded only by a Governed
  entry; and
- no file is split merely for cleanliness.

This preserves the existing mechanisms and changes when they are authoritative.
Personal adaptation remains opt-in and confined to a user-approved existing
home. Generalization remains gated behind three independent
Personal-Gate-verified mechanism families, privacy-safe summaries, sealed
holdouts, and an independent Meta Gate. Neither boundary belongs in ordinary
task context, and neither is activated by this architecture review.

## CAPABILITY ACTIVATION REVIEW

The capability lifecycle must remain seven distinct states:

    AVAILABLE
       -> DISCOVERED
       -> FIT VERIFIED
       -> SELECTED
       -> LOADED
       -> USED
       -> ATTRIBUTED

| State transition | Primary decision | Required enforcement / proof | Failure if absent |
| --- | --- | --- | --- |
| Unknown to AVAILABLE | Filesystem, installed-plugin, or tool roster fact | Exact identity, provenance, compatibility surface; a path alone is not credit | Phantom or duplicate capability |
| AVAILABLE to DISCOVERED | Bounded job-relevance scan | Roster/read record scoped to the task | 4C-style capability invisibility |
| DISCOVERED to FIT VERIFIED | Model judges unique behavior, project fit, overlap, permissions, and likely outcome value | Explicit fit comparison; unknown remains unknown | Popularity or description substituted for verification |
| FIT VERIFIED to SELECTED | Model chooses non-overlapping set with expected material value | Selected identity, assigned job, and rejection/merge rationale for overlap | Capability collection or ambiguous ownership |
| SELECTED to LOADED | Lane controller/context loader | Body or tool-binding event before first governed action | 3A/4C: selected or available capability cannot govern work |
| LOADED to USED | Product executor applies the assigned behavior | Task action tied to unique instruction/tool effect; otherwise use remains unknown | Presence mistaken for use |
| USED to ATTRIBUTED | Independent evaluation judges contribution | Downstream verified result against a fair baseline plus ordered activation evidence | Skill/Agent evolution trained on non-causal failures |

Only ATTRIBUTED evidence may justify evolving or retiring a capability because
of its task performance. A separate explicit cleanup request can authorize a
lifecycle action without prior performance attribution, but the action must
still be observable and verified.

This pipeline makes future Skill Evolution testable without experiment-specific
activation hacks: the ordinary product path itself emits or preserves the
ordered facts needed for attribution.

## STATE ARCHITECTURE REVIEW

Ordinary product execution should not preload durable harness state. State is
lazy and stage-specific.

| State | Purpose | Reader | Writer | Write event | Active context required? | Lazy access possible? | Needed by ordinary product task? | Current architectural issue |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| docs/nulnul/project.md | Stable project contract, hosts, outcomes, topology, permissions | Structural Setup lane; Project-Fit lane only when a project fact is materially needed | Structural Setup Owner | Setup, adoption/upgrade, or verified material topology change | Structural lane for writes | Yes | Usually no | Can become coupled to ordinary setup fallthrough |
| checkpoint.json | Concise durable resume boundary with exact completion command | Continuity lane and eligible Fast Path | Continuity Writer; runner owns verification fields | Deliberate checkpoint create/replace or exact check result | Continuity lane or explicit Fast Path | Yes | No, unless the request is continuation/resume | Root entry validates it before task classification |
| checkpoint.verification.json | Machine-valid receipt bound to checkpoint fingerprint | Fast Path validator and continuity verifier | run_checkpoint_check.py only | Exact recorded command execution | Continuity/Fast Path | Yes | No | Correct writer can be invoked for an unrelated task |
| evolution.json | Active and recent governed learning state | Evolution lane, validators, Gate | Evolution State Writer | Authorized episode entry or validated stage transition | Evolution lane | Yes | No | Reading the contract/history lacks an authoritative entry event |
| evolution.archive.json | Digest-bound closed history and targeted rejected lookup | Evolution lane only when a matching proposal requires it | compact_evolution_state.py only | Authorized terminal compaction | Evolution lane | Yes | No | 6C wrote it outside the frozen write set |
| Managed root entry | Host-local availability and lane selection | Host on every request | Host Entry Writer | Setup/adoption/repair/host addition or router update | Host-routed context only | No; it is the always-loaded surface | Yes, but only the tiny router | It currently embeds eager state validation and therefore imports state cost |

The checkpoint can safely become stale after an unrelated simple task. A later
Fast Path validator should reject it. Eagerly refreshing it is not necessary
unless the current request explicitly owns continuity for that scope.

## EVOLUTION ARCHITECTURE REVIEW

Self-evolution should reuse the same evolution transaction with a harness
target. It should not become a parallel special system.

| Stage | Frozen champion today | Classification | Recommended executable boundary |
| --- | --- | --- | --- |
| FEEDBACK | Durable feedback and validator links exist | **PARTIAL executable mechanism** | One reproduced nonpass tied to task evidence and capability attribution state |
| EVOLUTION TRIGGER | Described in evolution contracts | **Natural-language expectation / ambiguous** | Evolution Controller opens one episode before candidate work |
| WHERE | Required by bounded autonomous validation | **Deterministic record guard after invocation** | Fixed component locus in the entry envelope |
| WHY | Required pathology statement | **Deterministic record guard after invocation** | Reproduced mechanism, not a wording preference |
| REJECTED HISTORY | Active/archive compaction and targeted lookup exist | **Executable mechanism plus deterministic guard** | Record lookup hit/miss; read only, no archive-write authority |
| COACH PROPOSAL | Coach role and bounded proposal fields exist | **Partial natural-language mechanism** | One proposal linked to feedback and pathology |
| CANDIDATE | Count/budget/identity checks exist; generation is model action | **Partial executable mechanism** | Candidate author can write only isolated fixed target after entry and attribution preconditions |
| FREEZE | Frozen artifacts and evidence practices exist | **Deterministic guard** | Champion and candidate identities fixed before evaluation |
| GATE / EVALUATION | Independent Gate, fair baseline, sealed holdout, permission checks exist | **Strong deterministic envelope; semantic evaluation remains model/project work** | Gate refuses invalid activation, authority, freeze, or evidence regardless of score |
| PROMOTE / REJECT / ROLLBACK | Provisional/live-cycle/rollback validators exist | **Executable mechanism plus guards** | Separate promotion authority; candidate never self-approves |
| ARCHIVE | Atomic compactor and reconstruction exist | **Executable mechanism with missing invocation boundary** | Terminal episode authorizes sole compactor and exact adjacent path |
| SELF-EVOLUTION | Meta references exist; 6C attribution failed | **AMBIGUOUS / UNPROVEN** | Same episode with target_kind=harness and pre-candidate NULNUL attribution |

Self-evolution activation ends neither at candidate generation nor at a Gate
win. It begins when the governed harness-target episode has valid entry and
attribution. Promotion is a later independent transition.

## CONTEXT / PERFORMANCE REVIEW

| Evidence slice | Input | Runtime | Repository reads | Interpretation |
| --- | ---: | ---: | ---: | --- |
| Experiment 5A target pair, candidate relative to Champion | about 161% | about 193% | about 200% | Full activation can cost far more without a strict gain. |
| Experiment 5B capability-relevant child, relative to Champion | about 145% | about 130% | about 133% | Correct Skill activation produced outcome value, but the tax remains material. |
| Experiment 5B simple child, relative to Champion | about 231% | not the decisive sole metric | unnecessary state reads/work observed | A no-Skill task paid the largest relative context tax and suffered side effects. |

These figures do not prove a universal cost ratio. They prove that a design
which routinely loads continuity, setup, discovery, and evolution context for
simple work violates the performance North Star.

The target cost shape is:

- fixed small cost: one host-loaded lane decision;
- variable project-fit cost: only when capability value is plausible;
- structural/evolution cost: only after an explicit governed entry;
- attribution storage cost: only when evidence is retained for learning.

## RECOMMENDED EXECUTION MODEL

    Host-managed micro-router (always loaded, read-only)
                              |
            classify before state or capability discovery
                 /                 |                    \
                v                  v                     v
         DIRECT lane        PROJECT-FIT lane       GOVERNED lane
         no harness core    load thin core          choose one substage
         no state           bounded discovery       setup / continuity /
         no capability      fit -> select -> load   evolution
                |                  |                     |
                v                  v                     v
         Product Executor   Product Executor        named stage owner
                |                  |                     |
                v                  v                     v
         smallest real      real project check      deterministic writer /
         project check      + attribution facts     validator / Gate
                \                  |                     /
                 +-----------------+--------------------+
                                   v
                         one verified user result
                                   |
                  retain learning evidence only when justified

The three top-level lanes are mutually exclusive for the initial request. A
lane may request a deliberate transition later, but that transition must be
observable and re-authorized; it is not an incidental fallthrough.

## SIMPLE TASK TARGET FLOW

Example: “rename this variable” or “fix this small formatting bug.”

| Item | Target behavior |
| --- | --- |
| Files read | Host root entry, target file, only directly necessary callers/project instructions, and the minimal check definition if needed |
| Harness components loaded | Micro-router only |
| Capabilities loaded | None |
| State touched | None: no project.md, checkpoint, receipt, evolution state, archive, or host sync |
| Product owner | Direct Product Executor |
| Verification | Smallest real repository check that can falsify the change; strict diff/scope check |
| Learning | No durable evolution write. If a reproducible nonpass later justifies learning, it enters a separate governed transition. |

The task pays for classification and verification, not for proving that every
installed capability is irrelevant.

## CAPABILITY TASK TARGET FLOW

Example: an API change for which a verified local API Skill has unique value.

1. The micro-router selects Project-Fit because a capability could materially
   improve the result.
2. The thin NULNUL core becomes HARNESS ACTIVE.
3. Discovery is bounded to the task's job; the full project setup and
   continuity state stay unloaded.
4. Available candidates are compared, one non-overlapping set is selected, and
   the exact Skill body is loaded before implementation.
5. One Product Executor implements and runs real project checks.
6. Ordered activation, use, outcome, cost, and protected-state diff are
   available for attribution.
7. No capability or harness mutation occurs unless a separate evolution entry
   is authorized.

## STRUCTURAL / EVOLUTION TARGET FLOW

Examples: adopt NULNUL, repair a host entry, create a durable checkpoint, or
run an authorized evolution episode.

1. The micro-router selects Governed and names exactly one initial substage.
2. Only that substage's contract and required state enter context.
3. Its stage owner declares target and allowed writes before mutation.
4. The deterministic writer performs state changes; validators check the
   transition and a negative control.
5. Evolution, when selected, fixes feedback, WHERE, WHY, budget, permissions,
   candidate target, and write set before generation.
6. Independent Gate and promotion/rollback stay separate from candidate
   authorship.
7. A new task class requires another explicit transition, not fallthrough.

## SIMPLE vs PROJECT-CAPABILITY vs STRUCTURAL / EVOLUTION

    Request
      |
      v
    [Micro-router: classify from request + minimum target context]
      |
      +-- DIRECT / SIMPLE
      |     reads: target + necessary callers
      |     loads: no NULNUL core, no capability, no durable state
      |     writes: product scope only
      |     verifies: smallest real project check
      |
      +-- PROJECT-CAPABILITY
      |     reads: thin core + bounded roster + selected body + task files
      |     loads: exact selected capability before governed work
      |     writes: product scope only
      |     verifies: real checks + activation/use attribution facts
      |
      +-- STRUCTURAL / EVOLUTION
            reads: exactly one stage contract + its state
            loads: setup, continuity, or evolution authority
            writes: declared stage-owned write set only
            verifies: deterministic transition guard + real project check

## ARCHITECTURAL INVARIANTS

1. **Verified project outcome outranks capability count and routing
   sophistication.**
2. **Project-fit survivor value, not ecosystem size, determines KEEP,
   UPGRADE, REPLACE, MERGE, RETIRE, or CREATE.**
3. **Availability is not activation.**
4. **Activation is not authority.**
5. **Observation or contract reachability is not a state transition.**
6. **Ordinary product work is not setup, continuity, or evolution work.**
7. **Simple work has a bounded harness tax and does not preload durable
   harness state.**
8. **A capability receives causal credit only when loaded before the work it
   governs and tied to downstream verification.**
9. **Every durable state target has one stage owner and one writing process.**
10. **A lifecycle decision is incomplete until its required action and
    verification are observable.**
11. **Evolution begins with one authorized, bounded episode; reading an
    evolution contract does not enter it.**
12. **A candidate cannot approve or promote itself; freeze and valid evidence
    precede Gate judgment.**
13. **Unknown remains distinct from verified and failed; lack of observability
    cannot be converted into credit.**
14. **Closed history is lazy, digest-bound, reconstructable, and queried only
    for a matching proposal.**

## KEEP

| Mechanism | Decision | Reason |
| --- | --- | --- |
| Frozen Product North Star | **KEEP** | It correctly makes architecture serve outcome and project fit. |
| Outcome-first evaluation and real repository checks | **KEEP** | Prevented activation and completion from being mistaken for strict success. |
| Exact Champion/candidate identity and frozen artifacts | **KEEP** | Required for causal comparison and rollback. |
| Independent Gate and no self-approval | **KEEP** | Essential authority separation. |
| Host ownership and inactive-entry preservation | **KEEP** | Correct cross-host boundary; no evidence justifies weakening it. |
| One live-state target | **KEEP** | Reduces split authority. |
| Exact checkpoint completion command, fingerprint, and sole receipt writer | **KEEP** | Strong deterministic continuity mechanism; invocation must be narrowed, not removed. |
| Rejected-history preservation and digest-bound archive | **KEEP** | Prevents repeated proposals while keeping ordinary context bounded. |
| Provisional candidate, observed live cycle, rollback, no partial promotion | **KEEP** | Correct safety boundary for mutable capabilities. |
| Preregistration, sealed/retired holdouts, exposure accounting, fair retry baseline | **KEEP** | Protects learning claims from leakage and weak baselines. |
| Permission boundaries and no unapproved publish/deploy/credential use | **KEEP** | Activation cannot broaden authority. |
| Logical Navigator, Coach, and Gate responsibilities | **KEEP as roles, not mandatory agents** | Separation is useful; agent count is not a target. |

## SIMPLIFY / REMOVE / MOVE

| Current mechanism | Why it exists | Measured value | Measured cost / failure | Recommendation |
| --- | --- | --- | --- | --- |
| Root entry validates live state before task classification | Fast resume and continuity | Root is reliably host-loaded; Case 31 receipt refresh works | Cases 22/25 and 5B simple entangle ordinary work with state; high context | **MOVE RESPONSIBILITY:** root classifies; Continuity lane validates state |
| Primary SKILL.md exposes setup, resume, routing, execution, evolution, and generalization | One self-contained orchestrator | Contracts are discoverable and deterministic references are reachable | Competing clauses and large context; no clean ordinary fallthrough mode | **SIMPLIFY:** thin Project-Fit core; lazy governed references |
| Full Workflow has Fast, Adopt/Upgrade, and New Setup as its exhaustive modes | Separate setup histories | Setup/adoption distinctions are useful | Existing setup ordinary work fits none; LOCUS_D | **MERGE/SIMPLIFY:** top-level Direct, Project-Fit, Governed; setup modes live under Governed |
| State-exists/selects-state triggers can cause host sync | Maintain one live target | Correct after real setup/state transition | VALID_EXECUTOR / INVALID_INVOCATION on ordinary work | **NARROW AUTHORITY:** only structural transition may invoke sync |
| Capability lifecycle is primarily descriptive | Encourage cleanup and survivor selection | Correct product identity | Experiment 2 and Cases 28/29 show no action | **KEEP semantics; ADD SMALL MECHANISM:** bind decision to required diff/check |
| Roster enumeration and discovery are broadly available in full workflow | Find project-fit capabilities | 5B relevant selection succeeded | 4C skipped it; simple work should not pay it | **MOVE:** Project-Fit/Structural lanes only, bounded by job |
| Checkpoint and receipt machinery | Fast durable resume | Case 31 and deterministic validation | Wrong-scope invocation in Cases 22/25/5B simple | **KEEP and NARROW AUTHORITY** |
| Evolution active state and archive | Learn without unbounded resume context | Strong validation, reconstruction, rejected lookup | 6C archive write outside write set | **KEEP; ADD SMALL ENTRY GUARD** before any evolution writer |
| Meta-evolution as additional readable contract | Allow NULNUL to improve itself | 6C could reach reasoning and candidate primitives | Reachability was mistaken for activation | **MOVE RESPONSIBILITY:** target_kind inside the normal evolution transaction |
| Personal adaptation and generalization clauses in the primary path | Future cross-project learning | Strong permission/holdout boundaries on paper | No need on ordinary project work; context and premature relevance | **MOVE:** lazy Governed references; do not remove safeguards |
| Many special prohibitions expressed independently | Patch observed failures | Some contract tests pass | Wording accumulates without an executable commitment | **MERGE:** use the fourteen invariants and stage authority table |

## ARCHITECTURE OPTION A — POINTER-ONLY ENTRY

| Required concern | Option A |
| --- | --- |
| Host entry | Identifies that verified NULNUL state/capabilities may exist and points to the harness on explicit demand. |
| Cheap task classification | Host executes directly by default; user wording or an obvious structural request must opt into NULNUL. |
| Harness activation | Explicit invocation or a later model decision loads the current harness. |
| Capability activation | Current discovery/selection/load behavior after invocation. |
| Product execution | Direct host executor for most work; harness executor after explicit activation. |
| Verification | Real repository checks in either path. |
| State authority | Existing state writers remain behind explicit harness invocation. |
| Evolution entry | Explicit evolution request or later harness decision. |
| Self-evolution | Same evolution machinery after explicit activation and attribution. |
| Observability | Host routing is easy to prove; automatic non-activation versus missed activation is hard to distinguish. |
| Simple-task cost | Lowest of the three options: pointer plus direct work. |
| Complex-task cost | Low when direct execution is sufficient; potentially poor when a useful local capability is never discovered. |
| User experience | Calm, but the user may need to know when NULNUL should be invoked. |

**Assessment:** Option A solves much of the simple-task cost problem but does
not naturally repair Experiments 3A or 4C. It weakens the 3.0 promise that the
user need not manage the ecosystem. It can be a safe fallback, not the target.

## ARCHITECTURE OPTION B — BOUNDED LANE ARCHITECTURE

| Required concern | Option B |
| --- | --- |
| Host entry | Tiny read-only micro-router with Direct, Project-Fit, and Governed outputs. No state validation or roster enumeration. |
| Cheap task classification | Model classifies from the request and minimum target context before lane-only reads. Uncertain material capability value selects Project-Fit; uncertainty never grants structural authority. |
| Harness activation | Project-Fit loads the thin NULNUL core; Governed loads one named stage contract; Direct loads neither. |
| Capability activation | Bounded lifecycle from AVAILABLE through LOADED before work, then USED and ATTRIBUTED after verification. |
| Product execution | One Codex/Claude Product Executor owns implementation and final synthesis. |
| Verification | Real project checks plus strict scope/protected-state diff; receipt machinery only for an authorized continuity event. |
| State authority | Each governed stage has one writer and fixed allowed writes; activation alone grants none. |
| Evolution entry | Evolution Controller opens one bounded episode before WHERE/WHY/candidate work. |
| Self-evolution | Same evolution episode with a frozen harness target and pre-candidate NULNUL attribution. |
| Observability | Ordered lane, contract load, capability load, product action, check, and state-diff evidence; persist only evidence needed for learning. |
| Simple-task cost | Micro-router, target context, direct execution, smallest real check; no harness state or capability reads. |
| Complex-task cost | Pays bounded discovery and selected-capability context; avoids unrelated setup, continuity, and evolution context. |
| User experience | User asks only for the result; routing and ecosystem selection remain internal and inspectable. |

**Assessment:** Option B explains both under-activation and over-activation with
one boundary. Its highest-risk assumption is **UNPROVEN**: that the earliest
host surface can make a sufficiently accurate cheap class decision and keep
unselected contract bodies out of context on the tested hosts.

## ARCHITECTURE OPTION C — ALWAYS-ACTIVE ISOLATED HARNESS

| Required concern | Option C |
| --- | --- |
| Host entry | Always loads a minimal NULNUL kernel. |
| Cheap task classification | The active kernel selects a Direct, Capability, or Governed sub-lane. |
| Harness activation | Every request is HARNESS ACTIVE by definition. |
| Capability activation | Selected bodies still require pre-work load proof. |
| Product execution | One executor under the always-active kernel. |
| Verification | Real checks and lane-specific state guards. |
| State authority | Sub-lanes isolate writes even though the harness is active. |
| Evolution entry | Explicit episode transition inside the kernel. |
| Self-evolution | Same evolution transaction with harness target. |
| Observability | Uniform lane event is easy to collect. |
| Simple-task cost | Kernel plus classification on every task; lower than today's full harness only if the kernel stays genuinely tiny. |
| Complex-task cost | Predictable, but the kernel remains additive context and can become a new accumulation point. |
| User experience | Simple outside; internal behavior is uniform. |

**Assessment:** Option C could make activation evidence cleaner. It conflicts
with the measured direction of 5A and 5B: the product has already shown a
tendency for a “minimal” always-active surface to accumulate state and routing
responsibilities. It also changes the identity from always available to always
governing.

## HISTORICAL FAILURE COUNTERFACTUAL

These are architecture counterfactuals, not proof that an unbuilt option would
have passed.

| Historical evidence | Option A: pointer only | Option B: bounded lanes | Option C: always-active isolated |
| --- | --- | --- | --- |
| Case 22 stale same-scope checkpoint | Likely avoids state if direct, but explicit resume behavior becomes less automatic | Direct lane cannot invoke continuity; explicit Continuity lane may reject or refresh by scope | Can avoid mutation only if kernel perfectly isolates continuity |
| Case 25 unrelated task | Likely avoids state | Naturally prevents it: Direct/Project-Fit have zero checkpoint/root authority | Preventable, but always-active context still exposes continuity |
| Case 28/29 duplicate Skill cleanup | Does not improve lifecycle activation | Governed cleanup/lifecycle action requires selected diff and strict verification | Lifecycle lane could help, but still needs executable action binding |
| Experiment 2 ACTIVATED_NO_SURVIVOR_ACTION | Unchanged after explicit activation | Decision is incomplete without action proof; naturally rejected before completion | Same guard can work, with more routine context |
| Experiment 3A Skill not observed | Likely repeats | LOADED is a required pre-work transition and evaluation precondition | Can prevent if capability-load event is enforced |
| Experiment 4C NO_LIVE_ACTIVATION | Likely repeats on implicit relevant work | Micro-router chooses Project-Fit and load proof precedes work | Prevents harness non-activation; selected Skill load still needs proof |
| Experiment 5A high cost/no advantage | Lowest cost but may lose relevant Skill | Loads only core and selected capability; removes setup/continuity context | May reduce current cost but retains an always-on tax |
| Experiment 5B target success | May lose the successful automatic path | Preserves the successful Project-Fit lane and its no-setup write boundary | Preserves it if isolation works |
| Experiment 5B simple failure | Likely avoids harness/state work | Direct lane explains and prevents continuity work; strict task scope remains independently checked | Depends on kernel isolation and still pays kernel cost |
| Experiment 6C attribution failure | Self-evolution unlikely to start automatically | Candidate generation is forbidden until episode entry and NULNUL attribution | Can establish harness activation, but causal self-attribution still needs ordered evidence |
| Experiment 6C archive write | Explicit invocation may still mis-authorize archive | Only terminal Evolution stage owns compactor; rejected read grants no write | Preventable with the same stage guard |

Option B does not guarantee semantic success on Cases 28/29. It converts the
requested lifecycle decision into a checkable action boundary, which is the
missing prerequisite. The quality of the model's merge/retire choice remains
**UNPROVEN**.

## OPTION EVALUATION

Ratings are architecture judgments grounded in the cited evidence, not measured
scores for unbuilt systems.

| Criterion | Option A: pointer only | Option B: bounded lanes | Option C: always-active isolated |
| --- | --- | --- | --- |
| Verified outcome potential | Medium: strong direct baseline, missed capability risk | **High hypothesis:** preserves direct and measured 5B capability path | Medium-high, but context interference risk |
| Project-fit capability use | Low-medium | **High hypothesis** | High if kernel stays effective |
| Skill / Agent evolution readiness | Low: activation/attribution gaps persist | **High hypothesis:** activation-to-attribution chain is explicit | Medium-high |
| Harness self-evolution readiness | Low | **High hypothesis:** normal evolution target, separate authority | Medium-high |
| Beginner burden | Medium: explicit invocation may leak to user | **Low burden** | Low burden |
| No AI FOMO | Strong against overuse, weak against missed value | **Strong:** capability count never drives lane choice | Medium: NULNUL is present everywhere |
| Continuity safety | Medium: less accidental state, weaker automatic resume | **High hypothesis:** explicit Continuity authority | Medium-high if isolation is perfect |
| Observability | Low-medium | **High** by design | High |
| Simple-task latency/context | **Best** | **Near-best target** | Worse fixed tax |
| Complex-task efficiency | Variable; may miss reusable value | **Best balance hypothesis** | Predictable but additive kernel cost |
| Implementation complexity | Lowest | **Moderate, bounded** | Moderate-high because kernel must stay isolated across all responsibilities |
| Migration risk | Low | **Moderate** | High: redefines every request as harness governed |
| Host compatibility | High | **High hypothesis:** uses guaranteed root surface and skills-only loading | Medium-high; every host must support uniform always-active semantics |

## RECOMMENDED ARCHITECTURE

Choose **Option B — Bounded Lane Architecture**:

> A host-loaded read-only micro-router selects Direct, Project-Fit, or one
> Governed stage before state or capability context is loaded. The selected
> lane owns its reads; only a named governed stage owns durable harness writes.
> Product execution and real verification remain the center. Evolution reuses
> attributed task experience rather than governing every task.

This is an **ARCHITECTURAL HYPOTHESIS**, not an already superior product.

### WHY THIS ONE

1. It preserves 5B's strongest positive result: automatic pre-work loading of
   the relevant Skill with no setup writes on capability tasks.
2. It addresses 5B's simple failure and 5A's cost by keeping setup,
   continuity, evolution, and roster context out of Direct work.
3. It explains Cases 22/25 and the 6C archive write as authority violations,
   not as missing task-specific prohibitions.
4. It gives 3A/4C a general activation contract: selected capability bodies
   must load before governed work.
5. It gives Experiment 2 a general action contract: a lifecycle decision is
   incomplete without its required diff and check.
6. It turns self-evolution into a target of the normal governed evolution
   transaction rather than a second harness.
7. It uses the already proven guaranteed host surface without making that
   surface a full harness.

### WHY NOT THE OTHERS

Option A is cheaper but makes the user or the base model responsible for
knowing when NULNUL should engage. That is the 4C failure shape and conflicts
with invisible project-fit ecosystem management.

Option C gives the cleanest nominal activation, but the 5A/5B evidence shows
that always-active context is not free and can import state work into simple
tasks. It makes “NULNUL loaded” universal while doing less to distinguish
whether NULNUL materially helped.

### HISTORICAL FAILURES ADDRESSED

- **Cases 22/25:** state validation and refresh move behind Continuity entry.
- **Cases 28/29 and Experiment 2:** lifecycle decisions require observable
  survivor action and strict verification.
- **Experiment 3A and 4C:** pre-work capability load becomes a transition
  prerequisite.
- **Experiment 5A:** irrelevant setup/state context leaves the capability
  path.
- **Experiment 5B target:** the bounded successful capability lane is
  preserved.
- **Experiment 5B simple:** Direct has no state or capability authority.
- **Experiment 6C attribution:** self-evolution cannot begin from reachability;
  it needs ordered harness attribution.
- **Experiment 6C archive:** rejected-history read and compaction authority are
  separate.

### PROBLEMS THAT REMAIN UNSOLVED

1. **UNPROVEN:** the micro-router can classify a representative mixed workload
   with low enough cost and without missing useful capabilities.
2. **UNPROVEN:** physical context isolation plus skills-only deterministic
   writers is sufficient to hold write authority on live hosts.
3. **UNPROVEN:** loaded capabilities can be causally attributed reliably enough
   for live Skill or Agent evolution.
4. **UNPROVEN:** NULNUL can perform a correct MERGE/RETIRE survivor action after
   the execution boundary exists.
5. **KNOWN LIMITATION until migration proves otherwise:** the current resume
   fallthrough remains closed at LOCUS_D.
6. **UNPROVEN:** the target cost guardrails generalize beyond the measured
   fixtures.
7. Harness self-evolution, Generalization, and personal/core transfer remain
   unactivated or outside this review.

## PROJECT-FIT EVOLUTION ALIGNMENT

Option B prevents NULNUL from becoming only a routing engine because lane
selection is neither the success metric nor a durable learning event.

The product chain is:

    low-cost correct lane
      -> selected capability loaded before its job
      -> real product work and verification
      -> causal activation/use/outcome evidence
      -> governed lifecycle or evolution entry when warranted
      -> frozen competition and independent Gate
      -> project-fit survivor ecosystem

Direct execution is a first-class successful outcome. KEEP is also a
first-class evolution decision. Neither a route nor a newly generated
capability receives credit without downstream verified value.

## SIMPLE-TASK PERFORMANCE MODEL

The target simple-task budget contains only:

1. automatic loading of the tiny host micro-router;
2. enough target context to classify the request;
3. direct product work; and
4. the smallest falsifying repository check.

It excludes:

- primary NULNUL SKILL.md;
- project.md and live-state discovery;
- checkpoint validation or receipt refresh;
- evolution state/archive/history;
- installed and local capability roster enumeration;
- Skill/Agent bodies; and
- any setup, host-entry, or learning write.

If the target context reveals material uncertainty—for example an unfamiliar
domain with a known local job—the request may transition to Project-Fit. That
transition is observable and incurs the additional cost deliberately.

## MINIMUM MIGRATION SURFACE

No migration is implemented by this review.

| Change area | Decision | Minimum likely change |
| --- | --- | --- |
| Host entry | **SIMPLIFY / MOVE** | Replace eager state validation with the three-output read-only micro-router; retain host ownership, managed markers, and inactive-host preservation. |
| Core orchestration | **SIMPLIFY** | Keep SKILL.md as the thin Project-Fit kernel; stop treating all setup/evolution references as ordinary execution context. |
| Task classification | **ADD SMALL MECHANISM** | One explicit pre-read lane decision with a stable vocabulary and observable ordering; no scoring framework or model zoo. |
| Capability activation | **ADD SMALL MECHANISM** | Require selected identity/body load before governed work and record enough ordered evidence for attribution. |
| Product execution | **KEEP** | One executor owns implementation and final synthesis. |
| Verification | **KEEP / NARROW** | Real project checks remain; add lane-specific protected-state diff. |
| Project setup | **MOVE** | Put adoption/new setup/repair under the Governed Structural stage only. |
| Checkpoint and receipt | **KEEP / NARROW AUTHORITY** | Move validation/refresh behind explicit Continuity entry; retain exact command, fingerprint, and sole receipt writer. |
| Evolution entry | **ADD SMALL MECHANISM** | Canonical episode envelope before WHERE/WHY/candidate writes; reuse current state and validators. |
| Self-evolution | **MERGE** | Represent it as target_kind=harness inside the same evolution mechanism; no parallel state system. |
| Archive | **KEEP / NARROW AUTHORITY** | Sole compactor remains; only an authorized terminal episode may invoke it. |
| Personal adaptation/generalization | **MOVE** | Lazy governed references only; no implementation or new claim. |
| Observability | **ADD SMALL MECHANISM** | Ordered lane/load/action/check evidence and protected-state diff; do not create an always-on durable transcript. |
| Deterministic guards | **REUSE / EXTEND MINIMALLY** | Reuse existing writers and validators; add lane/episode preconditions only where the next experiment proves necessary. |
| New MCP server, hook, app, service, router daemon, or mandatory Agent | **DO NOT ADD** | Reconsider only if the bounded skills-only experiment demonstrates that the required boundary cannot hold. |

## VERSION RECOMMENDATION

**v2.3 ARCHITECTURE REWORK REQUIRED**

The evidence does not support releasing v2.3 with another routing wording
candidate. The architectural milestone—cheap lane selection, pre-work
capability activation, and stage-scoped authority—must precede a v2.3 release
claim. This is not a version bump and does not begin release work.

## NEXT SINGLE EXPERIMENT

### Name

**Experiment 7 — Bounded Lane Boundary**

### Highest-risk assumption

A tiny guaranteed host-loaded surface can select and physically isolate the
Direct, Project-Fit, and Governed contexts cheaply enough to preserve simple
work while still activating the right local capability before relevant work.

### Hypothesis

Against the exact frozen v2.2.1 Champion, a candidate that changes the load
topology—not merely the wording—will:

- keep simple tasks in Direct with no NULNUL core, capability, or durable-state
  reads/writes;
- put capability-relevant tasks in Project-Fit with NULNUL and the exact
  selected capability loaded before the first governed action;
- put explicit setup/continuity/evolution tasks in one Governed stage with only
  that stage's allowed writes; and
- improve mixed-workload strict verified outcomes or preserve them at
  materially lower verified-result cost.

### Champion

Exact frozen NULNUL v2.2.1 identified in CURRENT PRODUCT STATUS. No champion
bytes may change.

### Candidate concept

Instantiate one context boundary:

1. The generated managed host block contains only a three-lane micro-router; it
   no longer points ordinary execution at checkpoint/evolution validation.
2. Direct has no downstream harness entry.
3. Project-Fit loads a thin existing NULNUL core, then the exact selected
   capability body before work.
4. Governed loads exactly one existing setup, continuity, or evolution entry.
5. The experiment records ordered reads and a lane-specific protected-state
   diff. A lane fails if an unselected contract body or unauthorized durable
   state enters the run.

This is a physical change to the context/load graph and measured write
boundary. It is not another sentence telling the model to avoid setup.

No new state schema, MCP server, hook, app, service, mandatory Agent, evolution
candidate, or routing score is part of this experiment.

### Likely files

- plugins/nulnul-harness/skills/nulnul-harness/scripts/sync_host_entry.py
- plugins/nulnul-harness/skills/nulnul-harness/SKILL.md
- the minimum existing lane references needed to remove eager cross-links
- existing product tests and one bounded experiment protocol/fixture set

The candidate should not touch checkpoint, archive, Gate, personal, or
generalization schemas unless the experiment cannot be instantiated without
doing so; that condition is a scope failure, not permission to expand.

### Development evidence

Use already exposed families only:

- one 4C-style ordinary capability-relevant task;
- the 5B capability-relevant API tasks;
- the 5B simple no-Skill task;
- Cases 22, 25, and the positive-control Case 31;
- one New Setup or explicit host repair control; and
- a 6C-shaped evolution-entry preflight without candidate generation.

Development verifies the lane mechanism. It does not claim generalization or
self-evolution.

### Validation

After candidate freeze, run counterbalanced Champion/candidate pairs on a
preregistered mixed validation set containing Direct, Project-Fit, Continuity,
Structural, and evolution-entry cases. Validate:

- strict task completion and real repository checks;
- lane decision before lane-only reads;
- exact capability body load before governed work;
- exact permitted state writes and zero protected-state extras;
- completion, runtime, input, and repository reads;
- no harness-specific user questions; and
- deterministic negative controls for every new lane/write check.

### Sealed holdout

Before candidate freeze, preregister one fresh unseen case from each top-level
lane:

1. a simple no-capability product task;
2. a capability-relevant task with one useful and one irrelevant local
   capability; and
3. an explicit structural or evolution-entry task with a narrow allowed write
   set.

Use the holdout once, retire every case after exposure, and forbid candidate
tuning from its contents or results.

### Primary verified-outcome metric

Paired strict verified-result count across the mixed workload. Completion is a
required supporting control; routing/activation alone earns no point.

Report total input and runtime per strict verified result as the efficiency
tie-breaker, never as permission to trade away a strict outcome.

### Activation metric

- Direct: root micro-router observed 100%; NULNUL core, local capability body,
  and governed state contract observed 0%.
- Project-Fit: NULNUL core and exact selected capability body observed before
  first governed work 100%; irrelevant capability body 0%.
- Governed: exact selected stage contract observed before its transition 100%;
  unselected governed contracts 0%.

Any missing ordered proof is UNKNOWN, not a pass.

### State-authority metric

- Unauthorized durable harness writes: 0.
- Required authorized setup/continuity writes: 100% exact.
- Direct and Project-Fit protected state diff: empty.
- Evolution-entry preflight: no candidate or archive bytes.

### Simple-task context / latency guardrail

For every paired Direct case:

- input no more than 115% of Champion;
- runtime no more than 115% of Champion;
- repository reads no more than Champion plus one root-entry read;
- no NULNUL core, capability body, project state, checkpoint, receipt,
  evolution, or archive read; and
- no durable harness write.

Both cost ratios and exact reads are reported; a mean may not hide a violating
case.

### Complex-task outcome guardrail

- no Champion strict or completion pass may regress;
- every Project-Fit case must complete and pass its real strict check;
- candidate raw input per Project-Fit task must not exceed 135% of Champion;
  and
- total input per strict Project-Fit result must not exceed 110% of Champion.

The per-result guard allows bounded capability cost only when it buys verified
outcomes.

### User-burden guardrail

Zero harness, lane, Skill, Agent, checkpoint, or evolution questions on cases
whose answer is discoverable from the repository. Users issue ordinary outcome
requests only.

### Kill condition

Stop and reject the candidate on the first of:

- any Direct run loads NULNUL core, a capability body, or durable harness
  state;
- any Project-Fit run begins governed work before the exact selected capability
  load;
- any unauthorized state, host-entry, test, candidate, or archive write;
- a required structural/continuity write is absent;
- any Champion strict/completion pass regresses;
- any simple or complex cost guardrail fails;
- a lane/write check lacks a passing negative control;
- a new state system, service, hook, mandatory Agent, or parallel evolution
  mechanism becomes necessary; or
- holdout exposure/leakage occurs.

### Promotion condition

Only an independent Gate may mark the candidate provisional, and only if:

- all development, validation, and sealed-holdout strict checks pass;
- the activation and state-authority metrics are exact;
- there is at least one paired strict verified-outcome gain on the exposed
  failure families with no paired regression;
- both cost guardrails and user-burden guardrail pass;
- candidate identity, write set, evidence, and holdout retirement are frozen;
  and
- one observed live cycle later confirms the same boundaries.

Success does not promote v2.3, Skill Evolution, Agent Evolution,
Generalization, or self-evolution. It promotes only the bounded lane mechanism
for the next architectural step.

### Rollback

Keep the Champion active, generate the candidate in isolation, and restore all
fixture/project files after every arm. On kill, invalid evidence, no advantage,
or live-cycle failure, discard the candidate and its provisional state; retain
only sanitized rejected evidence through the existing authorized process.

### Roadmap check

**Yes.** If the experiment succeeds, it materially advances Project-Fit
Evolution:

    correct low-cost activation
      -> reliable capability use
      -> causal experience attribution
      -> later Skill / Agent / Harness evolution
      -> verified competition
      -> project-fit survivor ecosystem

If it produces only cleaner route labels without this ordered activation and
authority evidence, it fails.

## PRODUCT CHANGES

**0**

## RELEASE

**v2.3 NOT READY**

## NEXT

**STOP — do not implement architecture changes.**
