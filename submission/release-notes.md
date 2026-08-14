# nulnul harness 2.1.0

Keep governed evolution history without loading all of it into every resumed task.

The standard-library compactor leaves open work and each agent's latest accepted rollback point in `evolution.json`, moves closed feedback, proposals, promotions, and autonomous episodes to an adjacent `evolution.archive.json`, and binds the two with SHA-256. Deterministic validation reconstructs the complete state without exposing the archive to normal model context. Targeted rejected-history lookup remains available before the Coach proposes a matching change.

The real 164,211-byte project state compacted to a 20,560-byte active state in the regression check, with every record identity preserved. Compaction is idempotent, archive tampering fails closed, legacy schema versions remain supported, and no dependency, service, permission, credential, or external-write scope was added.

```bash
codex plugin marketplace add SeoNaRu/nulnul-harness --ref main
codex plugin add nulnul-harness@nulnul-harness
```

```bash
claude plugin marketplace add SeoNaRu/nulnul-harness
claude plugin install nulnul-harness@nulnul-harness
```
