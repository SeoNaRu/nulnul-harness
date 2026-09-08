# nulnul harness 3.1.0

Local release candidate, not published. The published baseline remains 3.0.0.

## Added

- Producer/consumer boundary QA with incremental checks and reproducible negative controls.
- Three on-demand task recipes: web/API changes, data migration/sync, and evidence-backed research.
- Six conditional execution patterns mapped to existing role, Task, Pack, and handoff contracts, without mandatory teams or fixed models.
- A bounded dependency-aware rerun planner and local check executor that reuse only matching verified contracts and input/output fingerprints.
- Skill use, near-miss skip, and follow-up development cases with explicit selection and check-reference scoring.
- Offline preparation of inspected pinned public skill bytes for the existing LOCAL_DIRECTORY competition adapter, with digest, license, permission, and rollback controls.

## Compatibility and limits

Existing 3.0 state formats, acceptance authorities, fast-resume checks, and single-writer rules remain unchanged. No new state migration is required. The package stays skills-only and adds no service, dependency, hook, credential use, or automatic installation.

Planner receipts and development scores are advisory, not Foundation evidence or promotion authority. Exposed examples are not sealed holdouts. Neither measured live quality improvement nor new public adoption is claimed.

## Validation and publication

The clean publication candidate passes all 442 checks and the 100/100 Release Gate product score. The original workspace's untracked `docs/research` directory was preserved outside the release tree, without weakening the legacy-boundary check. Exact-version public Claude and Meta adoption remain pending.

The candidate archive is `dist/nulnul-harness-3.1.0.zip`. Do not reuse a 3.0.0 archive digest, public Claude adoption, or public Meta adoption as evidence for these new bytes. Exact-version public adoption, publication approval, and green publication CI remain required before release completion.
