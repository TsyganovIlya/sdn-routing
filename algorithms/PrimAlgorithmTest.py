import unittest
from PrimAlgorithm import PrimAlgorithm


class PrimAlgorithmTest(unittest.TestCase):

    def test_do(self):
        switches = range(1, 7)
        weights_matrix = {1: {6: 1, 5: 15, 4: 10, 3: 20, 2: 4},
                          2: {1: 4, 3: 6, 6: 17},
                          3: {2: 6, 1: 20, 4: 15},
                          4: {3: 15, 1: 10, 5: 2},
                          5: {4: 2, 1: 15, 6: 9},
                          6: {5: 9, 1: 1, 2: 17}}
        expected_minimum_tree_links = [(1, 6), (6, 1),
                                       (1, 2), (2, 1),
                                       (2, 3), (3, 2),
                                       (6, 5), (5, 6),
                                       (5, 4), (4, 5)]
        alg = PrimAlgorithm(switches, weights_matrix)
        actual_minimum_tree_links = alg.do()
        self.assertItemsEqual(expected_minimum_tree_links, actual_minimum_tree_links)

if __name__ == '__main__':
    unittest.main()
