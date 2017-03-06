import unittest
from YenAlgorithm import YenAlgorithm
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
        self.assertItemsEqual(expected_paths, alg.shortest_paths)

if __name__ == '__main__':
    unittest.main()
