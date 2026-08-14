<p align="center">
  <img src="plugins/nulnul-harness/assets/nulnul-logo-green.svg" width="320" alt="NULNUL logo">
</p>

<p align="center">
  <strong>Start small. Let the harness grow with the project.</strong><br>
  NULNUL gives Codex and Claude Code only the setup your project needs now, then expands it only when real work proves the next need. Every change stays verifiable, bounded, and reversible.
</p>

<p align="center">
  <a href="https://github.com/SeoNaRu/nulnul-harness/actions/workflows/test.yml"><img src="https://github.com/SeoNaRu/nulnul-harness/actions/workflows/test.yml/badge.svg" alt="CI"></a>
  <img src="https://img.shields.io/badge/version-2.1.1-111111" alt="version 2.1.1">
  <a href="evals/results.json"><img src="https://img.shields.io/badge/Release_Gate-100%2F100-111111" alt="known behavior and safety score: 100/100"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-111111" alt="MIT license"></a>
</p>

<p align="center">
  <strong>English</strong> · <a href="README.ko.md">한국어</a>
</p>

<p align="center">
  <a href="#quick-start">Try it</a> · <a href="https://github.com/SeoNaRu/nulnul-harness/releases/tag/v2.1.1">2.1.1</a> · <a href="https://github.com/SeoNaRu/nulnul-harness/issues/new?template=bug_report.yml">Report friction</a>
</p>

> **NULNUL 2.1.1 makes the required documentation-debt check lazy.** On this tracked release repository, the same result moved from a 17.73645-second median to 0.2308 seconds across four counterbalanced A/B rounds.
>
> **2.1 keeps evolution context bounded.** Closed history moves to an integrity-checked local archive instead of loading into ordinary resume context.
>
> **1.7 status:** The first scoped adaptation passed two transfer shapes, skipped incompatible and revoked cases, and was reused from an approved opt-in home with no raw project memory. A fresh GitHub-marketplace Claude Code adoption also preserved two existing agents, made zero protected writes, and passed five executable checks.
>
> **2.0 status:** Three independent personal adaptation families feed a bounded summary selector. It preserved every sealed decision while reducing full compatibility checks from 9 to 4; the exact public Project M smoke reduced them from 3 to 1 with the same correct apply.
>
> **2.0.1 behavior:** In sequential Codex/Claude Code use, Codex owns only `AGENTS.md`, Claude owns only `CLAUDE.md`, and both reuse one shared `docs/nulnul/` state. Concurrent mutation is not claimed.
>
> **2.1 behavior:** The active evolution state retains open work and current rollback points. Full closed evidence remains recoverable and queryable in a digest-bound archive.

## What is NULNUL?

NULNUL is an adaptive, repository-local harness for Codex and Claude Code. It keeps the AI working environment aligned with the project instead of asking you to design the final agent structure on day one.

For a new project, it starts with the smallest useful contract. For an existing project, it reads the current setup first and preserves what already works. As the project gains real requirements—longer sessions, new checks, distinct responsibilities, permission boundaries, or repeated failures—the harness can add the smallest missing mechanism and verify it before keeping it.

You describe the result. NULNUL then:

```text
reads the repository
        ↓
reuses working setup and tools
        ↓
adds only what is missing
        ↓
does the requested work
        ↓
runs the repository's real checks
        ↓
leaves verified state for the next stage
```

Here, “harness” means the small set of project rules, capabilities, state, and checks that help a coding agent work reliably. It does not mean “create an agent team.” Sometimes the correct result is **zero new agents, zero new skills, and zero new infrastructure**.

## A harness that grows with the project

NULNUL does not install a large framework in anticipation of future complexity. On each user-triggered run, it compares the current project with the current harness.

```text
project changes
      ↓
new job, boundary, or reproduced failure
      ↓
is the current harness still enough?
    ↙                         ↘
  yes                         no
keep it              propose the smallest change
                                  ↓
                         independent verification
                            ↙             ↘
                         reject       keep / roll back
```

Growth is driven by demonstrated work, not project size labels or a target agent count.

| Project signal | Smallest justified harness response |
| --- | --- |
| A small repository with one clear check | Reuse the existing guidance and check; add no role. |
| Work now spans sessions | Add one concise verified checkpoint instead of retaining the whole conversation. |
| Governed evolution history keeps growing | Keep open work and latest rollback points active; move closed evidence to a digest-bound archive that is queried only when relevant. |
| A responsibility needs independent ownership | Split that boundary; do not generate a team around it. |
| A repeated workflow gains state or external writes | Add identity, deduplication, review state, and permission controls only where needed. |
| A failure becomes reproducible | Register one causal candidate, compare it with the current way, and keep it only if the Gate passes. |
| A role or mechanism loses its job | Merge or remove it. Harness growth is not append-only. |

Public 1.7.0 added the opt-in personal path. Version 2.0.0 builds on it: NULNUL does not reconsider every method from scratch. It uses privacy-safe evidence to narrow which verified adaptations are worth checking for the current project, then applies only those that pass compatibility. Past success alone never forces application, and unresolved conflicts stop automatic selection. The selection procedure itself is promoted only after downstream results improve through an independent Meta Gate.

## The operational problem

AI-assisted development often creates a second project: managing the AI environment itself.

- You repeat the same project explanation in every session.
- You keep adding recommended plugins, agents, and rules until the setup is harder to understand than the code.
- You have to learn context and token management before making the thing you wanted to make.
- The agent says the task is done, but the real tests were never run.
- A failed approach quietly returns in a later session.
- Every repository gets a new harness assembled from scratch.
- You spend more time choosing AI tools than working on the product.

NULNUL moves that work into an inspectable repository contract. It inspects before it asks, reuses before it creates, keeps durable state bounded, and treats an executable check—not a confident answer—as completion.

## Controlled evolution: proposal is not approval

NULNUL can change its project harness, but it cannot approve its own change.

```text
reproduced failure
        ↓
improvement candidate
        ↓
current way vs candidate
        ↓
Independent Gate
     ↙        ↘
  Reject      Accept
                 ↓
          live observation
             ↙       ↘
           Keep    Rollback
```

The process that proposes a change is separate from the process that assigns credit. A Coach may state a causal hypothesis, prediction, and falsification condition; none of those is evidence by itself. The Gate owns deterministic measurement across completion checks, validators, permission and privacy guardrails, cost, candidate identity, and rollback viability.

In bounded evolution, the candidate count, generation count, evaluation budget, permissions, and stop conditions are fixed before search begins. If nothing is better, **`NO_PROMOTION` is a correct result**.

For personal reuse, project approval is still not enough. A generalized candidate must pass representative transfer checks and a separate Personal Gate. A new project then checks compatibility and may apply, narrow, or skip it. This is user-triggered, bounded improvement—not continuous self-learning, an unattended loop, or open-ended self-improvement.

## When it fits — and when it does not

**Good fit:**

- a small project expected to gain features, checks, or workflows over time;
- a new project that should begin with a minimal AI working contract rather than a prebuilt agent team;
- an existing project whose current rules and tools should be preserved and upgraded in place;
- development that spans sessions and must resume from verified repository state;
- work where tests, permissions, independent review, or rollback become more important as the project grows;
- recurring workflows or reproducible failures that should lead to measured, project-scoped improvement;
- projects that want the harness to add, merge, or remove structure according to demonstrated jobs.

**Probably unnecessary:**

- a read-only question or a tiny one-off edit;
- a simple task whose clear, stable contract and runnable completion check already cover everything needed;
- an always-on workflow engine or hosted orchestration service;
- a system that should authenticate, deploy, publish, or write externally without approval;
- a tool intended to improve the underlying model's reasoning ability;
- raw personal memory, automatic global rules, or unapproved learning across unrelated projects—the 1.7 release stores only scoped verified adaptations in a user-selected local home.

If the repository already has everything the task needs, you may not need NULNUL at all.

## Quick start

Install for Codex:

```bash
codex plugin marketplace add SeoNaRu/nulnul-harness --ref main
codex plugin add nulnul-harness@nulnul-harness
```

Or install for Claude Code:

```bash
claude plugin marketplace add SeoNaRu/nulnul-harness
claude plugin install nulnul-harness@nulnul-harness
```

Start a fresh session and try the smallest prompt:

```text
Set up the harness for this repository. Reuse what already works and add only what is missing.
```

Or ask for the actual work immediately:

```text
Fix the booking API and verify that the existing behavior still passes.
```

You do not need to choose the agents or design the workflow first.

If anything feels uncomfortable in use, report the normal request, expected result, and actual result in an [Issue](https://github.com/SeoNaRu/nulnul-harness/issues/new?template=bug_report.yml). Do not include private code, credentials, or raw transcripts.

## Operational use cases

These prompts exercise the same contracts used by the published evaluation cases.

### Existing backend project

```text
Update the Spring booking API to reject overlapping reservations.
Inspect the current project setup first, reuse what already works,
and run the existing regression checks before calling it done.
```

### New project

```text
I want to build a local-first expense tracker.
Set up the smallest useful development harness, explain any permission
boundary, build the first working slice, and leave one runnable check.
```

### Long-running development

```text
Continue this project across sessions without reconstructing progress from chat.
Use a concise verified checkpoint and refuse fast resume if the checked files changed.
```

### Repeated workflow

```text
Build a workflow that finds finance YouTube creators, removes duplicates,
routes uncertain results to review, and keeps Google Sheets writes behind approval.
```

### Existing messy AI setup

```text
Inspect the current agents, skills, plugins, and project rules.
Keep or reuse what has a real job, identify overlap, and add nothing
unless the current task proves a gap.
```

### Repeated failure

```text
This failure has happened more than once. Reproduce it, check previously
rejected directions, run one bounded improvement episode, and keep the
current harness if no candidate wins on deterministic evidence.
```

### Reuse a verified method in another project (1.7)

```text
If this project produces a method worth reusing elsewhere, generalize only the
mechanism, run representative transfer and negative-skip checks, and ask before
writing it to a personal evolution home. In a new project, apply it only after
a compatibility check.
```

## What NULNUL actually does

Without a harness, the user often has to choose capabilities, write project rules, manage context, design completion checks, preserve session state, and remember which fixes failed.

With NULNUL, the user can ask for the result. The plugin then:

1. detects Codex or Claude Code and reads the repository before asking questions;
2. inventories the existing setup and searches proven capabilities before creating a local substitute;
3. keeps, upgrades, merges, or removes overlap instead of rebuilding the roster;
4. adds only uncovered work or independent verification boundaries;
5. continues the original task—setup alone is not completion;
6. runs an exact repository command and records bounded, sanitized evidence;
7. leaves verified state for later sessions when the project is durable;
8. turns reproducible nonpass results into bounded improvement proposals.
9. when explicitly opted in, can discover a Personal-Gate-approved adaptation, check it against the new project, and apply or skip it without copying the source project.
10. when at least three independent verified families exist, can shortlist relevant adaptations from bounded summaries before opening their full compatibility checks.

Navigator, Worker, Coach, and Gate are responsibility boundaries, not four mandatory agents. Simple work combines roles. A separate role exists only when it has a distinct job, such as independent verification.

The same inspection happens again as the project changes. A new job may justify a new boundary; disappearing overlap may justify a merge or removal. NULNUL adapts the harness topology instead of treating growth as a one-way accumulation of agents and files.

## Engineering model

NULNUL is deliberately skills-only. It adds no server, daemon, hosted control plane, or background self-improvement process. Reliability comes from a small set of repository-native contracts:

| Contract | Enforcement |
| --- | --- |
| Repository truth | Host surface, existing guidance, capabilities, agents, tests, and permissions are inspected before assembly. |
| Adaptive topology | Roles and mechanisms are added, merged, or removed only when a distinct project job and its check justify the change. |
| Verified continuity | Schema-v3 checkpoints use an exact completion command, bounded verification files, and a runner-owned freshness receipt. Mutated state cannot claim verified fast resume. |
| Governed evolution | Schema-v4 episodes freeze pathology, candidate/generation/evaluation budgets, permission delta, archive identity, deterministic credit ownership, and a stop reason before promotion. |
| Evaluation exposure | DEV, VALIDATION, HOLDOUT, first exposure, retirement, and mechanism identity are machine-readable. A used holdout cannot be relabeled unseen. |
| Personal adaptation | A user-selected local registry stores generalized mechanisms, activation conditions, contraindications, transfer summaries, provenance, permissions, and revocation state. Missing home, conflicts, private data, stale status, and false activation fail closed. |
| Cross-project selection | Typed privacy-safe summaries retain activation boundaries, failed transfers, status, permissions, and evidence-backed relations. Unknown relations stay `UNKNOWN`; raw project workloads never enter the aggregate. |
| Release integrity | Exact plugin provenance and version, protected writes, agent hashes, validators, negative controls, archive/source parity, and documentation debt fail closed. |
| Evidence hygiene | Stored artifacts exclude prompts, responses, raw transcripts, credentials, private project data, complete commands, and machine paths. |

These are executable contracts rather than architecture labels. Their validators and negative controls ship in the repository.

## How it differs from nearby categories

These categories can coexist. The distinction is about the default job, not a claim that one tool replaces every other tool.

| Category | Typical job | NULNUL's default |
| --- | --- | --- |
| Agent-team generator | Create a coordinated set of agents | Create no role unless an independent job requires it. |
| Prompt or rule bundle | Load a prepared set of instructions | Start from current repository state and executable checks. |
| Memory layer | Retain conversation or context | Prefer concise verified repository state; do not store raw conversations. |
| Hosted orchestrator | Run long-lived workflows on a service | Stay project-local and skills-only; no server or daemon is required. |
| NULNUL | Project-aligned harness, work execution, verification, and gated improvement | Start minimal, adapt only to demonstrated jobs, and promote only measured improvements. |

## What lands in the repository

Possibly nothing. A coherent existing setup is reused as-is. When durable support is genuinely missing, the footprint can look like this:

```text
your-project/
├── AGENTS.md or CLAUDE.md     # merged host guidance, only when needed
├── docs/nulnul/
│   ├── project.md             # stable goal, check, decisions, permissions
│   ├── checkpoint.json        # concise verified multi-session state
│   ├── evolution.json         # bounded active improvement state, when needed
│   └── evolution.archive.json # closed evidence, outside normal resume context
├── .agents/skills/<name>/     # only when no adequate capability exists
└── docs/nulnul/workflows/<name>.md
                                # reusable workflow, when justified
```

Ordinary continuity uses `checkpoint.json`; governed evolution uses `evolution.json`, never both as live writers. Generated setup remains removable without changing product code.

Closed feedback, proposals, promotions, and autonomous episodes are not summarized away. The standard-library compactor keeps the active state small, binds the adjacent archive by digest, reconstructs the full graph for deterministic validation, and supports targeted rejected-history lookup without loading the archive into every model turn.

## How NULNUL is validated

Research citations are background. The trust model is executable evidence:

```text
behavior check → negative controls → candidate comparison → Independent Gate
                                                        ↓
                                              live cycle / rollback

transfer claim only → sealed unseen check → scoped decision
```

Some of the strongest evidence came from failures:

- **Stale checkpoint defect.** An unverified repository mutation was accepted for fast resume in 3/3 interrupted runs. A runner-owned freshness receipt reduced that unsafe result to 0/3.
- **Plausible candidates rejected.** Navigator instruction changes sounded reasonable but still missed verification or increased reads and cost, so they were not promoted.
- **Invalid holdout preserved.** A Ruby fixture error consumed the first one-shot case. It was downgraded to validation, never renamed unseen, and replaced with a new case.
- **Scoped generalization.** Checkpoint freshness survived one unseen local Perl/TAP project shape. The decision was **Narrower Scope**, not “the harness generalizes.”
- **Live bounded evolution.** Two unchanged champion checks each found seven stale public-positioning surfaces. A newly generated one-generation candidate reached zero, passed the independent Gate, and stopped on `SUCCESS`. This establishes that behavior only for that activation-metadata failure family.
- **Personal transfer candidate.** The accepted checkpoint-freshness mechanism passed fresh Node and Make project shapes, skipped a one-shot shape, and was discovered and verified in a fresh data-CLI Project D. The Gate decision was `PERSONAL_PROMOTION` for the explicit durable-checkpoint conditions only; it does not establish a general personal-memory system.
- **Cross-project Meta Evolution.** Transactional local migration and machine-linked nonpass verdicts passed the same Personal Gate lifecycle, creating three independent families. A frozen one-generation selector then matched flat lookup on fresh Project X, no-match, and conflict decisions while reducing full compatibility checks from 9 to 4. The independent Meta Gate promoted it, and a later live cycle passed with zero rollback triggers.
- **Field failures became rules.** One workflow lost 12,000 decisions to concurrent writers, and an empty-cycle cursor repeatedly rescanned the same 120 items. Those incidents produced single-writer and cursor-persistence rules; they are not universal benchmarks.

| Evidence | Current result | What it means |
| --- | --- | --- |
| Repository tests | **219 passed (219/219)** | Deterministic product, state, compaction, host switching, privacy, rollback, transfer, cross-project, Meta Gate, documentation-debt A/B, and negative-control contracts hold. |
| Known behavior/safety score | **100/100** across 12 cases | Published fixtures pass; this is not a universal quality score. |
| Final 1.7.0 Release Gate | **Passed** | Fresh exact-tag Claude Code and personal-adaptation adoption passed, followed by green main CI run `31651306556`. |
| Checkpoint defect | Unsafe fast resume **3/3 → 0/3** | One reproduced correctness defect was closed. |
| Unseen transfer | **Narrower Scope** | One mechanism transferred to one project shape; harness-wide generalization is not established. |
| Bounded evolution | Champion/retry **7 violations**, new candidate **0**, stop `SUCCESS` | Live generation and bounded stopping worked once in a narrow failure family. |
| Personal transfer candidate | **2 apply, 1 skip, fresh Project D pass** | One adaptation can be transferred, compatibility-checked, reused, deduplicated, and revoked without raw project data; broader personal evolution is not established. |
| 2.0 local Meta Gate | **3 families, 9 → 4 full checks, 3/3 decisions correct** | Bounded summary evidence improved selection work in one sealed episode; token, runtime, universal, and cross-user gains are not established. |
| 2.1 release status | **Released and verified** | Exact public 2.1.0 Claude adoption passed five checks with protected writes 0; the active evolution fixture shrank **87.48%**, and exact Project M kept the correct apply with full checks **3 → 1**. Generalization remains narrower scope. |
| 2.1.1 release status | **Released and verified** | Four counterbalanced rounds preserved the same debt result and reduced median detector time **17.73645 s → 0.2308 s (−98.70%)**. Fresh exact-final Claude and Meta adoption passed, and Release Gate closed at **100/100**. |

Improvement does not have to win. Rejection, `NO_PROMOTION`, narrower scope, and rollback are normal outcomes.

Reproduce the repository checks:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/release_gate.py
```

The current public 2.1.1 evidence reports `release_ready: true`; [main CI run 31772275214](https://github.com/SeoNaRu/nulnul-harness/actions/runs/31772275214) passed, and the downloaded archive SHA-256 is `dc7718ea2f7894a411ee2e179fb015d10621e5d684d9e6f228e298a3ed131b03`.

The records are public: [behavior cases](evals/cases.json), [behavior results](evals/results.json), [performance evidence](evals/benchmarks/performance.json), [activation evidence](evals/benchmarks/activation/results.json), [documentation-debt A/B](evals/benchmarks/doc-debt/results.json), [rejected context-routing A/B](evals/benchmarks/context-routing/results.json), [generalization exposure](evals/generalization/manifest.json), [failed Ruby evidence](evals/generalization/results-ruby-failed.json), [Perl/TAP evidence](evals/generalization/results.json), the [live 1.6 preregistration](evals/autonomous/live-1.6-preregistration.json), the 1.7 [personal transfer preregistration](evals/personal-evolution/preregistration.json) and [results](evals/personal-evolution/results.json), the 2.0 [meta preregistration](evals/meta-evolution/preregistration.json), [typed evidence](evals/meta-evolution/cross-project-evidence.json), [Meta Gate result](evals/meta-evolution/results.json), and exact-public [Meta adoption evidence](evals/meta-evolution/public-adoption.json), plus post-2.0 [capability-authority `NO_ADVANTAGE`](evals/capability-authority/results.json), [intent/better-path `NO_PROMOTION`](evals/intent-better-path/results.json), [scoped decision artifact `NO_PROMOTION`](evals/decision-boundaries/results.json), and [repository receipt `NO_PROMOTION`](evals/repository-receipts/results.json) results. Version history belongs in the [`CHANGELOG.md`](CHANGELOG.md).

## Who I built NULNUL for

NULNUL is for people who want to build something with AI without first becoming experts in AI coding infrastructure. That includes non-developers, people starting development, and experienced developers who do not want to keep tuning skills, plugins, agent layouts, context, and stacks before every project.

It looks for useful existing skills and tools, and respects what already works in a project. But reuse should not trap someone in the first available method. The user owns the intended outcome and deliberate direction; NULNUL should examine the implementation means and explain important choices briefly.

**NULNUL looks for better tools, but does not choose what the user should want.**

This is product philosophy, not a guarantee that the current release resolves every design or architecture decision correctly. The verified behavior above and the linked accepted and rejected evidence define what NULNUL currently proves.

## Roots and influences

NULNUL started from the harness-engineering question raised in [GeekNews Weekly 353](https://news.hada.io/weekly/202615): as coding-agent capabilities multiply, why must every user keep assembling the surrounding system by hand?

Its design was influenced by editable task/meta boundaries, independent verification, champion/challenger comparison, and eval-gated delivery. [HyperAgents](https://ai.meta.com/research/publications/hyperagents/) ([paper](https://arxiv.org/abs/2603.19461), [code](https://github.com/facebookresearch/Hyperagents)) was an important reference for the editable task/meta question. NULNUL does not reproduce HyperAgents or claim open-ended self-improvement.

<details>
<summary>Technical references behind the measured evolution work</summary>

Observable Evolution was informed by [Agentic Harness Engineering](https://arxiv.org/abs/2604.25850), and Generalization Gate by [Rethinking the Evaluation of Harness Evolution](https://arxiv.org/abs/2607.12227). The bounded 1.6 episodes use selected ideas from [Gated Semantic Quality-Diversity](https://arxiv.org/abs/2607.13683), [Hierarchical Self-Improvement](https://arxiv.org/abs/2608.08466), and [Harness Updating Is Not Harness Benefit](https://arxiv.org/abs/2605.30621).

Papers provide questions and stronger falsification methods. They do not become product capabilities without local evidence. Detailed contracts live in the [evolution](plugins/nulnul-harness/skills/nulnul-harness/references/evolution.md), [meta-evolution](plugins/nulnul-harness/skills/nulnul-harness/references/meta-evolution.md), and [generalization](plugins/nulnul-harness/skills/nulnul-harness/references/generalization.md) references.
</details>

## Roadmap to 2.0

The roadmap describes user value, not an automatic release promise.

| Stage | Status | What gets better for the user |
| --- | --- | --- |
| 1.4 Observable Evolution | Completed | See why the harness failed instead of trusting a plausible explanation. |
| 1.5 Generalization Gate | Completed | Check whether a fix transfers or merely fits familiar evaluation cases. |
| 1.6 Bounded Autonomous Evolution | Completed | Let the harness search a tiny candidate space under fixed budgets and stop without changing anything when evidence is weak. |
| 1.7 Personal Evolution | Completed | Reuse a project-proven improvement elsewhere only after transfer evidence, a Personal Gate, and a new-project compatibility check. Exact public adoption and main CI passed. |
| 2.0 Cross-project / Meta Evolution | Released and verified | Three verified families feed a bounded selector. The sealed Meta Gate reduced full checks from 9 to 4 with identical decisions; exact public adoption passed with Project M at 3 to 1, no-match/conflict controls, and rollback. |

## Trust boundaries and limitations

- Authentication, external writes, deployment, publication, destructive operations, paid resources, and global registration require explicit approval.
- Credentials, raw conversations, transcripts, complete command histories, machine paths, and private project data do not become evolution memory.
- Personal Evolution requires an explicitly selected existing local directory. One real private local home is configured and validates; its machine path is deliberately absent from public evidence.
- Unattended Claude Code sessions may inspect host-owned `.claude/**` configuration but do not rewrite it.
- Checkpoints are compared with bounded repository reality before fast resume.
- Compacted evolution archives remain local project evidence and are integrity-checked before the active state is trusted; they are not loaded into ordinary resume context.
- Independent Gate ownership is validated from declared state; it is not cryptographic proof of separate runtime identities.
- NULNUL does not remove the underlying model's reasoning limits or prevent every agent error.
- One unseen transfer and one live bounded episode do not establish universal or harness-wide generalization.
- The 2.0 local evidence covers three mechanism families, three sealed selector cases, one confirmed `COMPLEMENTS` relation, and one live cycle. Other relations remain `UNKNOWN`; arbitrary project lessons, token/runtime gains, and cross-user learning are not established.
- There is no daemon, recursive Coach, candidate population, hosted evolution service, or unattended infinite loop.

## FAQ

<details>
<summary>Will NULNUL always add agents or files?</summary>

No. It first checks whether the repository already covers the job. Reusing the current setup and creating nothing is a successful result.
</details>

<details>
<summary>Does NULNUL continuously learn by itself?</summary>

No. Improvement is user-triggered, bounded, evidence-gated, and reversible. If no candidate wins, the current champion stays in place.
</details>

<details>
<summary>Does the harness grow automatically as the repository gets bigger?</summary>

Not from size alone, and not in the background. On a user-triggered task, NULNUL inspects the current repository and changes the harness only when a new job, boundary, or reproduced failure justifies it. Growth may mean adding one mechanism, merging overlap, removing an obsolete role, or changing nothing.
</details>

<details>
<summary>Can I use it with an existing AI setup?</summary>

Yes. NULNUL inspects and classifies the current setup before adding anything. It is designed to upgrade or reuse an existing roster, not replace it blindly.
</details>

<details>
<summary>Is the 100/100 score proof that NULNUL is better everywhere?</summary>

No. It covers known behavior and safety fixtures. Generalization Gate limits transfer claims separately; one accepted mechanism transferred on one unseen project shape, which is not harness-wide generalization.
</details>

## Update, remove, and develop

Codex refreshes its Git marketplace and reinstalls the plugin:

```bash
codex plugin marketplace upgrade nulnul-harness
codex plugin remove nulnul-harness@nulnul-harness
codex plugin add nulnul-harness@nulnul-harness
```

Claude Code updates the marketplace and plugin, then requires a restart:

```bash
claude plugin marketplace update nulnul-harness
claude plugin update nulnul-harness@nulnul-harness
```

If the marketplace came from a local clone, pull that clone first. Start a fresh agent session after either update. Project-local guidance and `docs/nulnul/` state are preserved.

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

Generated project state is separate; remove it only when you no longer need its checkpoint or evolution history.

Develop and verify locally:

```bash
python3 -m unittest discover -s tests -p 'test_product_plugin.py' -v
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/release_gate.py
```

See [`CHANGELOG.md`](CHANGELOG.md), [`SUPPORT.md`](SUPPORT.md), [`PRIVACY.md`](PRIVACY.md), [`TERMS.md`](TERMS.md), and the [MIT license](LICENSE).

MIT © [SeoNaRu](https://github.com/SeoNaRu)
