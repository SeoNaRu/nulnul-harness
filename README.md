<p align="center">
  <img src="plugins/nulnul-harness/assets/nulnul-logo-green.svg" width="320" alt="NULNUL logo">
</p>

<h1 align="center">NULNUL Harness</h1>

<p align="center">
  <strong>NULNUL is an open-source, repository-local AI development environment for OpenAI Codex and Anthropic Claude Code.</strong><br>
  Before changing the AI setup, it inspects existing <code>AGENTS.md</code> or <code>CLAUDE.md</code> guidance, skills, plugins, agents, and project checks. It keeps what fits, adds only missing support, and uses actual test, build, or validation results as the completion criterion.
</p>

<p align="center">
  <a href="https://github.com/SeoNaRu/nulnul-harness/actions/workflows/test.yml"><img src="https://github.com/SeoNaRu/nulnul-harness/actions/workflows/test.yml/badge.svg" alt="CI"></a>
  <img src="https://img.shields.io/badge/version-2.2.0-111111" alt="version 2.2.0">
  <a href="evals/results.json"><img src="https://img.shields.io/badge/Release_Gate-100%2F100-111111" alt="known behavior and safety score: 100/100"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-111111" alt="MIT license"></a>
</p>

<p align="center">
  <strong>English</strong> · <a href="README.ko.md">한국어</a>
</p>

<p align="center">
  <a href="#quick-start">Quick start</a> · <a href="#read-only-preview">Read-only preview</a> · <a href="https://github.com/SeoNaRu/nulnul-harness/releases/tag/v2.2.0">Current release: v2.2.0</a>
</p>

<p align="center">
  Checks the existing setup first · Adds only what is missing · Uses repository checks as the completion criterion
</p>

> A “harness” is the set of project rules, skills, work state, and executable checks that guide an AI coding agent. NULNUL keeps this setup in the repository; it is not an agent-team generator.

## Before / With NULNUL

| Before | With NULNUL |
| --- | --- |
| Re-explain the project every session | Read the repository and its current setup first |
| Accumulate overlapping skills and agents | Reuse what fits and add only uncovered support |
| Accept “done” without a real check | Run the repository's test, build, or validation command |
| Reconstruct old work from chat | Leave a concise, verified checkpoint when continuity is needed |

If the existing setup is sufficient, NULNUL adds **0 new agents, 0 new skills, and 0 new infrastructure**.

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

After installation, start a new session with this prompt:

```text
Inspect this repository first. Reuse what already works and add only what is
missing. Then continue the work I requested and run the real project checks.
```

You can also ask for the product change directly:

```text
Fix the booking API and verify that the existing behavior still passes.
```

### Read-only preview

See how NULNUL would reason about the setup without writing anything:

```text
Inspect this repository and show the smallest harness changes you would
recommend. Do not modify any files.
```

<a id="what-nulnul-is-for"></a>

## What problem does NULNUL solve?

AI coding agents need project-specific setup: plugins, rules, context, session state, and executable checks. Maintaining that setup by hand can leave overlapping agents and skills, stale work state, and completion claims without test results.

NULNUL records this setup in an inspectable, removable repository contract. It is intended for Codex and Claude Code projects that should preserve working settings and avoid unnecessary additions.

The user sets the product direction. NULNUL finds an implementation and verification path that fits the repository and explains material choices.

## Three common uses

### Add a feature without losing existing behavior

**Situation:** An established project already has rules, code, and regression tests.

**Prompt:**

```text
Update the Spring booking API to reject overlapping reservations.
Inspect the current setup first, reuse what already works, and run the
existing regression checks before calling it done.
```

**What NULNUL checks and leaves:** the current guidance and capabilities, the smallest scoped implementation, and the result of the repository's existing completion check.

### Continue work across sessions

**Situation:** A durable project should resume without replaying the whole conversation.

**Prompt:**

```text
Continue this project across sessions without reconstructing progress from chat.
Use a concise verified checkpoint and refuse fast resume if the checked files changed.
```

**What NULNUL checks and leaves:** one bounded checkpoint, its exact completion command, and a freshness receipt tied to the files that command verifies.

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
Set up the smallest useful development harness, explain any permission
boundary, build the first working slice, and leave one runnable check.
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
reuse working rules and capabilities
        ↓
add only an uncovered job or verification boundary
        ↓
continue the user's original work
        ↓
run the repository's exact completion check
        ↓
leave only the verified state the next session needs
```

In practice, the plugin:

1. detects Codex or Claude Code and reads the applicable `AGENTS.md` or `CLAUDE.md`, project metadata, tests, and run evidence;
2. inventories existing skills, plugins, agents, and tools before judging what is missing;
3. searches installed, official, curated, and reputable public capabilities before creating a project-local substitute;
4. keeps, upgrades, merges, or removes existing roles instead of recreating them;
5. prefers direct or single-agent execution and adds a separate role only for a concrete independent job or verification boundary;
6. continues the original request—setup alone is not completion;
7. runs the exact repository check and records bounded, sanitized evidence;
8. leaves concise verified state when the work must span sessions;
9. turns reproduced failures into bounded proposals, not silently accepted rules; and
10. when explicitly opted in, compatibility-checks verified personal adaptations without copying the source project.

Navigator, Worker, Coach, and Gate are responsibility boundaries, not four mandatory agents. Ordinary work combines them. The proposal author and the independent Gate separate only when a change needs measured promotion.

<a id="comparison-with-other-tool-types"></a>

## How is NULNUL different from other AI coding tools?

The categories below can work together. The difference is the default job, not a claim that NULNUL replaces every other tool.

| Category | Typical starting point | NULNUL's difference |
| --- | --- | --- |
| Agent-team generator | Create a coordinated roster | Creates no role unless an independent job justifies it; existing roles are upgraded in place. |
| Prompt or rule bundle | Load prepared instructions | Starts from the repository's current rules and executable checks. |
| Memory layer | Retain conversation or context | Stores concise verified project state, not raw conversations. |
| Hosted orchestrator | Run long-lived workflows on a service | Stays repository-local and skills-only; no server or daemon is required. |
| Repository template | Apply the same starting structure | Adapts to an existing repository and may add nothing. |
| NULNUL | Inspect, complete, verify, and improve project work | Reuses first, fills only proven gaps, and keeps only independently verified changes. |

<a id="repository-changes"></a>

## What files can NULNUL add to a repository?

If the existing setup is sufficient, NULNUL adds no files. When durable support is missing, it may add the following:

```text
your-project/
├── AGENTS.md or CLAUDE.md     # active host guidance, merged only when needed
├── docs/nulnul/
│   ├── project.md             # stable goal, checks, decisions, permissions
│   ├── checkpoint.json        # concise verified multi-session state
│   ├── evolution.json         # active governed-improvement state, when needed
│   └── evolution.archive.json # closed evidence, outside normal resume context
├── .agents/skills/<name>/     # Codex: only when no adequate capability exists
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
| [Repository test suite](tests/) | **234 passed (234/234)** | Deterministic product, state, host-switching, privacy, rollback, transfer, Meta Gate, documentation-debt, exact-candidate, behavior-boundary, and negative-control contracts pass. |
| [Known behavior and safety](evals/results.json) | **100/100 across 12 cases** | The published fixtures pass. This is not a universal quality score or proof of better results in every repository. |
| [Exact public 2.2.0 adoption](evals/personal-evolution/public-adoption.json) | **5/5 Claude checks; 0 protected writes** | A fresh public install preserved two existing agent profiles and the inactive Codex entry. |
| [Exact public Project M](evals/meta-evolution/public-adoption.json) | **3 → 1 full compatibility checks** | The bounded selector kept the same correct transactional-migration decision and passed no-match, conflict, privacy, permission, migration, and rollback controls. |
| [Release artifact](https://github.com/SeoNaRu/nulnul-harness/releases/tag/v2.2.0) | **Byte-identical; SHA-256 `779bd3d43178925fe53eafa348484d8bf6d0cb1e79fc00a31615b754b71124d0`** | The downloaded v2.2.0 archive matched the frozen local artifact exactly. |

The v2.2.0 evidence records `local_candidate_ready: true` and `release_ready: true`. [Main CI run 32348453221](https://github.com/SeoNaRu/nulnul-harness/actions/runs/32348453221) passed the full suite and Release Gate.

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
- a new project that should start with the smallest useful AI working contract, not a prebuilt team;
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

**v2.2.0**, published on August 20, 2026, is the current public release.

- A schema-v4 provisional-to-confirmed lifecycle keeps the confirmed version active until one observed cycle is healthy, otherwise it records rollback.
- Documentation-debt checks account for the active host and dirty worktree.
- Release evidence is bound to the candidate's exact bytes, not only its version string.
- The annotated release tag points to commit `14806e44bdc5bd2dbc3f2e52cea3b3799442d461`.
- Fresh exact-version Claude Code and Meta Evolution adoption passed without protected writes, permission expansion, private evidence, or retired-holdout reuse.
- The consent/continuity behavior candidate did **not** ship. Its strict Gate returned `NO_PROMOTION`, so Navigator remains v20 and no new consent or ordinary-product routing claim is made.

See the full history in [`CHANGELOG.md`](CHANGELOG.md).

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

- [behavior cases](evals/cases.json) and [behavior results](evals/results.json);
- [performance evidence](evals/benchmarks/performance.json), [activation evidence](evals/benchmarks/activation/results.json), and [documentation-debt A/B](evals/benchmarks/doc-debt/results.json);
- the rejected [context-routing A/B](evals/benchmarks/context-routing/results.json);
- the Generalization Gate [exposure manifest](evals/generalization/manifest.json), [failed Ruby evidence](evals/generalization/results-ruby-failed.json), and [Perl/TAP result](evals/generalization/results.json).

Evolution records:

- the [1.6 live preregistration](evals/autonomous/live-1.6-preregistration.json);
- 1.7 [personal transfer preregistration](evals/personal-evolution/preregistration.json), [results](evals/personal-evolution/results.json), and [public adoption](evals/personal-evolution/public-adoption.json);
- 2.0 [Meta preregistration](evals/meta-evolution/preregistration.json), [typed evidence](evals/meta-evolution/cross-project-evidence.json), [Meta Gate result](evals/meta-evolution/results.json), and [exact-public adoption](evals/meta-evolution/public-adoption.json);
- post-2.0 [capability-authority `NO_ADVANTAGE`](evals/capability-authority/results.json), [intent/better-path `NO_PROMOTION`](evals/intent-better-path/results.json), [decision-artifact `NO_PROMOTION`](evals/decision-boundaries/results.json), and [repository-receipt `NO_PROMOTION`](evals/repository-receipts/results.json);
- 2.2 behavior-boundary [preregistration](evals/behavior-boundaries/preregistration.json), [cases](evals/behavior-boundaries/cases.json), [sanitized rejection result](evals/behavior-boundaries/results.json), and the excluded [invalid first episode](evals/behavior-boundaries/invalid-evaluator-episode-1.json).

The last group records rejected work, not shipped behavior evidence.

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

For release-evidence changes, also run the full `test_*.py` suite and `python3 scripts/release_gate.py`.

Report a bug or setup mismatch in a [GitHub issue](https://github.com/SeoNaRu/nulnul-harness/issues/new?template=bug_report.yml). Include the request, expected result, and observed result—never private code, credentials, or raw transcripts.

See [`SUPPORT.md`](SUPPORT.md), [`PRIVACY.md`](PRIVACY.md), [`TERMS.md`](TERMS.md), and the [MIT license](LICENSE).

## Research background

NULNUL started from the harness-engineering problem described in [GeekNews Weekly 353](https://news.hada.io/weekly/202615): users repeatedly assemble the surrounding system as coding-agent capabilities multiply.

Its design was influenced by editable task/meta boundaries, independent verification, champion/candidate comparison, and eval-gated delivery. [HyperAgents](https://ai.meta.com/research/publications/hyperagents/) ([paper](https://arxiv.org/abs/2603.19461), [code](https://github.com/facebookresearch/Hyperagents)) was an important reference for the editable task/meta question. NULNUL does not reproduce HyperAgents or claim open-ended self-improvement.

<details>
<summary>Technical references behind the measured evolution work</summary>

Observable Evolution was informed by [Agentic Harness Engineering](https://arxiv.org/abs/2604.25850), and Generalization Gate by [Rethinking the Evaluation of Harness Evolution](https://arxiv.org/abs/2607.12227). The bounded 1.6 episodes use selected ideas from [Gated Semantic Quality-Diversity](https://arxiv.org/abs/2607.13683), [Hierarchical Self-Improvement](https://arxiv.org/abs/2608.08466), and [Harness Updating Is Not Harness Benefit](https://arxiv.org/abs/2605.30621).

Research provides questions and stronger falsification methods. It does not become a product capability without local evidence. Exact contracts live in the [evolution](plugins/nulnul-harness/skills/nulnul-harness/references/evolution.md), [meta-evolution](plugins/nulnul-harness/skills/nulnul-harness/references/meta-evolution.md), [personal adaptation](plugins/nulnul-harness/skills/nulnul-harness/references/personal-evolution.md), and [generalization](plugins/nulnul-harness/skills/nulnul-harness/references/generalization.md) references.
</details>

MIT © [SeoNaRu](https://github.com/SeoNaRu)
