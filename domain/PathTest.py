import unittest
from domain.Path import Path


class PathTest(unittest.TestCase):

    def test_eq(self):
        path1 = Path([1, 2, 3])
        path2 = Path([1, 2, 3])
        are_equal = path1 == path2
        self.assertTrue(are_equal)

        path1 = Path([1, 5, 3])
        path2 = Path([1, 2, 3])
        are_equal = path1 == path2
        self.assertFalse(are_equal)

        path1 = Path([1, 2, 3, 6])
        path2 = Path([1, 2, 3])
        are_equal = path1 == path2
        self.assertFalse(are_equal)

    def test_bytes(self):
        path = Path([1, 2, 3, 4])
        path_in_bytes = bytes(path)
        self.assertEqual(b'1,2,3,4', path_in_bytes)

if __name__ == '__main__':
    unittest.main()
