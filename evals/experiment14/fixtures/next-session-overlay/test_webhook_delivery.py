import unittest

from subscriptions import register_subscription


class WebhookDeliveryTests(unittest.TestCase):
    def test_webhook_is_an_accepted_delivery_without_mutation(self):
        request = {"name": "alpha", "delivery": "webhook"}
        registry = []
        self.assertEqual(register_subscription(request, registry), {"subscription": request})
        self.assertEqual(registry, [request])
        self.assertEqual(request, {"name": "alpha", "delivery": "webhook"})


if __name__ == "__main__":
    unittest.main()
