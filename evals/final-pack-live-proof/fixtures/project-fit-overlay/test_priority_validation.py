import unittest

from jobs import submit_job


class PriorityValidationTests(unittest.TestCase):
    def test_accepts_only_the_frozen_priority_set(self):
        for priority in ("low", "normal", "high"):
            queue = []
            request = {"name": "build", "priority": priority}
            self.assertEqual(submit_job(request, queue), {"job": request})
            self.assertEqual(queue, [request])

    def test_invalid_priority_uses_project_error_before_queue_mutation(self):
        queue = []
        request = {"name": "build", "priority": "urgent"}
        original = dict(request)
        self.assertEqual(
            submit_job(request, queue),
            {"error": {"field": "priority", "code": "INVALID_PRIORITY"}},
        )
        self.assertEqual(queue, [])
        self.assertEqual(request, original)

    def test_error_catalog_contains_the_project_code(self):
        import json
        from pathlib import Path

        codes = json.loads(Path("contracts/error-codes.json").read_text(encoding="utf-8"))
        self.assertIn("INVALID_PRIORITY", codes)


if __name__ == "__main__":
    unittest.main()
