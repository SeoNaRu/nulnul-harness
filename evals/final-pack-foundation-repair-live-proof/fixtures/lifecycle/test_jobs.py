import unittest

from jobs import submit_job


class JobTests(unittest.TestCase):
    def test_preserves_missing_empty_and_existing_priority_values(self):
        for request in (
            {"name": "build"},
            {"name": "build", "priority": ""},
            {"name": "build", "priority": "normal"},
        ):
            with self.subTest(request=request):
                queue = []
                original = dict(request)
                self.assertEqual(submit_job(request, queue), {"job": request})
                self.assertEqual(queue, [request])
                self.assertEqual(request, original)


if __name__ == "__main__":
    unittest.main()
