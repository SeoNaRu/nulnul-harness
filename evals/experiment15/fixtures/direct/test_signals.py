import unittest

from signals import sign_runs


class SignRunsTests(unittest.TestCase):
    def test_groups_adjacent_values_by_sign_class(self):
        self.assertEqual(
            sign_runs([-3, -1, 0, 0, 4, 2, -5, 0]),
            [[-3, -1], [0, 0], [4, 2], [-5], [0]],
        )

    def test_empty_and_single_value(self):
        self.assertEqual(sign_runs([]), [])
        self.assertEqual(sign_runs([0]), [[0]])

    def test_returns_new_lists_without_mutation(self):
        source = [-1, -2, 0, 3]
        result = sign_runs(source)
        self.assertEqual(source, [-1, -2, 0, 3])
        self.assertIsNot(result[0], source)


if __name__ == "__main__":
    unittest.main()
