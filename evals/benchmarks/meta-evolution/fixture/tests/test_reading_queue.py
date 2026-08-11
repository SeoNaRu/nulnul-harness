import unittest

from reading_queue import route


class ReadingQueueTests(unittest.TestCase):
    def test_routes_agent_notes_to_keep(self):
        self.assertEqual(route("A paper about meta agents"), "keep")

    def test_routes_unmatched_notes_to_review(self):
        self.assertEqual(route("A paper about soil"), "review")


if __name__ == "__main__":
    unittest.main()
