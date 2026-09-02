import unittest

from runs import contiguous_runs


class ContiguousRunsTests(unittest.TestCase):
    def test_groups_only_adjacent_equal_values(self):
        self.assertEqual(
            contiguous_runs(["a", "a", "b", "a", "a", "a", "c"]),
            [["a", "a"], ["b"], ["a", "a", "a"], ["c"]],
        )

    def test_empty_and_single_value(self):
        self.assertEqual(contiguous_runs([]), [])
        self.assertEqual(contiguous_runs([3]), [[3]])

    def test_returns_new_lists_without_mutation(self):
        source = [1, 1, 2]
        result = contiguous_runs(source)
        self.assertEqual(source, [1, 1, 2])
        self.assertIsNot(result[0], source)


if __name__ == "__main__":
    unittest.main()
