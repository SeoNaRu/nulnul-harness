# Task-sized workflow recipes

Load only the recipe matching the current task. Recipes describe artifact and check boundaries, not installed capabilities or mandatory agents. Inspect the host roster, reuse competitive capabilities, and preserve the existing project contract and live-state owner. Consult `workflow-delivery.md` for relevant boundary checks or partial reruns.

## Web application or API change

Outcome: the requested behavior works through its actual consumer, not merely an isolated endpoint.

| Stage | Input / output | Check and handoff |
| --- | --- | --- |
| Contract | Existing API, UI, request / exact shared shape and errors | Wrapper, nullability, pagination, asynchronous completion |
| Implementation | Stable contract / changed producer and consumer | Optional independent implementation; hand off touched files and runnable checks |
| Boundary QA | Actual producer and consumer / findings or passing evidence | Real integration plus one broken-shape control |
| Completion | Integrated behavior / project result | Existing authoritative completion check, one synthesis owner |

For an API-only or UI-only request, preserve the other side and check its expectations rather than inventing another implementation job. Changed producers invalidate affected consumers, not unrelated pages.

## Data migration or recurring synchronization

Outcome: intended records arrive once, excluded records stay excluded, and interruption is recoverable.

| Stage | Input / output | Check and handoff |
| --- | --- | --- |
| Profile and map | Source sample, destination, exclusions / mapping and identity | Required fields, collisions, privacy, destination permissions |
| Transform | Frozen mapping, bounded input / disposable records | Deterministic identity, deduplication, exclusion precedence |
| Reconcile | Source and destination facts / missing, extra, changed records | Independent reconciliation where materially helpful |
| Recover | Cursor, attempted writes / resumable result | Interrupt, replay, and empty-cycle checks before live mutation |

Apply `data-workflow-safety.md`, including single-writer, idempotency, approval, privacy, and cursor rules. Begin with disposable local data. A recipe or passing transformation never authorizes a production write. Use the real database/API check for remote freshness, not local file hashes.

## Evidence-backed research

Outcome: the answer distinguishes supported facts, inference, disagreement, and unknowns.

| Stage | Input / output | Check and handoff |
| --- | --- | --- |
| Scope | Question and constraints / bounded claims and criteria | Answer the actual question |
| Collect | Claim list / primary sources, URLs, relevant dates | Provenance, authority, relevance, conflicting evidence |
| Synthesize | Inspected sources / claim-to-source mapping | Separate facts, inference, unresolved disagreement |
| Verify | Answer and sources / supported result or corrections | Semantic support, not merely resolving links |

Skip collection when supplied authoritative content is sufficient. Independent collection is optional for genuinely independent claims. A changed source invalidates dependent claims; unrelated supported claims may remain reusable. Do not label subjective review machine-verified without the existing authoritative evidence path.

Direct execution with the same checks remains the baseline for all three recipes. Before claiming improvement, compare a bounded task against the current path under the same outcome check and comparable budget. Examples are development guidance, not holdouts or Release Gate points.

Inspected source samples: [web application](https://github.com/revfactory/harness-100/tree/8e8d35c6a19166614d1af1df85512266d51121ae/ko/16-fullstack-webapp), [data migration](https://github.com/revfactory/harness-100/tree/8e8d35c6a19166614d1af1df85512266d51121ae/ko/34-data-migration), and [research](https://github.com/revfactory/harness-100/tree/8e8d35c6a19166614d1af1df85512266d51121ae/ko/63-research-assistant). Do not import complete rosters, host assumptions, or mandatory teams.
