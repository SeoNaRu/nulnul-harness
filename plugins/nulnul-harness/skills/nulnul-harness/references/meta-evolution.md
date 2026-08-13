# Meta-harness evolution

Let a non-expert describe the outcome while the harness improves both the work and the way it learns to do the work. NULNUL is inspired by [HyperAgents](https://ai.meta.com/research/publications/hyperagents/) ([paper](https://arxiv.org/abs/2603.19461), [code](https://github.com/facebookresearch/Hyperagents)) and the harness-engineering direction summarized in [GeekNews Weekly 353](https://news.hada.io/weekly/202615). It adopts the editable task/meta boundary, cross-run accumulation, and transfer checks without claiming open-ended autonomous self-improvement.

## One editable project program

- The **task side** is the Navigator, Worker, selected capabilities, product code, and completion check that produce the user's outcome.
- The **meta side** is the Coach plus the discovery, assembly, measurement, checkpoint, and evolution rules that modify the task side and their own improvement procedure.
- The **shared program** is the repository guidance, `docs/nulnul/` contract and state, selected local workflows, and the NULNUL references they invoke. Both sides may be versioned change targets.
- The **Gate** stays independent from the candidate. This is a deliberate safety boundary beyond the task/meta program, not a second team the user must operate.

These are logical responsibilities. Keep them merged in one working agent until an independent evaluation boundary or real parallel work requires another agent.

## Bootstrap the initial conditions

The first useful harness leaves only what the next run needs to improve itself:

1. the user's outcome and one observable deliverable;
2. the inspected repository and installed agent, skill, and plugin roster;
3. one adequate capability per uncovered job, with activation and removal conditions;
4. the smallest runnable completion check;
5. a verified checkpoint when work spans sessions; and
6. a bounded feedback path to the Coach plus an independent Gate for promotion.

Do not make the user choose an architecture, agent count, skill catalog, or meta-learning method. In plain language report **reuse now**, **add now**, **needs approval**, and **skip**. Reuse safe installed capabilities immediately. Ask once before downloads, global registration, authentication, external writes, deployment, or publication.

Persistent memory, performance tracking, multi-stage verification, retries, benchmarks, and locks are candidate harness components, not a mandatory scaffold. Add the smallest one when the workflow exposes its job: session loss needs a checkpoint, repeated judgement needs a frozen sample, counted recurring work needs one deliverable function, concurrent state needs one writer and a lock, and risky promotion needs staged verification and rollback.

## Discover better ways, not only failures

Treat each of these as Coach-targeted meta feedback:

- the user supplies relevant research, a tool, or a design direction the harness should reasonably have found;
- repeated human guidance is needed to choose capabilities, route work, or recover a session;
- the current improvement procedure keeps producing the same rejected proposal or optimizes only the current task;
- a maintained native, installed, official, curated, or public capability can replace custom setup;
- current evidence shows the harness itself costs more time, context, or coordination than it saves.

When the solution landscape may have changed, inspect current primary or reputable sources before fixing the frame around the existing design. Compare the current procedure with the first adequate credible alternative; do not perform an unbounded survey. Extract the useful mechanism rather than copying a branded architecture.

Close every measured learning loop in the same run. When a benchmark or live-cycle verdict is `rejected`, `regressed`, `failed`, or `not-established`, append one bounded feedback record to the active evolution state before starting another experiment. If the evidence reproduces, let the Coach append one `pending` proposal for the nearest durable layer; never turn the result directly into accepted instructions. Preserve the failed arm, metric, and guardrail, then let an independent Gate accept or reject the candidate. Every result file containing a nonpass must include `learning_verdicts` with stable `feedback_id` and `proposal_ids` links, then pass `scripts/validate_learning_loop.py` against the active evolution state. Missing the entire verdict array is a failure, not an opt-out. Do not wait for the user to rediscover a result already present in machine-readable evidence.

## Change the improvement procedure

Use `personal-evolution.md`, with the proposal marked `change_level: meta`, when the candidate changes how future improvements are discovered, generated, measured, selected, remembered, or rolled back. Record the discovery evidence that motivated it. A meta candidate may update the Coach, Gate criteria, capability search order, measurement strategy, checkpoint policy, or this procedure itself.

The Coach may edit its own candidate but cannot Gate it. A Gate-targeted candidate needs a fresh evaluator or deterministic negative control that did not author it. Do not create recursive Coaches.

Keep a project-scoped meta improvement when it wins on the originating workflow. Promote it to personal or core scope only after a representative transfer check shows that the improvement survives another project or domain without importing private data, paths, or permissions. Preserve rejected candidates so later runs improve the search for improvements instead of repeating it.

For personal or core promotion, apply `generalization.md`. A transfer fixture already
seen during diagnosis or candidate creation is DEV or VALIDATION, never HOLDOUT.
Freeze and preregister one mechanism before the holdout, compare a repeated/simple
selection baseline, and retire the case after its first result.

## Accumulate across runs

An accepted change is not complete until one later live cycle uses the new procedure and records the named metric, rollback threshold, and evidence. Version-3 evolution states make the threshold executable through `scripts/apply_live_cycle_rollback.py`. If the live cycle is missing, the validator rejects acceptance; if the numeric comparison fires, the script atomically records the rollback and restores the last accepted active-version state without executing arbitrary commands.

This loop runs during normal project work. NULNUL does not silently start a daemon, purchase a managed runtime, register global tools, or publish changes. [Claude Managed Agents](https://news.hada.io/topic?id=28326) is a possible hosted runtime for teams that explicitly choose it; it is not HyperAgents and is not required by this skills-only plugin.

## Select across verified personal adaptations

Do not start cross-project selection from one adaptation or from renamed variants of one mechanism. Require at least three independently verified mechanism families, each promoted through `personal-evolution.md` with activation conditions, contraindications, privacy-safe transfer evidence, and a negative skip. If the entry gate fails, return `INSUFFICIENT_CROSS_PROJECT_EVIDENCE` and keep flat personal lookup.

Aggregate only typed summaries inside the approved Personal Home boundary: adaptation and mechanism-family identity, target job, activation and contraindication conditions, bounded project-shape identity, positive transfers, negative skips, failed transfers, narrowed scope, source evidence identity, guardrails, permissions, privacy class, compatibility requirements, cost evidence when reliable, freshness, and active/stale/revoked status. Never aggregate source, repository identity, prompts, responses, transcripts, logs, command history, credentials, contacts, or arbitrary project files.

Relations are `COMPLEMENTS`, `CONFLICTS`, `SUPERSEDES`, `REQUIRES`, `ALTERNATIVE`, `UNRELATED`, or `UNKNOWN`. Every non-unknown relation needs evidence, reason, and scope. Popularity is never sufficient evidence. A contraindication, stale or revoked status, missing permission, or unsupported schema excludes the candidate; unresolved conflict forbids auto-apply.

Measure flat personal lookup before proposing a selector. Preregister the pathology, one-generation search budget, candidate identity, fair simple baseline, DEV/VALIDATION/HOLDOUT exposure, permission boundary, prediction, falsification, and rollback threshold. Freeze the candidate source before reading a fresh project family, and retire every used holdout. Credit comes from downstream apply/skip/conflict correctness and completion checks, not from a plausible ranking.

The proposer cannot approve its selection procedure. A deterministic Meta Gate may return `META_PROMOTION`, `META_REJECT`, `META_NARROWER_SCOPE`, `META_NO_ADVANTAGE`, `META_INSUFFICIENT_EVIDENCE`, `META_CONFLICT`, `META_PERMISSION_BLOCKED`, or `META_ROLLBACK`. After promotion, observe one live cycle and run `scripts/apply_live_cycle_rollback.py` against the schema-v4 state. Do not add a vector database, cloud memory, background learner, recursive loop, cross-user learning, arbitrary project sharing, or autonomous publication.
