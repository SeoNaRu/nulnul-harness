<p align="center">
  <img src="plugins/nulnul-harness/assets/nulnul-logo-green.svg" width="320" alt="NULNUL logo">
</p>

<p align="center">
  <strong>Verified capabilities. Personal agents. Controlled evolution.</strong><br>
  A beginner-friendly Codex and Claude Code plugin that builds the agent team, capabilities, and evolving meta-harness around your project.
</p>

<p align="center">
  <a href="https://github.com/SeoNaRu/nulnul-harness/actions/workflows/test.yml"><img src="https://github.com/SeoNaRu/nulnul-harness/actions/workflows/test.yml/badge.svg" alt="CI"></a>
  <img src="https://img.shields.io/badge/version-1.5.0-111111" alt="version 1.5.0">
  <a href="evals/results.json"><img src="https://img.shields.io/badge/Release_Gate-100%2F100-111111" alt="Release Gate: 100/100"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-111111" alt="MIT license"></a>
</p>

<p align="center">
  <strong>English</strong> · <a href="README.ko.md">한국어</a>
</p>

## Why NULNUL

More tools do not make a better agent system. Unverified skills, overlapping roles, unnecessary servers, and self-declared “learning” create cost and failure points.

`NULNUL` takes the smaller path:

- inspect the repository and its completion checks before changing it;
- find and verify existing capabilities before creating new ones;
- activate only the skills and agents needed for the current job;
- finish the original task instead of stopping at setup;
- resume later sessions from repository evidence, not chat memory;
- turn reproducible feedback into agent upgrades that require an independent Gate;
- improve the Coach's own discovery and improvement procedure when the user had to find a better method.

You describe the result, not the AI architecture. On an existing project NULNUL inspects the repository and upgrades its current setup in place. In an empty project it asks what you want to make, then chooses the smallest useful team. It reuses suitable installed skills and plugins immediately, explains any new installation in plain language, asks once when approval is required, and skips overlapping tools.

## The baseline that is always on

Every setup keeps a seven-part **Baseline Kernel**: repository truth, the original outcome, one runnable completion check, a before state, inspected capability decisions, permission boundaries, and independently gated evolution with rollback. When durable continuity is needed, stable setup evidence stays in `docs/nulnul/project.md` while a concise checkpoint carries the current goal, check, bounded verification files, explicit `verified`/`failed`/`unknown` status, last evidence, next action, permission boundary, and blockers. Fast resume also requires a runner-owned receipt whose fingerprint matches those current files; a stale `verified` label is insufficient.

Heavier infrastructure still stays evidence-driven. Persistent memory appears when work spans sessions; performance tracking when an outcome needs comparison; a dashboard when repeated human decisions need trends; more agents when independent work justifies coordination; staged verification for risky changes; a lock for shared mutable state; MCP only for an uncovered tool or service boundary; and a project-local skill only after adequate existing candidates fail. See [`references/baseline-kernel.md`](plugins/nulnul-harness/skills/nulnul-harness/references/baseline-kernel.md).

## From harness engineering to a meta-harness

NULNUL began with [GeekNews Weekly 353: “In the age of abundant skills, build your own harness”](https://news.hada.io/weekly/202615). Its research foundation is Meta and UBC's [HyperAgents](https://ai.meta.com/research/publications/hyperagents/) ([paper](https://arxiv.org/abs/2603.19461), [code](https://github.com/facebookresearch/Hyperagents)): a task agent and a meta agent live in one editable program, and the meta agent may improve the procedure that produces later improvements.

NULNUL translates that idea into a removable project system for people who should not need to engineer a harness themselves:

| Editable side | NULNUL responsibility |
| --- | --- |
| Task side | Navigator and Worker complete the project with the selected skills and plugins |
| Meta side | Coach finds better capabilities and methods, then edits the task side or its own discovery and improvement rules |
| Independent boundary | Gate compares the candidate, blocks self-approval and permission expansion, and observes the next live run |

This is governed self-improvement during normal project work, not a claim that the plugin reproduces HyperAgents' open-ended research system. The initial conditions and exact meta-evolution contract live in [`references/meta-evolution.md`](plugins/nulnul-harness/skills/nulnul-harness/references/meta-evolution.md).

## How this was built

**The idea.** Most agent setups fail before the model does. The failure is rarely bad reasoning; it is a second process overwriting a state file, a check recorded as passing when it never ran, a counter that means something different in three places. So this project stayed a **skills-only plugin**: no server, no daemon, no background process. Just an execution contract the agent reads, plus templates it can delete afterward.

**The path.** Version 1.x answered the setup question — inspect the repository, verify existing capabilities before making new ones, assemble the smallest working set, run, checkpoint, evolve. That part held up, so it was never rewritten.

**The stress test.** Then a real recurring workflow (finding and reviewing creator leads) ran in an unattended loop for a full day. It broke in eleven ways that none of the references prevented, and none of the eleven were reasoning failures:

- three unattended loops each rewrote the whole state file from memory: **12,000 decisions lost**;
- the collector skipped writing a run record when it found nothing, and the next search window was derived from the last run record — so the window froze and the same 120 items were rescanned all day. After the fix, **1,265 new records in one pass**;
- a link checker skipped a check and the aggregator wrote it as `ok`, so never-verified rows shipped as verified;
- a domain check used `A` records instead of `MX` and froze **15 healthy mailboxes** as dead;
- a filter matched disclaimer text in long bios and rejected **20 valid records**;
- "completed" was counted in three places with three definitions, so the loop declared its target reached and exited on work that was not delivered.

Each failure became a rule with the number that produced it, written into the reference the agent actually loads. See [Field-hardened rules](#field-hardened-rules).

**What that day changed about the design.** The measured gains came from correcting judgment functions that already existed — not from adding agents. NULNUL now checks four jobs before adding an agent: repeated judgement may need a frozen benchmark, counted recurring work one deliverable function, changing source and guidance a documentation-debt hook, and concurrent state one writer plus a lock. It creates only the mechanisms whose jobs exist and lets later evidence add the rest. This is one project over one day, so treat it as field evidence, not a benchmark.

## Quick start

Codex:

```bash
codex plugin marketplace add SeoNaRu/nulnul-harness --ref main
codex plugin add nulnul-harness@nulnul-harness
```

Claude Code:

```bash
claude plugin marketplace add SeoNaRu/nulnul-harness
claude plugin install nulnul-harness@nulnul-harness
```

The same skill drives both surfaces. The harness detects the host and writes only repository-owned setup paths. In unattended Claude Code sessions, `.claude/**` is inspected but never modified; `CLAUDE.md`, `docs/nulnul/`, and the verified checkpoint provide session continuity and reusable local workflows.

Start a new session and describe the outcome. Asking for a harness is enough — you never describe agents, roles, or setup steps:

```text
Build me a harness that finds finance YouTube creators, deduplicates them,
and safely writes reviewed results to Google Sheets.
```

The harness inspects the project, reuses adequate instructions and tests, checks available capabilities, asks only for decisions it cannot safely discover, and continues through implementation and verification. Describing the product without the word "harness" works the same way. It does not activate for simple read-only questions or duplicate a coherent project setup.

## Update

Codex refreshes the Git marketplace, then reinstalls because its current plugin CLI has no separate plugin-update command:

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

If the marketplace was originally added from a local clone, run `git pull origin main` in that clone first and then use the same reinstall or update commands. Start a fresh agent session after either update. Project-local `AGENTS.md`, `CLAUDE.md`, and `docs/nulnul/` state are preserved.

## Product loop

```text
Discover → Verify → Assemble → Run → Checkpoint → Evolve the task or the improvement process
```

| Stage | Durable result |
| --- | --- |
| Discover | Required jobs and existing candidates |
| Verify | Provenance, compatibility, quality, permissions, and license |
| Assemble | The smallest complete capability and agent set |
| Run | The user-visible result and its completion check |
| Checkpoint | Verified state, next action, blockers, and approved permissions |
| Evolve | Task or meta-procedure change, transfer check, live observation, and rollback |

One run, in full:

```text
your request
     │
     ▼
inspect the repository ──▶ coherent setup and completion check already exist? ──yes──▶ reuse, skip setup
     │ no                                                                                     │
     ▼                                                                                        │
map the required jobs ──▶ search installed and existing capabilities                          │
     │                             │                                                          │
     │                             └─ none adequate ──▶ verify one candidate ──▶ create only what is missing
     ▼                                                                                        │
assemble the smallest working set ◀───────────────────────────────────────────────────────────┘
     │
     ▼
do the actual work ──▶ verify with the repository's own checks
     │                          │
     │                          └─ failed ──▶ feedback ──▶ Coach proposal ──▶ independent Gate ──▶ promote or roll back
     ▼
checkpoint the verified state ──▶ the next session resumes from here, not from chat memory
```

The `yes` branch is the common one on a mature repository, and it produces no files at all.

## What lands in your repository

```text
your-project/
├── AGENTS.md or CLAUDE.md     # host-loaded guidance, merged with what you already wrote
├── docs/nulnul/
│   ├── project.md             # goal, completion check, capabilities, permission boundaries, rollback
│   ├── checkpoint.json        # concise resume state for ordinary multi-session work
│   └── evolution.json         # replaces checkpoint.json when agent evolution needs governed history
├── .agents/skills/<name>/      # Codex: only when no adequate existing skill covers the workflow
└── docs/nulnul/workflows/<name>.md
                                # unattended Claude Code: reusable workflow referenced by CLAUDE.md
```

That is the entire footprint. Ordinary multi-session work gets `checkpoint.json`; agent-specific feedback and promotion history replace it with `evolution.json`, never a second live-state writer. Upgrading a legacy durable setup preserves its contract and permission constraints, starts the checkpoint as `unknown`, and requires the recorded check before fast resume. The project-local skill appears only when every existing candidate was checked and rejected, and a fast-path run writes nothing. Remove the generated `docs/nulnul/` and project-local skill directory to remove the harness without touching product code. Host-owned agent definitions are never part of that footprint.

The goal is fewer generated files, not more. A setup that produces dozens of agent definitions has moved the problem, not solved it.

## Use cases

Each of these is one sentence in a fresh session. Every one is a recurring data workflow, so it inherits deduplication, exclusion precedence, `unknown` states, cursor persistence, and single-writer locking without asking for them.

```text
Build me a harness that finds finance YouTube creators, deduplicates them, and writes reviewed results to Google Sheets.
Build me a harness that watches job boards for new postings, drops duplicates, and keeps one reviewable queue.
Build me a harness that snapshots competitor pricing pages weekly and reports only what changed.
Build me a harness that collects new papers and release notes in my field and produces one weekly digest.
Build me a harness that classifies an inbound inquiry inbox and routes anything uncertain to a review queue.
Build me a harness that collects product reviews, tags recurring issues, and keeps a running summary sheet.
Build me a harness that verifies every link in our docs and reports dead ones with the state it could not check.
Build me a harness that collects CI failures and clusters the ones that repeat across runs.
```

## Personal agent evolution

```text
Worker feedback ──▶ Coach proposal ──▶ independent Gate
       ▲                                      │
       └──────── Navigator resumes work ◀─────┘
```

| Responsibility | Job |
| --- | --- |
| Navigator | Own the outcome, completion check, permissions, checkpoint, and resume |
| Worker | Complete one bounded job and report observable evidence |
| Coach | Act as the meta-agent: discover better methods and propose one task- or meta-level change |
| Gate | Compare the candidate with the accepted version, then promote, reject, or roll back |

These are responsibility boundaries, not four mandatory live agents. Simple work can combine roles; every promotion still separates its author from its Gate. The Coach can upgrade its own discovery and improvement procedure, but it cannot approve its own candidate.

For multi-session work, the harness stores only bounded state in `docs/nulnul/evolution.json`. Its standard-library validator rejects target or proposal-author self-approval, contradictory records, missing evidence, invalid version transitions, sensitive persisted keys, and permission expansion without prior approval.

The 1.4 Observable Evolution candidate adds bounded Experience Digests to the existing activation runner: stable `activation`/`resume`/`verification` stages, logical owner, elapsed time, aggregate tool/read/validator/test/completion-check counts, bounded signals, and verification status. It stores no prompt, response, transcript, command list, or machine path. The 1.4.1 runs falsified path resolution, supported final-action ordering, and rejected two Navigator-instruction candidates. The final 1.4.2 interruption test then found the real defect: all three mutated states remained fast-resumable before independent Gate verification. Schema-v3 checkpoints now require a runner-owned bounded file fingerprint; the candidate reduced unverified mutated-state acceptance from 3/3 to 0/3 without changing Navigator wording.

The 1.5 Generalization Gate keeps exposed DEV/VALIDATION cases separate from candidate-frozen, one-shot HOLDOUT evidence. Its first Ruby holdout failed because the fixture itself was invalid and was permanently downgraded to validation; that failure added mandatory fixture preflight. A new Perl/TAP CLI case absent from the frozen Navigator v15 snapshot then showed 3/3 stale-state blocks and 3/3 successful post-check resumes; three champion retries and best-of-3 remained unsafe. The decision is deliberately **Narrower Scope**: checkpoint freshness transferred to this unseen shape, but harness-wide generalization is not established. Release adoption also requires the bounded `claude plugin list --json` inventory before coverage decisions; two sanitized 1.5.0 nonpasses made this an explicit main-workflow rule.

## Field-hardened rules

These rules come from a full day of unattended loop operation on a real recurring workflow. Every row replaced a failure that the previous references did not prevent.

| Rule | Failure it prevents |
| --- | --- |
| One writer per state file: an exclusive lock, a stopped process group, one shard per parallel collector | Concurrent loops each rewrite the whole state from memory; the last writer wins and the rest is gone. Atomic rename prevents torn files, not lost updates |
| A distinct `unknown` verification state next to `verified` and `failed` | A skipped or timed-out check recorded as a pass, or frozen as a failure that deletes healthy records |
| Cursors written even on a cycle that found nothing | The next window is derived from the last run record, so a missing record freezes the range and the collector rescans it forever |
| One observed live cycle after every promotion, with an automatic rollback threshold | Regressions that only appear at run time — resolver behavior, load, execution order, longer input — pass a frozen sample untouched |
| One function defines the goal metric; every counter imports it | Counter definitions drift, and a loop reaching its target on a proxy metric stops on work that is not delivered |
| Every validity check proven against a negative control | Checks where a nonexistent target answers exactly like a real one, so the check measures nothing |
| Each stage records its own start and end | Unrecorded time attaches to the neighboring stage and names the wrong bottleneck |
| Rejected and rolled-back proposals kept with their diff and reason, queried before the next proposal | The Coach reproposing a candidate the Gate already rejected |
| Gate decisions logged, with the false-positive share reported | Accumulated false alarms train people to wave the gate through, and the gate stops protecting anything |
| A documentation debt detector when source and durable guidance evolve together | A fix that lands only in code is invisible to the next session |
| Benchmark, deliverable function, doc-debt hook, and state lock selected from inspected jobs | Speculative scaffolding on a simple project, or no mechanism when a recurring job actually needs one |

## Prior art

None of the parts here are new. Split the design and every piece has an existing name, and the mapping below is accurate:

| Part of NULNUL | Existing name | Where it lives here |
| --- | --- | --- |
| Editable task and meta sides | [HyperAgents](https://ai.meta.com/research/publications/hyperagents/) — the meta agent can modify the task agent and its own modification procedure | `references/meta-evolution.md`, with an independent Gate added as a safety boundary |
| Coach and Gate separated | actor-critic ([Sutton & Barto](http://incompleteideas.net/book/the-book.html)); the generator–verifier gap — checking an answer is a different, easier job than producing it | `references/personal-evolution.md` |
| Automatic promotion and rollback | champion/challenger, model-registry promotion gates ([MLflow](https://mlflow.org/docs/latest/model-registry.html)), [canary release](https://martinfowler.com/bliki/CanaryRelease.html) | promotion condition 8: one observed live cycle, automatic revert on a metric drop |
| Gating on regression checks | eval-gated CI ([promptfoo](https://www.promptfoo.dev/), [Braintrust](https://www.braintrust.dev/), [LangSmith](https://docs.smith.langchain.com/)) | [`evals/cases.json`](evals/cases.json), `scripts/release_gate.py`, the repository test suite |
| Optimizing against a metric | [DSPy](https://arxiv.org/abs/2310.03714) compiles prompts against a metric | the single goal-metric function every counter imports, and the Coach's named primary metric |
| Learning from failure and retrying | [Reflexion](https://arxiv.org/abs/2303.11366), [Self-Refine](https://arxiv.org/abs/2303.17651) | the feedback → proposal loop |
| An agent accumulating skills | [Voyager](https://arxiv.org/abs/2305.16291)'s skill library | `.agents/skills/<name>/`, created only after existing candidates were checked and rejected |
| Pulling skills and tools from outside | [MCP](https://modelcontextprotocol.io/) registries, plugin marketplaces | `references/capability-discovery.md` |

Two differences are deliberate:

- **The system improves itself; it cannot approve itself.** Reflexion-style loops let the same agent critique and accept its own retry. Here the Coach may modify its own improvement procedure, but promotion needs an independent Gate plus one observed live cycle, and the validator rejects a state file where the proposal author or target signed off on it.
- **Managed runtime is optional.** [Claude Managed Agents](https://news.hada.io/topic?id=28326) supplies hosted sessions, sandboxes, identity, and tracing; it is not HyperAgents and NULNUL does not require that service or lock a project to one model provider.
- **The loop's failures are operational, so the rules are too.** Locks, cursors, and a distinct `unknown` state are not agent-reasoning topics, and that is exactly why an agent-only design keeps losing data to them.

The contribution, if any, is the packaging: one portable contract that carries all of it into a fresh repository, with no service to run and nothing left behind after deletion.

## Evidence, not claims

| Check | Current result |
| --- | --- |
| Automated repository tests | 94 passed |
| Release Gate | 100/100 behavior and safety; recorded setup, workflow, fast-path, and scoped generalization gates also pass |
| Positive isolated scenarios | 9 passed |
| Negative safety scenarios | 3 passed |
| Two-run Codex meta-evolution | Coach v1 → v2; 0/2 relevant-method misses; 8/8 fixture tests; unnecessary infrastructure skipped |
| Independent forward evaluation | Found 3 validator gaps; all fixed and preserved as regressions |
| Offline workbook A/B (3 trials per arm) | All exact; Navigator v3 median time -25.76%, output tokens -22.76% vs 1.2.0 |
| Fresh Codex setup A/B | Exact behavior; accepted 1.3.0 input +2.31%, output -5.42%, reasoning -9.80% vs 1.2.1; initial +50.89% arm rejected |
| Fresh Codex resume A/B | Exact behavior in 3/3 trials; concise checkpoint reduced median input 38.52%, output 30.72%, and reasoning 56.33% vs 1.3.0; three weaker arms rejected |
| Later transfer cycle | A separate slugger project changed exactly one behavior and test, passed 3/3 tests and both harness checks, and did not read the marked full contract |
| Activation and fast-path runner | 10 positive/negative project shapes, 3 runs by default; the counterbalanced candidate was bounded in 4/4 runs and changed paired input -18.4% across 3 comparable pairs |
| Observable evolution | 3 bounded digests separated Navigator `0` from Gate `1`; invalid-stage and raw-transcript controls failed, and the ownership-rule candidate was rejected |
| Generalization Gate | Exposed benchmark inventory recorded; failed Ruby case retired into validation; fresh Perl/TAP case passed 3/3 while champion retry/best-of-3 stayed unsafe; decision: Narrower Scope |
| Headless Claude Code adoption | GitHub-marketplace-installed 1.3.5 kept both agent-profile hashes unchanged, made zero `.claude/**` write calls, created a verified checkpoint with an executable completion command, and passed five machine-recorded checks |
| Learning-loop and upgrade controls | Schema-v1 checkpoints are read-only; missing verdict inventories fail Product and Release Gates; injected migration write failure restores every earlier file |
| Executable rollback controls | Threshold breach restored Coach v1 active-version state; healthy metric produced no write |

Release Gate is not a universal performance benchmark. All twelve weighted behavior and safety cases pass, and release readiness also fails on a recorded setup, workflow, or fast-path regression. Generalization Gate is a separate adjunct activated only for personal/core promotion or transfer claims; ordinary project-local changes do not pay holdout cost. Performance evidence uses version-independent champion/candidate records; fast-path candidates run in counterbalanced paired order and are checked against a relative token budget instead of an absolute ceiling. The activation runner reports precision, recall, stage times, logical owners, and aggregate tool/read/validator/test/completion-check counts without retaining raw transcripts or command lists.

Reproduce the public checks:

```bash
python3 scripts/release_gate.py
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Inputs and decisions are published in [`evals/cases.json`](evals/cases.json), [`evals/results.json`](evals/results.json), the [`performance comparisons`](evals/benchmarks/performance.json), the [`fresh Codex setup baseline`](evals/benchmarks/setup-baseline/results.json), and the [`generalization exposure inventory`](evals/generalization/manifest.json) with its [one-shot result](evals/generalization/results.json).

## Reference workflow: YouTube → Google Sheets

The public example models a finance-creator research workflow without copying production identities or contact data. It covers channel discovery, classification, stable channel-ID deduplication, exclusion precedence, reviewer feedback, spreadsheet-formula escaping, safe upsert behavior, and run metrics.

- Synthetic example: [`examples/youtube-sheets`](examples/youtube-sheets)
- Offline quality scorer and A/B evidence: [`evals/benchmarks/youtube-sheets`](evals/benchmarks/youtube-sheets)

No real Google authentication or Sheet write is performed without explicit approval. The first isolated 3×3 comparison exposed overhead on an already-complete contract; Navigator v3 then skipped unnecessary activation and reproduced exact results with lower medians. This is task-specific preliminary evidence, not a universal performance claim.

## Trust model

- **Installed ≠ verified.** Availability is discovery evidence, not proof.
- **Popularity ≠ fitness.** Adoption cannot override provenance, permissions, license, or task fit.
- **Least privilege.** Authentication, external writes, deployment, publication, and global registration remain approval boundaries.
- **No secret persistence.** Credentials, raw conversations, and personal data do not become project memory.
- **Independent promotion.** An agent cannot approve its own upgrade.
- **Evaluation exposure is state.** A case seen during development cannot be relabeled as unseen; a used holdout is retired.
- **Verified resume.** Checkpoints are rechecked against repository reality before use.
- **Host-owned configuration stays host-owned.** Unattended sessions inspect `.claude/**` but never rewrite their own agents, skills, settings, or hooks.
- **Removable setup.** Generated project state can be deleted without damaging product code.

## What ships

```text
plugins/nulnul-harness/                 # only shipped product boundary
├── .codex-plugin/plugin.json           # Codex manifest
├── .claude-plugin/plugin.json          # Claude Code manifest
├── assets/nulnul-harness.svg
└── skills/nulnul-harness/
    ├── SKILL.md                        # execution contract
    ├── agents/openai.yaml              # Codex UI metadata
    ├── references/                     # discovery, assembly, safety, evolution
    ├── assets/                         # removable project templates
    └── scripts/                        # state validator and documentation debt detector
```

The plugin remains skills-only. It includes no MCP server, hook, app, authentication, remote telemetry, hosted service, or background process. Local release benchmarks retain sanitized aggregates only. Evolution happens during normal agent work; it is not an unsupervised daemon. Gate independence is validated from declared state; it is not cryptographic identity proof.

## FAQ

<details>
<summary>Is Release Gate a performance benchmark?</summary>

Not a universal one. It gates behavior and safety, then enforces the published task-specific setup, workflow, and fast-path performance budgets. The measurements remain scoped to their recorded fixtures and are reported in [Evidence, not claims](#evidence-not-claims).
</details>

<details>
<summary>Why does it create so few agents?</summary>

Because that is where the measurements pointed. Over a full day of unattended operation, every measured gain came from correcting a judgment function that already existed; new agents contributed nothing and added coordination cost. A role is added only for a concrete independent job, a context boundary, a parallel branch, or an independent verification need.
</details>

<details>
<summary>Why can't an agent accept its own improvement?</summary>

Producing an answer and checking one are different jobs, and the second is the easier one to keep honest. A promotion needs an independent Gate, a reproduced failure, passing regressions, and one observed live cycle with an automatic rollback threshold. The state validator rejects a file where the proposal author or the target agent signed its own promotion, so the rule survives a persuasive agent.
</details>

<details>
<summary>Why no MCP server, hook, or background process?</summary>

Nothing here needs to run continuously, and a component that runs continuously has to be operated, secured, and removed. Capability discovery can still adopt an MCP server or plugin when a job actually needs one — behind explicit approval, and recorded with its permission boundary and removal condition.
</details>

<details>
<summary>What is left after I remove it?</summary>

Product code, and whatever guidance you wrote yourself. Generated project state lives in `docs/nulnul/` and `.agents/`, and the plugin merges with user-owned instructions rather than replacing them.
</details>

<details>
<summary>How is this different from a harness that generates agent teams?</summary>

Different job. Team-generating factories produce a staffed organization from a domain description. This one starts from the repository you already have, reuses what covers the work, and generates the smallest set that passes a completion check — often nothing. It also carries the operational rules that decide whether an unattended loop keeps its data: locks, cursors, unverified states, and rollback thresholds.
</details>

## Removal

```bash
codex plugin remove nulnul-harness@nulnul-harness
codex plugin marketplace remove nulnul-harness
```

```bash
claude plugin uninstall nulnul-harness@nulnul-harness
claude plugin marketplace remove nulnul-harness
```

## Development

```bash
python3 -m unittest discover -s tests -p 'test_product_plugin.py' -v
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/release_gate.py
```

Product decisions and experiment notes are summarized in [`CHANGELOG.md`](CHANGELOG.md). See [`SUPPORT.md`](SUPPORT.md) and the [MIT license](LICENSE).

MIT © [SeoNaRu](https://github.com/SeoNaRu)
