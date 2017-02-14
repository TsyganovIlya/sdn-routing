import unittest
from Path import Path


class PathTest(unittest.TestCase):

    def test_eq(self):
        path1 = Path([1, 2, 3])
        path2 = Path([1, 2, 3])
        are_equal = path1 == path2
        self.assertEqual(True, are_equal)

        path1 = Path([1, 5, 3])
        path2 = Path([1, 2, 3])
        are_equal = path1 == path2
        self.assertEqual(False, are_equal)

        path1 = Path([1, 2, 3, 6])
        path2 = Path([1, 2, 3])
        are_equal = path1 == path2
        self.assertEqual(False, are_equal)


if __name__ == '__main__':
    unittest.main()
