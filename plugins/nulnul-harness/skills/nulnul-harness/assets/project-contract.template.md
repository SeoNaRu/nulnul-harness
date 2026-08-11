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

## Inspected roster

- Host surface: {Codex, Claude Code, or another detected host}
- Skills: {inspected installed skills, or none}
- Plugins: {inspected installed plugins, or none}
- Agents: {inspected existing agents, or none}

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

## Setup decisions

- Reuse now: {safe installed capabilities activated for named jobs, or none with reason}
- Add now: {project-local additions for named jobs, or none with reason}
- Needs approval: {downloads, registration, authentication, external writes, deployment, or none}
- Skip: {evaluated capabilities or infrastructure omitted with reason}

## Agent topology

{direct, single-agent, multi-agent, or hybrid topology chosen from concrete work boundaries; include distinct ownership, handoffs, checks, and one synthesis owner}

For multi-session or personally evolving work, record Navigator, Worker, Coach, and independent Gate responsibilities. Point to `docs/nulnul/evolution.json`; do not duplicate its live state here.

## Evolution baseline

- Representative run: {input and expected outcome}
- Primary metric: {current value}
- Guardrails: {cost, privacy, permissions, latency, and regression checks}
- Rollback: {how to restore the last accepted setup}

## Assumptions and accepted evolution

- Assumption: {narrow reversible assumption}
- Revisit when: {failure, test, workaround, or user correction}
- Accepted change: {change, before/after evidence, and removal condition}

## Continuity

- Evolution state: `docs/nulnul/evolution.json` or not needed
- Resume rule: read the last verified checkpoint, confirm repository reality, then perform exactly the recorded next action
- Personal promotion scope: project-local unless a private personal evolution home is explicitly configured
