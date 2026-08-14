# Changelog

All notable changes to `nulnul harness` are recorded here.

## 2.1.1 — 2026-08-14

- Made the documentation-debt detector defer its recursive modification-time fallback until a document without Git history actually needs it; tracked documents continue to use commit order and the non-Git path remains covered.
- Four counterbalanced exact-`v2.1.0`/candidate A/B rounds preserved the same debt result while median elapsed time fell from 17.73645 seconds to 0.2308 seconds (98.70%).
- Rejected a 26.0%-smaller skill-entry candidate after four same-model paired fast-resume rounds increased input tokens 11.07%, elapsed time 5.44%, output tokens 16.21%, and reasoning output tokens 36.27%; byte size was not promoted as a runtime proxy.
- Added no dependency, service, permission, credential, or external-write scope. Exact public `2.1.1-rc.1` adoption remains required before final promotion.

## 2.1.0 — 2026-08-14

- Added a standard-library evolution compactor that keeps open work and the latest accepted rollback point per agent in the active state while moving closed feedback, proposals, promotions, and autonomous episodes to an adjacent digest-bound archive.
- Added deterministic full-state reconstruction, archive integrity and count checks, idempotent rollback-safe batch writes, targeted rejected-history lookup, legacy schema compatibility, and an archive-tampering negative control.
- Reduced the real 164,211-byte evolution fixture to a 20,560-byte active resume state (87.48%) without losing any record identity; local active parse-and-validation median fell from about 5.5 ms to 0.2 ms while one-time compaction took about 13 ms.
- Fresh exact `v2.1.0` GitHub-tag Claude adoption preserved `AGENTS.md` and both existing agent profiles, made zero protected writes, left one verified shared state writer, and passed all five executable checks. The evidence reader now ignores non-object status messages emitted by newer Claude streams.
- Fresh exact-version Project M retained the correct transactional migration apply while reducing full compatibility checks from 3 to 1; no-match, conflict, privacy, permission, and rollback controls passed without reopening retired holdouts.
- The full 218-test suite passed and Release Gate closed at 100/100 with `release_ready=true`; the packaged archive remained byte-identical at SHA-256 `be76a1afa14c91f7a613aa04fba7b4058eb8c37e291879183cda270a76f43811`.

## 2.0.1 — 2026-08-13

- Added a standard-library active-host session-entry writer: Codex updates only `AGENTS.md`, Claude Code updates only `CLAUDE.md`, and both reuse exactly one existing `docs/nulnul/` checkpoint or evolution writer.
- Verified Codex-first, Claude-first, and both sequential adoption orders; the inactive host entry remained byte-identical, existing guidance and `.claude/**` remained unchanged, ambiguous state failed closed, and repeated sync was idempotent.
- Promoted Navigator v20 after one post-freeze mixed-host cycle passed without rollback, permission expansion, external writes, dependencies, services, or concurrent-mutation claims.
- Published annotated tag `v2.0.1` at `5198487` with archive SHA-256 `5b0d69f1fba2df23e6d2d78a07d25128a65f0ff901754d53eadf104bfd011aed`; the downloaded public asset was byte-identical.
- Published `v2.0.1-rc.1` outside `main`; the downloaded archive matched local bytes. A fresh GitHub-tag-installed Claude run with normal setup intent preserved `AGENTS.md` and two agent profiles, created only `CLAUDE.md` plus shared state, and passed all five adoption checks. Fresh Project M also retained the transactional migration apply while reducing full checks 3 to 1; migration, no-match, and conflict controls passed.
- Fresh exact `v2.0.1` adoption repeated those results on new project shapes: Claude preserved the Codex entry and both existing agent profiles, one shared state writer remained, and all five checks passed. Exact-final Project M kept the correct apply at 3-to-1 checks and passed migration, no-match, conflict, privacy, and permission controls.

## Post-2.0 dogfooding — 2026-08-13

- Reproduced one post-2.0 design dogfooding correction: approved personal knowledge, project context, and `frontend-design` were all read, but the selected skill's role was not made explicit until the user raised the authority concern. The evidence retains bounded attribution only.
- Evaluated two one-generation capability-authority candidates across six same-model runs. All arms preserved the correct project/personal design choices, zero unrelated personal reads, zero permission expansion, and an active domain skill, but neither candidate improved explicit role attribution reproducibly; the independent Gate returned `NO_ADVANTAGE`.
- Removed both candidates, kept Navigator v19 and public version 2.0.0 unchanged, and made no Personal, cross-domain, runtime, token, or aesthetic-quality claim. A different mechanism requires new dogfooding evidence.
- Reopened the question with a combined intent/means episode after a separate web-stack dogfooding report. Six evaluator-leaking DEV calls were retained but excluded before candidate generation; four corrected natural champion runs then reproduced one project-direction override and two unnecessary backend switches, while falsifying the narrower claim that the champion was stuck on Python templates.
- Tested one new main-workflow intent/means gate in six bounded runs. It preserved explicit Flask and a suitable production Python stack, kept `frontend-design` active, read no unrelated personal source, and changed no permission, but failed both repeated design and both repeated web-stack primary cases. The Gate returned `NO_PROMOTION`, removed the candidate, skipped live credit and README behavior claims, and kept 2.0.0/Navigator v19 unchanged.
- Refined the same pathology to decision scope and architecture-layer spillover. A one-generation scoped artifact plus deterministic validator passed all 14 structural controls and valid greenfield, existing-Python, explicit-rewrite, and required-dependency cases, but the nine-run model candidate failed both design and both web primary repeats plus the Flask artifact control.
- Rejected and removed the shipped candidate because the artifact proved only internal consistency: unbound or incorrect repository status, source, and value claims could still validate. Kept 2.0.0/Navigator v19, reserved live credit for an accepted candidate only, and documented the human product philosophy separately from verified behavior in both README locales.
- Froze one bounded repository-receipt candidate before six same-model runs. It independently re-parsed accepted design contracts and Python entrypoints, reran declared backend checks, fingerprinted only retained anchors, passed both repeated design and both repeated web cases, preserved approved quiet tone and `frontend-design`, allowed an exact current-user override and a failing required-capability challenge, and passed all sixteen declared evidence controls with no permission or external-write delta.
- Returned `NO_PROMOTION` because this repository-scoped experiment contained no fresh normal-intent real design/web task for the mandatory live cycle; known fixtures were not relabeled as live evidence. The frozen candidate remains evaluation-only, the two earlier rejections remain archived, README behavior claims and the shipped plugin remain unchanged, and 2.0.0/Navigator v19 stay active.

## 2.0.0 — 2026-08-13

- Promoted two additional privacy-safe personal adaptation families through the existing 1.7 lifecycle: transactional local multi-file migration and machine-linked nonpass verdicts. Each passed two positive transfer shapes, one negative skip, a fresh-project reuse, and an independent Personal Gate; the approved Personal Home now validates with three distinct families.
- Added a schema-version-1 typed cross-project evidence model containing activation boundaries, contraindications, transfer/skip/failure counts, source identity, guardrails, permissions, privacy class, freshness, status, and evidence-backed relations without raw workload or repository identity.
- Measured the 1.7 flat lookup and a status-permission heuristic across DEV/VALIDATION cases. Both made the same correct decisions but opened nine full compatibility checks, six irrelevant, establishing the selection pathology before candidate generation.
- Preregistered one candidate, one generation, nine deterministic evaluation runs, zero model invocations, two relation changes, one policy surface, no new permissions, sealed HOLDOUT identity, falsification conditions, and an executable rollback threshold.
- Froze `meta-selector-v1` before exposing fresh Project X, no-relevant-adaptation, and unresolved-conflict cases. The independent Meta Gate recorded `META_PROMOTION`: flat 9 checks, simple heuristic 9, candidate 4, with all three decisions and Project X downstream checks passing.
- Recorded one scoped `COMPLEMENTS` relation between checkpoint freshness and nonpass linkage after their joint downstream result. Other relationships remain `UNKNOWN`; the conflict control was not promoted as a real relationship.
- Observed one live cycle in the active harness: the selector opened one full check, selected only nonpass linkage, validated the downstream learning result, changed no permissions, and triggered no rollback. The shipped schema-v4 rollback executor also passed a threshold-breach negative control.
- Added fail-closed controls for insufficient or duplicate families, raw/private aggregation, revoked/stale evidence, false activation, contraindications, popularity-only selection, permission mismatch, unsupported schema, hidden failed transfer, unsupported relations, cloned shapes, HOLDOUT leakage/reuse, proposer self-approval, rejected replay, unbounded generation, forced no-match, conflict auto-resolution, and missing rollback.
- Published non-main `2.0.0-rc.1`; archive identity and fresh cross-project Meta adoption passed, including flat 3 versus meta 1 compatibility checks on Project M, no-match, conflict, live-cycle, and rollback controls.
- Preserved two authenticated fresh Claude `2.0.0-rc.1` nonpasses: both kept the existing profiles, protected paths, permissions, checkpoint truth, and repository checks, but omitted the durable adopt-and-upgrade contract. `2.0.0-rc.2` contains only the bounded instruction correction and remains blocked on fresh exact-version adoption.
- Fresh exact `2.0.0-rc.2` Claude adoption passed after creating the validated durable contract: both existing agent hashes were preserved, protected writes stayed zero, all five checks passed, and exact public GitHub provenance was retained across Claude's `source=git` marketplace label.
- Published final annotated tag `v2.0.0` at `7fa8af0` with archive SHA-256 `82b5e4e13da6866d96fa53cdce7763a4c67aa892610b2c2423b0a73613469502`; the downloaded public asset was byte-identical.
- Fresh exact `2.0.0` Claude adoption preserved both existing profiles, made zero protected writes, created the validated durable contract and verified checkpoint, and passed all five executable checks.
- Fresh exact-final Personal/Meta smoke loaded the same three families without user-named adaptations, selected transactional migration for Project M, reduced full compatibility checks from 3 to 1, and passed downstream migration. Public no-match, conflict, exposure, permission, privacy, and rollback controls remained valid over the frozen selector identity.
- Release Gate closed at 100/100 with `local_candidate_ready=true` and `release_ready=true`; Generalization remains `narrower_scope`, and no token, runtime, universal, cross-user, background-learning, or open-ended-improvement claim is made.

## 1.7.0 — 2026-08-13

- Tested whether a project-verified mechanism can become a privacy-safe personal adaptation rather than copied project memory. The accepted checkpoint-freshness receipt was selected because it closed a reproduced 3/3 stale-resume defect, passed its independent Gate and live cycle, has a binary transfer metric, and needs no project identity or raw artifact.
- Added one standard-library personal-adaptation CLI. It requires a user-selected existing local home, validates preregistered transfer evidence, writes only generalized bounded adaptations, deduplicates identical mechanism/activation identities, detects conflicts, checks new-project compatibility, and supports revocation. Missing home returns `PERSONAL_HOME_REQUIRED`; no default home, cloud store, daemon, MCP, or global rule was added.
- Froze the source evidence and candidate at ref `435a8e5` before three new one-shot transfer cases. Node and Make project shapes each blocked stale resume and restored it after the exact check; a one-shot shape correctly returned `SKIP`. All used cases were retired after first exposure.
- The independent Personal Gate recorded `PERSONAL_PROMOTION` only for durable local projects with deterministic completion checks, bounded verification files, and checkpoint receipt support. Raw source, private identity, paths, credentials, prompts, transcripts, logs, permission expansion, hidden failures, self-approval, false activation, conflict, stale/revoked use, duplicate identity, and universalized narrower scope fail closed.
- In an isolated opt-in Personal Home, a fresh data-CLI Project D discovered the adaptation without user restatement, passed compatibility, applied the already shipped checkpoint mechanism, and passed its exact completion check. A no-registry baseline also passed task behavior but discovered no approved adaptation; no token, elapsed-time, or broad task-quality win is claimed.
- Configured one explicit private local Personal Home, promoted the verified adaptation, and passed its registry and privacy validation without storing the path publicly.
- Published annotated tag `v1.7.0`; the exact public artifact passed fresh personal-adaptation reuse, incompatible-project skip, revocation, and a separate headless Claude Code adoption that preserved two agent profiles, made zero protected writes, produced verified resumable state, and passed five executable checks.
- Closed the release only after the exact-version evidence commit passed main CI in run `31651306556`.

## 1.6.0 — 2026-08-12

- Tested whether one reproduced failure can drive candidate search without one-at-a-time user direction while fixed budgets, permissions, sealed evaluation, and an independent Gate remain in control.
- Added schema-v4 autonomous episodes with machine-readable `WHERE × WHY` pathology, one-generation candidate/model/evaluation budgets, rejected-proposal archive identity, deterministic credit, comparable champion/retry/best-of-N arms, cost, decision, and stop reason.
- Replayed the recorded Claude adoption inventory failure: the archive deduplicated rejected Navigator v16 without evaluation, v17 passed one independent model run and five checks, and the episode stopped on `SUCCESS`. Two champion retries and best-of-2 produced zero primary successes.
- Added fail-closed controls for budget bypass, self-credit, rejected replay, HOLDOUT leakage, unapproved permission expansion, missing prediction or evidence, parent/mechanism identity mismatch, and forced promotion. A fully evidenced `NO_PROMOTION` remains valid.
- Ran a live one-generation episode on a newly reproduced activation failure: two unchanged champion checks each found seven public surfaces with stale agent-team positioning; archive lookup found no replay; a Coach-generated metadata candidate reduced the deterministic metric to zero within two model invocations and one candidate evaluation.
- The independent Gate accepted only the four preregistered metadata edits after product checks, permission/privacy/read-scope guardrails, Release Gate 100/100, and a post-promotion zero-violation live cycle. The episode stopped on `SUCCESS`; the executable rollback threshold remained clear.
- Extended fair baseline accounting only enough to compare deterministic completion checks as well as model invocations, with a negative control that rejects a completion-check budget bypass.
- Kept the claim narrow: live candidate generation and correct bounded stopping are established for this activation-metadata failure family, not as live open-ended generation, broad autonomous improvement, personal promotion, or cross-project aggregation.
- Verified a fresh GitHub-marketplace-installed 1.6.0 Claude Code adoption: two existing agent profiles remained byte-identical, protected writes stayed at zero, the checkpoint was fresh and fast-resumable, and five executable checks passed. No prior 1.5.0 evidence was relabeled.
- Fixed an evidence-attribution defect exposed by that run: one bounded shell loop actually read both agent profiles but the sanitizer recognized only separate structured read tools. The Gate now accepts the bounded read behavior and retains a paths-only negative control.
- Preserved the failed main CI caused by pushing a known stale exact-version artifact as Navigator feedback. Navigator v18 now requires exact-version evidence or a non-main publication candidate before a version-changing main push and an observed green CI before completion; the repair passed main CI in run 31570823735.
- Published annotated tag `v1.6.0` and a GitHub Release from green commit `5df8309`; the downloaded public archive is byte-identical to the validated local bundle with SHA-256 `90747ddc02f93d227409f322e2d65bc9a5a8c807a760058e5d20e114aea4c0bf`.
- Reinstalled 1.6.0 from the refreshed public GitHub marketplace into a new isolated project after publication. The run executed installed-plugin inventory, kept both agent profiles byte-identical, made zero protected writes, produced verified resumable state, and passed five checks with zero public-positioning violations.
- Preserved the initial post-public sanitizer nonpass: explicit bounded `cat` reads of both profiles were rejected despite valid behavior. Gate v9 now credits explicit content reads for every declared profile, retains the paths-only negative control, and requires machine-readable release tag, commit, asset digest, run identity, and positioning evidence.

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
