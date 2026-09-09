# Turn research into a review workbook

[English](README.md) | [한국어](README.ko.md) | [All cases](../README.md)

**Status: expected-output comparison and 5 related tests passed on 2026-09-09.** All records are synthetic; URLs use reserved `.invalid` domains and contacts use `example.invalid`. This models a real four-stage creator-research workflow without publishing source rows, identities, channel URLs, contact details, or private notes. See the [local validation record](../validation-2026-09-09.json).

## Request and visible result

> Turn these synthetic discoveries into a review workbook. Merge repeated channels, exclude previously contacted channels, apply the supplied quality rules, and separate direct contacts from records requiring a second review. Preserve the audit trail.

Inspect [input.json](input.json) and [expected.json](expected.json) side by side. The existing expected output, not a new measurement, contains:

| Stage | Published expected result |
| --- | --- |
| Discovery | 10 input rows collapse to 9 channel records |
| Contact-ready | 2 rows in `leads` |
| Second review | 3 rows in `needs_second_review` |
| Audit | All 9 unique channels in `research_log`, including 4 rejected channels |
| Exclusions | 1 previously contacted channel identifier |

The repeated crypto channel keeps both discovery paths and its better contact route. The channel-only, indirect, and missing-contact records have distinct review reasons. The formula-like name in the irrelevant record is escaped in the audit output.

## Run and completion check

From the repository root:

```bash
python3 scripts/build_youtube_sheets_example.py \
  examples/youtube-sheets/input.json
```

The generated JSON must equal the published expected structure. This command compares parsed values and does not overwrite the expected answer:

```bash
python3 - <<'PY'
import json
import subprocess
import sys
from pathlib import Path

actual = json.loads(subprocess.check_output([
    sys.executable, 'scripts/build_youtube_sheets_example.py',
    'examples/youtube-sheets/input.json',
], text=True))
expected = json.loads(Path('examples/youtube-sheets/expected.json').read_text(encoding='utf-8'))
if actual != expected:
    raise SystemExit('FAIL: output differs from the published expected workbook')
print('PASS: output matches the published expected workbook')
PY
```

## Capability decision and rejection conditions

This casebook reuses the existing [builder](../../scripts/build_youtube_sheets_example.py), fixture, and expected output. No new research agent, Google connector, scraping service, or spreadsheet writer was added. The public fixture does not establish which installed capabilities an original live agent selected.

Previously contacted, inactive, undersized, and irrelevant channels must not enter outreach. A channel-only route must not be called a direct contact, and a duplicate discovery must not create an extra lead. The current published fixture includes those rejection conditions; it does not exercise every possible policy threshold.

## Evidence and limits

This example was already present in the 3.1.0 repository. The product archive contains only the plugin, not these example inputs. The expected-output comparison above and `python3 -m unittest discover -s tests -p 'test_youtube_sheets_example.py' -v` passed on 2026-09-09, with 5 tests. This is a local deterministic rerun, not a new live research session. Runtime, token cost, monetary cost, and an independently measured harness advantage for this case are `unknown`.

The artifact is workbook-shaped JSON, not a generated XLSX file or a live Google spreadsheet. It proves no live YouTube coverage, contact accuracy, outreach success, or financial judgment. The finance-themed channels are synthetic workflow data, not recommendations. Nothing is fetched, uploaded, or sent to a contact.
