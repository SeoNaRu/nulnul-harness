import unittest

from reading_queue import route


class ReadingQueueTests(unittest.TestCase):
    def test_routes_ai_notes_to_keep(self):
        self.assertEqual(route("AI agent notes"), "keep")

    def test_routes_unmatched_notes_to_review(self):
        self.assertEqual(route("Garden notes"), "review")


if __name__ == "__main__":
    unittest.main()
