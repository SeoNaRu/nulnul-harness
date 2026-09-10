# Trace evidence v1

Status: integration candidate; deterministic producer-to-API/browser checks passed locally.
The changed bytes are not covered by the frozen public release adoption evidence.
This is local outcome observability, not release evidence or a comparative benchmark.

## What NULNUL adds

An ordinary log can show a tool call. NULNUL additionally links an accepted capability
Pack, selected identity, body inclusion before work, the authoritative check and a
task outcome. Trace reads that chain instead of interpreting a "done" message as success.
It does not establish sole causal credit or superiority over another harness.

The existing Foundation writer embeds a schema-version-1 `trace` projection in its
existing `docs/nulnul/.runtime/events/<session_id>.jsonl` records. No parallel writer,
daemon, hook, MCP, external dependency, remote export, or summarization model is added.
The projection is not returned in CLI event output, so the model need not reread it.
Ordinary Direct work does not initialize a Foundation lifecycle just for telemetry.

The projection contains only typed identities, digests, counters and verdict codes.
It excludes goals, prompts, reasoning, source bodies, commands, output and credentials.
Existing raw/local evidence is not made public. Trace validates a strict allowlist and
rejects unsupported schema versions. A producer digest binds the exact five scripts
rather than treating a reported version label as an exact release identity.

## Identity and receipts

Use an explicit `NULNUL_TRACE_SESSION` when the host supplies its session identity.
Codex's `CODEX_THREAD_ID` is used only when supplied and the recorded host is Codex.
Claude may be linked by Trace observing the complete JSON result of the actual
`foundation_runtime.py start-session` command in its existing PostToolUse hook.
An unknown, conflicting, or absent mapping stays unassigned. Repository path and
"most recently active" never establish identity. Existing sessions are not relabelled
or retrospectively backfilled as NULNUL runs.

Trace reads the named canonical Pack/check receipts without executing repository code.
It recomputes the check identity, command hash and Pack digest, checks session/task/
capability identity, and requires selection < Pack < body < work < check.
An unchanged delivery is idempotent. Failed or unassigned delivery does not advance
its cursor. The same task/receipt is not credited once per tool call or replay.

Checkpoint receipts now bind the exact command with `completion_check_digest`.
The existing validator accepts historical receipts for compatibility, but detects a
changed command when the new field exists. Trace is stricter: legacy command-unbound,
missing, stale, ambiguous and oversized evidence cannot produce a current PASS.
Trace hashes only declared files; it neither reruns the recorded command nor proves
that the declared file set covers all product behavior.

## Measurement limits

The UI counts observed tasks, linked checked successes/failures, unverified endings,
open tasks, explicit empty selections, distinct checks, repeated command hashes,
elapsed start/end intervals and Context Pack bytes. Waiting is included in elapsed
time. Bytes are not tokens. Repeated checks are a signal, not proof of waste.
Unverified endings remain in the denominator, not only successful selected-capability runs.

Token consumption, billing, fresh-session resume success and comparative improvement
remain unknown or not measured. No synthetic percentage, cost estimate, superiority
score, evolution eligibility or automatic promotion is manufactured.

Trace reads the newest 16 runtime ledgers and at most 1 MiB of unread data per file.
Larger backlogs stay unconsumed; collection is incomplete, never a failed task.
Views cap stored observations at 2,000 and disclose truncation. Local structured
records are not approved for public sharing or cross-project Memory promotion.

## Checks to run with approval

Harness:

~~~bash
python3 -m unittest discover -s tests -p 'test_trace_evidence.py' -v
~~~

Trace:

~~~bash
pnpm test
~~~

Normal product packing, the full suite, documentation-debt check and Release Gate
still apply before release. This change does not alter the published v3.1.0 tag or
claim its frozen adoption evidence covers the new implementation.
