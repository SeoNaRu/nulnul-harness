# nulnul project setup

Status: initial, removable hypothesis.

## Goal

{product outcome and intended user}

## Current milestone

{smallest outcome that must work now}

Observable completion check: {user-visible or machine-verifiable result}

## Constraints and permissions

- {non-negotiable constraint}
- External services, credentials, deployment, public writes, and global configuration require explicit user approval.

## Capability requirements

| Required job | Input → output | Quality check | Data or permission boundary |
| --- | --- | --- | --- |
| {job} | {input → output} | {observable check} | {local, public, private, external write, credential, cost} |

## Candidate evidence

| Candidate | Source | Fit and quality evidence | Permission and license | Verification status | Decision |
| --- | --- | --- | --- | --- | --- |
| {existing skill, plugin, or native tool} | {installed, curated, or public source} | {evidence} | {boundary} | {verified, provisional with gap, or rejected} | {reuse or reject with reason} |

Create a custom capability only when the checked candidates are inadequate.

## Capability routing

| Capability | Source | Job | Activate when | Check | Permission boundary | Remove or replace when |
| --- | --- | --- | --- | --- | --- | --- |
| {name} | {source and revision when needed} | {necessary non-overlapping job} | {trigger} | {observable check} | {authority limit} | {removal condition} |

Available capabilities and capabilities active for the current task are separate sets.

## Agent topology

{direct, single-agent, multi-agent, or hybrid topology chosen from concrete work boundaries; include distinct ownership, handoffs, checks, and one synthesis owner}

## Evolution baseline

- Representative run: {input and expected outcome}
- Primary metric: {current value}
- Guardrails: {cost, privacy, permissions, latency, and regression checks}
- Rollback: {how to restore the last accepted setup}

## Assumptions and accepted evolution

- Assumption: {narrow reversible assumption}
- Revisit when: {failure, test, workaround, or user correction}
- Accepted change: {change, before/after evidence, and removal condition}
