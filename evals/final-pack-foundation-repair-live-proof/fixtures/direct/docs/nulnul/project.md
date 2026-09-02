# nulnul project setup

Status: configured and reusable.

## Goal

Maintain deterministic numeric utilities without changing public request or release behavior.

## Current milestone

Correct inclusive range chunking.

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
| API validation | public request → accepted response or project error | api-contract | local files |
| Release docs | release delta → verified documentation | release-docs | local documentation |

## Candidate evidence

| Candidate | Source | Fit and quality evidence | Permission and license | Verification status | Decision |
| --- | --- | --- | --- | --- | --- |
| project-api-validation | project-local | preserves public request and error-catalog invariants | local project guidance | verified | reuse only for API-validation work |
| project-release-docs | project-local | preserves release-documentation structure | local project guidance | verified | reuse only for release documentation |

## Accepted capabilities

| Capability ID | Job | Activate when | Project check | Status | Version or digest | Logical load target |
| --- | --- | --- | --- | --- | --- | --- |
| project-api-validation | Preserve public request validation and structured error-catalog invariants | public API acceptance, rejection, or structured error behavior changes | api-contract | accepted/current | 13ffff5d869132d68ca2554d64a4b3e425d268f6e99e938bf46cf56881cfa2b9 | capabilities/project-api-validation/SKILL.md |
| project-release-docs | Preserve release documentation | release-note or publication documentation changes | release-docs | accepted/current | a8f8376eba73fc198d5edec7e19ca1736346931854ac56a97d016394b870646e | capabilities/project-release-docs/SKILL.md |

## Capability routing

| Capability | Source | Job | Activate when | Check | Permission boundary | Remove or replace when |
| --- | --- | --- | --- | --- | --- | --- |
| project-api-validation | project-local | public API validation | API behavior changes | api-contract | local files | its job disappears |
| project-release-docs | project-local | release docs | release documentation changes | release-docs | local docs | its job disappears |

Available capabilities and capabilities active for the current task are separate sets.

## Setup decisions

- Reuse now: accepted capabilities only for their named material jobs
- Add now: none
- Needs approval: none
- Skip: unrelated capability and infrastructure loads

## Agent topology

Direct Codex execution with deterministic project checks.

## Evolution baseline

- Representative run: inclusive range chunking with unit verification
- Primary metric: all unit tests pass
- Guardrails: no unrelated state or external writes
- Rollback: restore the last accepted implementation

## Continuity

- Active checkpoint: `docs/nulnul/checkpoint.json`
