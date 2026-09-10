# Runtime visibility

Use this read-only view when the user asks whether NULNUL ran, what it did, or why
the development source and an installed copy disagree. No Trace server, notification,
model invocation, global registration or second state writer is required.

```bash
python3 scripts/harness_status.py --root /path/to/project --lang en
python3 scripts/harness_status.py --root /path/to/project --lang ko
python3 scripts/harness_status.py --root /path/to/project --installed-plugin /path/to/installed/nulnul-harness --lang ko
```

The host supplies its actual `CODEX_THREAD_ID` or `NULNUL_TRACE_SESSION`. Without a
matching binding, current operation is unknown. A host may pass an exact `--session-id`
for history; this is an explicit record lookup, not proof that the current host ran it.
Users do not manage these IDs. No latest-session or repository-recency guess is made.

An optional `--installed-plugin` inspects one explicitly supplied on-disk copy.
Only that option enables full shipped-file comparison of the executing plugin source
and the supplied copy: all file paths and contents, including references and assets,
excluding generated `__pycache__` and `.pyc` files. Each tree is bounded to 4,096
directory entries, 1 MiB per file and 16 MiB total. Symlinks, special files, unreadable
paths and exceeded limits make full comparison `unknown`; no partial digest counts
as a match. This is local content comparison, not signed release verification.

`installation_status` is `same` when full file digests match, `stale` when they differ,
and `unknown` when comparison is unavailable. Here `stale` means different from this
source; it does not establish which version is newer. The existing `component_digest`
and `installation_comparison` fields retain their named-component meanings; matching
components can coexist with stale references. `shipped_digest`, `shipped_file_count`
and `shipped_bytes` describe a completed full read. English and Korean output give
the full status and next action. Ordinary status performs no full-tree scan.

Passing the source directory itself is marked `same_path_not_install_proof`, with
full installation status `unknown`. A plugin listing can prove registration and
enablement; it cannot establish which skill body an already-open host thread loaded.

For an existing local Codex development registration, confirm the source with
`codex plugin list --marketplace nulnul-harness --json`. When that installed entry
points to the intended checkout and the user has authorized installation, refresh its cached copy with
`codex plugin add nulnul-harness@nulnul-harness --json`, then compare the copies
again. An unchanged version string does not prove unchanged file contents. Verify
body loading in a fresh host session; refreshing disk files is not evidence that
an already-open session replaced its loaded instructions.

Give a short handoff: task, selected capability and its recorded reason, changes,
check result and evidence limits. Keep `unknown` distinct from explicit Direct work.
Do not invent a selection reason or infer body loading from installation. Recorded
ACTIVE means only the last recorded task state, not that a process is currently alive.
Body loading requires one inclusion event after Pack creation with exactly the Pack's
capability identities. Conflicting, duplicate or reordered inclusion is reported as
invalid evidence, even if another event records a check pass. Malformed session tasks
return unknown status without changing the stored records.

The report separates recorded check exits from a digest- and event-bound historical
Pack/check receipt. A historical pass is not a new test of today's tree. Missing,
conflicting, oversized or wrong-session evidence cannot become a verified pass.
Check attempts and repeated known command hashes are observations, not token savings.
Local maintenance without an accepted capability can record real checks and outcomes,
but must not gain individual capability credit or comparative benefit claims.

The view reads one selected session, at most 1 MiB of its ordered ledger and 4,096
events. It never initializes or repairs state, scans other projects, uploads raw data,
executes project commands or updates installed plugins. Stable records remain owned
by Foundation. Readable output is local and bounded; it is not a public export format.

Do not add this inspection to ordinary no-fit Direct work or a verified fast resume.
Reuse already-read evidence for their short final summary instead of adding overhead.

When changing the projection or validating a trace integration, read
[trace evidence](trace-evidence.md) for receipt, privacy, and attribution requirements.
