<p align="center">
  <img src="plugins/nulnul-harness/assets/nulnul-logo-green.svg" width="300" alt="NULNUL logo">
</p>

<h1 align="center">NULNUL Harness</h1>

<p align="center">
  <strong>A project-aware AI coding harness for OpenAI Codex and Anthropic Claude Code.</strong><br>
  Tell it what you want. NULNUL loads only the project capabilities that matter, verifies the work with real checks, remembers verified experience, and evolves only when evidence justifies change.
</p>

<p align="center">
  <a href="https://github.com/SeoNaRu/nulnul-harness/actions/workflows/test.yml"><img src="https://github.com/SeoNaRu/nulnul-harness/actions/workflows/test.yml/badge.svg" alt="CI"></a>
  <img src="https://img.shields.io/badge/version-3.2.0-111111" alt="version 3.2.0">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-111111" alt="MIT license"></a>
</p>

<p align="center">
  <strong>English</strong> · <a href="README.ko.md">한국어</a>
</p>

<p align="center">
  <a href="#quick-start">Quick start</a> ·
  <a href="#what-nulnul-does">What it does</a> ·
  <a href="examples/README.md">In action</a> ·
  <a href="#evidence">Evidence</a> ·
  <a href="https://github.com/SeoNaRu/nulnul-harness/releases/tag/v3.2.0">v3.2.0 candidate</a>
</p>

<p align="center"><strong>Outcome first · Verify the result · Keep only what earns its place</strong></p>

---

## Why NULNUL?

AI coding agents are powerful, but the project-specific setup around them tends to drift: rules get duplicated, skills accumulate, context goes stale, and “done” can mean “the model thinks it is done.”

NULNUL keeps that layer project-aware and evidence-driven.

| Without NULNUL | With NULNUL |
| --- | --- |
| Re-explain project context every session | Resume from bounded verified project state |
| Load a familiar pile of rules and skills | Load only task-relevant capabilities |
| Trust a completion message | Run the repository's authoritative checks |
| Keep adding AI setup | Keep, improve, replace, merge, retire, or create only when evidence supports it |
| Rebuild useful context from chat history | Store verified Experience and retrieve only what is relevant |

If the existing project setup is already the strongest justified path, **adding nothing is a correct result**.

---

## Quick start

Want to see the output first? **[NULNUL in Action](examples/README.md)** collects a local booking UI/API demo, a synthetic research-workbook example, and the recorded 3.1.0 adoption of an existing project. Each case labels its evidence and limitations; these are not three independently verified customer projects or a new performance benchmark.

These new-installation commands target the `v3.2.0` publication candidate once its public tag is available. Exact-version public adoption is pending; the verified `v3.1.0` baseline remains documented below. Use a Codex or Claude Code build that supports plugin commands, and follow the host's trust and permission prompts. A pinned installation does not automatically follow later releases.

### OpenAI Codex

```bash
codex plugin marketplace add SeoNaRu/nulnul-harness --ref v3.2.0
codex plugin add nulnul-harness@nulnul-harness
```

### Anthropic Claude Code

```bash
claude plugin marketplace add 'https://github.com/SeoNaRu/nulnul-harness.git#v3.2.0'
claude plugin install nulnul-harness@nulnul-harness
```

For first-time adoption, including a repository with an existing harness, ask:

```text
Set up NULNUL for this repository, preserving its existing instructions and agent roles.
Then fix the booking API and verify that the existing behavior still passes.
```

For a project already using NULNUL, just ask for the work:

```text
Fix the booking API and verify that the existing behavior still passes.
```

That is the intended normal workflow. You do **not** need to manually choose a Skill, create a Session, save Memory, pick an Agent topology, or run Evolution.

A task already covered by a complete local contract can stay on the Direct path. Installing the plugin does not force setup or durable Memory for every request.

Upgrading an existing NULNUL project? The [3.0 foundation upgrade guide](docs/upgrade-3.0.md) still applies; 3.1 does not change existing checkpoint shapes. If you maintain custom Setup Plans, each inspected existing role now needs a `name: disposition` entry rather than a bare name. Allowed dispositions are `reuse`, `kept`, `upgraded`, `merged`, and `removed`; `kept` normalizes to `reuse`.

<details>
<summary>Read-only preview</summary>

```text
Inspect this repository and show the strongest justified path for this task.
Explain what you would reuse, what you would omit, and why. Do not modify files.
```

</details>

---

<a id="what-nulnul-does"></a>

## What NULNUL does

### 1. Continues the project, not the chat

NULNUL keeps bounded Session, handoff, Experience, Decision, Lesson, and Open Thread state. A later session restores only relevant verified Memory instead of replaying the whole conversation.

Interrupted work is recovered without inventing completion.

### 2. Builds a task-fit Capability Pack

Before work starts, NULNUL selects capabilities for the strongest justified task outcome and verification. Only among materially equivalent outcome paths does it prefer lower context, coordination, runtime, maintenance, and permission cost. Capability or agent count is not the primary objective.

```text
Task
  ↓
Project + relevant Memory
  ↓
Capability selection
  ↓
Pre-Session Capability Pack
  ↓
Work
```

A clear Direct task receives **no capability body**. A task-fit path receives only the selected body or bodies.

### 3. Verifies the result

NULNUL does not treat model confidence as proof.

```text
Work
  ↓
Repository check / build / test
  ↓
Authoritative Check receipt
  ↓
Verified Experience
```

The check that matters is the project's actual check, not an agent-authored “looks good.”

### 4. Learns from verified Experience

Verified work becomes bounded Experience with provenance. Future sessions can retrieve relevant Experience, while raw transcripts stay out of normal Memory and Context.

### 5. Evolves only when evidence says it should

NULNUL does not constantly rewrite itself.

For capabilities, lifecycle decisions can be:

```text
KEEP · UPGRADE · REPLACE · MERGE · RETIRE · CREATE
```

`KEEP` is a first-class decision. If there is no verified weakness, the current capability stays.

External candidates, Agent topology changes, Harness-control changes, and cross-project priors are all evidence-triggered rather than always-on maintenance work.

---

## NULNUL 3.1 in one flow

```text
USER TASK
   ↓
SESSION + PROJECT CONTEXT
   ↓
RELEVANT MEMORY
   ↓
AGENT TOPOLOGY OPPORTUNITY
   ↓
CAPABILITY PACK
   ↓
WORK
   ↓
AUTHORITATIVE VERIFICATION
   ↓
EXPERIENCE
   ↓
MEMORY
   ↓
EVIDENCE-TRIGGERED EVOLUTION
   ├─ Capability Natural Selection
   ├─ External Capability Competition
   ├─ Agent Evolution
   ├─ Guarded Harness Evolution
   └─ Cross-Project Generalization
```

**Simple outside. Inspectable inside.** Ordinary tasks do not load the maintenance/evolution machinery when it is not needed.

---

## A concrete example

User:

```text
Add validation to the import endpoint and keep the existing error contract.
```

NULNUL can:

1. inspect the existing project contract and checks;
2. restore only relevant Memory;
3. select the project API-validation capability;
4. prepare that capability before work begins;
5. implement the change;
6. run the repository's authoritative validation command;
7. store the verified Experience;
8. reuse that Experience later when it is actually relevant.

The user still asked for one thing: **the product outcome**.

---

## How NULNUL is different

NULNUL is not an agent-team generator, a giant prompt bundle, or a hosted orchestrator.

| Tool type | Typical default | NULNUL's default |
| --- | --- | --- |
| Agent-team generator | Create a roster | Reuse direct execution when competitive; add bounded roles for material outcome value |
| Prompt / rule bundle | Load prepared instructions | Inspect the repository and select task-fit capability context |
| Memory layer | Retain conversation/context | Keep bounded verified project Memory, not raw chat |
| Hosted orchestrator | Run a remote workflow service | Stay repository-local; no server or daemon is required |
| Capability marketplace | Browse/install more capabilities | Discover or compare candidates only when a verified project need exists |
| NULNUL | — | Complete the task, verify it, remember useful Experience, evolve only when justified |

---

## Evolution without churn

NULNUL 3.1 separates several kinds of change instead of treating “self-improvement” as one unrestricted rewrite.

### Capability Natural Selection

A project capability can stay, improve, be replaced, merge with another capability, retire, or be created from a verified uncovered need.

### External Capability Competition

External candidates are treated as **untrusted** and quarantined before evaluation. They do not enter ordinary Pack selection merely because they exist.

In 3.1, the offline preparation helper packages inspected, pinned public Skill files for the existing local-directory quarantine path. It does not fetch, install, or automatically accept candidates. Remote marketplace superiority is **not** claimed.

### Agent Evolution

Agent topology is about **who owns which execution responsibility**. Direct or single-agent execution is preferred when outcome-competitive. Additional bounded roles must materially improve specialization, context isolation, parallel work, or independent verification; one owner keeps final synthesis.

### Guarded Harness Evolution

NULNUL separates a guarded Kernel from evolvable control policy. Evidence may justify bounded control tuning or replacement, but candidates cannot change their own evidence, promotion result, provenance, authority, or rollback rules.

### Cross-Project Generalization

Cross-project reuse is opt-in and requires an existing local Personal Home chosen and approved by the user. Projects never copy raw Memory into one another. Only privacy-safe abstract priors with provenance and applicability boundaries are eligible; they remain subordinate to target-project truth and require compatibility and target validation. Public Meta adoption evidence covers its frozen selector and a bounded case, not universal transfer or live proof of every Generalization path.

---

<a id="evidence"></a>

**3.2.0 publication candidate:** concise task routing, executable host resume commands, full installed-copy comparison, safer checkpoint verification, and bounded Trace evidence. The results below distinguish prior local observations from frozen public 3.1.0 evidence; exact-public 3.2.0 adoption is pending.

The skill entry now puts ordinary covered tasks first and routes setup, continuity, workflow and evolution details on demand. Its description is 244 characters and its entry is about 1,026 words; these are document sizes, not measured runtime gains. Required permission/check ownership and the verified checkpoint read/check boundaries are preserved. This user-directed documentation cleanup is separate from the closed experiment below.

Current local maintenance also reduces the developer entry to 615 words by moving subsystem-specific invariants into the [development contract](docs/development-contract.md). Checkpoint rechecks invalidate old verification before execution, malformed fields fail closed, status requires matching ordered body evidence, and the non-Git documentation fallback scans once. [Reproductions and validation](docs/runtime-maintenance.md) describe these changes; frozen public-adoption results do not certify them.

A subsequent [installed-copy and live-use check](docs/live-use-validation.md) refreshed the stale local cache, completed a real receipt-schema correction, and recovered an interrupted check in a fresh Codex session. Each session ran its completion check once and passed all 12 checks. Both still listed files before checkpoint validation; an ineffective section reorder was restored, so fast-resume conformance and comparative speed are not claimed.

The [three-upgrade follow-up](docs/live-use-validation.md#follow-up-all-three-requested-upgrades) adds executable host-entry commands and full installed-file comparison. Two fresh document/bug resumes validated the checkpoint before discovery and ran completion once; an interrupted check recovered safely. Local-only adoption preserved the original code and roles after an inventory guard repair. The full local suite passed 476 checks. Extra skill loading and an adoption recheck remain explicit limits; no comparative speed or public-release claim is made.

The [instruction-routing evaluation](docs/instruction-routing.md) ended with NO_PROMOTION after eight model attempts: the first evaluator was invalidated, and the repaired evaluator withheld acceptance for an unknown candidate event. This episode’s product and guidance changes were restored; only the verified local evaluator repair and rejection evidence remain. The frozen 3.1.0 evidence below is unchanged.

## New in 3.1

The published **3.1.0** baseline added six task-delivery improvements without changing the 3.0 state formats, fast resume, acceptance authorities, or skills-only boundary:

1. [Boundary QA](plugins/nulnul-harness/skills/nulnul-harness/references/workflow-delivery.md): inspect actual producers and consumers, check integration incrementally, and retain a reproducible negative control.
2. [Task recipes](plugins/nulnul-harness/skills/nulnul-harness/references/workflow-recipes.md): web/API changes, data migration/sync, and evidence-backed research.
3. [Execution patterns](plugins/nulnul-harness/skills/nulnul-harness/references/workflow-delivery.md): six conditional patterns using existing roles and handoffs, without mandatory teams or fixed models.
4. [Partial reruns](plugins/nulnul-harness/skills/nulnul-harness/scripts/workflow_delivery.py): invalidate affected dependency chains and reuse only matching verified contracts and input/output fingerprints.
5. [Skill acceptance cases](plugins/nulnul-harness/skills/nulnul-harness/references/skill-acceptance.md): actual use, near-miss skips, and follow-ups, with authoritative check references.
6. [Offline candidate preparation](plugins/nulnul-harness/skills/nulnul-harness/references/external-candidate-preparation.md): prepare inspected pinned skill bytes for existing quarantine and competition, without fetching, installing, or granting adoption.

These references load only when needed. Planner receipts and development scores are advisory, not Foundation evidence, promotion authority, sealed holdouts, or proof of live quality gains. No new state migration is required.

Public adoption exposed three gaps, now repaired: [installed-plugin bootstrap](evals/benchmarks/claude-adopt/release-3.1.0-failure.json), [cold-setup listing and document completion](evals/benchmarks/claude-adopt/release-3.1.0-r2-failure.json), and [explicit role dispositions](evals/benchmarks/claude-adopt/release-3.1.0-r3-failure.json). Setup receipts bind the project, host, and executing package digests; the transaction rejects missing, duplicate, ambiguous, or unknown role dispositions. No shadow skill, extra state writer, protected-path write, or checkpoint migration is required. The [fresh fourth public run passes](evals/benchmarks/claude-adopt/release-3.1.0-r4.json) without relaxing the validator. Earlier failures and their prerelease archives remain preserved; these are release regressions, not sealed holdouts or a universal quality-gain benchmark.

```bash
python3 plugins/nulnul-harness/skills/nulnul-harness/scripts/workflow_delivery.py demo
```

## Evidence

The results below certify the frozen **3.1.0 release on 2026-09-08**, not every subsequent working-tree change. Suite counts refer to the clean publication tree. New delivery helpers have deterministic coverage, not a claimed live quality advantage.

| Evidence | Result | What it supports |
| --- | --- | --- |
| [Repository test suite](tests/) | **446 passed (446 checks)** | Clean-release coverage for delivery, candidate preparation, both-host installed-plugin bootstrap, explicit role dispositions, and negative controls. This does not certify an arbitrarily modified local workspace. |
| [Release Gate](scripts/release_gate.py) | **100/100 PASS** | `release_ready=true` with exact-version public adoption evidence. |
| [Public Claude adoption](evals/benchmarks/claude-adopt/release-3.1.0-r4.json) | **PASS, 5/5 checks** | Installed-roster inspection, role classifications, verified checkpoint, original task completion, document freshness, preserved profiles and inactive Codex entry, zero protected writes. |
| [Public Meta adoption](evals/meta-evolution/release-3.1.0-meta-r4.json) | **PASS** | Same applicable adaptation with 3 flat checks versus 1 Meta check; no-match, conflict, migration, and rollback controls. Scoped to the frozen selector and this fresh adoption case. |
| [NULNUL 3.1.0 release](https://github.com/SeoNaRu/nulnul-harness/releases/tag/v3.1.0) | **Verified public artifact** | Frozen product commit `a9fd59e8c5852e8808f6698262e90d389f39f42a`; [tag CI passed](https://github.com/SeoNaRu/nulnul-harness/actions/runs/34212367385). |
| `nulnul-harness-3.1.0.zip` | **60 files, 237,942 bytes** | Reproducible archive; public download and actual installed files match. |
| Release archive SHA-256 | `7716a8ddfeb43632b4ad836c29deb1fd2981a84d423d2f2705fb88becad9e49d` | Frozen artifact identity. |

One previously frozen live Direct pair kept the NULNUL path within the project's preferred `<=120%` input target while preserving zero capability bodies for a clear Direct task. This is historical, scoped evidence, not a new 3.1 live benchmark or a universal performance guarantee.

### Evidence discipline

The following distinctions matter:

- **Live-proven:** core Session/Pack/Check/Experience/Memory continuity and the Skill `KEEP` path.
- **Implemented and deterministically validated:** broader lifecycle mechanics such as non-KEEP capability changes, Agent Evolution, Harness Evolution, and Generalization.
- **Not claimed:** globally optimal capabilities, universal multi-Agent superiority, recursive self-evolution, or universal cross-project best practices.

<details>
<summary>Historical v2.2 / v2.3 research evidence</summary>

Earlier Project-Fit experiments did **not** show an advantage over exact v2.2.1 and explicitly recorded `v2.3 NOT READY`. Those failures drove the 3.0 architecture changes: bounded Direct behavior, Pre-Session Capability Packs, deterministic verification receipts, Experience/Memory, evidence-gated evolution, and retirement of the runtime-exclusive activation design.

See:

- [Post-2.2.1 proof decision](docs/roadmap/post-2.2.1-proof-decision.md)
- [Baseline findings](docs/roadmap/post-2.2.1-baseline-findings.md)
- [Meta HyperAgents](https://ai.meta.com/research/publications/hyperagents/)
- [GeekNews Weekly 2026-15](https://news.hada.io/weekly/202615)

Historical failure evidence remains available; it is no longer presented as the current product state.

</details>

---

## Safety and privacy

NULNUL 3.1 keeps the important boundaries explicit:

- **Repository-local operation:** no NULNUL server or daemon is required.
- **Raw evidence stays local-only:** raw transcripts/runtime events are not normal durable Memory.
- **Project Memory stays isolated:** cross-project transfer uses abstract priors, not source-project Memory copies.
- **External candidates are quarantined:** discovery does not grant authority or execute untrusted install behavior.
- **Capability context is not authority:** loading a Skill does not grant structural project/Harness write permission.
- **Authoritative checks stay deterministic:** model-authored success does not replace check receipts.
- **Mutations are transactional:** lifecycle changes validate, preserve provenance, and roll back on failure.
- **Host trust remains host/user-owned:** NULNUL does not silently take over host trust.

Read [SECURITY.md](SECURITY.md) and [PRIVACY.md](PRIVACY.md) for the full boundaries.

---

## What NULNUL may add to a project

NULNUL prefers reusing the project that already exists. Durable state is added only when it has a job.

Typical managed surfaces include:

- `AGENTS.md` or `CLAUDE.md` managed guidance for the active host;
- `docs/nulnul/project.md` for stable project facts and checks;
- bounded checkpoint / Session / Experience / Memory state under `docs/nulnul/`;
- a project-local Skill only when the current capability ecosystem does not already cover the job.

Only the active host's entry may change: Codex owns `AGENTS.md`, and Claude Code owns `CLAUDE.md`. Sequential adoption preserves the inactive entry and reuses the same shared contract with one live-state writer. Concurrent mutation of that state by both hosts is not supported.

The foundation migration and ownership rules remain documented in the [3.0 upgrade guide](docs/upgrade-3.0.md).

---

## Inspectability

NULNUL is designed so the normal path stays small while the internal decisions remain inspectable.

Advanced inspection can answer questions such as:

- Why was this capability selected?
- Which project check ran?
- What verified Experience was stored?
- What Memory was restored in the next Session?
- Why did Evolution choose `KEEP` instead of changing something?
- Which capability/Agent/Harness version produced an outcome?

The durable records are provenance-linked; raw internal transcripts are not required for ordinary inspection.

---

## Current limitations

NULNUL 3.1 deliberately does **not** claim more than its recorded evidence supports.

- The Skill `KEEP` lifecycle has live evidence; a naturally occurring live Skill `UPGRADE` has not yet been observed in the public evidence set.
- External Capability Competition is implemented with bounded source/quarantine mechanics; there is no claim that NULNUL finds the best capability on the internet.
- Agent Evolution mechanics are implemented, but multi-Agent execution is not claimed to be universally better than Single-Agent execution.
- Harness Evolution is first-order and guarded; recursive unrestricted self-evolution is not supported.
- Cross-Project Generalization is privacy-gated and implemented, but universal transferability is not claimed.
- Host feature depth can differ between Codex and Claude Code; host-independent records do not imply perfect host parity.

These limitations are product boundaries, not hidden TODO claims.

---

## Architecture details

<details>
<summary>Core layers</summary>

```text
Project Model
Session / Task
Context Assembly
Capability Selection
Pre-Session Capability Pack
Agent Topology
Verification
Observability
Experience
Memory
Provenance
Natural Selection
External Competition
Agent Evolution
Guarded Harness Evolution
Cross-Project Generalization
```

Across the stateful layers, identity and provenance stay explicit. Ordinary work does not load the full maintenance stack.

</details>

<details>
<summary>Evolution lifecycle</summary>

```text
Verified Experience
        ↓
Evidence review
        ↓
No weakness? ─────────────→ KEEP
        ↓
Justified change
        ↓
Frozen Challenger
        ↓
Champion vs Challenger
        ↓
Verification + holdout + rollback gate
        ↓
Promote or reject
```

The model may propose semantic changes. Deterministic runtime owns identity, digests, evidence validation, promotion state, provenance, and rollback.

</details>

---

## Release and upgrade

- Publication candidate: [NULNUL 3.2.0](submission/release-notes.md); exact-version public adoption is pending.
- Verified baseline: [NULNUL 3.1.0](https://github.com/SeoNaRu/nulnul-harness/releases/tag/v3.1.0)
- Upgrade guide: [docs/upgrade-3.0.md](docs/upgrade-3.0.md), unchanged checkpoint shapes in 3.1 and 3.2.
- Changelog: [CHANGELOG.md](CHANGELOG.md)
- Security: [SECURITY.md](SECURITY.md)
- Privacy: [PRIVACY.md](PRIVACY.md)

---

## License

MIT — see [LICENSE](LICENSE).


## NULNUL + Trace: outcome evidence

Locally execution-validated integration candidate; not included in the frozen
v3.1.0 release evidence. NULNUL projects its existing runtime records into a
privacy-bounded, versioned contract for [NULNUL Trace](https://github.com/SeoNaRu/nulnul-trace).
The useful distinction is **selected capability -> body loaded -> work -> authoritative
check -> task outcome**, with source digests, rather than more logs or inferred success.

Trace separates project configuration from observed use, checks receipt/file/command
freshness and exposes checked outcomes, missing evidence and limited cost signals.
It does not call another model, export transcripts, mutate the harness or claim an
improvement percentage without a comparison. Token savings and fresh-resume success
remain unmeasured. See the [evidence contract](plugins/nulnul-harness/skills/nulnul-harness/references/trace-evidence.md).

### Seeing Harness work in Trace

1. Use the updated Harness producer with a new Foundation task. Setup alone and older sessions do not create runtime evidence; an unchanged installed plugin will not gain this integration automatically.
2. Run the matching Trace API, web app and collector. Apply the additional table with the existing `pnpm db:push` command when updating a database.
3. Open the session ticket, expand **하네스가 한 일**, and choose **이번 세션** (this session) or **이 프로젝트** (this project). Selection, body loading and receipt-linked results are separate observations.

### Local validation (2026-09-09)

- Trace tests: **71/71 passed** (domain 48/48, collector 23/23); API and web builds passed.
- Deterministic integration smoke: 12 canonical runtime events, one task and one receipt-linked pass reached the collector, API and browser. Session/project scopes, receipt provenance and a 390px mobile viewport passed.
- API negative controls passed: replay deduplication, wrong project/session, private-field rejection, missing authentication and cross-device session/project isolation.
- Harness workspace: **447/448 passed**; the remaining product-boundary failure is the pre-existing `docs/research` directory. It was not deleted or excluded to manufacture a pass.
- A separate publication-base copy was not green: 448 tests, 5 failures and 6 errors, including frozen-evidence source-identity mismatches. This is not clean release validation.
- Documentation-debt check passed. Release Gate still reports `release_ready: false`: exact-version public Claude and cross-project Meta adoption evidence does not cover the changed producer bytes.
- The smoke used synthetic data in a temporary DB schema, not an observed user or model trial. The temporary servers/schema were removed; existing sessions were untouched. Additional model calls: **0**. No global plugin update, push or release was performed.

### Request-first integration update (2026-09-09)

The Trace home screen now lists user requests with results, verification and next actions. **하네스가 한 일** distinguishes connected, absent, legacy and unbound runtime records; `nulnul-trace doctor` reports the local cause. The local installed Codex plugin was refreshed for this explicitly requested integration work.

An actual task in this coding session used `trace-core-purity`: selection, body loading and a passing Foundation receipt reached the running collector, API and browser. The earlier interrupted bootstrap remains a partial observation. This is one live development run, not a controlled model comparison or evidence of savings.

The source-state digest now follows Git-tracked and non-ignored untracked files, retaining tracked files even when ignored. Dependency and build trees no longer make bootstrap scan the entire worktree. The digest alone took about 2.1 seconds on the local Trace checkout; this is not an end-to-end performance benchmark. Added two regression checks. After repacking, the full Harness suite is **449/450 passed**, with only the previously recorded `docs/research` product-boundary failure remaining. Frozen public release evidence is unchanged.

## Operational visibility: local candidate

Ask what NULNUL is doing without opening Trace. The read-only view separates source
identity, an explicitly inspected installation, host-session binding, task state,
capability selection with its recorded reason, changes and verification evidence.

~~~bash
python3 plugins/nulnul-harness/skills/nulnul-harness/scripts/harness_status.py --root . --lang en
~~~

The host supplies its actual session key. Unknown binding is not inactivity; an
explicit historical lookup is not current execution. An installed/enabled plugin
entry is not proof that an already-open thread loaded the latest skill body.
Recorded check exits and validated historical receipts are shown separately.
No notification, extra model call, global installation or second state writer is added.

Repository research stays outside the product without being deleted. Packaging
rejects legacy lab paths and symlinks inside the shipped plugin, while retaining
normalized archive timestamps and permissions.

Local evidence and publication permission are separate commands:

~~~bash
python3 scripts/release_gate.py
python3 scripts/public_release_gate.py
~~~

The second command exits nonzero unless `release_ready` is exactly true. Main and
pull requests targeting main use this strict gate; non-main candidates retain the
local evidence gate. Frozen evaluator files and historical adoption hashes are not
rewritten to make a changed candidate look certified.

The updated candidate passes all 481 repository checks. An actual Trace project repair now recognizes quoted verification paths; the original workspace passed its completion check after the reviewed two-file patch. The fresh metadata-only setup follow-up reused its existing receipt through two transactions with zero additional completion executions; the initial repeated-check failure remains recorded. Exact public adoption is still pending.
This source change is not a new public release or proof of comparative superiority.
