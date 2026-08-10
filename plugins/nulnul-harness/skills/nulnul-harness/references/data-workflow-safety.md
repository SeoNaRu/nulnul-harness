# Recurring data workflow safety

Apply this reference when a workflow repeatedly discovers, classifies, reviews, or syncs records such as leads, creators, products, jobs, or research results.

## Identity and deduplication

- Choose one stable provider identifier as the primary key. Use a normalized canonical URL or handle only as a documented fallback.
- Merge repeated discoveries before routing or writing. Preserve distinct discovery paths as evidence instead of creating duplicate action rows.
- Make reruns idempotent: update the existing key, do not append a second logical record.

## Exclusions and state

- Apply contacted, blocked, rejected, deleted, or opted-out exclusions before any action queue or external write.
- Keep discovery evidence separate from actionable output.
- Use explicit states such as accepted, needs review, and rejected. Record one concrete reason for every review or rejection.
- Let verified human decisions override heuristics on later runs until an authorized rule changes them.

## Never record "not checked" as "checked"

- Every verification field carries at least three states: `verified`, `failed`, and `unknown`.
- A skipped, timed-out, quota-blocked, or tool-missing check is `unknown`. It is not `failed` and never `verified`.
- Writing `unknown` as `verified` destroys the ability to ask later which records were actually checked.
- Writing `unknown` as `failed` deletes healthy records and is not reversible from the stored state.

## One writer per state file

Atomic writes (temp file plus rename) prevent torn files. They do not prevent lost updates. When each process holds the whole state in memory and rewrites it, the last writer silently overwrites the others.

- One writing process per state file. A long-running loop takes an exclusive file lock at start and refuses to run as a second instance.
- Lock file descriptors are inherited by child processes. Killing the parent alone leaves the lock held and the loop half-alive; stop the whole process group.
- Stop the loop before editing state by hand. This is detectable: warn when a process without the loop's marker environment variable writes state while the loop holds the lock.
- Parallel collectors each write their own shard and merge in exactly one place. Never let two collectors write one file.
- Guard external snapshots and uploads against collapse: refuse the write when the row count falls below a set fraction of the previous accepted snapshot. This stops a damaged local state from propagating outward.

## Validate checks against a negative control

- Every validity check is proven with a control that must fail: a nonexistent id, domain, or link. If the nonexistent target returns the same answer as a real one, the check measures nothing.
- Prefer signals the medium cannot fake:
  - mail domains: resolve `MX`, not `A`; an `A` record does not mean the domain accepts mail;
  - messaging accounts: a generic landing or invite page renders for nonexistent handles, so use a real profile field such as the display name;
  - chat or group links: HTTP status and page title stay valid for dead links, so read the body text.
- Record which signal was checked, so a later change of signal is visible.

## Persist the cursor even when nothing happened

- Write a run record on every cycle, including cycles that found zero new records.
- Any cursor, offset, or window derived from run history freezes without that record: the next cycle recomputes the same range, finds zero again, writes nothing again, and the loop reinforces itself.
- "There was nothing to do" and "it did not run" are different facts. Confusing them sends the investigation to the wrong layer.

## Sensitive data

- Treat emails, phone numbers, private handles, personal messaging routes, notes, and contact history as sensitive even when they were found on public pages.
- Do not copy source identities or contact values into public examples, evals, logs, or repository memory. Use synthetic records and reserved domains.
- Persist only fields required by the approved workflow and keep external-write scope explicit.

## Safe writes

- Escape untrusted text that a spreadsheet could interpret as a formula.
- Preserve headers, validation, types, and manual-review columns during updates.
- Prefer keyed upserts and bounded batch writes over append-only retries.
- Verify no excluded or duplicate key reached an action queue after the write.

## Minimum check

Use a small synthetic fixture containing:

- one duplicate discovered through two paths;
- one previously excluded record;
- one accepted direct record;
- one record for each manual-review reason;
- one rejected quality or relevance case;
- one record whose verification could not run, expected to stay `unknown`;
- one cycle that discovers nothing, expected to still advance the run record; and
- one formula-like text value.

The check must prove deterministic routing, exclusion precedence, unique action keys, reason preservation, `unknown` never collapsing into `verified` or `failed`, cursor persistence on an empty cycle, safe cell output, and no real personal data.
