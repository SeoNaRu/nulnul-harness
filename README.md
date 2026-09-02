<p align="center">
  <img src="plugins/nulnul-harness/assets/nulnul-logo-green.svg" width="320" alt="NULNUL logo">
</p>

<h1 align="center">NULNUL Harness</h1>

<p align="center">
  <strong>NULNUL is an open-source, repository-local AI development environment for OpenAI Codex and Anthropic Claude Code.</strong><br>
  Before changing the AI setup, it inspects existing <code>AGENTS.md</code> or <code>CLAUDE.md</code> guidance, skills, plugins, agents, and project checks. It selects the strongest justified task-fit capability path, verifies the result, and removes anything that does not materially help.
</p>

<p align="center">
  <a href="https://github.com/SeoNaRu/nulnul-harness/actions/workflows/test.yml"><img src="https://github.com/SeoNaRu/nulnul-harness/actions/workflows/test.yml/badge.svg" alt="CI"></a>
  <img src="https://img.shields.io/badge/version-3.0.0-111111" alt="version 3.0.0">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-111111" alt="MIT license"></a>
</p>

<p align="center">
  <strong>English</strong> · <a href="README.ko.md">한국어</a>
</p>

<p align="center">
  <a href="#quick-start">Quick start</a> · <a href="#read-only-preview">Read-only preview</a> · <a href="https://github.com/SeoNaRu/nulnul-harness/releases/tag/v3.0.0">Current release: v3.0.0</a>
</p>

<p align="center">
  Outcome first · Evidence-backed capability selection · Waste removed after verification
</p>

> A “harness” is the set of project rules, skills, work state, and executable checks that guide an AI coding agent. NULNUL keeps this setup in the repository; it is not an agent-team generator.

**Outcome quality comes first. Verification makes it credible. Simplicity breaks ties between materially equivalent paths.**

## Before / With NULNUL

| Before | With NULNUL |
| --- | --- |
| Re-explain the project every session | Read the repository and its current setup first |
| Keep a familiar but materially weaker capability, or accumulate overlapping ones | Reuse when outcome-competitive; add or replace only for material outcome value |
| Accept “done” without a real check | Run the repository's test, build, or validation command |
| Reconstruct old work from chat | Leave a concise, verified checkpoint when continuity is needed |

When the existing setup already provides the strongest justified path, **0 new agents, 0 new skills, and 0 new infrastructure** is a correct result—not a target that overrides quality.

## Measured demo: verified continuity

In corrected benchmark case 31, the same short task asked each arm to fix repeated
whitespace in `slug()`, add a focused regression, run the existing checkpoint
runner once, and stop.

```text
RESULT
✓ Repeated-whitespace slug regression fixed

VERIFY
✓ checkpoint validation passed

RESUME
✓ verification receipt refreshed for the named files
```

<details>
<summary>Harness evidence</summary>

- USED: the existing verified project checkpoint
- UPGRADED / REPLACED / RETIRED / ADDED: nothing
- SKIPPED: a new Agent, Skill, or infrastructure

Vanilla changed the two product files but failed checkpoint validation. Exact
v2.2.1 and the frozen Project-Fit candidate changed those files plus the existing
verification receipt and passed. This demonstrates one bounded continuity case,
not long-term capability evolution.
</details>

### Historical post-2.2.1 Project-Fit proof

The corrected proof view combines 19 valid frozen cases with six preregistered
successors for invalid original contracts. It used zero result-driven retries.

| Variant | Strict task pass | Completion-check pass | Runtime | Input-token proxy |
| --- | ---: | ---: | ---: | ---: |
| Vanilla | 21/25 | 21/25 | 889.613 s | 2,123,954 |
| exact v2.2.1 | 21/25 | 23/25 | 1,154.986 s | 2,813,285 |
| frozen Project-Fit candidate | 21/25 | 23/25 | 1,248.134 s | 3,367,586 |

Verdict: **NO_ADVANTAGE** over exact v2.2.1 and **v2.3 NOT READY**. The current
candidate tied task outcomes while using 8.1% more runtime and 19.7% more reported
input tokens than exact v2.2.1. It won two cases against Vanilla and lost two; both
cleanup cases failed in every variant. No product challenger was promoted. See the
[proof decision](docs/roadmap/post-2.2.1-proof-decision.md) and
[baseline losses](docs/roadmap/post-2.2.1-baseline-findings.md). These numbers cover
only the recorded suite and are not a universal coding-quality claim. The original
Vanilla/v2.2.1 pairs were counterbalanced; the Project-Fit third arm ran later, so
its runtime and token differences are descriptive rather than causal paired deltas.

## Quick start

Install the NULNUL plugin for OpenAI Codex:

```bash
codex plugin marketplace add SeoNaRu/nulnul-harness --ref main
codex plugin add nulnul-harness@nulnul-harness
```

Or install it for Anthropic Claude Code:

```bash
claude plugin marketplace add SeoNaRu/nulnul-harness
claude plugin install nulnul-harness@nulnul-harness
```

Upgrading an existing project? Read [Upgrade to NULNUL 3.0](docs/upgrade-3.0.md)
before migrating durable state.

After installation, start a new session with this prompt:

```text
Inspect this repository first. Reuse what is outcome-competitive, add capability
only where it materially improves the result, then complete my request and run
the real project checks. Remove anything that did not materially help.
```

You can also ask for the product change directly:

```text
Fix the booking API and verify that the existing behavior still passes.
```

### Read-only preview

See how NULNUL would reason about the setup without writing anything:

```text
Inspect this repository and show the strongest justified harness path for the
outcome, including what you would omit as non-contributing. Do not modify files.
```

<a id="what-nulnul-is-for"></a>

## What problem does NULNUL solve?

AI coding agents need project-specific setup: plugins, rules, context, session state, and executable checks. Maintaining that setup by hand can leave overlapping agents and skills, stale work state, and completion claims without test results.

NULNUL records this setup in an inspectable, removable repository contract. It is intended for Codex and Claude Code projects that need task-fit capability selection, verifiable results, preserved working settings, and no non-contributing additions.

The user sets the product direction. NULNUL chooses the strongest justified implementation and verification path for that task within safety, permission, compatibility, and cost boundaries, then explains material choices.

## Three common uses

### Add a feature without losing existing behavior

**Situation:** An established project already has rules, code, and regression tests.

**Prompt:**

```text
Update the Spring booking API to reject overlapping reservations.
Inspect the current setup first, reuse what already works, and run the
existing regression checks before calling it done.
```

**What NULNUL checks and leaves:** the current guidance and capabilities, an outcome-complete implementation, and the result of the repository's existing completion check.

### Continue work across sessions

**Situation:** A durable project should resume without replaying the whole conversation.

**Prompt:**

```text
Continue this project across sessions without reconstructing progress from chat.
Use a concise verified checkpoint and refuse fast resume if the checked files changed.
```

**What NULNUL checks and leaves:** one bounded checkpoint, its exact completion command, and a freshness receipt tied to the files that command verifies.

> **NULNUL 3.0.0:** NULNUL restores only relevant verified project Memory. A bounded pre-session Capability Pack adds only selected bodies; Direct gets none. Authoritative checks create attributable Experience, and evidence-triggered Natural Selection, external competition, Agent Evolution, and guarded Harness Evolution can propose lifecycle changes without gaining structural authority. Cross-project Generalization keeps project Memory isolated and transfers only privacy-safe abstract priors after independent or target validation. One Agent and shipped control policies remain the defaults; ordinary tasks load none of these maintenance systems or cross-project history.

### Clean up an overgrown AI setup

**Situation:** `AGENTS.md`, `CLAUDE.md`, skills, plugins, and agents now overlap.

**Prompt:**

```text
Inspect the current agents, skills, plugins, and project rules.
Keep or reuse what has a real job, identify overlap, and add nothing
unless the current task proves a gap.
```

**What NULNUL checks and leaves:** a kept, upgraded, merged, or removed decision for existing roles, with no replacement roster created beside them.

<details>
<summary>More prompts: new projects, recurring workflows, repeated failures, and personal reuse</summary>

**New project**

```text
I want to build a local-first expense tracker.
Set up the strongest justified development harness for this outcome, explain
any permission boundary, build the first working slice, verify it, and remove
setup that did not materially help.
```

**Recurring workflow**

```text
Build a workflow that finds finance YouTube creators, removes duplicates,
routes uncertain results to review, and keeps Google Sheets writes behind approval.
```

**Repeated failure**

```text
This failure has happened more than once. Reproduce it, check previously
rejected directions, run one bounded improvement episode, and keep the
current harness if no candidate wins on deterministic evidence.
```

**Reuse a verified method elsewhere**

```text
If this project produces a method worth reusing elsewhere, generalize only the
mechanism, run representative transfer and negative-skip checks, and ask before
writing it to a personal evolution home. In a new project, apply it only after
a compatibility check.
```
</details>

<a id="how-nulnul-works"></a>

## How does NULNUL work?

```text
inspect the repository and host
        ↓
define the outcome and its quality checks
        ↓
reuse outcome-competitive capabilities; investigate material gaps
        ↓
select the strongest justified task-fit path
        ↓
complete the work and run its exact checks
        ↓
remove non-contributing setup; keep verified state when needed
```

In practice, the plugin:

1. detects Codex or Claude Code and reads the applicable `AGENTS.md` or `CLAUDE.md`, project metadata, tests, and run evidence;
2. inventories existing skills, plugins, agents, and tools before judging fit or gaps;
3. reuses installed capabilities when they are outcome-competitive and searches a bounded set of official, curated, or reputable public candidates only for a concrete material quality or verification gap;
4. keeps, upgrades, merges, or removes existing roles instead of recreating them;
5. uses direct or single-agent execution when outcome-competitive, and adds as many bounded roles as materially improve specialization, context isolation, parallel exploration, or independent verification;
6. continues the original request—setup alone is not completion;
7. runs the exact repository check and records bounded, sanitized evidence;
8. leaves concise verified state when the work must span sessions;
9. turns reproduced failures into bounded proposals, not silently accepted rules; and
10. when explicitly opted in, compatibility-checks verified personal adaptations without copying the source project.

Navigator, Worker, Coach, and Gate are responsibility boundaries, not four mandatory agents. Ordinary work combines them when that path is outcome-competitive. The proposal author and the independent Gate separate when a change needs measured promotion.

<a id="comparison-with-other-tool-types"></a>

## How is NULNUL different from other AI coding tools?

The categories below can work together. The difference is the default job, not a claim that NULNUL replaces every other tool.

| Category | Typical starting point | NULNUL's difference |
| --- | --- | --- |
| Agent-team generator | Create a coordinated roster | Uses no target role count; each added or retained role must materially improve the verified outcome. |
| Prompt or rule bundle | Load prepared instructions | Starts from the repository's current rules and executable checks. |
| Memory layer | Retain conversation or context | Stores concise verified project state, not raw conversations. |
| Hosted orchestrator | Run long-lived workflows on a service | Stays repository-local and skills-only; no server or daemon is required. |
| Repository template | Apply the same starting structure | Adapts to an existing repository and may add nothing when that is the strongest justified path. |
| NULNUL | Inspect, complete, verify, and improve project work | Reuses outcome-competitive capabilities, adds what materially helps, and removes what does not. |

<a id="repository-changes"></a>

## What files can NULNUL add to a repository?

If the existing setup already provides the strongest justified path, NULNUL adds no files. When durable support materially improves the outcome or its verification, it may add the following:

```text
your-project/
├── AGENTS.md or CLAUDE.md     # active host guidance, merged only when needed
├── docs/nulnul/
│   ├── project.md             # stable goal, checks, decisions, permissions
│   ├── checkpoint.json        # concise verified multi-session state
│   ├── evolution.json         # active governed-improvement state, when needed
│   └── evolution.archive.json # closed evidence, outside normal resume context
├── .agents/skills/<name>/     # Codex: only when no outcome-competitive capability exists
└── docs/nulnul/workflows/<name>.md
                                # Claude Code: only for a justified reusable workflow
```

Codex owns only `AGENTS.md`; Claude Code owns only `CLAUDE.md`. During sequential use, both point to the same `docs/nulnul/` contract and exactly one live-state writer. Concurrent mutation by both hosts is not claimed.

Ordinary continuity uses `checkpoint.json`. Governed evolution uses `evolution.json`. They are not simultaneous live-state writers. Generated setup stays removable without changing product code.

Closed evolution history is kept in a digest-bound adjacent archive. Deterministic code verifies and reconstructs it, while ordinary resume reads only the active state and queries rejected history only when relevant.

Each state file has one writer. Verification keeps `verified`, `failed`, and `unknown` distinct, and every validity check must also pass a negative control that is expected to fail.

<a id="verification-and-trust-model"></a>

## How does NULNUL verify AI coding work?

NULNUL does not treat model confidence as proof. It runs repository checks and records bounded evidence. For broader claims, it also uses negative controls, a frozen candidate, an independent Gate, and a rollback path.

```text
repository check → negative controls → candidate comparison → Independent Gate
                                                            ↓
                                                  live cycle or rollback

transfer claim only → sealed unseen check → scoped decision
```

### Current public evidence

| Evidence | Current result | What it establishes |
| --- | --- | --- |
| [Repository test suite](tests/) | **431 passed (431/431)** | Deterministic product, Foundation, lifecycle, host-switching, privacy, rollback, transfer, evolution, documentation-debt, and negative-control contracts pass. |
| [Known behavior and safety](evals/results.json) | **100/100 across 12 cases** | The published fixtures pass. This is not a universal quality score or proof of better results in every repository. |
| [Exact public 2.2.1 Claude adoption](evals/benchmarks/claude-adopt/evidence.json) | **5/5 checks; 0 protected writes** | A fresh public-tag install preserved two existing agent profiles and the inactive Codex entry. |
| [Exact public Project M](evals/meta-evolution/public-adoption.json) | **3 → 1 full compatibility checks** | The bounded selector kept the same correct transactional-migration decision and passed no-match, conflict, privacy, permission, migration, and rollback controls. |
| [Release artifact](https://github.com/SeoNaRu/nulnul-harness/releases/tag/v2.2.1) | **Byte-identical; SHA-256 `f2d320804c5b86a7d1797c8088a36cf824a8009a6b825f19dcda8b8fa2c3388e`** | The downloaded v2.2.1 archive matches the frozen local artifact exactly. |

The v2.2.1 evidence records `local_candidate_ready: true` and `release_ready: true`. [Candidate CI run 32689502007](https://github.com/SeoNaRu/nulnul-harness/actions/runs/32689502007) and [main CI run 32689545235](https://github.com/SeoNaRu/nulnul-harness/actions/runs/32689545235) passed the full suite and Release Gate; [tag CI run 32688807083](https://github.com/SeoNaRu/nulnul-harness/actions/runs/32688807083) also passed.

### Earlier local constraint-lifecycle evaluation (not shipped)

The 2026-08-25 constraint-lifecycle work tested possible 2.3 behavior, but it did not upgrade the core product.

| Question | Verified answer |
| --- | --- |
| Did NULNUL become 2.3? | **No.** Every evaluated candidate was rejected and removed. The active core version remains **2.2.1**. |
| What did the A/B tests show? | [Episode 1](evals/constraint-lifecycle/gate-decision.json) improved the best exact result from 0/4 to 2/4 but omitted required conflict identifiers. The [follow-up](evals/constraint-reconciliation-v2/gate-decision.json) completed those identifiers at +1.42% paired input, but champion and candidate both scored 0/4 because permission and inactive-guard fields were still wrong. |
| What did that cycle's green run prove? | **241/241** repository tests, **15/15** product-plugin tests, documentation debt **0**, and Release Gate **100/100** proved that the rejected code was removed and the 2.2.1 rollback state was intact. They did **not** prove the proposed 2.3 behavior. |
| What was upgraded? | Three audited project-local harness setups were repaired and pass their own completion checks. Those local repairs are not core-product promotion evidence. |

<details>
<summary>Measured evidence behind the current contracts</summary>

| Evidence | Result | Limit |
| --- | --- | --- |
| Final 1.7.0 Release Gate | Passed exact-tag Claude Code and personal-adaptation adoption; main CI `31651306556` passed | Establishes that release path, not all future environments |
| Stale checkpoint defect | Unsafe fast resume **3/3 → 0/3** | One reproduced correctness defect |
| Unseen transfer | **Narrower Scope** | One mechanism transferred to one unseen Perl/TAP project shape; harness-wide generalization is not established |
| Bounded live evolution | Champion and retries found **7 violations**; one-generation candidate found **0** and stopped on `SUCCESS` | One activation-metadata failure family |
| Personal adaptation | **2 apply, 1 skip, fresh Project D pass** | One checkpoint-freshness mechanism; not a general memory system |
| Cross-project Meta Gate | **3 families, 9 → 4 full checks, 3/3 decisions correct** | One sealed selection episode; no token, runtime, universal, or cross-user claim |
| Bounded resume context | Active evolution fixture **87.48% smaller** | One published fixture; full evidence remains in the integrity-checked archive |
| Documentation-debt A/B | Median **17.73645 s → 0.2308 s (−98.70%)** across four counterbalanced rounds | Same result on the tracked release repository |
</details>

Rejected and failed candidates remain in the evidence:

- a plausible Navigator candidate missed verification or increased cost and was rejected;
- an invalid first Ruby holdout was retired and preserved instead of being relabeled unseen;
- the 2.2 consent/continuity candidate was removed after the preregistered strict Gate returned `NO_PROMOTION`;
- post-2.0 capability-authority, intent, decision-artifact, and repository-receipt candidates remain recorded as `NO_ADVANTAGE` or `NO_PROMOTION`; and
- field incidents that lost 12,000 decisions to multiple writers and rescanned the same 120 items after empty cycles became single-writer and cursor-persistence rules, not universal benchmarks.

Reproduce the release-level checks:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/release_gate.py
```

## Controlled Evolution

A proposed harness change must pass checks owned by an independent Gate before it can be retained.

```text
reproduced failure
        ↓
bounded candidate
        ↓
current way vs candidate
        ↓
Independent Gate
     ↙        ↘
  reject    provisional
                 ↓
          one live cycle
             ↙       ↘
         confirm   rollback
```

Before candidate generation, NULNUL fixes the failure description, candidate and generation count, evaluation and model budget, permission boundary, rejected-history lookup, fair retry baseline, and stop conditions. The Coach proposes; deterministic checks and the independent Gate assign credit. If the candidate does not improve the result, the decision is `NO_PROMOTION`.

Evaluation exposure is state: DEV may inform development, VALIDATION may select a candidate, and a sealed HOLDOUT is used once for a transfer estimate. First exposure and retirement stay machine-readable; a used case cannot be renamed “unseen.”

A Gate pass does not immediately replace the confirmed version. The candidate remains **provisional** while the last confirmed version stays active. One observed healthy cycle confirms it; an executable threshold breach records rollback. The shipped executor does not run arbitrary rollback commands or edit product files.

### Personal adaptation

Personal reuse is opt-in and adaptation-only. It requires a user-selected existing local home, representative transfer and negative-skip checks, and an independent Personal Gate. A new project checks compatibility again. Missing permission, private data, duplicate identity, conflict, stale or revoked status, and false activation fail closed. Raw project memory is never copied between repositories.

### Cross-project / Meta Evolution

Cross-project selection begins only after three independent mechanism families pass the Personal Gate lifecycle. NULNUL aggregates typed, privacy-safe summaries inside the approved local boundary, keeps failed transfers and unknown relations, and compares a frozen selector with flat and simple baselines on fresh cases. A Meta Gate owns promotion, rejection, narrower scope, no advantage, conflict, permission block, or rollback.

This is user-triggered, bounded improvement. It is not continuous self-learning, an unattended loop, a vector database, a hosted evolution service, or cross-user learning.

<a id="where-nulnul-fits"></a>

## Who is NULNUL for?

**Good fit:**

- an existing project whose current rules, skills, plugins, agents, and checks should be preserved;
- a new project that should start with an outcome-fit, waste-aware AI working contract, not a prebuilt team;
- development that spans sessions and must resume from verified repository state;
- work where tests, permissions, independent review, or rollback matter;
- recurring workflows or reproducible failures that justify measured project-local improvement; and
- setups that should merge or remove obsolete structure instead of only accumulating it.

**Probably unnecessary or not a fit:**

- a read-only question or tiny one-off edit;
- a task already covered by a clear local contract and runnable completion check;
- an always-on workflow engine or hosted orchestration service;
- a system expected to authenticate, deploy, publish, or write externally without approval;
- a tool meant to improve the underlying model's reasoning ability; or
- raw personal memory, automatic global rules, or unapproved learning across unrelated projects.

If the repository already has everything the task needs, you may not need NULNUL at all.

## Trust boundaries and known limits

- Authentication, external writes, deployment, publication, destructive operations, paid resources, and global registration require explicit approval.
- Credentials, raw conversations, transcripts, complete command histories, machine paths, and private project data do not become evolution memory.
- Personal Evolution requires an explicitly selected existing local directory. One real private local home has passed validation; its path is absent from public evidence.
- Unattended Claude Code sessions may inspect host-owned `.claude/**` configuration but do not rewrite it.
- Checkpoints are compared with a bounded repository fingerprint before fast resume.
- Compacted archives are integrity-checked local evidence and are not loaded into ordinary resume context.
- Independent Gate ownership is validated from declared state; it is not cryptographic proof of separate runtime identities.
- NULNUL does not remove the underlying model's reasoning limits or prevent every agent error.
- One unseen transfer and one bounded live episode do not establish universal or harness-wide generalization.
- The 2.0 evidence covers three mechanism families, three sealed selector cases, one confirmed `COMPLEMENTS` relation, and one live cycle. Other relations remain `UNKNOWN`. Arbitrary project lessons, token or runtime gains, and cross-user learning are not established.
- There is no daemon, recursive Coach, candidate population, hosted control plane, or unattended infinite loop.

<a id="current-release"></a>

## Current NULNUL release

**v3.0.0** is the current product version.

- Sessions, concise handoffs, verified Experience, and durable Memory preserve useful continuity without replaying raw conversation history.
- Pre-session Capability Packs keep Direct empty and place only selected current capability bodies into project-fit work.
- Deterministic check receipts connect work, outcome, Memory, and later evolution evidence.
- Skills, capability ecosystems, Agent topologies, and bounded Harness controls change only through evidence-gated Champion/Challenger decisions with rollback.
- External candidates remain quarantined and untrusted until project checks establish fit.
- Cross-project knowledge remains an abstract, privacy-checked prior until the target project validates it.
- The runtime-exclusive Codex-rule activation path is retired; upgrade cleanup is deterministic and does not mutate user trust.

See [Upgrade to 3.0](docs/upgrade-3.0.md), [Security](SECURITY.md), and the full history in [`CHANGELOG.md`](CHANGELOG.md).

<details>
<summary>Earlier evolution milestones</summary>

| Stage | Status | User-facing result |
| --- | --- | --- |
| 1.4 Observable Evolution | Completed | Diagnose why the harness failed instead of trusting a plausible explanation. |
| 1.5 Generalization Gate | Completed | Distinguish a transferable fix from one fitted to familiar cases. |
| 1.6 Bounded Autonomous Evolution | Completed | Search a tiny candidate space under fixed budgets and stop unchanged when evidence is weak. |
| 1.7 Personal Evolution | Completed | Reuse one project-proven mechanism only after transfer evidence, a Personal Gate, and new-project compatibility. |
| 2.0 Cross-project / Meta Evolution | Released and verified | Three verified families feed a bounded selector; sealed decisions stayed correct while full checks fell from 9 to 4. |
| 2.0.1 Host ownership | Released and verified | Sequential Codex and Claude Code use one shared state while each owns only its root entry; concurrent mutation is not claimed. |
| 2.1 Bounded history | Released and verified | Closed evolution evidence moved outside ordinary resume context without losing deterministic reconstruction. |
| 2.1.1 Documentation debt | Released and verified | Four counterbalanced rounds kept the same result while cutting median detector time by 98.70%. |
</details>

<a id="technical-records-and-evaluation-data"></a>

## NULNUL evaluation results and technical records

Public product records:

- the frozen [Product North Star](docs/product-north-star.md), the Korean [beginner-to-advanced product guide](docs/how-nulnul-works.ko.md), and the [post-2.2.1 proof decision](docs/roadmap/post-2.2.1-proof-decision.md);
- [behavior cases](evals/cases.json) and [behavior results](evals/results.json);
- the 15-case [outcome-first and project-fit selection contract](evals/outcome-first/cases.json), which checks deterministic routing and lifecycle expectations rather than measured model task performance;
- [performance evidence](evals/benchmarks/performance.json), [activation evidence](evals/benchmarks/activation/results.json), and [documentation-debt A/B](evals/benchmarks/doc-debt/results.json);
- the rejected [context-routing A/B](evals/benchmarks/context-routing/results.json);
- the Generalization Gate [exposure manifest](evals/generalization/manifest.json), [failed Ruby evidence](evals/generalization/results-ruby-failed.json), and [Perl/TAP result](evals/generalization/results.json).

Evolution records:

- the [1.6 live preregistration](evals/autonomous/live-1.6-preregistration.json);
- 1.7 [personal transfer preregistration](evals/personal-evolution/preregistration.json), [results](evals/personal-evolution/results.json), and [public adoption](evals/personal-evolution/public-adoption.json);
- 2.0 [Meta preregistration](evals/meta-evolution/preregistration.json), [typed evidence](evals/meta-evolution/cross-project-evidence.json), [Meta Gate result](evals/meta-evolution/results.json), and [exact-public adoption](evals/meta-evolution/public-adoption.json);
- post-2.0 [capability-authority `NO_ADVANTAGE`](evals/capability-authority/results.json), [intent/better-path `NO_PROMOTION`](evals/intent-better-path/results.json), [decision-artifact `NO_PROMOTION`](evals/decision-boundaries/results.json), and [repository-receipt `NO_PROMOTION`](evals/repository-receipts/results.json);
- 2.2 behavior-boundary [preregistration](evals/behavior-boundaries/preregistration.json), [cases](evals/behavior-boundaries/cases.json), [sanitized rejection result](evals/behavior-boundaries/results.json), and the excluded [invalid first episode](evals/behavior-boundaries/invalid-evaluator-episode-1.json).
- the rejected 2.3 constraint-lifecycle [preregistration](evals/constraint-lifecycle/preregistration.json) and [Gate decision](evals/constraint-lifecycle/gate-decision.json): the champion scored 0/4 exact runs, candidate 1 scored 1/4 at +38.94% paired input, and the one allowed refinement scored 2/4 at +19.98%, so `NO_PROMOTION` kept 2.2.1 active.
- the rejected derived-review follow-up [preregistration](evals/constraint-reconciliation-v2/preregistration.json) and [Gate decision](evals/constraint-reconciliation-v2/gate-decision.json): champion and candidate both scored 0/4; the candidate completed conflict identifiers at +1.42% paired input but changed a permission field and remained inconsistent on the inactive guard, so its code was removed and 2.2.1 remained active.

The behavior-boundary and both constraint entries record rejected work, not shipped behavior evidence.

## Update, remove, develop, and contribute

Update Codex:

```bash
codex plugin marketplace upgrade nulnul-harness
codex plugin remove nulnul-harness@nulnul-harness
codex plugin add nulnul-harness@nulnul-harness
```

Update Claude Code, then restart it:

```bash
claude plugin marketplace update nulnul-harness
claude plugin update nulnul-harness@nulnul-harness
```

If the marketplace points to a local clone, update that clone first. Start a fresh agent session afterward. Project-local guidance and `docs/nulnul/` state remain separate from the plugin.

Remove from Codex:

```bash
codex plugin remove nulnul-harness@nulnul-harness
codex plugin marketplace remove nulnul-harness
```

Remove from Claude Code:

```bash
claude plugin uninstall nulnul-harness@nulnul-harness
claude plugin marketplace remove nulnul-harness
```

Generated project state is not removed with the plugin. Delete it only when its checkpoint or evolution history is no longer needed.

Validate a local change:

```bash
python3 scripts/pack_plugin.py
python3 -m unittest discover -s tests -p 'test_product_plugin.py' -v
python3 plugins/nulnul-harness/skills/nulnul-harness/scripts/check_doc_debt.py . --host codex
```

Packaging normalizes ZIP timestamps and permissions, so the same plugin tree produces byte-identical archives across local rebuilds. Fresh-checkout CI runs that packer before archive consistency tests.

For release-evidence changes, also run the full `test_*.py` suite and `python3 scripts/release_gate.py`.

Release maintainers can run `python3 scripts/meta_adopt_evidence.py capture PUBLIC_ZIP LOCAL_ZIP PERSONAL_HOME OUTPUT --release-commit COMMIT --run-id ID --run-date YYYY-MM-DD` to rerun the frozen Meta controls from the downloaded artifact. The output is sanitized and does not store the Personal Home path.

Report a bug or setup mismatch in a [GitHub issue](https://github.com/SeoNaRu/nulnul-harness/issues/new?template=bug_report.yml). Include the request, expected result, and observed result—never private code, credentials, or raw transcripts. If an evaluation produced a bounded Experience Digest, run `validate_experience_digest.py DIGEST --feedback-capsule` for local, reviewable Markdown; it does not save or upload anything.

See [`SUPPORT.md`](SUPPORT.md), [`SECURITY.md`](SECURITY.md), [`PRIVACY.md`](PRIVACY.md), [`TERMS.md`](TERMS.md), the [3.0 upgrade guide](docs/upgrade-3.0.md), and the [MIT license](LICENSE).

## Research background

NULNUL started from the harness-engineering problem described in [GeekNews Weekly 353](https://news.hada.io/weekly/202615): users repeatedly assemble the surrounding system as coding-agent capabilities multiply.

Its design was influenced by editable task/meta boundaries, independent verification, champion/candidate comparison, and eval-gated delivery. [HyperAgents](https://ai.meta.com/research/publications/hyperagents/) ([paper](https://arxiv.org/abs/2603.19461), [code](https://github.com/facebookresearch/Hyperagents)) was an important reference for the editable task/meta question. NULNUL does not reproduce HyperAgents or claim open-ended self-improvement.

<details>
<summary>Technical references behind the measured evolution work</summary>

Observable Evolution was informed by [Agentic Harness Engineering](https://arxiv.org/abs/2604.25850), and Generalization Gate by [Rethinking the Evaluation of Harness Evolution](https://arxiv.org/abs/2607.12227). The bounded 1.6 episodes use selected ideas from [Gated Semantic Quality-Diversity](https://arxiv.org/abs/2607.13683), [Hierarchical Self-Improvement](https://arxiv.org/abs/2608.08466), and [Harness Updating Is Not Harness Benefit](https://arxiv.org/abs/2605.30621).

Research provides questions and stronger falsification methods. It does not become a product capability without local evidence. Exact contracts live in the [evolution](plugins/nulnul-harness/skills/nulnul-harness/references/evolution.md), [meta-evolution](plugins/nulnul-harness/skills/nulnul-harness/references/meta-evolution.md), [personal adaptation](plugins/nulnul-harness/skills/nulnul-harness/references/personal-evolution.md), and [generalization](plugins/nulnul-harness/skills/nulnul-harness/references/generalization.md) references.
</details>

MIT © [SeoNaRu](https://github.com/SeoNaRu)
