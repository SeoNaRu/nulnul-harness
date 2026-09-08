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
  <img src="https://img.shields.io/badge/version-3.1.0-111111" alt="version 3.1.0">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-111111" alt="MIT license"></a>
</p>

<p align="center">
  <strong>English</strong> · <a href="README.ko.md">한국어</a>
</p>

<p align="center">
  <a href="#quick-start">Quick start</a> ·
  <a href="#what-nulnul-does">What it does</a> ·
  <a href="#evidence">Evidence</a> ·
  <a href="https://github.com/SeoNaRu/nulnul-harness/releases/tag/v3.0.0">v3.0.0 release</a>
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

### OpenAI Codex

```bash
codex plugin marketplace add SeoNaRu/nulnul-harness --ref main
codex plugin add nulnul-harness@nulnul-harness
```

### Anthropic Claude Code

```bash
claude plugin marketplace add SeoNaRu/nulnul-harness
claude plugin install nulnul-harness@nulnul-harness
```

Then just ask for the work:

```text
Fix the booking API and verify that the existing behavior still passes.
```

That is the intended normal workflow. You do **not** need to manually choose a Skill, create a Session, save Memory, pick an Agent topology, or run Evolution.

Upgrading an existing NULNUL project? Read [Upgrade to NULNUL 3.0](docs/upgrade-3.0.md) first.

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

Before work starts, NULNUL selects the smallest justified set of project capabilities for the task.

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

## NULNUL 3.0 in one flow

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
| Agent-team generator | Create a roster | Start with one execution path; add topology only when evidence justifies it |
| Prompt / rule bundle | Load prepared instructions | Inspect the repository and select task-fit capability context |
| Memory layer | Retain conversation/context | Keep bounded verified project Memory, not raw chat |
| Hosted orchestrator | Run a remote workflow service | Stay repository-local; no server or daemon is required |
| Capability marketplace | Browse/install more capabilities | Discover or compare candidates only when a verified project need exists |
| NULNUL | — | Complete the task, verify it, remember useful Experience, evolve only when justified |

---

## Evolution without churn

NULNUL 3.0 separates several kinds of change instead of treating “self-improvement” as one unrestricted rewrite.

### Capability Natural Selection

A project capability can stay, improve, be replaced, merge with another capability, retire, or be created from a verified uncovered need.

### External Capability Competition

External candidates are treated as **untrusted** and quarantined before evaluation. They do not enter ordinary Pack selection merely because they exist.

The current 3.0 source adapter is intentionally bounded; remote marketplace superiority is **not** claimed.

### Agent Evolution

Agent topology is about **who owns which execution responsibility**. One Agent remains the default. Multi-Agent structure must earn its coordination cost through verified outcome value.

### Guarded Harness Evolution

NULNUL separates a guarded Kernel from evolvable control policy. Evidence may justify bounded control tuning or replacement, but candidates cannot change their own evidence, promotion result, provenance, authority, or rollback rules.

### Cross-Project Generalization

Projects do not share raw Memory. Generalization transfers privacy-safe abstract priors with provenance and applicability boundaries. Target-project truth always wins, and target validation is required before a transferred prior becomes project-local truth.

---

<a id="evidence"></a>

## New in 3.1

Version **3.1.0** is a publication candidate pending exact-version public adoption. It adds six task-delivery improvements without changing the 3.0 state formats, fast resume, acceptance authorities, or skills-only boundary:

1. [Boundary QA](plugins/nulnul-harness/skills/nulnul-harness/references/workflow-delivery.md): inspect actual producers and consumers, check integration incrementally, and retain a reproducible negative control.
2. [Task recipes](plugins/nulnul-harness/skills/nulnul-harness/references/workflow-recipes.md): web/API changes, data migration/sync, and evidence-backed research.
3. [Execution patterns](plugins/nulnul-harness/skills/nulnul-harness/references/workflow-delivery.md): six conditional patterns using existing roles and handoffs, without mandatory teams or fixed models.
4. [Partial reruns](plugins/nulnul-harness/skills/nulnul-harness/scripts/workflow_delivery.py): invalidate affected dependency chains and reuse only matching verified contracts and input/output fingerprints.
5. [Skill acceptance cases](plugins/nulnul-harness/skills/nulnul-harness/references/skill-acceptance.md): actual use, near-miss skips, and follow-ups, with authoritative check references.
6. [Offline candidate preparation](plugins/nulnul-harness/skills/nulnul-harness/references/external-candidate-preparation.md): prepare inspected pinned skill bytes for existing quarantine and competition, without fetching, installing, or granting adoption.

These references load only when needed. Planner receipts and development scores are advisory, not Foundation evidence, promotion authority, sealed holdouts, or proof of live quality gains. No new state migration is required.

```bash
python3 plugins/nulnul-harness/skills/nulnul-harness/scripts/workflow_delivery.py demo
```

## Evidence

NULNUL's public claims are intentionally narrower than its architecture.

| Evidence | Result | What it supports |
| --- | --- | --- |
| [Repository test suite](tests/) | **442 passed (442 checks)** | Clean publication-candidate validation includes workflow delivery and candidate preparation. The original workspace's untracked research files are preserved outside the release tree; the legacy-boundary check remains unchanged. |
| [Release Gate](scripts/release_gate.py) | **100/100 PASS** | Release integrity for the frozen 3.0.0 product |
| [NULNUL 3.0.0 release](https://github.com/SeoNaRu/nulnul-harness/releases/tag/v3.0.0) | **Published stable release** | Public `v3.0.0` tag and release |
| `nulnul-harness-3.0.0.zip` | **53 files · 220,223 bytes** | Reproducible release archive |
| Release archive SHA-256 | `99fd14bef3432f1542270cbdd8640f0a185d319cafcf054505b37260bc9335c1` | Frozen artifact identity |

One frozen live Direct pair also kept the NULNUL path within the project's preferred `<=120%` input target while preserving zero capability bodies for a clear Direct task. These measurements are scoped evidence, not a universal performance guarantee.

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

NULNUL 3.0 keeps the important boundaries explicit:

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

The exact migration and ownership rules are documented in [Upgrade to NULNUL 3.0](docs/upgrade-3.0.md).

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

NULNUL 3.0 deliberately does **not** claim more than the current evidence supports.

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
<summary>Core 3.0 layers</summary>

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

- Current stable release: [NULNUL 3.0.0](https://github.com/SeoNaRu/nulnul-harness/releases/tag/v3.0.0)
- Upgrade guide: [docs/upgrade-3.0.md](docs/upgrade-3.0.md)
- Changelog: [CHANGELOG.md](CHANGELOG.md)
- Security: [SECURITY.md](SECURITY.md)
- Privacy: [PRIVACY.md](PRIVACY.md)

---

## License

MIT — see [LICENSE](LICENSE).
