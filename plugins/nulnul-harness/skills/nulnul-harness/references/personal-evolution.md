# Personal agent evolution

Turn user corrections and agent feedback into tested agent versions, not free-form memory. Keep the user out of routine maintenance without letting agents expand their own authority.

## Responsibilities

- **Navigator** owns the outcome, verified checkpoint, next action, blockers, permissions, and session resume.
- **Worker** completes one bounded job and reports an observable result, failure, workaround, or critique.
- **Coach** is the meta-agent. It reproduces feedback, discovers credible better methods when the current frame is insufficient, and proposes one causal task- or meta-level change plus a regression check and rollback.
- **Gate** is independent from the proposal author. It compares the candidate with the last accepted version and records promote, reject, or rollback.

Combine roles for low-risk execution when useful. Separate Coach and Gate for every promotion. When the Coach or Gate is the target, use a fresh evaluator or deterministic check that did not author the candidate. Do not create recursive coaches.

## Persist only when needed

For work that spans sessions or needs agent-specific learning, create `docs/nulnul/evolution.json` from `../assets/evolution-state.template.json`. Validate it with `../scripts/validate_evolution_state.py` after each change.

New states use schema version 4. Versions 1 through 3 remain readable for compatibility. Version 3 added an executable live-cycle threshold. Version 4 adds bounded autonomous episodes that link a reproduced feedback item, `WHERE`/`WHY` pathology, fixed search budget, rejected archive lookup, candidates, independent evidence, comparable retry baseline, cost, decision, and stop reason without duplicating proposal or promotion fields. Cross-project personal adaptations use their own schema-version-1 registry so project evolution history is not copied into a personal home.

The Navigator owns checkpoint intent but not verification truth. Concise checkpoints use schema version 3 and store the goal, current milestone, completion check, bounded verification file list, explicit `verified`, `failed`, or `unknown` status, last verified summary, exact next action, permission constraints and approvals, and blockers. The completion runner alone writes the sibling verification receipt after executing the check. Fast resume requires the receipt's fingerprint to match current repository reality; older schemas, missing receipts, failed, unknown, and stale states fail closed. Recheck that evidence and continue from the next action instead of reconstructing a plan from chat.

## Convert feedback into evidence

Accept feedback from `user`, `agent`, `test`, or `gate`. Record only:

- a stable feedback id and target agent
- observed and expected behavior
- the smallest reproducible evidence or check
- intended scope: `agent`, `project`, `personal`, or `core`
- triage status

Do not store raw conversation, full logs, secrets, credentials, personal data, or unverifiable opinions. User corrections have high priority but still require a reproduction before they become a durable rule.

## Coach one change

For each reproducible feedback cluster:

1. identify whether the defect belongs to product code, data, tool routing, capability choice, agent profile, handoff, checkpoint, or the Coach diagnosis;
2. target the nearest durable layer and one agent version;
3. state the proposal author, cause, candidate change, reproduction, primary metric, guardrails, permission delta, and rollback; before building a new schema-v3 candidate, also record its `prediction`, flat `expected_delta`, and `falsification_condition` so the Gate can test the proposed mechanism rather than explain the result afterward;
   - set `change_level` to `task` for the work or its harness and `meta` when changing how future improvements are discovered, generated, measured, selected, remembered, or rolled back;
   - for a meta change, record `discovery_evidence`; for personal or core scope also record a representative `transfer_check`;
4. keep the current accepted version active while the candidate is evaluated;
5. never bundle unrelated lessons or let a Worker edit another profile directly.

Workers may critique the Coach. Feed those critiques back as Coach-targeted events. The Coach may author its next version, but only an independent Gate may promote it.

Apply `meta-evolution.md` when the feedback says the user had to find a better method, research direction, skill, plugin, or harness pattern. That is evidence that the improvement mechanism missed an opportunity, not merely a request to add a citation.

## Gate and promote

Promote only when all are true:

1. the original failure reproduces on the accepted version;
2. the candidate fixes it or improves the named metric;
3. unrelated regressions and guardrails pass;
4. the result is reproducible on representative input;
5. no unapproved permission, cost, credential, external-write, deployment, or publication scope is added;
6. rollback points to the last accepted version;
7. the Gate is neither the target agent nor the proposal author;
8. one live cycle after promotion is observed against the recorded metric, and the promotion is rolled back automatically when the metric drops past the stated threshold.

Condition 8 is not optional. A frozen sample judges stored records only; it cannot reproduce what appears at run time — resolver behaviour, load, execution order, or input that grew longer than the sample. Record the metric value at promotion, compare it at the start of the next cycle, and deactivate the candidate on a drop. The frozen sample catches regressions against known cases; the live cycle catches the ones the sample cannot contain. Both are required.

For schema-version-3 state, record `metric_value`, `rollback_operator` (`lt`, `lte`, `gt`, `gte`, `eq`, or `ne`), and `rollback_value`, then run the currently loaded skill's `scripts/apply_live_cycle_rollback.py` against the state. It atomically restores the previous active agent-version pointer when the comparison is true and leaves the state untouched otherwise. Validate the result afterward. The executor intentionally does not run arbitrary rollback commands or edit product files; candidate artifacts must remain versioned and the Gate restores them through the proposal's recorded, permission-safe rollback path.

Reject or roll back otherwise. Never let an agent serve as Gate for its own upgrade. If no independent Gate or valid check is available, leave the proposal pending and continue the project with the last accepted version.

## Define the goal metric once

- Define the goal metric in exactly one function. Every counter — the autonomous loop, status output, shell scripts, reports — imports that function instead of recounting.
- Define it as the deliverable unit after review. Records in `rejected` or `hold` do not count toward the goal.
- Never make a proxy metric the goal. Rows discovered is not rows deliverable, and a loop that reaches its target on the proxy stops early on work that is not done.
- The `init` question is "what unit does this project deliver?", not "which metric do you want to track?".

## Keep rejected knowledge

- Preserve rejected and rolled-back proposals with their candidate diff and the reason for the decision. Keep the diff reachable from the proposal and the reason in the Gate's promotion record.
- The Coach queries rejected and rolled-back proposals for the same target before authoring a proposal, and states why this candidate differs from the one already rejected.
- A feedback record may list `rejected_proposals` with the proposal ids already rejected for it, so the pipeline sees the history the document already holds.
- A loop that keeps only its wins repeats its losses.

## Run one bounded autonomous episode

Run an episode only for reproduced feedback and only when the user requests evolution or ordinary work emits an evolution signal. Freeze `max_candidates`, `max_generations`, `max_evaluation_runs`, `max_failed_candidates`, `max_identical_pathology_retries`, and `max_model_invocations` before candidate generation. Start with one generation and the current accepted champion as parent.

Classify the failure with bounded `pathology.where` and `pathology.why`; use `unknown` instead of inventing a cause. Query rejected and rolled-back proposals before generating candidates. The same pathology and causal mechanism is a rejected replay: deduplicate it without another evaluation unless the candidate records a materially different mechanism. Diversity means distinct causal mechanisms, not wording variants.

The Coach proposes and the independent Gate owns credit. Prefer deterministic completion checks, validators, danger counts, guardrails, and measured costs; free-form self-evaluation cannot promote a candidate. Unapproved permission deltas become `blocked_by_permission` without execution. DEV and VALIDATION may guide the search, but HOLDOUT material remains sealed.

Stop on success, exhausted budget, uninformative feedback, repeated pathology, no advantage over retry, suspected capability bound, permission block, or no promotion. `NO_PROMOTION` is a valid outcome. Validate schema-version-4 episodes with `scripts/validate_autonomous_evolution.py`; do not create a daemon, recursive Coach, multi-generation loop, personal promotion, or cross-project aggregation.

## Measure the Gate itself

- Log every Gate decision: verdict, reason, and target. Include the firing count and the false-positive share in the regular report.
- Once false positives accumulate, people start approving or ignoring the gate by reflex, and the gate stops protecting anything.
- On a false positive the correct response is avoidance, not approval: get the same result without the new permission, and narrow the gate's condition so the same case does not fire again.

## Scope learning safely

- Default to **agent** or **project** scope.
- Promote to **personal** scope only when the rule generalizes across representative projects or the user explicitly requests personal scope. Store it only in a user-selected private evolution home.
- Promote to **core** or public plugin behavior only with cross-project evidence, full regression checks, and explicit publication approval.
- A broader scope never inherits project data, paths, contacts, credentials, or raw examples.
- Before a personal/core transfer claim, apply `generalization.md`; a known regression is validation evidence, not proof that the mechanism generalizes.

## Reuse a verified adaptation personally

Personal scope is an opt-in adaptation registry, not copied project memory. Require a user-selected existing local directory; when none is configured, return `PERSONAL_HOME_REQUIRED`. Never infer a home directory, create hidden global state, or sync it externally. Store only a generalized mechanism, activation conditions, contraindications, bounded source and transfer summaries, permissions, provenance, status, and disable condition.

Project acceptance does not grant personal promotion. Freeze the source evidence and transfer claim, keep fresh cases outside the candidate snapshot, retire each used holdout, and let an independent Personal Gate decide `PERSONAL_PROMOTION`, `NARROWER_PERSONAL_SCOPE`, rejection, insufficient evidence, privacy block, or permission block. Use `scripts/personal_adaptation.py validate-evidence` before promotion.

After promotion, inspect the current project and call `scripts/personal_adaptation.py discover --home <approved-directory> <project-facts.json>`. Apply only an active compatible adaptation after a small project-local check. A contraindication, revoked or stale status, missing permission, or unresolved conflict returns skip or fail-closed instead of automatic application. `promote` deduplicates the same mechanism and activation identity; `revoke` disables it without deleting its evidence.

Never move source code, repository or customer identity, machine paths, credentials, contacts, prompts, responses, transcripts, full command history, raw logs, private issues, or arbitrary project files into the registry. A personal adaptation is a candidate for reuse, not a global rule. Keep Personal Gate separate from the originating Project Gate. Only after three independent families pass this lifecycle may `meta-evolution.md` aggregate their typed privacy-safe summaries; the projects themselves remain isolated.

## Resume the original work

After a promotion, rejection, or rollback, the Navigator records the decision, updates the target version when accepted, checkpoints the verified state, and resumes the unfinished user outcome. Evolution is not task completion.
