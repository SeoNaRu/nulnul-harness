import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class BookingServiceExampleTests(unittest.TestCase):
    def test_local_http_contract_and_rejections(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "examples/booking-service/app.py"), "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS: UI response, availability, booking, conflict, invalid input, and local-origin checks.", result.stdout)


if __name__ == "__main__":
    unittest.main()
