import unittest

from ranges import chunk_inclusive


class ChunkInclusiveTests(unittest.TestCase):
    def test_splits_an_inclusive_range_without_gaps(self):
        self.assertEqual(
            chunk_inclusive(3, 11, 4),
            [(3, 6), (7, 10), (11, 11)],
        )

    def test_handles_empty_and_rejects_nonpositive_sizes(self):
        self.assertEqual(chunk_inclusive(5, 4, 2), [])
        with self.assertRaises(ValueError):
            chunk_inclusive(1, 3, 0)


if __name__ == "__main__":
    unittest.main()
