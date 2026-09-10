# NULNUL v2.3 foundation contract

Load this reference only for explicit NULNUL setup, adoption, continuity, recovery, inspection, or later evolution-input work. Ordinary no-fit product work uses an empty pre-session Capability Pack and does not load this file.

## Canonical architecture

```text
USER TASK
    ↓
SESSION / TASK
    ↓
CONTEXT ASSEMBLY
    ↓
AGENT TOPOLOGY SELECTION
(SINGLE_AGENT unless evidence justifies more)
    ↓
CAPABILITY SELECTION
    ↓
PRE-SESSION CAPABILITY PACK PER AGENT
    ↓
WORK SESSION
    ↓
VERIFICATION + OBSERVABILITY
    ↓
EXPERIENCE
    ↓
DURABLE MEMORY
    ↓
EVOLUTION INPUT
    ↓ (only on a material evidence/maintenance trigger)
┌───────────────────────────────┬───────────────────────────────┬───────────────────────────────┐
│ CAPABILITY NATURAL SELECTION  │ AGENT EVOLUTION               │ HARNESS CONTROL EVOLUTION     │
│ KEEP / UPGRADE / REPLACE      │ KEEP / UPGRADE / SPLIT        │ KEEP / TUNE / REPLACE         │
│ MERGE / RETIRE / CREATE       │ MERGE / REPLACE / RETIRE      │ RETIRE / CREATE               │
│                               │ CREATE                        │ guarded Kernel outside loop   │
└───────────────────────────────┴───────────────────────────────┴───────────────────────────────┘
    ↓
CHAMPION / ONE FROZEN CHALLENGER
    ↓
VERIFIED COMPETITION + TRANSACTION
    ↓
UPDATED CAPABILITY ECOSYSTEM / AGENT TOPOLOGY
    ↓
NEXT TASK
```

Capability-only need may continue through:

```text
CAPABILITY NATURAL SELECTION
├─ KEEP
├─ UPGRADE
├─ REPLACE
├─ MERGE
├─ RETIRE
└─ CREATE
    ↓
CAPABILITY NEED (UPGRADE / REPLACE / CREATE only)
    ↓
LOCAL / EXTERNAL DISCOVERY
    ↓
QUARANTINE → COMPETITION → SURVIVOR
    ↓
LIFECYCLE TRANSACTION
    ↓
UPDATED CAPABILITY ECOSYSTEM
    ↓
NEXT TASK
```

Cross-project learning remains outside project Memory and activates only on a
reusable-pattern or target lifecycle trigger:

```text
PROJECT EXPERIENCE
    ↓
PRIVACY-SAFE GENERALIZATION CANDIDATE
    ↓
INDEPENDENT PROJECT OR TARGET VALIDATION
    ↓
TRANSFERABLE PRIOR
    ↓
TARGET EXPERIENCE / CHECK
    ↓
EXISTING CAPABILITY / AGENT / HARNESS LIFECYCLE
```

Across every layer: IDENTITY / PROVENANCE. Agent topology chooses responsibility structure; Capability Packs still choose reusable guidance for each Agent scope. Governed authority remains separate.

The complete machine-inspectable layer registry is `../assets/layer-contracts.json`. Validate it with `../scripts/foundation_runtime.py validate-layers`. It is one registry of ownership boundaries, not twelve frameworks.

## Layer map and ownership

| Layer | Owns | Does not own |
| --- | --- | --- |
| Project Model | Stable current project truth in `docs/nulnul/project.md` | Session history, raw evidence, evolution decisions |
| Session / Task Lifecycle | Host session, concrete and Agent-scoped task status, bounded handoff | Project truth, capability selection, full chat |
| Context Assembly | A bounded relevant Context Pack | Memory mutation, full history, semantic routing |
| Capability Ecosystem | Accepted metadata, exact identities, lifecycle status, and bounded Pack candidates | Capability bodies during selection, execution, host trust |
| Activation / Authority | Current Agent topology selection, immutable per-Agent pre-work Capability Pack context, and separate named-stage write authority | Capability mutation, host trust, runtime privilege, arbitrary writes |
| Verification | Actual configured checks and receipts | Model-authored success claims, memory promotion |
| Runtime Observability | Genuinely observable ordered events and completeness | Fabricated events, durable project memory |
| Experience Layer | Meaningful verified or partial work outcomes with optional Agent/Topology attribution | Raw chat, automatic Skill or topology changes, unsupported attribution |
| Durable Memory | Active Decisions, Lessons, Open Threads, and bounded records | Checkpoint position, project history prose, raw transcripts |
| Provenance / Lineage | Identity, derivation, source, and supersession validity | Ranking, promotion judgment, deletion |
| Memory Lifecycle | Active, superseded, retired, and compacted state | Destructive retention, capability evolution |
| Evolution Input | Bounded verified Capability, Agent, or Harness-control Experience queries | Raw sessions, mutation, promotion decisions |

## Stable project model and accepted capabilities

`docs/nulnul/project.md` remains the stable current project model. It is not an event log or session history.

The `Accepted capabilities` table is the one acceptance contract for New Setup, Adopt/Upgrade, the bounded opportunity, Project-Fit activation, Memory references, and later Evolution. Its exact fields are:

- Capability ID
- Job
- Activate when
- Project check
- Status
- Version or digest
- Logical load target

Only `accepted/current` rows enter the bounded runtime view. Capability identity owns its host-independent logical target: `capability_contract.py` deterministically maps ID `X` to `capabilities/X/SKILL.md`. This is a durable logical address, not an ordinary readable filesystem path. `.agents/skills/X/SKILL.md` is a host materialization/source path and is invalid in the logical-target field.

New Setup and Adopt schema-v2 plans supply accepted IDs plus the project-specific job, trigger, check identity, and version/digest facts that have no global project-independent registry. The transaction derives `accepted/current` status and the canonical target; the model cannot choose either. A schema-v1 plan may be adopted only when its asserted target already matches exactly—alternate or legacy paths fail before any transaction-owned write. An existing project with a stale target continues to permit ordinary Direct work but positive activation remains unavailable until explicit Governed Adopt rewrites the canonical contract.

`../scripts/setup_transaction.py` renders accepted rows through the same `capability_contract.py` interpretation consumed by the bounded view, Pack construction, Memory references, and Evolution Input. Before success it resolves every accepted ID again through that shared surface and requires the exact same immutable row. A setup that runtime cannot use therefore rolls back and cannot report success.

Legacy projects without the table continue to run directly. A legacy routing table that claims project capabilities must migrate to the canonical table before positive activation; its absence is not silently interpreted as acceptance.

## Governed setup and host ownership

Host trust and security approvals always belong to the user and host. NULNUL never writes Codex `trust_level`. Project-Fit Pack construction requires no Codex rule, restart, sandbox escape, or privileged command admission.

Governed stages reuse a valid project-local contract when present. Otherwise, a host-admitted plugin uses only the contract beside its executing guard and transaction scripts, with the matching host manifest. No arbitrary skill-directory argument, shadow skill, host registration, or protected-path copy is needed. The executing-plugin receipt binds the project root, host, stage, unchanged write authority, and the contract, manifest, and two execution-script digests; setup recomputes it and rejects stale, cross-project, or wrong-host receipts before writing. Unsafe paths or malformed explicit local contracts still fail closed. This establishes executing-package identity, not independent publisher provenance: the host and discovery process must verify the installed source before executing it. It neither expands authority nor changes the Direct or verified-resume path.

During a positively activated `new-setup` or `adopt-upgrade` stage, one deterministic Setup transaction:

1. accepts only mode, host, project goal/milestone/check, constraints, inspected roster, topology, accepted capability IDs, and project-specific semantic capability facts from the model;
2. writes the project contract, active host entry, checkpoint, and verification receipt through their existing writers;
3. validates the same accepted-capability view used by runtime plus the active host and checkpoint;
4. commits all valid transaction-owned surfaces or restores every original byte;
5. does not mutate host trust, install a capability-activation rule, or require a capability-only restart.

The Setup Plan is transaction input, not project truth. Create it under the ignored local runtime directory or an external temporary directory, pass it once, and remove it after the transaction result is captured. Its schema is `assets/setup-plan.template.json`; do not add artifact bodies, raw transcripts, credentials, or duplicate durable Memory to it.

The retired runtime-exclusive design's exact legacy `.codex/rules/nulnul-activation.rules` can be removed only by explicit Adopt/teardown cleanup. Cleanup removes only its frozen digest, never a foreign rule, and never changes trust.

## Pre-session Capability Pack

`../scripts/capability_pack.py` implements the active Project-Fit boundary as a pre-work phase inside the same automatic NULNUL Session and Task:

```text
TASK < SELECTION < PACK CREATED < BODY INCLUDED < WORK SESSION < CHECK < EXPERIENCE
```

Selection is hybrid. Deterministic metadata retrieval creates an empty Pack for a clear zero match and a single-capability Pack for one strong unique match. Only adjacent or ambiguous bounded candidates require the current model to return exact listed IDs or `NO_CAPABILITY`; selection never sees bodies or performs product work. The candidate set is capped at three.

A Pack is immutable local execution state under ignored `.runtime/`, not project truth or Memory. It binds `PACK_ID`, `TASK_ID`, project revision, exact capability refs/digests, selection evidence, relevant Memory refs, creation time, status, and its own digest. The Foundation host constructs and binds it before the main work model starts. Clear zero and unique strong matches require no work-model Pack calls; only an ambiguous metadata set may use a bounded selector before automatic construction. The work context contains only selected bodies and relevant bounded Memory. Unselected bodies do not enter it. Pack construction grants no filesystem, host, or Governed authority.

For a single selected capability, `capability_pack.py finalize` derives the exact check from the immutable Pack and canonical project contract, executes it after observable work, writes the Check receipt, and only then finalizes the `CAPABILITY_EXPERIENCE`. A verified check failure remains eligible learning evidence. This attribution proves intentional selection and body presence before work, not sole causal responsibility for the outcome. A multi-capability Pack receives Pack-level attribution only until independent per-capability work/check evidence exists.

## Direct path

The Codex-owned root block exposes no Pack lifecycle command to the work model. The Foundation host creates an internal empty Pack for provenance before a clear no-match Direct session starts; its schema and receipt are not model context. Direct continues without loading the NULNUL Skill, this reference, setup/adopt instructions, governed stage contracts, capability bodies, checkpoint/evolution state, raw evidence, or unrelated Memory.

Memory is always available, not always loaded. A Direct task may request one bounded Context Pack only when durable knowledge is concretely relevant; it never reads raw transcripts or full history.

The host passes only the `model_context` envelope returned by Task start: Session ID, Task ID, and selected Context items. It does not repeat the user goal, full Task record, empty Context Pack schema, budgets, setup lifecycle, or Foundation implementation details in model context.

## Session and task lifecycle

At first NULNUL-aware work in a host session, run:

```bash
python3 scripts/foundation_runtime.py --root . session-start \
  --goal "<current user goal>" --host codex --host-version "<observed>" \
  --model "<observed>" --nulnul-revision "<observed>" \
  --project-revision "<observed>" --host-trust "<observed>" \
  --admission-state "<observed>"
python3 scripts/foundation_runtime.py --root . task-start --goal "<concrete task>" --job "<job>"
```

The runtime creates `SESSION_ID` and `TASK_ID`; never ask the user to manage them. Valid Session states are `STARTED`, `ACTIVE`, `COMPLETED`, `PARTIAL`, `BLOCKED`, `ABORTED`, and `RECOVERED`. A leftover local active record is finalized as `PARTIAL`; the next Session records `recovered_from`, stores one non-evolution-eligible `RECOVERY_EXPERIENCE`, and preserves only evidence that exists.

At an observable task outcome, call `task-finish` with one bounded structured outcome. At an observable session boundary, call `session-finalize`. A host without a termination hook cannot guarantee graceful finalization; the next start performs deterministic recovery instead of pretending completion.

One local project-wide lock detects concurrent writers and fails safely. The current foundation intentionally does not support concurrent NULNUL state writers.

## Runtime observability

Supported event classes include `SESSION_STARTED`, `TASK_STARTED`, `CONTEXT_ASSEMBLED`, bounded capability opportunity/selection, Pack creation, selected-body inclusion, work-session start, governed activation, tool execution, observable file read/write, check start/completion, Experience attribution, task completion/failure, and session finalization.

Record only events the host genuinely exposes. Each Session and Experience declares `COMPLETE`, `PARTIAL`, or `MINIMAL` evidence; Capability evolution eligibility requires `COMPLETE` causal observability. Raw JSONL/tool transcripts remain local under `docs/nulnul/.runtime/`, which the runtime adds to `docs/nulnul/.gitignore`. They may contain sensitive content and are never copied into project.md, Session records, Experiences, Memory, Context Packs, or Evolution Input. The local `raw-retention` command records either keep-until-user-removal (default) or a bounded expiry policy; this foundation does not destructively delete retained evidence by default.

## Experience

The small initial taxonomy is:

- `TASK_EXPERIENCE`
- `CAPABILITY_EXPERIENCE`
- `GOVERNED_EXPERIENCE`
- `RECOVERY_EXPERIENCE`

Quality is `VERIFIED`, `PARTIAL`, `UNATTRIBUTED`, or `INVALID`; there is no numeric confidence.

A generic Experience records the Session, Task, job, revisions, changes, checks, product outcome, result, host fingerprint, and source references. A single-capability Experience is evolution-eligible only when an accepted/current exact ref, `PACK_ID` and digest, positive selection evidence, body active before the work session, body digest, product outcome, linked capability-relevant `CHECK_ID`, check result, and success/failure are all valid and ordered. A deterministically checked failure may be `VERIFIED` and eligible; a success claim cannot disagree with its check receipt. Missing evidence remains inspectable with `EVOLUTION_ELIGIBLE = false`. A multi-capability Pack does not automatically assign the same result to each member.

## Durable memory

The lazily initialized layout is:

```text
docs/nulnul/
├─ project.md
├─ checkpoint.json or evolution.json
├─ .gitignore                 # excludes local runtime evidence
├─ .runtime/                  # LOCAL-ONLY, sensitive, regenerable
└─ memory/
   ├─ sessions/
   ├─ experiences/
   ├─ decisions.jsonl
   ├─ lessons.jsonl
   ├─ open-threads.json
   ├─ handoff.json
   └─ index.json
```

Finalized bounded Sessions, Experiences, Decisions, Lessons, Open Threads, handoff, and index are project-durable according to the project's policy. The active session, lock, ordered runtime events, and raw transcripts are local-only. The index is regenerable from durable records.

The data flow is one-way:

```text
RAW EVIDENCE → SESSION RECORD → EXPERIENCE → DURABLE MEMORY
```

Session says what happened. Experience says what outcome can be learned from. Memory says what should influence later work. Checkpoint still says where work is now.

Verified task outcomes automatically consider explicitly structured Decision, Lesson, and Open Thread candidates. Partial or unverified outcomes do not promote them. This is bounded deterministic promotion, not autonomous rewriting of project guidance or capabilities.

A Setup transaction returns a ready-to-store `GOVERNED_EXPERIENCE` outcome with its transaction ID, stage, host, authorized write set, validation and rollback result. Pack-only setup reports no capability restart requirement. Success and exact rolled-back failure remain inspectable, but neither is Capability Evolution input without an independent Pack and check chain.

## Context Assembly

Preview a Context Pack with:

```bash
python3 scripts/foundation_runtime.py --root . context --task "<task>" \
  [--capability ID] [--module PATH]
```

The runtime deterministically enforces at most 8 items and 4096 serialized bytes, active status, deduplication, provenance, and raw-transcript exclusion. It uses bounded local metadata: task/job terms, exact capability, module paths, tags, recency, active status, and Open Thread linkage. The model may rank the already bounded set; no vector database, embedding service, external RAG, or search daemon exists.

Every item states why it was included, such as `active decision`, `active lesson`, `same capability`, `same module`, `open thread`, or `relevant verified experience`.

## Provenance and lifecycle

Canonical identities are `SESSION_ID`, `TASK_ID`, `PACK_ID`, `EXPERIENCE_ID`, `DECISION_ID`, `LESSON_ID`, `CAPABILITY_ID`, `CHECK_ID`, and later `EVOLUTION_ID`. Records consistently use `derived_from`, `source_refs`, `supersedes`, `superseded_by`, `created_at`, `project_revision`, `host_fingerprint`, and `nulnul_revision` where applicable.

`validate-lineage` rejects dangling required references, malformed source references, unknown capability attribution, invalid causal eligibility, self-supersession, broken reciprocal links, and supersession cycles.

Memory status is `ACTIVE`, `SUPERSEDED`, `RETIRED`, or `COMPACTED`. Context Assembly reads only active Decisions, Lessons, Open Threads, and verified Experiences. Exact duplicate Lessons compact into one active Lesson with combined source lineage; older records remain non-active for provenance. Closing an Open Thread retires it through the same lifecycle writer. No automatic destructive deletion exists.

## Handoff and recovery

Finalization creates one bounded handoff containing `DONE`, `FAILED`, `OPEN`, `NEXT`, important Decision IDs, relevant Memory IDs, and the current checkpoint. A new Session reads stable project state, detects an incomplete prior Session, reads the handoff, and assembles only relevant Memory. It never replays the whole previous chat.

## Evolution input boundary

Inspect bounded eligible Experiences with:

```bash
python3 scripts/foundation_runtime.py --root . evolution-query \
  [--capability ID] [--job JOB] [--since VERSION_OR_DIGEST] [--limit N]
```

Only active, `VERIFIED`, causally attributable Capability Experiences are returned. The result is bounded to 50 and defaults to 20. A structured `CONTROL_CANDIDATE` may preserve one suggestion plus valid evidence refs from a verified Experience for later consideration, but this foundation does not modify Skills, Agents, Tools, host rules, or harness source from it.

Future evolution consumes these Experience records, never an entire chat or raw session by default.

## Capability Natural Selection

`../scripts/natural_selection.py` is the triggered NULNUL 3.0 layer above the completed Foundation. It does not run an ecosystem review on ordinary tasks. A materially new attributable failure, repeated uncovered work, evidence-backed overlap, project-state change, or explicit maintenance boundary may invoke its read-only `snapshot` and `evaluate` commands. They reuse the canonical capability table, Foundation Experiences, Pack evidence, Checks, and durable Decisions; raw chat and transcripts are not inputs.

The current accepted/current set and exact body digests form the `ECOSYSTEM CHAMPION`. Evaluation can return `KEEP`, one bounded lifecycle candidate, `MORE_EXPERIENCE_REQUIRED`, or `NO_ACTION`, but cannot mutate state. For a justified non-KEEP result, `candidate` derives the canonical record and freezes the proposed body digest before competition without writing product state. Every frozen candidate competes as an isolated `ECOSYSTEM CHALLENGER`; quality and project checks dominate context, maintenance, and capability-count savings. Only that exact candidate plus a passing bounded competition may enter `transact`.

The transaction revalidates the frozen Champion, Experience provenance, candidate identity and body digest, then atomically updates the existing accepted-capability table, project-local Skill materialization, Memory Decision/index, active Session, and Decision event. `accepted/current` remains the only Pack-selectable status. Retired and superseded capabilities remain in the contract and historical evidence but leave ordinary Pack selection. An Upgrade archives the prior body beside the materialized Skill under `versions/<old-digest>/SKILL.md`. Any partial write, stale Champion, broken lineage, or invalid post-mutation Pack resolution restores every transaction-owned file.

Capability refs carry a generic `SKILL`, `AGENT`, `TOOL`, or `VERIFICATION` type, but Capability Natural Selection mutation deliberately remains project-local Skill-only. Agent responsibility topology evolves separately through the Agent Evolution contract below; Tool and Harness Evolution remain closed. Reconsideration is evidence-based rather than timer-based: KEEP waits for materially new Experience; Upgrade/Create wait for post-change Experience; Retire needs contradictory verified evidence plus an explicit reactivation transaction. Natural Selection Decisions use the existing `DECISION_ID`, Memory, Context, and provenance surfaces instead of a parallel history.

## External Capability Competition

`../scripts/external_competition.py` is subordinate to Natural Selection. It accepts only a current, digest-valid `UPGRADE_CANDIDATE`, `REPLACE_CANDIDATE`, or `CREATE_CANDIDATE`; `KEEP`, `NO_ACTION`, and `MORE_EXPERIENCE_REQUIRED` cannot trigger discovery. The first supported adapter is a read-only `LOCAL_DIRECTORY` source with an explicit source ID and revision. It reads one bounded `capability.json`, UTF-8 body, and license evidence without executing candidate instructions, install hooks, or source code. Network catalogs, marketplace APIs, and remote installers are not implemented.

Every discovered body is frozen under ignored `docs/nulnul/.runtime/external-competition/quarantine/` with its source revision, source/body/fetched digests, license classification, declared requirements, and normalized competition manifest. Quarantine has no authority, is never a canonical capability-table row, and cannot enter ordinary Pack selection. The externally disclosed query is limited to the target job, verified weakness summary, required invariant, capability type, project-check identity, bounded safe constraints, and Experience IDs; raw project files, Memory, transcripts, and credentials are excluded.

A competition freezes one ecosystem Champion, at most three Challengers, one project revision, exact task/check/write identities, and one sealed holdout. Every run must come from a disposable workspace under the same conditions. Strict outcome, authoritative project check, completion, state authority, regression count, and preregistered quality dominate carrying cost; context, dependency, tool, permission, setup, and verification cost only break equivalent-quality ties. External candidates remain untrusted until the existing Natural Selection transaction validates the survivor, source/license provenance, canonical capability contract, Pack resolution, lineage, and rollback. A candidate needing adaptation becomes a separately frozen local Challenger and must compete again. Rejected identical bytes remain cooled down until a new source revision or materially new verified Experience.

## Agent topology and Agent Evolution

`../scripts/agent_evolution.py` keeps Agent responsibility separate from Skill guidance. An Agent contract binds one role, job, responsibility set, task/input/output boundaries, Capability and Tool requirements, delegation, verification, authority, handoff, failure escalation, and context requirements. An Agent topology binds those contracts, delegation edges, one synthesis owner, one verification owner, a stable topology ID, and a digest. A legacy project with no machine topology lazily resolves an implicit one-Agent `topology-project-execution`; absence is not corruption and causes no project write.

Topology selection precedes Pack construction. Each Agent gets its own child Task and only the Capability Pack and bounded Memory relevant to that responsibility. An Agent identity grants no structural authority. Delegation edges require parent/child task boundaries, expected output, allowed scope, required check, and return contract; local handoffs contain only `DONE`, `FAILED`, or `OPEN`, artifact refs, Check IDs, and the return contract. Full child transcripts never enter parent context.

Normal Capability or Task Experiences may carry bounded Agent/Topology attribution rather than entering a second Experience store. Eligible Agent evidence binds the current topology and Agent contract digests before work, exact task scope, authoritative Check IDs, observed responsibility, ordered events, and source refs. Multi-Agent work records per-Agent credit only for observed responsibilities and may add one Topology-attributed Experience over its child Experiences; it never assigns the overall result independently to every participant.

The evaluator is trigger-only and returns `KEEP`, one of `UPGRADE_CANDIDATE`, `SPLIT_CANDIDATE`, `MERGE_CANDIDATE`, `REPLACE_CANDIDATE`, `RETIRE_CANDIDATE`, `CREATE_CANDIDATE`, `MORE_EXPERIENCE_REQUIRED`, or `NO_ACTION`. `SINGLE_AGENT` is the Champion unless verified Agent-attributable evidence justifies more structure. One local Challenger freezes contracts, graph, Pack requirements, owners, source Experience IDs, and topology digest. Competition uses at most three frozen task groups including a sealed holdout; strict outcome, authoritative checks, completion, state authority, and regression protection dominate Agent count, calls, context, handoffs, reads, runtime, or maintenance cost. Equivalent quality promotes only with one verified meaningful advantage.

The transaction revalidates Champion, Experiences, Challenger, competition, graph, current Capability refs, Pack bindings, verification owner, and provenance before atomically writing `docs/nulnul/agent-topology.json`, bounded topology history under `memory/agent-topologies/`, and the existing Decision/Session/index/event surfaces. Failure restores every owned byte. `KEEP` records an evidence reconsideration boundary without materializing the implicit topology. Upgrade/Split/Create require post-change Experience; Merge does not immediately split again; Retire needs new evidence plus explicit reactivation. Candidate and competition receipts, Agent-Pack bindings, and Agent handoffs stay local under ignored `.runtime/agent-evolution/`.

Agent Evolution never changes the canonical capability table. A missing reusable Capability emits a Natural Selection need. External Agent discovery, Tool Evolution, and distributed scheduling remain closed.

## Guarded Kernel and evolvable Harness controls

`../assets/harness-controls.json` classifies behavior, not whole files. Its guarded Kernel binds stable identity, provenance, the single atomic writer, rollback, evidence integrity, raw-transcript privacy, authority/trust separation, lifecycle history, authoritative Check receipts, Champion/Challenger separation, deterministic promotion, and the eight-item/4096-byte Context maximum. A Harness Challenger cannot edit those invariants, the Harness evaluator, its safety gate, or its transaction.

The same registry exposes five non-speculative declarative controls: Capability selection, Context ranking, Memory promotion, Agent opportunity, and maintenance/discovery trigger. Their input/output contracts, allowed and forbidden effects, evidence signals, bounded policy schemas, checks, dependencies, and rollback contracts are digest-bound. Authoritative verification remains Kernel-owned; a supplemental orchestration control requires repeated evidence before CREATE. Absence of `docs/nulnul/harness-controls.json` means the shipped Champion defaults; it is not missing setup. A promoted project policy is read only by its existing execution boundary. Ordinary Direct neither loads the registry into model context nor invokes Harness Evolution.

A completed Pack may attach bounded Harness attribution to its existing authoritative Check and Capability Experience. `harness_evolution.py query` returns only active `VERIFIED` records with exact CONTROL_ID/digest, observed decision, expected and actual effects, cost, Check refs, and an allowed attribution class. Capability, Agent, model, project, or host failures do not become Harness evidence merely because a Harness control was present.

The trigger-only evaluator returns KEEP, one TUNE/REPLACE/RETIRE/CREATE candidate, MORE_EXPERIENCE_REQUIRED, or NO_ACTION. Mutation needs repeated control-attributed weakness plus a diagnosis; TUNE changes one bounded policy, REPLACE changes the strategy while preserving control identity, RETIRE removes a fully covered control, and CREATE adds one recurring unowned control job. One frozen declarative Challenger must pass the Kernel safety gate and at most three equivalent task groups including target weakness and a sealed holdout. Quality, checks, selection/topology/Memory correctness, state authority, and regression protection dominate cost.

Only the deterministic transaction can mark a winning control current. It revalidates the Champion, Experience IDs, Kernel digest, safety receipt, competition, policy schema, dependencies, and post-write registry; then it atomically writes `docs/nulnul/harness-controls.json`, archives the prior registry under `memory/harness-controls/`, and appends one ordinary Decision with lineage. Any write or validation failure restores every byte. KEEP records the reconsideration boundary without materializing project policy. Harness Evolution is first-order: it cannot evolve its own attribution, safety, evidence, mutation, rollback, or provenance machinery.

## Cross-project Generalization

`../scripts/generalization_core.py` generalizes verified project evidence without sharing project Memory. It reuses the explicitly approved existing Personal Home and one `generalizations.json` registry; no network, daemon, service, database, vector index, or project-global Memory is added. The frozen `cross_project_evolution.py` personal-adaptation selector remains historical input for Meta selection and is not silently promoted into this Foundation Experience contract.

A project Experience stays project-local. The Generalization transaction stores only a privacy-safe abstract pattern, applicability and non-applicability boundaries, hashed project identities, Experience identities and digests, bounded Capability/Agent/Control refs, validation results, counterevidence, and reciprocal lifecycle lineage. One project with repeated verified evidence may create a Candidate. Transferable status requires either two independent source projects or one verified different-project target confirmation. Raw transcripts, source bodies, source paths, repository/customer names, credentials, and private project Decisions fail the exportability gate.

Target retrieval is an explicit lifecycle/maintenance lookup, never an ordinary task bootstrap step. Its prior pack is capped at three records and 2048 bytes and excludes source Memory and evidence bodies. A target Experience links only the Generalization ID, runs target-owned verification, and records confirmed, adaptation-required, not-applicable, contradicted, or insufficient evidence. Target truth and target-local Decisions/Experiences always outrank the prior. The prior can seed Natural Selection, Agent Evolution, or Harness Evolution, but cannot mutate any of them directly. Contradiction narrows, supersedes, or retires the Generalization without changing source history.

## Inspection

`foundation_runtime.py inspect` provides read-only views for the current Session, recent Sessions, recent Experiences, active Decisions, active Lessons, Open Threads, and Memory statistics. `context` previews a task Context Pack; `evolution-query` shows eligible Experience lineage. These read-only commands do not initialize Memory on a legacy project.

Users do not manage IDs, save sessions, sort memory files, choose routing lanes, or maintain provenance. They may inspect every bounded record.

## Privacy and host independence

Known structured credential fields are redacted before durable writes. This is bounded redaction, not a claim of perfect secret detection. Never intentionally promote API keys, auth tokens, passwords, credentials, raw credential-bearing output, or raw conversations.

Core Session, Pack, Experience, Memory, Context, and lineage schemas are host-independent. A host only needs to start work with prepared bounded context; Codex rules, sandbox escape, and project trust are not Pack prerequisites. Claude may expose different event evidence and body materialization paths; a full Claude bootstrap integration remains outside this foundation.

In user terms: NULNUL remembers verified project decisions and work across sessions and restores only the relevant memory for the next task. Host security approvals remain owned by Codex or Claude, not NULNUL.

## Completion checks for this mode

Apply only the checks whose named state or operation is present. Reuse current authoritative results; repeat after changed inputs, failure, or a concrete unresolved concern.

- Confirm `scripts/foundation_runtime.py validate-layers` and `validate-lineage` pass for initialized Foundation state, Context Packs remain within 8 items and 4096 bytes, and only verified causally attributable Capability Experiences enter `evolution-query`.
- For a Capability Natural Selection decision, confirm `scripts/natural_selection.py validate` passes, the source Experiences are real Foundation records, the frozen ecosystem digest is current, every non-KEEP mutation has passing competition evidence, and retired or superseded capabilities no longer enter Packs while history remains intact.
- For external capability competition, confirm `scripts/external_competition.py validate` passes, discovery had one justified Natural Selection trigger, candidate and source digests are frozen, quarantine is non-authoritative and non-Pack-selectable, license/permission/dependency filters passed, comparison used disposable equivalent conditions and the project check, and adoption or rejection provenance names the exact competition outcome without storing candidate bodies.
- For Agent Evolution, confirm `scripts/agent_evolution.py validate` passes, source Experiences are real and Agent-attributable where required, Champion and one Challenger digests are frozen, graph and verification ownership are valid, each Agent receives only its scoped Pack, non-KEEP promotion has a sealed quality-first competition, and the topology transaction preserves Decision lineage and rollback.
- For Harness Evolution, confirm `scripts/harness_evolution.py validate` passes, `scripts/harness_evolution.py query` returns only active verified Harness-attributed Foundation Experiences, the shipped and project control registries preserve the exact guarded-Kernel digest, one declarative Challenger cannot self-promote or disable checks/provenance/rollback/authority/privacy, non-KEEP promotion has a passing safety receipt and sealed competition, and injected partial or post-validation failure reconstructs the Champion.
- Confirm each work Task has at most one immutable Pack, every selected ref is accepted/current with its canonical target and body digest, empty Direct Packs include no body, and multi-capability Packs receive no unsupported individual credit.
