# nulnul project setup

Status: configured and reusable.

## Goal

Maintain deterministic internal signal-grouping utilities.

## Current milestone

Keep the internal grouping helper correct without changing public API contracts.

Observable completion check: `python3 -m unittest -q`

## Constraints and permissions

- Local product files only; no external writes or credentials.

## Inspected roster

- Host surface: Codex; it owns AGENTS.md and shares this contract with one live-state writer
- Skills: NULNUL plus two accepted project-local capabilities
- Plugins: nulnul-harness
- Agents: direct Codex owner

## Capability requirements

| Required job | Input → output | Quality check | Data or permission boundary |
| --- | --- | --- | --- |
| API validation | API request → accepted response or project error | api-contract | local files |
| Release notes | release delta → verified notes | release-docs | local documentation |

## Candidate evidence

| Candidate | Source | Fit and quality evidence | Permission and license | Verification status | Decision |
| --- | --- | --- | --- | --- | --- |
| project-api-validation | project-local | preserves API error and side-effect invariants | local project guidance | verified | reuse only for API-validation work |
| project-release-docs | project-local | preserves release-note structure | local project guidance | verified | reuse only for release documentation |

## Accepted capabilities

| Capability ID | Job | Activate when | Project check | Status | Version or digest | Logical load target |
| --- | --- | --- | --- | --- | --- | --- |
| project-api-validation | Preserve request-validation and error-catalog invariants | API acceptance, rejection, or structured-error behavior changes | api-contract | accepted/current | v1 | capabilities/project-api-validation/SKILL.md |
| project-release-docs | Preserve release documentation | Release-note or publication documentation changes | release-docs | accepted/current | v1 | capabilities/project-release-docs/SKILL.md |

## Capability routing

| Capability | Source | Job | Activate when | Check | Permission boundary | Remove or replace when |
| --- | --- | --- | --- | --- | --- | --- |
| project-api-validation | project-local | API validation | API behavior changes | api-contract | local files | its job disappears |
| project-release-docs | project-local | release notes | release docs change | release-docs | local docs | its job disappears |

Available capabilities and capabilities active for the current task are separate sets.

## Setup decisions

- Reuse now: accepted capabilities only for their named material jobs
- Add now: none; current jobs are covered
- Needs approval: none
- Skip: unrelated capability and infrastructure loads

## Agent topology

Direct Codex execution with deterministic project checks.

## Evolution baseline

- Representative run: adjacent sign-grouping change with unit verification
- Primary metric: all unit tests pass
- Guardrails: no unrelated state or external writes
- Rollback: restore the last accepted implementation

## Continuity

- Active checkpoint: `docs/nulnul/checkpoint.json`
