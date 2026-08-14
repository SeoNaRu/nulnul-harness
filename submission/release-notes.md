# nulnul harness 2.1.1-rc.1

Make the required documentation-debt check fast on tracked repositories without weakening its fallback.

The detector now scans the repository by modification time only when it encounters a document with no Git history. Tracked documents continue to use commit order, and repositories without usable history retain the existing modification-time behavior.

Four counterbalanced A/B rounds against exact `v2.1.0` returned the same debt inventory in every pair while median elapsed time fell from 17.73645 seconds to 0.2308 seconds, a 98.70% reduction on the release repository. Seven focused controls cover Git-history and modification-time paths. A separate same-model context-routing candidate was rejected because it increased paired input tokens by 11.07%; the shipped skill entry remains unchanged.

No dependency, service, permission, credential, or external-write scope was added.

```bash
codex plugin marketplace add SeoNaRu/nulnul-harness --ref main
codex plugin add nulnul-harness@nulnul-harness
```

```bash
claude plugin marketplace add SeoNaRu/nulnul-harness
claude plugin install nulnul-harness@nulnul-harness
```
