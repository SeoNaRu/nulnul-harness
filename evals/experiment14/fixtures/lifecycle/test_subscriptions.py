import unittest

from subscriptions import register_subscription


class SubscriptionTests(unittest.TestCase):
    def test_preserves_missing_empty_and_existing_delivery_values(self):
        for request in ({"name": "alpha"}, {"name": "alpha", "delivery": ""}, {"name": "alpha", "delivery": "email"}):
            with self.subTest(request=request):
                registry = []
                original = dict(request)
                self.assertEqual(register_subscription(request, registry), {"subscription": request})
                self.assertEqual(registry, [request])
                self.assertEqual(request, original)


if __name__ == "__main__":
    unittest.main()
