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
- one rejected quality or relevance case; and
- one formula-like text value.

The check must prove deterministic routing, exclusion precedence, unique action keys, reason preservation, safe cell output, and no real personal data.
