import unittest

from jobs import submit_job


class UrgentPriorityTests(unittest.TestCase):
    def test_urgent_is_accepted_without_weakening_existing_validation(self):
        queue = []
        request = {"name": "incident", "priority": "urgent"}
        original = dict(request)
        self.assertEqual(submit_job(request, queue), {"job": request})
        self.assertEqual(queue, [request])
        self.assertEqual(request, original)

        invalid_queue = []
        invalid = {"name": "incident", "priority": "URGENT"}
        self.assertEqual(
            submit_job(invalid, invalid_queue),
            {"error": {"field": "priority", "code": "INVALID_PRIORITY"}},
        )
        self.assertEqual(invalid_queue, [])


if __name__ == "__main__":
    unittest.main()
