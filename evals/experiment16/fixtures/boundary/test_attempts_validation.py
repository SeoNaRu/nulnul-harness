import json
import unittest
from pathlib import Path

from jobs import submit_job, submit_jobs


class AttemptsValidationTests(unittest.TestCase):
    def test_accepts_missing_empty_and_integer_range(self):
        for attempts in (None, "", 2, 6):
            request = {"name": "retryable"}
            if attempts is not None:
                request["attempts"] = attempts
            queue = []
            self.assertEqual(submit_job(request, queue), {"job": request})
            self.assertEqual(queue, [request])

    def test_rejects_boundary_and_type_errors_before_mutation(self):
        for attempts in (1, 7, True, 1.5, "2"):
            with self.subTest(attempts=attempts):
                invalid = {"name": "retryable", "attempts": attempts}
                original = dict(invalid)
                queue = []
                self.assertEqual(
                    submit_job(invalid, queue),
                    {"error": {"field": "attempts", "code": "INVALID_ATTEMPTS"}},
                )
                self.assertEqual(queue, [])
                self.assertEqual(invalid, original)

        queue = []
        self.assertEqual(
            submit_jobs([{"name": "ok", "attempts": 2}, {"name": "bad", "attempts": 1}], queue),
            {"error": {"field": "attempts", "code": "INVALID_ATTEMPTS"}},
        )
        self.assertEqual(queue, [])

    def test_catalog_contains_attempts_code(self):
        codes = json.loads(Path("contracts/error-codes.json").read_text(encoding="utf-8"))
        self.assertIn("INVALID_ATTEMPTS", codes)


if __name__ == "__main__":
    unittest.main()
