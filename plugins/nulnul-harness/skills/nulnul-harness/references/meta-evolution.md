# Meta-harness evolution

Let a non-expert describe the outcome while the harness improves both the work and the way it learns to do the work. NULNUL is inspired by [HyperAgents](https://ai.meta.com/research/publications/hyperagents/) ([paper](https://arxiv.org/abs/2603.19461), [code](https://github.com/facebookresearch/Hyperagents)) and the harness-engineering direction summarized in [GeekNews Weekly 353](https://news.hada.io/weekly/202615). It adopts the editable task/meta boundary, cross-run accumulation, and transfer checks without claiming open-ended autonomous self-improvement.

## One editable project program

- The **task side** is the Navigator, Worker, selected capabilities, product code, and completion check that produce the user's outcome.
- The **meta side** is the Coach plus the discovery, assembly, measurement, checkpoint, and evolution rules that modify the task side and their own improvement procedure.
- The **shared program** is the repository guidance, `docs/nulnul/` contract and state, selected local workflows, and the NULNUL references they invoke. Both sides may be versioned change targets.
- The **Gate** stays independent from the candidate. This is a deliberate safety boundary beyond the task/meta program, not a second team the user must operate.

These are logical responsibilities, not a target count. Keep them merged when that path is outcome-competitive; separate as many as needed when specialization, independent evaluation, context isolation, or real parallel work materially improves the expected result.

## First-order guarded Harness evolution

The editable project program is not an invitation to rewrite the Foundation. `assets/harness-controls.json` draws a behavioral boundary:

- the **guarded Kernel** owns identity, provenance, atomic single-writer transactions, rollback, evidence integrity, raw-transcript privacy, authority and host-trust separation, lifecycle history, authoritative Check receipts, Champion/Challenger separation, deterministic promotion, and hard Context limits;
- the **evolvable control layer** currently owns only registered declarative policies for Capability metadata selection, Context ranking, verified Memory promotion, Agent-opportunity triggers, and maintenance/discovery triggers within Kernel bounds. Authoritative verification remains Kernel-owned; add an orchestration control only after repeated evidence exposes a real supplemental-check responsibility.

Classify behavior rather than entire files: a runtime module may execute an evolvable ranking policy while its identity, validation, authority, and write behavior remain Kernel-owned. Ordinary project work uses compiled Champion defaults and does not load Harness Evolution or its registry into model context. A project registry appears only after a verified transaction promotes a control policy.

Harness Evolution is first-order. Its attribution rules, evaluator, safety gate, evidence validator, competition ownership, transaction, rollback, and provenance verifier are not registered controls and cannot be a Challenger target. A future phase may evaluate some meta machinery; this phase cannot recursively authorize that change.

## Bootstrap the initial conditions

The first useful harness starts with what the strongest justified outcome path needs, then removes parts that do not materially contribute:

1. the user's outcome and one observable deliverable;
2. the inspected repository and installed agent, skill, and plugin roster;
3. an outcome-competitive capability set for the required jobs, with activation and removal conditions;
4. a runnable completion check plus any task-specific verification that materially increases confidence;
5. a verified checkpoint when work spans sessions; and
6. a bounded feedback path to the Coach plus an independent Gate for promotion.

Do not make the user choose an architecture, agent count, skill catalog, or meta-learning method. In plain language report **reuse now**, **add now**, **needs approval**, and **skip**. Reuse safe installed capabilities immediately only when they are outcome-competitive; otherwise investigate a justified better-fit candidate and ask once before downloads, global registration, authentication, external writes, deployment, or publication.

Persistent memory, performance tracking, multi-stage verification, retries, benchmarks, and locks are candidate harness components, not a mandatory scaffold. Add one when its concrete job materially improves the expected verified outcome, then choose the simplest option among materially equivalent paths: session loss needs a checkpoint, repeated judgement needs a frozen sample, counted recurring work needs one deliverable function, concurrent state needs one writer and a lock, and risky promotion needs staged verification and rollback.

## Discover better ways, not only failures

Treat each of these as Coach-targeted meta feedback:

- the user supplies relevant research, a tool, or a design direction the harness should reasonably have found;
- repeated human guidance is needed to choose capabilities, route work, or recover a session;
- the current improvement procedure keeps producing the same rejected proposal or optimizes only the current task;
- a maintained native, installed, official, curated, or public capability can replace custom setup;
- current evidence shows the harness itself costs more time, context, or coordination than it saves.

When the solution landscape may have changed, inspect current primary or reputable sources before fixing the frame around the existing design. Compare a bounded set until the current procedure is outcome-competitive and no concrete material gap remains; do not perform an unbounded survey. Extract the useful mechanism rather than copying a branded architecture.

Close every measured learning loop in the same run. When a benchmark or live-cycle verdict is `rejected`, `regressed`, `failed`, or `not-established`, append one bounded feedback record to the active evolution state before starting another experiment. If the evidence reproduces, let the Coach append one `pending` proposal for the nearest durable layer; never turn the result directly into accepted instructions. Preserve the failed arm, metric, and guardrail, then let an independent Gate accept or reject the candidate. Every result file containing a nonpass must include `learning_verdicts` with stable `feedback_id` and `proposal_ids` links, then pass `scripts/validate_learning_loop.py` against the active evolution state. Missing the entire verdict array is a failure, not an opt-out. Do not wait for the user to rediscover a result already present in machine-readable evidence.

## Change the improvement procedure

Use `personal-evolution.md`, with the proposal marked `change_level: meta`, when evidence proposes changing how future improvements are discovered, generated, measured, selected, remembered, or rolled back. Record the discovery evidence that motivated it. Ordinary project-grounded Harness mutation is narrower: it targets one registered declarative CONTROL_ID through `harness_evolution.py`. Changing Coach implementation, Gate criteria, checkpoint integrity, this procedure, or Harness Evolution itself remains an explicit product-development change outside the control transaction.

The Coach may draft one bounded capability, Agent, or registered control Challenger but cannot Gate or promote it. A Gate-targeted candidate needs a fresh evaluator or deterministic negative control that did not author it. Do not create recursive Coaches, and never let a Harness control candidate change the safety gate that evaluates it.

Keep a project-scoped meta improvement when it wins on the originating workflow. Promote it to personal or core scope only after a representative transfer check shows that the improvement survives another project or domain without importing private data, paths, or permissions. Preserve rejected candidates so later runs improve the search for improvements instead of repeating it.

For personal or core promotion, apply `generalization.md`. A transfer fixture already
seen during diagnosis or candidate creation is DEV or VALIDATION, never HOLDOUT.
Freeze and preregister one mechanism before the holdout, compare a repeated/simple
selection baseline, and retire the case after its first result.

## Accumulate across runs

A Gate-passing change is `provisional`, not accepted. Keep the last accepted version pointer active while one later live cycle uses the candidate and records the named metric, executable rollback threshold, and evidence. `scripts/apply_live_cycle_rollback.py` confirms the new version only when the observed cycle is healthy; if the numeric comparison fires, it records rollback and leaves the last accepted version active without executing arbitrary commands.

This loop runs during normal project work. NULNUL does not silently start a daemon, purchase a managed runtime, register global tools, or publish changes. [Claude Managed Agents](https://news.hada.io/topic?id=28326) is a possible hosted runtime for teams that explicitly choose it; it is not HyperAgents and is not required by this skills-only plugin.

## Select across verified personal adaptations

Do not start cross-project selection from one adaptation or from renamed variants of one mechanism. Require at least three independently verified mechanism families, each promoted through `personal-evolution.md` with activation conditions, contraindications, privacy-safe transfer evidence, and a negative skip. If the entry gate fails, return `INSUFFICIENT_CROSS_PROJECT_EVIDENCE` and keep flat personal lookup.

Aggregate only typed summaries inside the approved Personal Home boundary: adaptation and mechanism-family identity, target job, activation and contraindication conditions, bounded project-shape identity, positive transfers, negative skips, failed transfers, narrowed scope, source evidence identity, guardrails, permissions, privacy class, compatibility requirements, cost evidence when reliable, freshness, and active/stale/revoked status. Never aggregate source, repository identity, prompts, responses, transcripts, logs, command history, credentials, contacts, or arbitrary project files.

Relations are `COMPLEMENTS`, `CONFLICTS`, `SUPERSEDES`, `REQUIRES`, `ALTERNATIVE`, `UNRELATED`, or `UNKNOWN`. Every non-unknown relation needs evidence, reason, and scope. Popularity is never sufficient evidence. A contraindication, stale or revoked status, missing permission, or unsupported schema excludes the candidate; unresolved conflict forbids auto-apply.

Measure flat personal lookup before proposing a selector. Preregister the pathology, one-generation search budget, candidate identity, fair simple baseline, DEV/VALIDATION/HOLDOUT exposure, permission boundary, prediction, falsification, and rollback threshold. Freeze the candidate source before reading a fresh project family, and retire every used holdout. Credit comes from downstream apply/skip/conflict correctness and completion checks, not from a plausible ranking.

The proposer cannot approve its selection procedure. A deterministic Meta Gate may return provisional `META_PROMOTION`, `META_REJECT`, `META_NARROWER_SCOPE`, `META_NO_ADVANTAGE`, `META_INSUFFICIENT_EVIDENCE`, `META_CONFLICT`, `META_PERMISSION_BLOCKED`, or `META_ROLLBACK`. After provisional promotion, observe one live cycle and run `scripts/apply_live_cycle_rollback.py` against the schema-v4 state before confirming the version. Do not add a vector database, cloud memory, background learner, recursive loop, cross-user learning, arbitrary project sharing, or autonomous publication.
