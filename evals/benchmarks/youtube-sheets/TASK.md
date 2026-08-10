# Offline YouTube → Sheets workbook task

Create `build.py`. It must read `input.json`, write `output.json`, use only the Python standard library, and make no network or external spreadsheet calls.

The output is an object with four arrays in this order: `leads`, `needs_second_review`, `research_log`, `exclusions`.

## Stable identity and deduplication

- The stable key is a trimmed, lowercase `channel_id`. If it is blank, use the final YouTube URL handle, lowercase and without `@`, prefixed with `handle:`.
- Merge repeated discoveries into one record. Keep the first nonblank field value, but keep the contact with the highest rank: `none` < `indirect` < `channel_only` < any `direct_*` type.
- Preserve unique discovery paths in input order, joined with ` | `.
- Sort all row arrays by stable key. `exclusions` is the sorted, lowercase, unique input exclusion list.

## Verdicts

Evaluate one merged record in this order and stop at the first matching rejection:

1. excluded stable key → `already_contacted`
2. category outside `crypto`, `stocks`, `both` → `not_relevant`
3. subscribers outside the inclusive configured range → `subscriber_range`
4. engagement below the configured minimum → `engagement_below_threshold`
5. recent upload age above the configured maximum → `inactive`
6. otherwise → `accepted`

Every merged record produces one `research_log` row with these fields in order:

`channel_id`, `name`, `verdict` (`O` when accepted, otherwise `X`), `reason`, `subscribers`, `engagement`, `recent_upload_days`, `membership`, `discovery_path`.

## Accepted routing

- `direct_email`, `direct_open_chat`, and `direct_telegram` go to `leads`, with contact grades `direct-email`, `direct-open-chat`, and `direct-telegram`.
- `channel_only`, `indirect`, and `none` go to `needs_second_review`.
- Their grades and reasons are respectively:
  - `channel-only` / `channel link has no direct message route`
  - `indirect` / `only an indirect community or social route was found`
  - `none` / `no contact route was found`

Accepted rows first include these fields in order:

`channel_id`, `name`, `channel_url`, `subscribers`, `engagement`, `recent_upload_days`, `membership`, `category`, `discovery_path`.

Lead rows then add `contact`, `contact_grade`. Second-review rows add `current_contact`, `contact_grade`, `review_reason`.

## Spreadsheet safety

Prefix any output string starting with `=`, `+`, `-`, or `@` with a single apostrophe.

Run `python3 build.py input.json output.json` before finishing.
