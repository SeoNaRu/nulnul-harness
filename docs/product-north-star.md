# NULNUL Product North Star

Status: NULNUL 3.0.0 product contract, updated 2026-09-02.

NULNUL is an outcome-first, project-fit, adaptive, evidence-driven, waste-aware
meta-harness. It does not collect globally fashionable capabilities or optimize
Agent, Skill, Plugin, Tool, or infrastructure counts. It forms the strongest
justified capability ecosystem for this project, improves that ecosystem and its
own routing from observed project outcomes, and keeps only changes that evidence
supports.

> The goal is not to collect the best capabilities. The goal is to evolve the best
> capability ecosystem for this project.

## Objective function

First maximize the strongest verified outcome justified by the task, repository,
user intent, permissions, safety, compatibility, reproducibility, and reasonable
cost. Select the quality dimensions that matter to the current work: correctness,
completeness, robustness, maintainability, security, usability, performance,
regression safety, and requirement satisfaction are candidates, not a universal
scorecard.

Only among paths with materially equivalent verified outcomes, minimize duplicate
capability, context, coordination, runtime, maintenance, state, permissions, and
other waste. Waste reduction never overrides a materially stronger verified
outcome.

## A. Outcome first

The user's result is the primary metric. Setup, discovery, capability creation,
evolution, and lower counts are not completion. Use additional specialization or
verification when it materially improves the result; use zero additions when the
current project already provides the strongest justified path.

## B. Project-fit first

Evaluate a capability against this repository's tasks, conventions, failures,
checks, recurring work, and permission boundary. Global popularity and local
ownership are not quality evidence. A mature project-local capability may beat a
famous external candidate; a materially stronger external candidate may replace a
local one. Project fit is determined by evidence, not ownership.

The reasoning contract distinguishes `incapable`, merely `adequate`, `strong`,
`project-fit`, and `preferred` without requiring a new enum or scoring engine.
“Can perform the job” is not automatically “best justified for this project.”

## C. Calm and beginner first

The user states the product outcome, not the harness topology. NULNUL decides which
Skill, Agent, Plugin, Tool, workflow, verification, and project knowledge the work
needs. It does not ask the user to choose Agent count, reviewer architecture, MCPs,
or current AI fashions. It still asks for real authority decisions: authentication,
external installation, permission expansion, destructive work, deployment,
publication, privacy, and meaningful cost.

## D. No AI FOMO

Do not search, recommend, install, or expose a capability because it is new or
popular. Search is bounded and justified by a current gap, meaningful quality gap,
repeated failure, verification weakness, stale capability, missed better method, or
task-specific reason. A strong project-fit capability is a valid stopping point.

## E. Continuity

Resume from verified project state, not raw conversation memory. A valid checkpoint
or evolution state should spare the user from re-explaining established facts.
Changed task files, permissions, intent, or invalid evidence reject fast resume and
fall through safely.

## F. Adaptation and evolution

Project experience may improve Skills, Agents, verification, capability composition,
routing, and the harness decision procedure. A signal is not a promotion:

```text
experience -> bounded feedback -> reproduction -> hypothesis -> candidate
           -> champion comparison -> independent Gate -> promote/reject
           -> live confirmation or rollback
```

Evolution means measured project outcomes improve or remain materially equivalent
while justified waste falls. A longer instruction or newer capability is not an
improvement by itself.

## G. Inspectable and learnable

NULNUL should work without teaching its internals. When requested, bounded evidence
must explain what was used, upgraded, replaced, merged, retired, created, or skipped;
why; how the outcome was verified; what evolved; what can roll back; and where the
next session resumes. Do not expose or store private transcripts, secrets, personal
data, or chain-of-thought.

## H. Waste awareness

Remove duplicate Agents and Skills, obsolete capability, unused Plugins, redundant
reviewers, excess context and coordination, dead state, and unjustified maintenance
only after protecting outcome and verification. More capability is justified only
by more project outcome value.

## Capability lifecycle

Use the current discovery, assembly, evolution, Gate, archive, and rollback contracts;
do not add a lifecycle engine.

| Decision | Meaning |
| --- | --- |
| `KEEP` | The capability remains strong and project-fit. |
| `UPGRADE` | Reproduced project evidence justifies a bounded new version of the same capability. An external replacement is not required. |
| `REPLACE` | A candidate is materially stronger; preserve only proven unique value, activate the winner, and retire the defeated active capability when safe. |
| `MERGE` | An overlapping composition wins on outcome and improves routing, context, or ownership; otherwise keep the clearer current arrangement. |
| `RETIRE` | The job disappeared, a replacement won, the capability is duplicate, unsafe, unmaintained, or removal has no material outcome cost. Keep rollback evidence outside ordinary active context. |
| `CREATE` | A real reusable project job remains uncovered after bounded comparison and project evidence can support a verifiable local capability. |

Capability accumulation is not evolution. A new candidate competes with the active
set. Defeated or obsolete capability does not remain active merely because it once
existed.

## Two evidence-driven evolution layers

1. **Project capability evolution:** improve, replace, merge, retire, or create the
   Skills, Agents, verification, and local knowledge used by the project.
2. **Harness routing evolution:** improve when and how NULNUL selects, activates,
   composes, isolates, verifies, or retires those capabilities.

Do not rewrite a good capability when the reproduced failure is routing. Do not
change routing when a capability itself reproducibly misses the project job. Both
layers use bounded candidates, champion comparison, an independent Gate, live
confirmation, and rollback.

## Project-fit selection contract

```text
define the project outcome
-> inspect current capabilities and verified project state
-> identify a concrete material gap, if any
-> compare KEEP / UPGRADE / external candidate / CREATE / restructuring paths
-> choose the strongest verified project outcome
-> among materially equivalent paths choose lower waste
-> retire defeated or obsolete active capability when safe
```

External capabilities are candidates, not goals. When neither current nor external
capability is good enough, upgrade or create a project-local capability from bounded
project evidence. External installation, authentication, expanded permissions, and
publication keep their existing approval boundaries.

## User-visible evidence

Default output is progressive rather than architectural:

```text
RESULT
VERIFY
RESUME
```

On request, reveal:

```text
HARNESS: USED / UPGRADED / REPLACED / MERGED / RETIRED / CREATED / SKIPPED
WHY / EVIDENCE / EVOLUTION / ROLLBACK
```

Every displayed action must link to machine-valid evidence. Do not invent a merge,
retirement, check, or resume state for presentation.

## NULNUL 3.0 product boundary

NULNUL 3.0 includes verified Session continuity, bounded pre-session Capability
Packs, authoritative checks, Experience and durable Memory, evidence-triggered
Capability and Agent lifecycle decisions, guarded first-order Harness control
evolution, quarantined external competition, and privacy-safe cross-project priors.

It does not provide a hosted service, global Memory, vector database, daemon,
mandatory multi-Agent runtime, automatic trust expansion, universal capability
ranking, unrestricted self-rewrite, or proof of global optimality. Project truth,
user authority, deterministic verification, provenance, and rollback remain the
release boundary.
