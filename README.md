<p align="center">
  <img src="plugins/nulnul-harness/assets/nulnul-logo-green.svg" width="320" alt="NULNUL logo">
</p>

<p align="center">
  <strong>Tell it the outcome. NULNUL builds only the harness your project needs, does the work, and verifies the result.</strong><br>
  For developers who want reliable Codex and Claude Code workflows without designing an AI org chart first.<br>
  <em>Verified capabilities. Personal agents. Controlled evolution.</em>
</p>

<p align="center">
  <a href="https://github.com/SeoNaRu/nulnul-harness/actions/workflows/test.yml"><img src="https://github.com/SeoNaRu/nulnul-harness/actions/workflows/test.yml/badge.svg" alt="CI"></a>
  <img src="https://img.shields.io/badge/version-1.6.0-111111" alt="version 1.6.0">
  <a href="evals/results.json"><img src="https://img.shields.io/badge/Release_Gate-100%2F100-111111" alt="Release Gate: 100/100"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-111111" alt="MIT license"></a>
</p>

<p align="center">
  <strong>English</strong> · <a href="README.ko.md">한국어</a>
</p>

## What is NULNUL?

NULNUL is a skills-only plugin for Codex and Claude Code. You describe the result you want; it inspects the repository, reuses suitable skills, plugins, agents, and project conventions, fills only the missing gaps, continues the original task, and runs the repository's real checks.

If work spans sessions, it leaves a small verified checkpoint instead of asking the next session to reconstruct everything from chat. If a failure is reproducible, NULNUL can check already rejected directions, propose a tiny one-generation candidate set within a frozen budget, and let an independent Gate accept, reject, or keep the current champion. No improvement means no promotion.

Sometimes the correct result is **zero new agents, zero new skills, and zero new infrastructure**.

## Why use it?

NULNUL is for the work around the coding agent that keeps becoming your work:

- **You repeat the same project explanation every session.** NULNUL resumes from bounded repository state whose verification still matches the files.
- **Every repository grows another pile of agent rules and tools.** NULNUL inventories what already exists and adds only uncovered jobs.
- **The agent says “done,” but nobody ran the real check.** Completion is an executable repository command, not a confidence statement.
- **You have to choose the agents, skills, plugins, and context layout yourself.** NULNUL starts from the outcome and makes those decisions from repository evidence.
- **A plausible fix fails, then quietly returns later.** Accepted, rejected, and rolled-back candidates keep their reasons so the same weak direction is not rediscovered inside the project.

## When it fits — and when it does not

**Good fit:**

- development that spans multiple sessions;
- recurring workflows with state, deduplication, permissions, or review queues;
- repositories with several possible skills, plugins, tools, or agent roles;
- work where tests, validators, delivery checks, or rollback matter;
- projects whose agent setup is growing faster than its demonstrated jobs;
- project-scoped improvement from reproducible failures.

**Probably not needed:**

- a read-only question or a tiny one-off edit;
- a task that already has explicit inputs, outputs, constraints, and a runnable completion check;
- a background workflow engine, hosted control plane, or always-on daemon;
- a system that should authenticate, publish, deploy, or write externally without approval;
- a way to overcome the underlying model's reasoning limits;
- personal memory or automatic learning across unrelated projects—those are not current capabilities.

If the existing project contract already covers the job, you do not need NULNUL for that task.

## Quick start

Install for Codex:

```bash
codex plugin marketplace add SeoNaRu/nulnul-harness --ref main
codex plugin add nulnul-harness@nulnul-harness
```

Or for Claude Code:

```bash
claude plugin marketplace add SeoNaRu/nulnul-harness
claude plugin install nulnul-harness@nulnul-harness
```

Start a fresh session and ask for the outcome, not the agent structure:

```text
Set up the harness for this repository, fix the booking API,
and verify that the existing behavior still passes.
```

Or start from a recurring workflow:

```text
Build a workflow that finds finance YouTube creators, removes duplicates,
and sends reviewed results to Google Sheets safely.
```

The same skill supports both hosts. It detects the active surface, inspects the current setup before asking questions, and preserves explicit approval boundaries. In unattended Claude Code work, `.claude/**` is read-only; removable project state lives in repository-owned guidance and `docs/nulnul/`.

## See it work

The public [YouTube → Google Sheets example](examples/youtube-sheets) starts from a normal request rather than an agent diagram. NULNUL's job is to:

1. inspect the repository and installed capabilities;
2. reuse adequate discovery and spreadsheet behavior;
3. add only the missing classification, deduplication, and review flow;
4. keep Google authentication and Sheet writes behind explicit approval;
5. run the offline completion checks;
6. leave verified state for the next session when the work is durable.

The fixture is synthetic and stores no production identity or contact data. Its [offline benchmark](evals/benchmarks/youtube-sheets) checks classification, channel-ID deduplication, exclusion precedence, reviewer feedback, formula escaping, safe upserts, and run metrics. It is one task example, not a universal performance claim.

## How it works

```text
Inspect → Reuse → Fill the gaps → Do the work → Verify → Resume / Improve
```

NULNUL follows six preferences:

- **Reuse before creation.** Search installed, official, curated, and reputable capabilities before making a local substitute.
- **Smallest useful system.** Direct or single-agent execution is the default; a new role needs a real independent job.
- **Repository truth over chat memory.** Contracts, files, state, and executable checks outrank a previous session's prose.
- **Verification over confidence.** A passing command and bounded evidence matter more than an agent saying it is finished.
- **Evidence before infrastructure.** Memory, benchmarks, locks, agents, hooks, MCP, and services need a measured job first.
- **Improvement without self-approval.** A Coach may propose a change, but its author and target cannot serve as the independent Gate.

The always-on [Baseline Kernel](plugins/nulnul-harness/skills/nulnul-harness/references/baseline-kernel.md) is deliberately small: repository truth, the original outcome, one runnable check, a before state, inspected capability decisions, permission boundaries, and gated improvement with rollback.

Navigator, Worker, Coach, and Gate are responsibility boundaries, not four mandatory agents. Simple work combines roles. Separation becomes mandatory only where independent verification is the actual job.

### What makes it different

- It is **not an agent-team generator**: adding no role is often the best result.
- It is **not a prompt bundle**: it uses repository state and executable checks.
- It is **not a memory product**: it does not store raw conversations or private workloads.
- It is **not a hosted orchestration platform**: the plugin needs no server, daemon, hook, app, or MCP service.
- It is **not an autonomous deployment system**: credentials, external writes, publication, deployment, and global registration remain approval boundaries.

## What lands in your repository

Possibly nothing. A coherent setup is reused as-is. When durable support is genuinely missing, the footprint can look like this:

```text
your-project/
├── AGENTS.md or CLAUDE.md     # merged host-loaded guidance when needed
├── docs/nulnul/
│   ├── project.md             # stable goal, check, decisions, permissions, rollback
│   ├── checkpoint.json        # concise ordinary multi-session state
│   └── evolution.json         # governed history; replaces checkpoint when needed
├── .agents/skills/<name>/     # only when no adequate capability already exists
└── docs/nulnul/workflows/<name>.md
                                # reusable unattended workflow when needed
```

There is one continuity writer: ordinary work uses `checkpoint.json`; governed evolution uses `evolution.json`, never both. Legacy state starts `unknown` and must rerun its exact check before fast resume. Generated state and local skills can be removed without touching product code.

## How NULNUL is validated

Research links are not the trust model. The trust model is executable evidence:

```text
behavior check → negative controls → candidate comparison → independent Gate
                                                        ↓
                                              live cycle / rollback

transfer claim only → sealed unseen check → scoped decision
```

Four examples show the difference between a plausible story and measured behavior:

- **Stale verified checkpoint.** A repository mutation remained fast-resumable in 3/3 interrupted runs. Runner-owned freshness receipts reduced that reproduced unsafe outcome to 0/3.
- **Plausible instructions rejected.** Two Navigator wording/order candidates sounded reasonable but still missed verification or increased reads and cost, so they were not promoted.
- **Scoped transfer, not a victory lap.** Checkpoint freshness survived one unseen local Perl/TAP project shape, but the result was recorded as **Narrower Scope**. Harness-wide generalization is not established.
- **Field failures became invariants.** In one full-day workflow, concurrent writers lost 12,000 decisions and an empty-cycle cursor repeatedly scanned the same 120 items. Those failures produced single-writer and cursor-persistence rules; they are field evidence, not universal benchmarks.

| Evidence | Current result | What it tells us |
| --- | --- | --- |
| Repository tests | **110 passed (110/110)** | Deterministic product, state, privacy, rollback, and negative-control contracts still hold. |
| Release Gate | **100/100** across 12 behavior and safety cases | The behavior fixtures and latest published 1.5.0 adoption evidence pass. Exact-version 1.6.0 public adoption is still pending. |
| Checkpoint defect | Unsafe fast resume **3/3 → 0/3** | One reproduced correctness defect was closed by the freshness mechanism. |
| Unseen transfer | **Narrower Scope** | One mechanism transferred to one Perl/TAP shape; the whole harness is not proven to generalize. |
| Live bounded evolution | Champion and retry kept **7 violations**; one new candidate reached **0** and stopped on `SUCCESS` | Live candidate generation and bounded stopping worked for one activation-metadata failure family. Public v1.6.0 adoption and broader autonomy are not established. |

Reproduce the public checks:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/release_gate.py
```

The underlying records are public: [behavior cases](evals/cases.json), [behavior results](evals/results.json), [performance evidence](evals/benchmarks/performance.json), [activation evidence](evals/benchmarks/activation/results.json), [generalization exposure](evals/generalization/manifest.json), [failed Ruby evidence](evals/generalization/results-ruby-failed.json), the [Perl/TAP result](evals/generalization/results.json), and the [live 1.6 preregistration](evals/autonomous/live-1.6-preregistration.json). Version-by-version detail belongs in the [`CHANGELOG.md`](CHANGELOG.md).

## Why I built NULNUL

When I use coding agents, the model is not always the annoying part. The surrounding setup is. For every project I end up deciding which skills to use, whether another agent is necessary, which rules belong in context, how the next session should continue, and what would actually prove the work is done.

I thought it was strange that the user had to design an AI org chart before asking for a result. I wanted to state the outcome and let the harness absorb the repeated setup and verification work. I also wanted a system whose default was to avoid creating unnecessary agents and infrastructure, not to manufacture more of them.

Sessions should resume from verified repository state rather than vague chat memory. Failed approaches should leave enough evidence that the project is less likely to repeat them. That is why I started NULNUL.

## Roots and influences

NULNUL started from the harness-engineering question raised in [GeekNews Weekly 353](https://news.hada.io/weekly/202615): as agent capabilities multiply, why must every user keep assembling the surrounding system by hand?

Its design was later influenced by editable task/meta boundaries, generator/verifier separation, champion/challenger evaluation, and eval-gated delivery. [HyperAgents](https://ai.meta.com/research/publications/hyperagents/) ([paper](https://arxiv.org/abs/2603.19461), [code](https://github.com/facebookresearch/Hyperagents)) was an important reference for the editable task/meta question. NULNUL does not reproduce HyperAgents or claim open-ended self-improvement.

<details>
<summary>Technical research behind the measured evolution work</summary>

The 1.4 observability work was informed by [Agentic Harness Engineering](https://arxiv.org/abs/2604.25850). The 1.5 evaluation boundary was informed by [Rethinking the Evaluation of Harness Evolution](https://arxiv.org/abs/2607.12227). The bounded 1.6 episodes use selected ideas from [Gated Semantic Quality-Diversity](https://arxiv.org/abs/2607.13683), [Hierarchical Self-Improvement](https://arxiv.org/abs/2608.08466), and [Harness Updating Is Not Harness Benefit](https://arxiv.org/abs/2605.30621).

Papers supply questions, candidate mechanisms, and stronger ways to falsify a claim. They do not become features without local evidence. Detailed contracts live in the [evolution](plugins/nulnul-harness/skills/nulnul-harness/references/evolution.md), [meta-evolution](plugins/nulnul-harness/skills/nulnul-harness/references/meta-evolution.md), and [generalization](plugins/nulnul-harness/skills/nulnul-harness/references/generalization.md) references.
</details>

## Roadmap to 2.0

This repository is a local **1.6.0 release candidate**. Exact-version public adoption evidence still covers 1.5.0, so publication is not yet complete. The roadmap describes user value, not an automatic release promise.

| Stage | Status | User value |
| --- | --- | --- |
| 1.4 Observable Evolution | Completed | See where a harness failed and distinguish evidence from a plausible explanation. |
| 1.5 Generalization Gate | Completed | Separate a fix that transfers from one tuned to familiar fixtures. |
| 1.6 Bounded Autonomous Evolution | Local release candidate; publication pending | Search a tiny candidate space within fixed budgets and stop without promotion when evidence does not support a winner. One new live candidate was generated and gated; exact-version public adoption remains pending. |
| 1.7 Personal Evolution | Next, not started | Carry a project-proven improvement forward only after it survives a small transfer check in another project. |
| 2.0 Cross-project / Meta Evolution | Long-term target | Combine scoped lessons across projects without sharing raw workloads, and improve the improvement procedure itself. |

## Trust boundaries and limitations

- Installed or popular does not mean verified; provenance, compatibility, maintenance, permissions, license, and task fit still matter.
- Authentication, external writes, deployment, publication, destructive actions, paid resources, and global registration require explicit approval.
- Credentials, raw conversations, transcripts, complete command histories, machine paths, and private project data do not become evolution memory.
- Unattended sessions inspect host-owned `.claude/**` configuration but do not rewrite it.
- Checkpoints are rechecked against bounded repository reality before fast resume.
- Independent Gate ownership is validated from declared state; it is not cryptographic proof of two runtime identities.

This does **not** prove that NULNUL improves every project, prevents every agent error, fixes model reasoning limits, generalizes across repositories, or provides hosted-service reliability. The current unseen result covers one mechanism on one project shape. The 1.6 live result covers one activation-metadata failure family; it is not continuous, open-ended, personal, cross-project, or harness-wide autonomous improvement.

## FAQ

<details>
<summary>Will NULNUL always add agents or files?</summary>

No. It first checks whether the repository already covers the job. Reusing the current setup and creating nothing is a successful result.
</details>

<details>
<summary>Does NULNUL continuously learn by itself?</summary>

No. Improvement is user-triggered, bounded, evidence-gated, and reversible. There is no daemon, candidate population, recursive Coach, or unattended infinite loop.
</details>

<details>
<summary>Is Release Gate proof that NULNUL is better everywhere?</summary>

No. It protects published behavior and safety fixtures. Generalization Gate separately limits transfer claims, and harness-wide generalization is not established.
</details>

<details>
<summary>Why is the plugin skills-only?</summary>

No observed workflow currently needs a server, hook, app, or MCP service. Those components would add permissions and maintenance before adding a demonstrated job.
</details>

## Update, remove, and develop

Codex refreshes the Git marketplace and reinstalls because its current plugin CLI has no separate plugin-update command:

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

Remove the plugin:

```bash
codex plugin remove nulnul-harness@nulnul-harness
codex plugin marketplace remove nulnul-harness
```

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

See [`CHANGELOG.md`](CHANGELOG.md), [`SUPPORT.md`](SUPPORT.md), and the [MIT license](LICENSE).

MIT © [SeoNaRu](https://github.com/SeoNaRu)
