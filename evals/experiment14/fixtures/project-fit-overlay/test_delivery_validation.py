import unittest

from subscriptions import register_subscription


class DeliveryValidationTests(unittest.TestCase):
    def test_invalid_nonempty_delivery_is_rejected_before_registration(self):
        for value in ("EMAIL", "postal", "web-hook"):
            with self.subTest(value=value):
                request = {"name": "alpha", "delivery": value}
                registry = []
                self.assertEqual(
                    register_subscription(request, registry),
                    {"error": {"field": "delivery", "code": "INVALID_DELIVERY"}},
                )
                self.assertEqual(registry, [])
                self.assertEqual(request, {"name": "alpha", "delivery": value})

    def test_only_current_lowercase_delivery_values_are_accepted(self):
        for value in ("email", "sms", "push"):
            with self.subTest(value=value):
                registry = []
                request = {"name": "alpha", "delivery": value}
                self.assertEqual(register_subscription(request, registry), {"subscription": request})
                self.assertEqual(registry, [request])

    def test_error_code_is_catalogued(self):
        import json
        from pathlib import Path

        codes = json.loads(Path("contracts/error-codes.json").read_text(encoding="utf-8"))
        self.assertIn("INVALID_DELIVERY", codes)


if __name__ == "__main__":
    unittest.main()
