import unittest
from algorithms.YenAlgorithm import YenAlgorithm
from domain.Path import Path


class YenAlgorithmTest(unittest.TestCase):

    def test_compute_shortest_paths(self):
        switches = range(1, 6)
        weights_matrix = {1: {2: 9, 3: 5, 4: 10},
                          2: {1: 9, 5: 12},
                          3: {1: 5, 5: 6},
                          4: {1: 10, 5: 20},
                          5: {2: 12, 3: 6, 4: 20}}
        expected_paths = [
            Path([1, 3, 5]),
            Path([1, 2, 5]),
            Path([1, 4, 5])
        ]
        alg = YenAlgorithm(weights_matrix, switches, k=3)
        alg.compute_shortest_paths(source_vertex=1, destination_vertex=5)
        self.assertSequenceEqual(expected_paths, alg.shortest_paths)

        switches = range(1, 7)
        weights_matrix = {1: {2: 50, 3: 10, 4: 50},
                          2: {1: 50, 5: 60},
                          3: {1: 10, 5: 30, 6: 20},
                          4: {1: 50, 6: 50},
                          5: {2: 60, 3: 30, 6: 40},
                          6: {5: 40, 3: 20, 4: 50}}
        expected_paths = [
            Path([1, 3, 6]),
            Path([1, 3, 5, 6]),
            Path([1, 4, 6])
        ]
        alg = YenAlgorithm(weights_matrix, switches, k=3)
        alg.compute_shortest_paths(source_vertex=1, destination_vertex=6)
        self.assertSequenceEqual(expected_paths, alg.shortest_paths)

if __name__ == '__main__':
    unittest.main()
