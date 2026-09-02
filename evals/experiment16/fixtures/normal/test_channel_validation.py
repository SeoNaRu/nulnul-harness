import json
import unittest
from pathlib import Path

from jobs import submit_job, submit_jobs


class ChannelValidationTests(unittest.TestCase):
    def test_accepts_missing_empty_and_supported_channels(self):
        for channel in (None, "", "web", "cli"):
            request = {"name": "ship"}
            if channel is not None:
                request["channel"] = channel
            queue = []
            original = dict(request)
            self.assertEqual(submit_job(request, queue), {"job": request})
            self.assertEqual(queue, [request])
            self.assertEqual(request, original)

    def test_rejects_unknown_channel_before_single_or_batch_mutation(self):
        invalid = {"name": "ship", "channel": "fax"}
        for operation, requests in (
            (submit_job, invalid),
            (submit_jobs, [{"name": "ok", "channel": "web"}, invalid]),
        ):
            queue = []
            self.assertEqual(
                operation(requests, queue),
                {"error": {"field": "channel", "code": "INVALID_CHANNEL"}},
            )
            self.assertEqual(queue, [])

    def test_catalog_contains_channel_code(self):
        codes = json.loads(Path("contracts/error-codes.json").read_text(encoding="utf-8"))
        self.assertIn("INVALID_CHANNEL", codes)


if __name__ == "__main__":
    unittest.main()
