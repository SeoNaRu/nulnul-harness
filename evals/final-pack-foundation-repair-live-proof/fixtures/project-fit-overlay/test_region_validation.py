import json
import unittest
from pathlib import Path

from jobs import submit_job


class RegionValidationTests(unittest.TestCase):
    def test_accepts_only_the_frozen_nonempty_region_set(self):
        for region in ("us-east", "eu-west"):
            queue = []
            request = {"name": "build", "region": region}
            self.assertEqual(submit_job(request, queue), {"job": request})
            self.assertEqual(queue, [request])

    def test_invalid_region_uses_project_error_before_queue_mutation(self):
        queue = []
        request = {"name": "build", "region": "moon-1"}
        original = dict(request)
        self.assertEqual(
            submit_job(request, queue),
            {"error": {"field": "region", "code": "INVALID_REGION"}},
        )
        self.assertEqual(queue, [])
        self.assertEqual(request, original)

    def test_error_catalog_contains_the_project_code(self):
        codes = json.loads(Path("contracts/error-codes.json").read_text(encoding="utf-8"))
        self.assertIn("INVALID_REGION", codes)


if __name__ == "__main__":
    unittest.main()
