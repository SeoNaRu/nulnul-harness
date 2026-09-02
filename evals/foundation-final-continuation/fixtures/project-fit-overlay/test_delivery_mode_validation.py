import unittest

from webhooks import register_webhook


class DeliveryModeValidationTests(unittest.TestCase):
    def test_accepts_only_the_registered_nonempty_modes(self):
        for value in ("sync", "async", "batch"):
            registry = []
            request = {"endpoint": "https://example.test/hook", "delivery_mode": value}
            self.assertEqual(register_webhook(request, registry), {"webhook": request})
            self.assertEqual(registry, [request])

    def test_rejects_other_nonempty_modes_before_registry_mutation(self):
        for value in ("SYNC", "deferred", " batch", "batch "):
            registry = []
            request = {"endpoint": "https://example.test/hook", "delivery_mode": value}
            original = dict(request)
            self.assertEqual(
                register_webhook(request, registry),
                {"error": {"field": "delivery_mode", "code": "INVALID_DELIVERY_MODE"}},
            )
            self.assertEqual(registry, [])
            self.assertEqual(request, original)


if __name__ == "__main__":
    unittest.main()
