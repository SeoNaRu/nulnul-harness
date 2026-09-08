# nulnul harness 3.1.0

Outcome-first delivery improvements for the skills-only Codex and Claude Code plugin. The shipped boundary remains `plugins/nulnul-harness/`; no server, hook, global tool registration, or new live-state writer is added.

## What's new

- Producer/consumer boundary QA with explicit checks and negative controls.
- On-demand web/API, migration/sync, and evidence-research recipes.
- Six conditional execution patterns mapped to existing roles, Tasks, Packs, and handoffs, without fixed teams or model assignments.
- Dependency- and fingerprint-aware partial rerun planning.
- Skill use, near-miss skip, and follow-up development cases with observed selection/check references.
- Offline pinned public Skill preparation into the existing quarantine and competition path. Preparation does not download, install, execute, or grant authority to a candidate.

## Public-adoption repairs

- Bootstrap resolves the host-admitted executing plugin when no project-local contract exists. Receipts bind project, host, manifest, skill, and runtime digests; unsafe local contracts still fail closed.
- Cold Claude setup must enumerate installed plugins and read existing profiles. Product tests do not override unresolved documentation debt or other adoption checks.
- Every existing role is explicitly classified through the existing Setup Plan roster field. Missing, duplicate, ambiguous, or unknown dispositions fail before setup writes. `kept` normalizes to `reuse`; unchanged profiles alone do not establish unchanged responsibilities.
- Existing checkpoints and live-state shapes need no migration. Fresh Setup Plans must use the documented `name: disposition` roster entries.

## Verification

- Full repository suite: **446 passed**. Both-host public-plugin bootstrap and role-disposition negative controls are included.
- Active Codex documentation debt: **0**.
- Release Gate: **100/100**, `release_ready=true`.
- Fresh exact-public Claude adoption: **PASS**, all five completion checks; installed roster inspected, both existing roles classified, profiles and inactive Codex entry preserved, zero protected-path writes.
- Fresh exact-public Meta adoption: **PASS**; same applicable adaptation with 3 flat checks versus 1 Meta check, with no-match, conflict, migration, and rollback controls.
- Frozen product tag CI: [passed](https://github.com/SeoNaRu/nulnul-harness/actions/runs/34212367385). Final evidence is committed to `main`; its resulting CI must be green before stable promotion.
- English and Korean README evidence, version, artifact identity, and claim boundaries are synchronized.

## Artifact

- Tag: `v3.1.0`
- Frozen product commit: `a9fd59e8c5852e8808f6698262e90d389f39f42a`
- Asset: `nulnul-harness-3.1.0.zip`
- Contents: **60 files, 237,942 bytes**
- SHA-256: `7716a8ddfeb43632b4ad836c29deb1fd2981a84d423d2f2705fb88becad9e49d`
- Public download matches the reproducible local archive; installed relative paths and file bytes also match exactly.

## Evidence and limitations

[Claude r4](https://github.com/SeoNaRu/nulnul-harness/blob/main/evals/benchmarks/claude-adopt/release-3.1.0-r4.json) and [Meta r4](https://github.com/SeoNaRu/nulnul-harness/blob/main/evals/meta-evolution/release-3.1.0-meta-r4.json) certify these exact bytes. Three earlier public nonpasses remain unchanged and linked to bounded Coach feedback and proposals; their assets are preserved as [failed preview 1](https://github.com/SeoNaRu/nulnul-harness/releases/tag/v3.1.0-adoption-failed.1), [failed preview 2](https://github.com/SeoNaRu/nulnul-harness/releases/tag/v3.1.0-adoption-failed.2), and [failed preview 3](https://github.com/SeoNaRu/nulnul-harness/releases/tag/v3.1.0-adoption-failed.3).

These are sequential release-regression candidates with one fresh Claude run per artifact, not sealed holdouts, independent mechanism families, or a best-of-N quality advantage claim. The six delivery improvements are implemented and deterministically checked; universal live quality gains, full live host parity, and broader Meta transfer are not claimed. Raw transcripts and authentication remain local-only. Original user research files stay outside the clean release tree; no legacy-boundary test was weakened.
