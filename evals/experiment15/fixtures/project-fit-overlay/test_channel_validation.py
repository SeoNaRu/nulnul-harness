import json
import unittest
from pathlib import Path

from alerts import create_alert


class ChannelValidationTests(unittest.TestCase):
    def test_invalid_nonempty_channel_is_rejected_before_enqueue(self):
        for value in ("EMAIL", "postal", "web-hook"):
            with self.subTest(value=value):
                request = {"topic": "build", "channel": value}
                outbox = []
                self.assertEqual(
                    create_alert(request, outbox),
                    {"error": {"field": "channel", "code": "INVALID_CHANNEL"}},
                )
                self.assertEqual(outbox, [])
                self.assertEqual(request, {"topic": "build", "channel": value})

    def test_only_current_lowercase_channels_are_accepted(self):
        for value in ("email", "sms", "push"):
            with self.subTest(value=value):
                request = {"topic": "build", "channel": value}
                outbox = []
                self.assertEqual(create_alert(request, outbox), {"alert": request})
                self.assertEqual(outbox, [request])

    def test_error_code_is_catalogued(self):
        codes = json.loads(Path("contracts/error-codes.json").read_text(encoding="utf-8"))
        self.assertIn("INVALID_CHANNEL", codes)


if __name__ == "__main__":
    unittest.main()
