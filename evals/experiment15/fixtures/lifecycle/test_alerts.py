import unittest

from alerts import create_alert


class AlertTests(unittest.TestCase):
    def test_preserves_missing_empty_and_existing_channel_values(self):
        for request in (
            {"topic": "build"},
            {"topic": "build", "channel": ""},
            {"topic": "build", "channel": "email"},
        ):
            with self.subTest(request=request):
                outbox = []
                original = dict(request)
                self.assertEqual(create_alert(request, outbox), {"alert": request})
                self.assertEqual(outbox, [request])
                self.assertEqual(request, original)


if __name__ == "__main__":
    unittest.main()
