# nulnul harness 2.2.1-rc.2

Turn bounded evaluation evidence into user-reviewable feedback without collecting raw conversations.

The existing Experience Digest validator now supports `--feedback-capsule`. It rejects prohibited or malformed evidence before printing deterministic Markdown with plugin and run identity, bounded stage counts, signals, a canonical SHA-256, the validated digest, and blank sanitized request/expected/observed fields.

The bug-report form accepts the capsule as optional supporting evidence. Generation stays local and writes no file; review and any submission remain user-controlled. Exact-archive Meta evidence now has a deterministic privacy-safe capture command, and the decorative 100/100 README shield is gone from both locales. The reproducible packer, product-first Codex activation copy, metadata coverage, and CI documentation-debt check from rc.1 remain included.

No dependency, service, permission, credential, external-write scope, MCP server, hook, app, schema, or additional product skill was added.

This is a local prerelease candidate. Exact-version public Claude and Meta adoption have not been captured, so it is not a final release and must not be pushed to `main` as release-complete evidence.

Plugin and skill validation, 237 tests, documentation debt, and Release Gate 100/100 pass with `local_candidate_ready: true`. The normalized 38-entry archive has SHA-256 `6e28f04efdb8fcf433b035ded0fa2418c776da7bd0248c9f655e715a70606998`; stale public 2.2.0 evidence receives no exact-version credit, so `release_ready: false`.

```bash
codex plugin marketplace add SeoNaRu/nulnul-harness --ref main
codex plugin add nulnul-harness@nulnul-harness
```

```bash
claude plugin marketplace add SeoNaRu/nulnul-harness
claude plugin install nulnul-harness@nulnul-harness
```
