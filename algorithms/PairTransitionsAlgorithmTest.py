import unittest
from algorithms.PairTransitionsAlgorithm import PairTransitionsAlgorithm


class PairTransitionsAlgorithmTest(unittest.TestCase):

    def test_collect_statistics(self):
        switches = range(1, 4)
        weights_matrix = {1: {2: None, 3: None},
                          2: {1: None, 3: None},
                          3: {2: None, 1: None}}
        alg = PairTransitionsAlgorithm(switches, weights_matrix)
        alg.previous = {1: None, 3: 1}
        alg.collect_statistics()

        expected = {(1, 3), (3, 1)}
        actual = alg.tree_edges
        self.assertItemsEqual(expected, actual)

        expected = {(1, 2), (2, 1),
                    (3, 2), (2, 3)}
        actual = alg.replacement_edges
        self.assertItemsEqual(expected, actual)

    def test_unpack_edges_from_weights(self):
        switches = range(1, 4)
        weights_matrix = {1: {2: None, 3: None},
                          2: {1: None, 3: None},
                          3: {2: None, 1: None}}
        alg = PairTransitionsAlgorithm(switches, weights_matrix)
        actual = alg.unpack_edges_from_weights(weights_matrix)
        expected = {(1, 2), (1, 3),
                    (2, 1), (2, 3),
                    (3, 2), (3, 1)}
        self.assertItemsEqual(expected, actual)

    def test_unpack_edges_from_previous(self):
        switches = range(1, 7)
        weights_matrix = {1: {6: 1, 5: 15, 4: 10, 3: 20, 2: 4},
                          2: {1: 4, 3: 6, 6: 17},
                          3: {2: 6, 1: 20, 4: 15},
                          4: {3: 15, 1: 10, 5: 2},
                          5: {4: 2, 1: 15, 6: 9},
                          6: {5: 9, 1: 1, 2: 17}}
        prev = {6: None, 1: 6, 2: 1}
        alg = PairTransitionsAlgorithm(switches, weights_matrix)
        actual = alg.unpack_edges_from_previous(prev)
        expected = {(1, 6), (6, 1),
                    (1, 2), (2, 1)}
        self.assertItemsEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()
