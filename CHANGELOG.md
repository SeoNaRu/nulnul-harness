# Changelog

All notable changes to `nulnul harness` are recorded here.

## Unreleased — 1.6.0 Bounded Autonomous Evolution release candidate

- Tested whether one reproduced failure can drive candidate search without one-at-a-time user direction while fixed budgets, permissions, sealed evaluation, and an independent Gate remain in control.
- Added schema-v4 autonomous episodes with machine-readable `WHERE × WHY` pathology, one-generation candidate/model/evaluation budgets, rejected-proposal archive identity, deterministic credit, comparable champion/retry/best-of-N arms, cost, decision, and stop reason.
- Replayed the recorded Claude adoption inventory failure: the archive deduplicated rejected Navigator v16 without evaluation, v17 passed one independent model run and five checks, and the episode stopped on `SUCCESS`. Two champion retries and best-of-2 produced zero primary successes.
- Added fail-closed controls for budget bypass, self-credit, rejected replay, HOLDOUT leakage, unapproved permission expansion, missing prediction or evidence, parent/mechanism identity mismatch, and forced promotion. A fully evidenced `NO_PROMOTION` remains valid.
- Ran a live one-generation episode on a newly reproduced activation failure: two unchanged champion checks each found seven public surfaces with stale agent-team positioning; archive lookup found no replay; a Coach-generated metadata candidate reduced the deterministic metric to zero within two model invocations and one candidate evaluation.
- The independent Gate accepted only the four preregistered metadata edits after product checks, permission/privacy/read-scope guardrails, Release Gate 100/100, and a post-promotion zero-violation live cycle. The episode stopped on `SUCCESS`; the executable rollback threshold remained clear.
- Extended fair baseline accounting only enough to compare deterministic completion checks as well as model invocations, with a negative control that rejects a completion-check budget bypass.
- Kept the claim narrow: live candidate generation and correct bounded stopping are established for this activation-metadata failure family, not as live open-ended generation, broad autonomous improvement, personal promotion, or cross-project aggregation.
- Aligned local product surfaces to 1.6.0. Exact-version public adoption remains pending because the candidate has not been pushed or published; no prior 1.5.0 adoption evidence was relabeled.

## 1.5.0 — 2026-08-12

- Added the 1.5 Generalization Gate as a scoped adjunct to Release Gate: machine-readable DEV/VALIDATION/HOLDOUT exposure, preregistered candidate-source identity, one-shot holdout retirement, and no holdout requirement for ordinary project-local changes.
- Preserved an invalid Ruby holdout as failed validation evidence, added deterministic fixture preflight, and used a new Perl/TAP CLI holdout that was absent from the frozen Navigator v15 snapshot.
- Compared Navigator v15 with a single v14 champion run, three retries, and best-of-3 on equal deterministic trials. v15 blocked stale resume and restored verified resume 3/3; every v14 retry remained unsafe. The result is scoped to checkpoint freshness, not harness-wide generalization.
- Added leakage, reuse, task-failure, identity, budget, relabeling, and privacy controls without a service, daemon, MCP, raw transcript store, or new agent.
- Preserved three sanitized release-adoption nonpasses, rejected the first instruction candidate, and accepted a branch-first bounded plugin inventory only after a fresh GitHub-installed run passed roster, agent, permission, checkpoint, and five completion checks.

- Added bounded Experience Digests to the existing activation runner, with stable stage/owner attribution and aggregate counts but no prompts, responses, transcripts, command lists, or machine paths.
- Reproduced the reported completion-check signal, then disproved it: broad substring telemetry reported `[1, 1, 2]`, while exact classification showed Navigator `0` and independent Gate `1` in all three fresh runs.
- Rejected the one-sentence Navigator ownership candidate on its first falsifying run; it still invoked zero checks and also crossed the fast-path read boundary.
- Added falsifiable proposal fields, exact-command known-answer controls, invalid-stage and raw-transcript controls, a shipped digest validator, Release Gate coverage, and a post-promotion live cycle with executable rollback.
- Closed the 1.4.1 causal question with two three-run conditions: exposing the exact wrapper path still produced Navigator `0`, Gate `1`, and final synthesis without post-implementation verification in every run, falsifying path resolution and supporting final-action ordering.
- Rejected the ordering-only Navigator v14 candidate on its first valid run; it again skipped verification and increased reads, tools, input, and elapsed cost, so Navigator v12 remains active and no completion-count release invariant was added.
- Reproduced the remaining 1.4.2 truth defect in 3/3 fresh interruptions: product state changed with zero Navigator checks while a new process still received `fast_path_ready=true` from stale schema-v2 evidence.
- Bound schema-v3 fast resume to a runner-owned verification receipt over an explicit bounded file list. Mutation, failed, unknown, missing-evidence, and old-evidence controls now fail closed; the candidate reduced unverified mutated-state acceptance from 3/3 to 0/3 without changing Navigator wording.

- Made published setup, workflow, and fast-path token/time measurements release-blocking, with negative controls for token, elapsed-time, and read-scope regressions.
- Expanded activation coverage from four one-shot cases to ten positive/negative project shapes with three runs by default, precision/recall, medians, bounded stderr, and fail-closed summaries.
- Replaced the absolute 250,000-token fast-path ceiling with four counterbalanced champion/candidate rounds and a 20% paired relative budget; Navigator v12 stayed bounded in 4/4 runs and improved median paired input 18.4% across three comparable pairs.
- Added fixture, agent, verification, and total timing plus aggregate tool/read/validator/test counts without retaining raw transcripts; telemetry exposed fixed-order bias and the completion-check attribution gap investigated in 1.4.
- Made performance evidence version-independent: one generic champion/candidate schema now gates setup, resume, workflow, and paired runtime comparisons, with mismatched-pair and regression negative controls.
- Connected the repository root agent to the user's approved external Obsidian LLM Wiki through an ignored local path, updating only durable lessons, index links, and the append-only log without publishing a machine-specific path.

## 1.3.5 — 2026-08-11

- Require an exact checkpoint completion command and execute it through the shipped runner before verified fast resume.
- Make the Release Gate validate a sanitized Claude adoption artifact instead of trusting a hand-edited `passed` status; negative controls reject protected writes.
- Re-run adoption using the GitHub marketplace installation with no local plugin override, preserving both existing agent hashes and passing five recorded checks.

## 1.3.4 — 2026-08-11

- Promoted the Claude Code unattended boundary to a top-level guard: `.claude/**` is classified read-only before roster inspection, and even a host-denied write call fails setup.
- Re-ran the existing-project adoption case after the first run reproduced two protected-profile write attempts. The fresh run made zero such calls, kept and contract-upgraded both agents, enumerated the installed roster, and left a valid fast-resumable checkpoint.
- Closed the Release Gate at 100/100 after the isolated repository test, project-contract validator, checkpoint validator, and documentation-debt check all passed.

## 1.3.3 — 2026-08-11

- Versioned the concise checkpoint contract correctly: new state uses schema v2, schema v1 remains readable but cannot fast-resume, and unknown future versions fail closed.
- Made learning-loop inventory mandatory in both Product and Release Gates, including a negative control that removes the entire verdict array.
- Made legacy migration transactional across its project files and added a failure-injection control that restores every earlier replacement.

## 1.3.2 — 2026-08-11

- Added explicit `verified`, `failed`, and `unknown` checkpoint states; only verified state may enter fast resume, and permission constraints now travel with the concise checkpoint.
- Added a deterministic learning-loop validator so every machine-readable nonpass verdict must link to Coach feedback and a proposal instead of remaining a report-only result.
- Added a safe legacy durable-setup migrator that preserves 1.3.0 contracts and 1.3.1 checkpoint values and permission constraints, starts as unknown, updates the existing host entry, and skips when `evolution.json` already owns continuity.

## 1.3.1 — 2026-08-11

- Added a validated concise resume checkpoint that keeps stable setup evidence out of the host-loaded entry. Three exact A/B trials reduced median input 38.52%, output 30.72%, and reasoning 56.33% versus 1.3.0, and a later transfer cycle passed without reading the full contract.
- Closed the measured-result loop: every reproducible rejected, regressed, failed, or not-established verdict now becomes Coach feedback and one bounded proposal in the same run. Three losing resume mechanisms remain recorded instead of being retried silently.

## 1.3.0 — 2026-08-11

- Added repeatable Git-marketplace installation and update instructions for Codex and Claude Code, with a real semver release boundary.
- Added evolution schema v3 and an atomic standard-library live-cycle rollback executor so numeric thresholds restore the prior active agent-version state instead of remaining prose; schema versions 1 and 2 remain readable, and arbitrary commands or product files are never auto-edited.
- Added a frozen Codex setup A/B: an initial +50.89% input-token regression exposed recursive roster discovery, bounded discovery reduced the accepted candidate to +2.31% versus 1.2.1, and a fresh continuation passed 3/3 project tests and both state validators. Continuation context savings remain unproven and are reported as such.
- Added a seven-invariant Baseline Kernel for repository truth, observable outcomes, before-state checks, capability decisions, permission boundaries, task continuation, and governed evolution.
- Added a deterministic project-setup validator with negative controls so durable contracts cannot omit the inspected roster, completion check, plain-language setup decisions, or continuity fields.
- Grounded the product's meta-harness in Meta and UBC's HyperAgents research and the GeekNews harness discussion, while explicitly avoiding a claim of reproducing the open-ended research system.
- Unified the task side and Coach-led meta side as one editable project program. User-supplied better methods now become discovery feedback, and the Coach may improve its own discovery, assembly, measurement, memory, and improvement procedure.
- Added evolution schema v2 with discovery evidence, transfer checks for broader changes, and a required observed live cycle plus rollback threshold before acceptance; schema v1 checkpoints remain readable.
- Made persistent memory, performance tracking, multi-stage verification, frozen benchmarks, delivery counters, document-debt checks, and state locks job-driven candidates instead of unconditional scaffolding.
- Passed a two-session isolated Codex meta-evolution: Coach v1 stayed active while v2 was gated, a fresh evaluator observed zero relevant-method misses across two mechanisms, accepted v2 with rollback evidence, and passed all 8 fixture tests and negative controls.
- Added an adopt-and-upgrade mode so a setup request on a repository that already has work no longer asks what to build.
- Required the host's installed skills, plugins, and agents to be enumerated before coverage is judged, and reported as a roster.
- Required every existing agent to be classified as kept, upgraded, merged, or removed instead of recreated.
- Added a host surface map covering Codex and Claude Code paths, a context-cost verification dimension, and a durable session entry instruction in day-one output.
- Added multilingual setup triggers to the skill description (English, Korean, Chinese, Japanese) with a deterministic test that fails if a phrase is dropped.
- Published the plugin for Claude Code: `.claude-plugin/plugin.json` and a repository-root `.claude-plugin/marketplace.json`.
- Renamed Harness 100 to Release Gate, matching what the script actually computes.
- Added `references/capability-registry.md`: where to search when the installed roster falls short, with the host marketplace commands, the sources already trusted on the machine, and named context-economy candidates.
- Fixed both halves of the gate that let an adopt run skip day-one output: step 8 judged sufficiency before reading the list, and the list described itself as belonging to a "cold project", which a repository with code and agents read as excluding itself. Measured runs delivered the `CLAUDE.md` contract and nothing else — no checkpoint, no benchmark, no debt detector.
- Added the `positive-adopt-existing-harness` and `positive-multilingual-setup-trigger` scenarios. The trigger passed in four languages. The former adoption result was invalidated after its headless Claude Code run attempted host-protected `.claude/**` writes and left a missing session entry; it now requires a clean rerun, so Release Gate is 90/100 until that evidence exists.
- Treat Claude Code's `.claude/**` tree as a read-only discovery surface in unattended sessions. Session continuity and reusable local workflows now enter through host-loaded repository guidance and `docs/nulnul/` instead of requiring the host to let an agent rewrite its own configuration.

## 1.2.1 — 2026-08-10

- Skip harness activation when a user-named local task contract already contains explicit inputs, outputs, constraints, and a runnable completion check.
- Preserved activation for project setup, capability selection, external writes, multi-session checkpoints, and evidence-gated evolution.
- Added reproducible 3×3 A/B evidence and two cross-task activation guards; Navigator v3 reduced median elapsed time 25.76% versus 1.2.0 without changing exact-result success or intervention rate.

## 1.2.0 — 2026-08-10

- Added equivalent English and Korean product onboarding with deterministic locale, version, command, evidence, and local-link checks.
- Added a direct fast path for repositories whose existing setup already covers the requested work, and bounded discovery to uncovered jobs.
- Fixed evolution-state validation so continuous multi-promotion history and rejected candidates remain valid while the current agent links only to its latest accepted promotion.
- Added proposal-author records and reject promotions whose declared author also serves as Gate.
- Independently gated the bilingual onboarding, fast path, and historical promotion behavior before release.

## 1.1.0 — 2026-08-10

- Added Navigator, Worker, Coach, and independent Gate responsibilities for personal agent evolution.
- Added a removable repository checkpoint for verified multi-session resume.
- Added bounded feedback, versioned proposals, promotion, rejection, and rollback contracts.
- Added a deterministic validator that rejects self-approval, invalid state, sensitive fields, and unapproved permission expansion.
- Added regression tests for Coach upgrades, independent promotion, permissions, and checkpoint validity.

## 1.0.1 — 2026-08-10

- Strengthened implicit activation when repository setup is missing or unknown.
- Added Release Gate, a weighted 100-point release gate covering six positive and three negative scenarios.
- Completed all nine isolated scenarios, including permission, secret, global-registration, and YouTube-to-Sheets checks.
- Added an offline YouTube classification and deduplication benchmark with deterministic scoring.
- Added a synthetic public YouTube-to-Sheets workbook example derived from read-only workflow structure, with no copied identity or contact data.
- Added recurring data-workflow safety rules for stable identity, deduplication, exclusion precedence, review routing, sensitive data, idempotent writes, and formula-safe spreadsheet output.
- Added the Obsidian product and experiment wiki.
- Rebuilt the public README around verified behavior, trust boundaries, and explicit limitations.

## 1.0.0 — 2026-08-10

- Initial skills-only Codex plugin.
- Added reuse-first capability discovery, minimal agent assembly, project setup, and evidence-gated evolution.
