<p align="center">
  <img src="plugins/nulnul-harness/assets/nulnul-logo-green.svg" width="320" alt="NULNUL logo">
</p>

<h1 align="center">NULNUL</h1>

<p align="center">
  <strong>Verified capabilities. Personal agents. Controlled evolution.</strong><br>
  A skills-only Codex plugin for turning ideas into verified agent systems.
</p>

<p align="center">
  <a href="https://github.com/SeoNaRu/nulnul-harness/actions/workflows/test.yml"><img src="https://github.com/SeoNaRu/nulnul-harness/actions/workflows/test.yml/badge.svg" alt="CI"></a>
  <img src="https://img.shields.io/badge/version-1.2.1-111111" alt="version 1.2.1">
  <a href="evals/results.json"><img src="https://img.shields.io/badge/Harness_100-100%2F100-111111" alt="Harness 100: 100/100"></a>
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
- turn reproducible feedback into agent upgrades that require an independent Gate.

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

**What that day changed about the design.** The measured gains came from correcting judgment functions that already existed — not from adding agents. So the setup output now ships four mechanisms before it ships any agent roster: a minimal frozen benchmark, the one function that defines the deliverable unit, a documentation debt hook, and a lock on the state file. This is one project over one day, so treat it as field evidence, not a benchmark.

## Quick start

```bash
git clone https://github.com/SeoNaRu/nulnul-harness.git
cd nulnul-harness
codex plugin marketplace add "$PWD"
codex plugin add nulnul-harness@nulnul-harness
```

Start a new Codex session and describe the outcome. Asking for a harness is enough — you never describe agents, roles, or setup steps:

```text
Build me a harness that finds finance YouTube creators, deduplicates them,
and safely writes reviewed results to Google Sheets.
```

The harness inspects the project, reuses adequate instructions and tests, checks available capabilities, asks only for decisions it cannot safely discover, and continues through implementation and verification. Describing the product without the word "harness" works the same way. It does not activate for simple read-only questions or duplicate a coherent project setup.

## Product loop

```text
Discover → Verify → Assemble → Run → Checkpoint → Evolve
```

| Stage | Durable result |
| --- | --- |
| Discover | Required jobs and existing candidates |
| Verify | Provenance, compatibility, quality, permissions, and license |
| Assemble | The smallest complete capability and agent set |
| Run | The user-visible result and its completion check |
| Checkpoint | Verified state, next action, blockers, and approved permissions |
| Evolve | Reproducible feedback, version comparison, independent promotion, and rollback |

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
├── AGENTS.md                  # short repo-wide guidance, merged with what you already wrote
├── docs/nulnul/
│   ├── project.md             # goal, completion check, capabilities, permission boundaries, rollback
│   └── evolution.json         # checkpoint, agent versions, bounded feedback, Gate decisions
└── .agents/skills/<name>/     # only when a recurring workflow has no adequate existing skill
```

That is the entire footprint. `evolution.json` appears only for multi-session or self-improving work, the project-local skill only when every existing candidate was checked and rejected, and a fast-path run writes nothing. Deleting `docs/nulnul/` and `.agents/` removes the harness without touching product code.

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
| Coach | Diagnose the nearest responsible layer and propose one versioned change |
| Gate | Compare the candidate with the accepted version, then promote, reject, or roll back |

These are responsibility boundaries, not four mandatory live agents. Simple work can combine roles; every promotion still separates its author from its Gate. The Coach can be upgraded from feedback, but it cannot approve its own candidate.

For multi-session work, the harness stores only bounded state in `docs/nulnul/evolution.json`. Its standard-library validator rejects target or proposal-author self-approval, contradictory records, missing evidence, invalid version transitions, sensitive persisted keys, and permission expansion without prior approval.

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
| A documentation debt detector in the day-one setup | A fix that lands only in code is invisible to the next session |
| Day-one setup ships a minimal frozen benchmark, the deliverable-unit function, the doc-debt hook, and the state lock | A cold start has nothing for the Gate to run against, so evolution cannot begin |

## Prior art

None of the parts here are new. Split the design and every piece has an existing name, and the mapping below is accurate:

| Part of NULNUL | Existing name | Where it lives here |
| --- | --- | --- |
| Coach and Gate separated | actor-critic ([Sutton & Barto](http://incompleteideas.net/book/the-book.html)); the generator–verifier gap — checking an answer is a different, easier job than producing it | `references/personal-evolution.md` |
| Automatic promotion and rollback | champion/challenger, model-registry promotion gates ([MLflow](https://mlflow.org/docs/latest/model-registry.html)), [canary release](https://martinfowler.com/bliki/CanaryRelease.html) | promotion condition 8: one observed live cycle, automatic revert on a metric drop |
| Gating on regression checks | eval-gated CI ([promptfoo](https://www.promptfoo.dev/), [Braintrust](https://www.braintrust.dev/), [LangSmith](https://docs.smith.langchain.com/)) | [`evals/cases.json`](evals/cases.json), `scripts/harness_100.py`, the repository test suite |
| Optimizing against a metric | [DSPy](https://arxiv.org/abs/2310.03714) compiles prompts against a metric | the single goal-metric function every counter imports, and the Coach's named primary metric |
| Learning from failure and retrying | [Reflexion](https://arxiv.org/abs/2303.11366), [Self-Refine](https://arxiv.org/abs/2303.17651) | the feedback → proposal loop |
| An agent accumulating skills | [Voyager](https://arxiv.org/abs/2305.16291)'s skill library | `.agents/skills/<name>/`, created only after existing candidates were checked and rejected |
| Pulling skills and tools from outside | [MCP](https://modelcontextprotocol.io/) registries, plugin marketplaces | `references/capability-discovery.md` |

Two differences are deliberate:

- **Self-refinement judges itself; this does not.** Reflexion-style loops let the same agent critique and accept its own retry. Here a promotion needs an independent Gate plus one observed live cycle, and the validator rejects a state file where the proposal author or the target agent signed off on it.
- **The loop's failures are operational, so the rules are too.** Locks, cursors, and a distinct `unknown` state are not agent-reasoning topics, and that is exactly why an agent-only design keeps losing data to them.

The contribution, if any, is the packaging: one portable contract that carries all of it into a fresh repository, with no service to run and nothing left behind after deletion.

## Evidence, not claims

| Check | Current result |
| --- | --- |
| Automated repository tests | 31 passed |
| Harness 100 behavior and safety gate | 100/100 |
| Positive isolated scenarios | 6 passed |
| Negative safety scenarios | 3 passed |
| Independent forward evaluation | Found 3 validator gaps; all fixed and preserved as regressions |
| Offline workbook A/B (3 trials per arm) | All exact; Navigator v3 median time -25.76%, output tokens -22.76% vs 1.2.0 |

Harness 100 is a release gate, not a universal performance benchmark. It covers implicit project activation, ambiguous empty repositories, reuse of coherent setups, capability-first automation, permission boundaries, evidence-gated evolution, read-only non-activation, secret persistence, and unapproved global registration.

Reproduce the public checks:

```bash
python3 scripts/harness_100.py
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Inputs and decisions are published in [`evals/cases.json`](evals/cases.json) and [`evals/results.json`](evals/results.json).

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
- **Verified resume.** Checkpoints are rechecked against repository reality before use.
- **Removable setup.** Generated project state can be deleted without damaging product code.

## What ships

```text
plugins/nulnul-harness/                 # only shipped product boundary
├── .codex-plugin/plugin.json
├── assets/nulnul-harness.svg
└── skills/nulnul-harness/
    ├── SKILL.md                        # execution contract
    ├── agents/openai.yaml              # Codex UI metadata
    ├── references/                     # discovery, assembly, safety, evolution
    ├── assets/                         # removable project templates
    └── scripts/                        # deterministic state validator
```

The plugin remains skills-only. It includes no MCP server, hook, app, authentication, telemetry, hosted service, or background process. Evolution happens during normal agent work; it is not an unsupervised daemon. Gate independence is validated from declared state; it is not cryptographic identity proof.

## FAQ

<details>
<summary>Is Harness 100 a performance benchmark?</summary>

No. It is a release gate over behaviors and safety boundaries: implicit activation, ambiguous empty repositories, reuse of a coherent setup, capability-first automation, permission boundaries, evidence-gated evolution, read-only non-activation, secret persistence, and unapproved global registration. Speed and quality evidence is separate, task-specific, and reported as such in [Evidence, not claims](#evidence-not-claims).
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

## Development

```bash
python3 -m unittest discover -s tests -p 'test_product_plugin.py' -v
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/harness_100.py
```

Product decisions and experiment notes are summarized in [`CHANGELOG.md`](CHANGELOG.md). See [`SUPPORT.md`](SUPPORT.md) and the [MIT license](LICENSE).

MIT © [SeoNaRu](https://github.com/SeoNaRu)
