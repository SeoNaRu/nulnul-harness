import unittest

from runs import collapse_adjacent


class CollapseAdjacentTests(unittest.TestCase):
    def test_collapses_only_adjacent_duplicates_without_mutating_input(self):
        values = [1, 1, 2, 1, 1, 3, 3, 3]
        original = list(values)
        result = collapse_adjacent(values)
        self.assertEqual(result, [1, 2, 1, 3])
        self.assertEqual(values, original)
        self.assertIsNot(result, values)

    def test_handles_empty_and_singleton_inputs(self):
        self.assertEqual(collapse_adjacent([]), [])
        self.assertEqual(collapse_adjacent([7]), [7])


if __name__ == "__main__":
    unittest.main()
