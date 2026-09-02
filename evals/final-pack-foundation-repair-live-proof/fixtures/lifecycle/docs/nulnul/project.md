# nulnul project setup

Status: configured and reusable.

## Goal

Maintain a job-submission API with verified local validation conventions.

## Current milestone

Add region validation while preserving the project error contract.

Observable completion check: `python3 -m unittest -q && python3 tools/verify_error_catalog.py`

## Constraints and permissions

- Keep all work local; capability Packs carry context but no structural authority.

## Inspected roster

- Host surface: Codex; it owns AGENTS.md and shares this contract with one live-state writer
- Skills: NULNUL plus two accepted project-local capabilities
- Plugins: nulnul-harness
- Agents: direct Codex owner

## Capability requirements

| Required job | Input → output | Quality check | Data or permission boundary |
| --- | --- | --- | --- |
| API validation | job request → accepted job or project error | api-contract | local files |
| Release docs | release delta → verified documentation | release-docs | local documentation |

## Candidate evidence

| Candidate | Source | Fit and quality evidence | Permission and license | Verification status | Decision |
| --- | --- | --- | --- | --- | --- |
| project-api-validation | project-local | preserves missing, empty, accepted, and cataloged-invalid request behavior | local project guidance | verified | reuse for API validation |
| project-release-docs | project-local | preserves release documentation | local project guidance | verified | reuse only for release documentation |

## Accepted capabilities

| Capability ID | Job | Activate when | Project check | Status | Version or digest | Logical load target |
| --- | --- | --- | --- | --- | --- | --- |
| project-api-validation | Preserve public request validation and structured error-catalog invariants | public API acceptance, rejection, or structured error behavior changes | api-contract | accepted/current | 13ffff5d869132d68ca2554d64a4b3e425d268f6e99e938bf46cf56881cfa2b9 | capabilities/project-api-validation/SKILL.md |
| project-release-docs | Preserve release documentation | release-note or publication documentation changes | release-docs | accepted/current | a8f8376eba73fc198d5edec7e19ca1736346931854ac56a97d016394b870646e | capabilities/project-release-docs/SKILL.md |

## Capability routing

| Capability | Source | Job | Activate when | Check | Permission boundary | Remove or replace when |
| --- | --- | --- | --- | --- | --- | --- |
| project-api-validation | project-local | public API validation | request-validation behavior changes | api-contract | local files | its job disappears |
| project-release-docs | project-local | release docs | release documentation changes | release-docs | local docs | its job disappears |

Available capabilities and capabilities active for the current task are separate sets.

## Setup decisions

- Reuse now: verified project-local capabilities for their named jobs
- Add now: no activation rule, trust mutation, restart, daemon, or service
- Needs approval: none
- Skip: retired runtime-exclusive activation surfaces

## Agent topology

Direct Codex execution with a pre-session Capability Pack and deterministic checks.

## Evolution baseline

- Representative run: job-region validation with catalog verification
- Primary metric: product and catalog checks pass
- Guardrails: local files only, bounded context, no structural authority from Packs
- Rollback: restore the last accepted implementation

## Continuity

- Active checkpoint: `docs/nulnul/checkpoint.json`
