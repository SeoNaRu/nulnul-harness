# nulnul harness 2.2.0

Make evolution confirmation executable, fix dirty-worktree documentation debt, and bind release evidence to exact candidate bytes.

A Gate-passing schema-v4 evolution candidate now remains provisional while the confirmed agent version stays active. The shipped executor confirms it only after one healthy observed cycle, or records rollback when the frozen numeric threshold fires. Legacy accepted-version rollback remains compatible.

Documentation-debt checks now distinguish the active host and treat a dirty document as updated for the current change while still reporting dirty source against a clean document. Release freshness requires both exact version and archive SHA; a closed `NO_PROMOTION` episode receives no product-behavior credit.

The consent/continuity behavior candidate was tested and removed. Its corrected DEV/VALIDATION comparison met the core routing observations but failed the frozen strict Gate and controls, so Navigator remains v20 and no consent or ordinary-product routing claim ships in this candidate.

No dependency, service, permission, credential, external-write scope, MCP server, hook, app, or additional product skill was added.

This is the public 2.2.0 release. The downloaded archive is byte-identical at SHA-256 `779bd3d43178925fe53eafa348484d8bf6d0cb1e79fc00a31615b754b71124d0`; fresh exact-version public Claude and Meta adoption passed, Release Gate reports `release_ready: true`, and main CI run `32348453221` passed.

```bash
codex plugin marketplace add SeoNaRu/nulnul-harness --ref main
codex plugin add nulnul-harness@nulnul-harness
```

```bash
claude plugin marketplace add SeoNaRu/nulnul-harness
claude plugin install nulnul-harness@nulnul-harness
```
