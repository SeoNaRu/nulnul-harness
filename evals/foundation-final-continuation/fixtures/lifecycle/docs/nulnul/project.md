# nulnul project setup

Status: legacy setup awaiting Foundation adoption.

## Goal

Maintain a webhook-delivery registry with verified local API conventions.

## Current milestone

Adopt the v2.3 Foundation contract and supported Codex activation lifecycle.

Observable completion check: `python3 -m unittest -q`

## Constraints and permissions

- Keep all work local and never modify Codex project trust.

## Inspected roster

- Host surface: Codex; it owns AGENTS.md
- Skills: project-api-validation and project-release-docs
- Plugins: nulnul-harness
- Agents: direct Codex owner

## Capability requirements

| Required job | Input → output | Quality check | Data or permission boundary |
| --- | --- | --- | --- |
| API validation | webhook request → accepted response or project error | api-contract | local files |
| Release notes | release delta → verified notes | release-docs | local documentation |

## Candidate evidence

| Candidate | Source | Fit and quality evidence | Permission and license | Verification status | Decision |
| --- | --- | --- | --- | --- | --- |
| project-api-validation | project-local | preserves webhook error envelope, pre-registry rejection, and catalog | local project guidance | verified | reuse for API validation |
| project-release-docs | project-local | preserves release documentation | local project guidance | verified | reuse for release documentation |

## Capability routing

| Capability | Source | Job | Activate when | Check | Permission boundary | Remove or replace when |
| --- | --- | --- | --- | --- | --- | --- |
| project-api-validation | project-local | Preserve request-validation and error-catalog invariants | API acceptance, rejection, or structured-error behavior changes | api-contract | local files | its procedure loses verified value |
| project-release-docs | project-local | Preserve release documentation | release-note or publication documentation changes | release-docs | local docs | its job disappears |

Available capabilities and capabilities active for the current task are separate sets.

## Setup decisions

- Reuse now: verified project-local capabilities for their named jobs
- Accepted revisions: `project-api-validation` v1 and `project-release-docs` v1
- Add now: v2.3 Foundation contract and Codex project activation rule
- Needs approval: Codex project trust remains user and host owned
- Skip: global rules, services, and unrelated infrastructure

## Agent topology

Direct Codex execution with deterministic verification and one state writer.

## Evolution baseline

- Representative run: webhook delivery-mode validation change with catalog check
- Primary metric: product and catalog checks pass
- Guardrails: local files only, bounded context, no trust mutation
- Rollback: remove only the exact NULNUL project setup surfaces

## Continuity

- Active checkpoint: `docs/nulnul/checkpoint.json`
