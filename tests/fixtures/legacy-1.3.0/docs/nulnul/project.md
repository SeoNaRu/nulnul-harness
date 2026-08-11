# nulnul project setup

## Goal

Ship the legacy project safely.

## Current milestone

Keep the health route working.

Observable completion check: python3 -m unittest -v

## Constraints and permissions

- No external writes.
- Deployment requires explicit approval.

## Continuity

- Evolution state: `docs/nulnul/evolution.json`
- Resume rule: read the last verified checkpoint, confirm repository reality, then perform exactly the recorded next action
