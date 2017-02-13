import unittest
from Path import Path


class PathTest(unittest.TestCase):

    def test_convert_to_ordered_sequence(self):
        path = Path(4, 3, {4: None, 2: 4, 1: 2, 3: 1})
        actual = path.convert_to_ordered_sequence()
        expected = [4, 2, 1, 3]
        self.assertSequenceEqual(expected, actual)

    def test_repr(self):
        path = Path(4, 3, {4: None, 2: 4, 1: 2, 3: 1})
        actual = str(path)
        expected = "s4->s2->s1->s3"
        self.assertEqual(expected, actual)

    def test_to_byte_array(self):
        path = Path(4, 3, {4: None, 2: 4, 1: 2, 3: 1})
        actual = str(path.to_byte_array())
        expected = "4,2,1,3"
        self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()
