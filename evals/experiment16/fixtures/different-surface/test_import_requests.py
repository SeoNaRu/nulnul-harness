import json
import unittest
from pathlib import Path

from imports import queue_import


class ImportRequestTests(unittest.TestCase):
    def test_accepts_default_empty_json_and_ndjson_formats(self):
        for format_name in (None, "", "json", "ndjson"):
            request = {"source": "inventory"}
            if format_name is not None:
                request["format"] = format_name
            outbox = []
            original = dict(request)
            self.assertEqual(queue_import(request, outbox), {"import": request})
            self.assertEqual(outbox, [request])
            self.assertEqual(request, original)

    def test_rejects_unsupported_format_before_outbox_mutation(self):
        request = {"source": "inventory", "format": "xml"}
        original = dict(request)
        outbox = []
        self.assertEqual(
            queue_import(request, outbox),
            {"error": {"field": "format", "code": "INVALID_FORMAT"}},
        )
        self.assertEqual(outbox, [])
        self.assertEqual(request, original)

    def test_catalog_contains_format_code(self):
        codes = json.loads(Path("contracts/error-codes.json").read_text(encoding="utf-8"))
        self.assertIn("INVALID_FORMAT", codes)


if __name__ == "__main__":
    unittest.main()
