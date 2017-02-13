import unittest
from Graph import Graph


class PathTest(unittest.TestCase):

    def test_count_distance_for(self):
        switches = range(1, 7)
        weights_matrix = {1: {6: 1, 5: 15, 4: 10, 3: 20, 2: 4},
                          2: {1: 4, 3: 6, 6: 17},
                          3: {2: 6, 1: 20, 4: 15},
                          4: {3: 15, 1: 10, 5: 2},
                          5: {4: 2, 1: 15, 6: 9},
                          6: {5: 9, 1: 1, 2: 17}}
        graph = Graph(weights_matrix, switches)
        path = [6, 1, 3]

        actual = graph.count_distance_for(path)
        expected = 21
        self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()
