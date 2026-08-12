<p align="center">
  <img src="plugins/nulnul-harness/assets/nulnul-logo-green.svg" width="320" alt="NULNUL logo">
</p>

<p align="center">
  <strong>Verified capabilities. Personal agents. Controlled evolution.</strong><br>
  A research-driven meta-harness for Codex and Claude Code: turn current agent research into falsifiable local experiments, and keep only mechanisms that survive evidence and an independent Gate.
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

## What NULNUL does

You describe the outcome. NULNUL inspects the repository, reuses what already works, builds only the missing harness, completes and verifies the task, and turns reproducible failures into gated improvements.

It is not a paper-to-feature pipeline. Research supplies questions, possible mechanisms, stronger baselines, and ways an evaluation may be wrong. NULNUL converts those into bounded experiments and leaves failed or unsupported ideas out of the product.

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

Start a fresh session and describe the result, not an agent architecture:

```text
Build me a harness that finds finance YouTube creators, deduplicates them,
and safely writes reviewed results to Google Sheets.
```

The same skill drives both surfaces. It detects the host, inspects an existing setup before asking questions, and writes only repository-owned paths. In unattended Claude Code sessions, `.claude/**` is read-only; `CLAUDE.md` and `docs/nulnul/` carry removable project state.

### Update

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

If the marketplace came from a local clone, pull that clone first. Start a fresh agent session after either update. Project-local guidance and `docs/nulnul/` state are preserved.

## Why NULNUL

More tools do not make a better agent system. NULNUL takes the smaller path:

- **Reuse before creation.** Inspect installed, official, curated, and reputable public capabilities before making a local substitute.
- **Repository truth.** Read the actual contract, code, state, and runnable completion check before changing the project.
- **Verified resume.** A `verified` label is insufficient; fast resume requires a runner-owned receipt that still matches bounded repository files.
- **Permission boundaries.** Authentication, external writes, deployment, publication, and global registration still require explicit approval.
- **Independent promotion.** The Coach may propose a task or meta-level change, but cannot approve its own candidate.
- **Removable setup.** Keep stable evidence in the repository and avoid services, daemons, and generated roles without a demonstrated job.
- **Evidence-driven infrastructure.** Add memory, benchmarks, locks, agents, hooks, or MCP only when a measured workflow exposes the need.

The always-on [Baseline Kernel](plugins/nulnul-harness/skills/nulnul-harness/references/baseline-kernel.md) is only seven things: repository truth, original outcome, one runnable check, a before state, inspected capability decisions, permission boundaries, and independently gated evolution with rollback.

## Research-driven evolution

NULNUL does not treat papers as a feature checklist. It reads the questions current agent and harness research raises, turns them into reproducible hypotheses inside NULNUL, and accepts only mechanisms that survive the relevant Gate.

```text
Research → Question → Reproduce → Candidate → Independent Gate → Live cycle
                                                                    │
                                                        Keep / Reject / Roll back
```

| Stage | Research question | NULNUL experiment | Evidence and decision |
| --- | --- | --- | --- |
| Origin | Can the procedure that improves a task agent also be editable? | Editable task/meta boundary; Coach proposals; independent Gate; cross-run state | Governed [meta-evolution](plugins/nulnul-harness/skills/nulnul-harness/references/meta-evolution.md), without claiming to reproduce HyperAgents |
| 1.4 Observable Evolution | Can we observe what changed, why, and whether that change caused the result? | Bounded Experience Digests, stable stage/owner separation, prediction and falsification | Broad test counts `[1, 1, 2]` hid Navigator `0` vs Gate `1`; path resolution was falsified, final-action ordering was supported, two instruction candidates were rejected, and a stale-checkpoint defect fell from unsafe 3/3 to 0/3 |
| 1.5 Generalization Gate | Does evolution beat simple search and survive a case that did not shape the candidate? | Machine-readable exposure state, preregistration, one-shot holdouts, champion/retry/best-of-3 controls | Invalid Ruby fixture failed and became validation; a fresh Perl/TAP shape blocked stale state 3/3 and resumed after verification 3/3 while champion retry and best-of-3 stayed unsafe; decision: **Narrower Scope** |
| Next | What bottleneck is now worth changing? | Require new dogfooding or evolution evidence before implementation | **Evidence pending. No milestone or research-watch item is committed.** |

The 1.4 and 1.5 labels above name research evidence milestones. The public plugin containing both is version **1.5.0**.

### Paper → product

> **Paper ≠ feature.** A paper can reveal a question, suggest a mechanism, define a stronger baseline, or expose an evaluation flaw. It enters NULNUL only after local reproducible evidence, independent acceptance where required, and a live-cycle check. Rejections remain evidence instead of becoming instructions.

NULNUL's 1.4 work was informed by the observability question, but its specific findings are local: completion-count attribution failed, a path hypothesis was disproved, and the measured defect was checkpoint freshness. Likewise, 1.5 does not inherit a paper's transfer claim; it reports only what its own one-shot evidence established.

## Research lineage

### Foundations

The original project context was [GeekNews Weekly 353: “In the age of abundant skills, build your own harness”](https://news.hada.io/weekly/202615). The design also uses established ideas rather than renaming them:

| Foundation | What NULNUL takes from it | What NULNUL does not claim |
| --- | --- | --- |
| Meta/UBC [HyperAgents](https://ai.meta.com/research/publications/hyperagents/) ([paper](https://arxiv.org/abs/2603.19461), [code](https://github.com/facebookresearch/Hyperagents)) | One editable program with task and meta sides; the meta side can change its own improvement procedure | Full reproduction, open-ended evolution, or autonomous self-modification |
| Actor/critic and generator/verifier separation ([Sutton & Barto](http://incompleteideas.net/book/the-book.html)) | Coach proposes; an independent Gate verifies | Cryptographic proof that two runtime identities are independent |
| Champion/challenger and canary release | Keep the accepted version, compare a bounded candidate, observe a live cycle, roll back on an executable threshold | A managed model registry or hosted rollout system |
| Eval-gated CI | Behavior and safety evidence block release | Universal performance or safety outside the published fixtures |

### Mechanisms tested in NULNUL

| Primary research question | Implemented and measured in NULNUL |
| --- | --- |
| [Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses](https://arxiv.org/abs/2604.25850): component, experience, and decision observability; prediction → evaluation | Bounded Experience Digest, owner/stage attribution, falsifiable candidates, rejection preservation, checkpoint-freshness discovery. See [evolution rules](plugins/nulnul-harness/skills/nulnul-harness/references/evolution.md) and [activation evidence](evals/benchmarks/activation/results.json). |
| [Rethinking the Evaluation of Harness Evolution for Agents](https://arxiv.org/abs/2607.12227): matched feedback/inference budgets, test-time search baselines, held-out evaluation, limited generalization | DEV/VALIDATION/HOLDOUT exposure state, retry and best-of-3 controls, one-shot holdout retirement, scoped decisions. See the [Generalization Gate](plugins/nulnul-harness/skills/nulnul-harness/references/generalization.md), [manifest](evals/generalization/manifest.json), and [result](evals/generalization/results.json). |

The paper columns name the research questions and reported mechanisms. The right column names what this repository actually implemented and measured; the two are not interchangeable.

### Research Watch — not implemented, not a committed roadmap

| Research | Question being watched | Status |
| --- | --- | --- |
| [Self-Evolving Agent Harnesses via Gated Semantic Quality-Diversity](https://arxiv.org/abs/2607.13683) | Can sealed credit assignment and a pathology-based candidate archive outperform sequential one-off proposals without overfitting? | Watching — no candidate population, quality-diversity archive, or autonomous evolution loop exists here |
| [EvolveNet: Collaborative Harness Evolution for Agent Self-Improvement](https://arxiv.org/abs/2608.04968) | Can scope-typed, verified adaptations transfer across isolated projects without sharing raw workloads? | Watching — no cross-project adaptation sharing or aggregation exists here |

Research Watch is not a release plan. The next direction is chosen only when NULNUL's own evidence shows a bottleneck that one of these ideas can test.

## Product loop

```text
Discover → Verify → Assemble → Run → Checkpoint → Evolve the task or improvement process
```

| Stage | Durable result |
| --- | --- |
| Discover | Required jobs, repository truth, and existing candidates |
| Verify | Provenance, compatibility, quality, permissions, maintenance, and license |
| Assemble | The smallest complete capability and responsibility set |
| Run | The user-visible result and its exact completion check |
| Checkpoint | Current verified state, bounded files, next action, blockers, and permissions |
| Evolve | One causal change, independent decision, live observation, and rollback |

On a mature repository, the common path is to reuse its coherent setup and write no harness files. Setup is never task completion: NULNUL continues the user's original work and verifies it with the repository's own check.

### Responsibility boundaries

| Responsibility | Job |
| --- | --- |
| Navigator | Own the outcome, completion check, permissions, checkpoint, and resume |
| Worker | Complete one bounded job and report observable evidence |
| Coach | Diagnose reproducible feedback and propose one task- or meta-level change |
| Gate | Compare the candidate with the accepted version, then promote, reject, or roll back |

These are logical boundaries, not four mandatory live agents. Simple work combines them; a promotion still separates its author from its Gate. Bounded state lives in `docs/nulnul/evolution.json`, and its validator rejects self-approval, contradictory records, missing evidence, sensitive keys, invalid version transitions, and unapproved permission expansion.

## What lands in your repository

```text
your-project/
├── AGENTS.md or CLAUDE.md     # merged host-loaded guidance
├── docs/nulnul/
│   ├── project.md             # stable goal, check, capabilities, permissions, rollback
│   ├── checkpoint.json        # concise ordinary multi-session state
│   └── evolution.json         # replaces checkpoint when governed evolution needs history
├── .agents/skills/<name>/     # only when no adequate existing skill covers the workflow
└── docs/nulnul/workflows/<name>.md
                                # reusable workflow for unattended Claude Code
```

Ordinary multi-session work gets `checkpoint.json`; governed agent history replaces it with `evolution.json`, never a second state writer. Legacy state starts `unknown` and must run its recorded command before fast resume. Remove generated `docs/nulnul/` and local skills to remove the harness without touching product code. Host-owned agent definitions are never part of this footprint.

## Use cases

One sentence in a fresh session is enough:

```text
Build me a harness that watches job boards, drops duplicates, and keeps one review queue.
Build me a harness that snapshots competitor pricing weekly and reports only changes.
Build me a harness that collects new papers and release notes into one weekly digest.
Build me a harness that groups recurring CI failures without storing raw logs as memory.
```

Recurring data workflows inherit stable identity, deduplication, exclusion precedence, `unknown` verification, cursor persistence, idempotent writes, and a single state writer when those jobs exist.

## Field-hardened rules

Most observed failures were operational invariants, not model-reasoning failures. In one full-day unattended creator workflow, concurrent writers lost 12,000 decisions; an empty-cycle cursor bug rescanned the same 120 items until a fix produced 1,265 new records; skipped checks became `ok`; an `A`-instead-of-`MX` test froze 15 healthy mailboxes; a broad text filter rejected 20 valid records; and three definitions of “completed” stopped on undelivered work. This is one workflow over one day—field evidence, not a universal benchmark.

| Rule | Failure it prevents |
| --- | --- |
| One writer per state file: an exclusive lock, a stopped process group, one shard per parallel collector | Concurrent loops rewrite the whole state from memory; atomic rename prevents torn files, not lost updates |
| A distinct `unknown` state next to `verified` and `failed` | A skipped or timed-out check recorded as a pass, or frozen as a failure |
| Cursors written even when a cycle finds nothing | A missing record freezes the next range and rescans old work forever |
| One observed live cycle after promotion, with an executable rollback threshold | Runtime-only regressions that a frozen sample cannot expose |
| One function defines the goal metric; every counter imports it | Counters drift until a proxy metric declares unfinished work complete |
| Every validity check proven against a negative control | A check that answers the same for a missing and a real target |
| Each stage records its own start and end | Unrecorded time attaches to a neighbor and names the wrong bottleneck |
| Rejected and rolled-back proposals remain queryable with reason | The Coach proposes an already-rejected candidate again |
| Gate decisions preserve false-positive evidence | Repeated false alarms teach operators to ignore the Gate |
| Documentation debt is checked when source and durable guidance evolve together | A code-only fix disappears from the next session's operating rules |
| Benchmarks, locks, roles, and hooks are selected from inspected jobs | Speculative scaffolding, or a missing mechanism where the job is real |

## Evidence, not claims

### Behavior

| Check | Current result |
| --- | --- |
| Repository tests | **94 passed** |
| Release Gate | **100/100** across 12 weighted behavior and safety cases; 9 positive and 3 negative isolated scenarios |
| Release-blocking regressions | Setup, bounded workflow, activation, fast-resume cost/read scope, Claude adoption, learning loop, observable evolution, and scoped generalization evidence are validated |
| Activation and fast resume | 10 positive/negative project shapes, 3 runs by default; accepted candidate bounded in 4/4 counterbalanced runs, paired input −18.4% across 3 comparable pairs |
| Public Claude adoption | GitHub-marketplace-installed **1.5.0**, zero `.claude/**` write calls, unchanged agent hashes, verified checkpoint, and five machine-recorded checks |

### Evolution

| Check | Current result |
| --- | --- |
| Experience observability | Three bounded digests separated Navigator completion checks `0` from Gate `1`; no prompts, responses, transcripts, command lists, or machine paths retained |
| Causal candidates | Path resolution falsified; final-action ordering supported; two Navigator instruction candidates rejected rather than promoted on plausible prose |
| Checkpoint freshness | Unverified mutated repository state was fast-resumable **3/3** before the mechanism and **0/3** after runner-owned bounded receipts; post-Gate task behavior/read scope/verified resume passed **3/3** |
| Release adoption learning | Three sanitized v1.5.0 nonpasses were preserved; Navigator v16 was rejected and v17 accepted only after branch-first installed-roster inventory passed a fresh run |

### Generalization

| Check | Current result |
| --- | --- |
| Exposure accounting | Every prior Release, activation, setup, workflow, meta-evolution, Claude-adoption, and deterministic fixture family is recorded as previously exposed DEV or VALIDATION evidence |
| Failed first holdout | The invalid Ruby fixture failed its completion check, was preserved, and became validation; its failure added mandatory fixture preflight |
| Fresh transfer estimate | The then-unseen Perl/TAP case blocked stale resume **3/3** and restored verified resume **3/3**; it is now retired after one use |
| Search baseline | Single champion, three champion retries, and best-of-3 all remained unsafe. Deterministic arms used the same six subprocess calls per trial; no inference-budget win is claimed |
| Decision | **Narrower Scope. Checkpoint freshness transferred to one unseen local Perl/TAP CLI shape. Harness-wide generalization is not established.** |

Release Gate is not a universal benchmark. Generalization Gate is a separate adjunct activated for personal/core mechanism promotion, transfer claims, or public generalization claims; ordinary project-local changes do not pay holdout cost. A case seen during development cannot be renamed HOLDOUT, and a used holdout cannot support a second unseen claim.

Reproduce the public checks:

```bash
python3 scripts/release_gate.py
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

The source evidence is public: [behavior cases](evals/cases.json), [behavior results](evals/results.json), [performance comparisons](evals/benchmarks/performance.json), [activation evidence](evals/benchmarks/activation/results.json), [exposure manifest](evals/generalization/manifest.json), [failed Ruby result](evals/generalization/results-ruby-failed.json), and [Perl/TAP result](evals/generalization/results.json). Full version archaeology remains in [`CHANGELOG.md`](CHANGELOG.md).

## Reference workflow: YouTube → Google Sheets

The public example models creator research without copying production identities or contact data. It covers discovery, classification, channel-ID deduplication, exclusion precedence, reviewer feedback, spreadsheet-formula escaping, safe upserts, and run metrics.

- Synthetic example: [`examples/youtube-sheets`](examples/youtube-sheets)
- Offline scorer and A/B evidence: [`evals/benchmarks/youtube-sheets`](evals/benchmarks/youtube-sheets)

No Google authentication or Sheet write happens without explicit approval. Its preliminary performance evidence is task-specific, not a universal claim.

## Trust model

- **Installed ≠ verified.** Availability is discovery evidence, not proof.
- **Popularity ≠ fitness.** Adoption cannot override provenance, permissions, maintenance, license, or task fit.
- **Least privilege.** Authentication, external writes, deployment, publication, and global registration remain approval boundaries.
- **No secret persistence.** Credentials, raw conversations, transcripts, and private project data do not become evolution memory.
- **Independent promotion.** An agent cannot approve its own upgrade.
- **Evaluation exposure is state.** A development case cannot be relabeled unseen; a used holdout is retired.
- **Verified resume.** Checkpoints are rechecked against bounded repository reality before use.
- **Host-owned configuration stays host-owned.** Unattended sessions inspect `.claude/**` but never rewrite it.
- **Removable setup.** Generated state can be deleted without damaging product code.

## What ships

```text
plugins/nulnul-harness/                 # only shipped product boundary
├── .codex-plugin/plugin.json
├── .claude-plugin/plugin.json
├── assets/nulnul-harness.svg
└── skills/nulnul-harness/
    ├── SKILL.md                        # execution contract
    ├── agents/openai.yaml              # Codex UI metadata
    ├── references/                     # discovery, assembly, safety, evolution
    ├── assets/                         # removable project templates
    └── scripts/                        # validators, check runner, rollback, doc debt
```

The plugin remains skills-only: no MCP server, hook, app, authentication, remote telemetry, hosted service, dashboard, daemon, or background process. Local evidence retains sanitized aggregates only. Evolution happens during normal user-triggered work, not as an unsupervised process. Gate independence is validated from declared state; it is not cryptographic identity proof.

## FAQ

<details>
<summary>Does NULNUL continuously learn by itself?</summary>

No. It converts a reproducible failure into one bounded candidate during normal work. Promotion needs evidence and an independent Gate; a later live cycle can trigger executable rollback. There is no autonomous population or daemon.
</details>

<details>
<summary>Is Release Gate a universal performance benchmark?</summary>

No. It gates the published behavior, safety, and task-specific cost evidence. Generalization Gate separately limits transfer claims, and the current harness-wide claim is explicitly not established.
</details>

<details>
<summary>Why so few agents and no MCP server?</summary>

Roles and infrastructure are costs. NULNUL adds them only for a concrete independent job, uncovered tool boundary, coordination need, or verification boundary. The current product needs none beyond a skills-only plugin.
</details>

<details>
<summary>Why can't an agent accept its own improvement?</summary>

Producing and checking a candidate are different jobs. The validator rejects author or target self-approval, and promotion requires reproduced evidence plus a live-cycle rollback threshold.
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

Generated project state is separate; remove it only when you no longer need its checkpoint or evolution history.

## Development

```bash
python3 -m unittest discover -s tests -p 'test_product_plugin.py' -v
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/release_gate.py
```

See [`CHANGELOG.md`](CHANGELOG.md), [`SUPPORT.md`](SUPPORT.md), and the [MIT license](LICENSE).

MIT © [SeoNaRu](https://github.com/SeoNaRu)
