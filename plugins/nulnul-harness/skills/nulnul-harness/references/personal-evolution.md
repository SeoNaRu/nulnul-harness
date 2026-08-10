# Personal agent evolution

Turn user corrections and agent feedback into tested agent versions, not free-form memory. Keep the user out of routine maintenance without letting agents expand their own authority.

## Responsibilities

- **Navigator** owns the outcome, verified checkpoint, next action, blockers, permissions, and session resume.
- **Worker** completes one bounded job and reports an observable result, failure, workaround, or critique.
- **Coach** reproduces feedback, identifies the nearest responsible layer, and proposes one causal change plus a regression check and rollback.
- **Gate** is independent from the proposal author. It compares the candidate with the last accepted version and records promote, reject, or rollback.

Combine roles for low-risk execution when useful. Separate Coach and Gate for every promotion. When the Coach or Gate is the target, use a fresh evaluator or deterministic check that did not author the candidate. Do not create recursive coaches.

## Persist only when needed

For work that spans sessions or needs agent-specific learning, create `docs/nulnul/evolution.json` from `../assets/evolution-state.template.json`. Validate it with `../scripts/validate_evolution_state.py` after each change.

The Navigator updates a checkpoint only after verifying repository reality. Store the goal, current milestone, completion check, status, last verified evidence, exact next action, blockers, and approved permission changes. On resume, recheck the evidence and continue from the next action instead of reconstructing a plan from chat.

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
3. state the cause, candidate change, reproduction, primary metric, guardrails, permission delta, and rollback;
4. keep the current accepted version active while the candidate is evaluated;
5. never bundle unrelated lessons or let a Worker edit another profile directly.

Workers may critique the Coach. Feed those critiques back as Coach-targeted events. The Coach may author its next version, but only an independent Gate may promote it.

## Gate and promote

Promote only when all are true:

1. the original failure reproduces on the accepted version;
2. the candidate fixes it or improves the named metric;
3. unrelated regressions and guardrails pass;
4. the result is reproducible on representative input;
5. no unapproved permission, cost, credential, external-write, deployment, or publication scope is added;
6. rollback points to the last accepted version.

Reject or roll back otherwise. Never let an agent serve as Gate for its own upgrade. If no independent Gate or valid check is available, leave the proposal pending and continue the project with the last accepted version.

## Scope learning safely

- Default to **agent** or **project** scope.
- Promote to **personal** scope only when the rule generalizes across representative projects or the user explicitly requests personal scope. Store it only in a user-selected private evolution home.
- Promote to **core** or public plugin behavior only with cross-project evidence, full regression checks, and explicit publication approval.
- A broader scope never inherits project data, paths, contacts, credentials, or raw examples.

## Resume the original work

After a promotion, rejection, or rollback, the Navigator records the decision, updates the target version when accepted, checkpoints the verified state, and resumes the unfinished user outcome. Evolution is not task completion.
