import unittest

from webhooks import register_webhook


class DeferredDeliveryTests(unittest.TestCase):
    def test_deferred_is_an_accepted_delivery_mode(self):
        registry = []
        request = {"endpoint": "https://example.test/hook", "delivery_mode": "deferred"}
        self.assertEqual(register_webhook(request, registry), {"webhook": request})
        self.assertEqual(registry, [request])


if __name__ == "__main__":
    unittest.main()
