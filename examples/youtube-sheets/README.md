# YouTube → Sheets public example

This example models a real four-stage creator-research workbook without publishing any source row, identity, channel URL, contact detail, or private note.

All records are synthetic. URLs use reserved `.invalid` domains and contacts use `example.invalid`.

## What it verifies

1. Duplicate discoveries collapse to one stable channel key.
2. Previously contacted channels are excluded before outreach routing.
3. Configurable quality gates record a specific rejection reason.
4. Direct contacts go to `leads`.
5. Channel-only, indirect, and missing contacts go to `needs_second_review` with distinct reasons.
6. Every candidate remains visible in `research_log` for auditability.
7. Formula-like public text is escaped before spreadsheet output.

## Run

```bash
python3 scripts/build_youtube_sheets_example.py \
  examples/youtube-sheets/input.json
```

The generated JSON must match `expected.json`. The repository test suite verifies the result and ensures the public fixture contains only synthetic identifiers and reserved domains.

This is a deterministic behavior example, not a claim about live YouTube coverage or contact accuracy.
