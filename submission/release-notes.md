# nulnul harness 2.2.1

Turn bounded evaluation evidence into user-reviewable feedback without collecting raw conversations.

The existing Experience Digest validator now supports `--feedback-capsule`. It rejects prohibited or malformed evidence before printing deterministic Markdown with plugin and run identity, bounded stage counts, signals, a canonical SHA-256, the validated digest, and blank sanitized request/expected/observed fields.

The bug-report form accepts the capsule as optional supporting evidence. Generation stays local and writes no file; review and any submission remain user-controlled. Exact-archive Meta evidence now has a deterministic privacy-safe capture command, and the decorative 100/100 README shield is gone from both locales. Fresh-checkout CI runs the reproducible packer before archive checks; the product-first Codex activation copy, metadata coverage, and CI documentation-debt check from rc.1 remain included.

No dependency, service, permission, credential, external-write scope, MCP server, hook, app, schema, or additional product skill was added.

This is a frozen final candidate. The RC's downloaded asset was byte-identical and its exact-version public Claude and Meta adoption passed. The final artifact still needs its own public-byte and exact-version adoption evidence before release or `main` promotion.

The normalized 38-entry final archive has SHA-256 `f2d320804c5b86a7d1797c8088a36cf824a8009a6b825f19dcda8b8fa2c3388e`. Plugin and skill validation, all 239 tests, documentation debt, and Release Gate 100/100 pass with `local_candidate_ready: true`; the RC evidence is intentionally stale for this final identity, so `release_ready` remains false until exact-final public adoption.

The first clean candidate run exposed a missing pre-test pack step. That nonpass is linked to one bounded proposal; corrected candidate CI run `32685218407` passed and the shipped lifecycle executor confirmed the change.

```bash
codex plugin marketplace add SeoNaRu/nulnul-harness --ref main
codex plugin add nulnul-harness@nulnul-harness
```

```bash
claude plugin marketplace add SeoNaRu/nulnul-harness
claude plugin install nulnul-harness@nulnul-harness
```
