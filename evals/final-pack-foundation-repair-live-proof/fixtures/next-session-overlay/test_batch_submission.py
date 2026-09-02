import unittest

from jobs import submit_jobs


class BatchSubmissionTests(unittest.TestCase):
    def test_validates_the_whole_batch_before_queue_mutation(self):
        requests = [
            {"name": "compile", "region": "us-east"},
            {"name": "package", "region": "eu-west"},
        ]
        queue = []
        self.assertEqual(submit_jobs(requests, queue), {"jobs": requests})
        self.assertEqual(queue, requests)

        invalid = [
            {"name": "compile", "region": "us-east"},
            {"name": "package", "region": "moon-1"},
        ]
        queue = []
        self.assertEqual(
            submit_jobs(invalid, queue),
            {"error": {"field": "region", "code": "INVALID_REGION"}},
        )
        self.assertEqual(queue, [])


if __name__ == "__main__":
    unittest.main()
