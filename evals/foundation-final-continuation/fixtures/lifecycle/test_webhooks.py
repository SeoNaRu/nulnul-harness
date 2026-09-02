import unittest

from webhooks import register_webhook


class WebhookTests(unittest.TestCase):
    def test_preserves_missing_empty_and_existing_delivery_modes(self):
        for request in (
            {"endpoint": "https://example.test/hook"},
            {"endpoint": "https://example.test/hook", "delivery_mode": ""},
            {"endpoint": "https://example.test/hook", "delivery_mode": "sync"},
        ):
            with self.subTest(request=request):
                registry = []
                original = dict(request)
                self.assertEqual(register_webhook(request, registry), {"webhook": request})
                self.assertEqual(registry, [request])
                self.assertEqual(request, original)


if __name__ == "__main__":
    unittest.main()
