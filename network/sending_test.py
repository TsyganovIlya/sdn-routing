import unittest
import sending


class SendingTest(unittest.TestCase):

    def test_send_tree(self):
        links = [(1, 2), (2, 1), (4, 6), (6, 4)]
        actual = sending.send_tree(links)
        expected = "1,2-2,1-4,6-6,4"
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()