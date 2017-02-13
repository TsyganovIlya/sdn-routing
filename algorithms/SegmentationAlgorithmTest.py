import unittest
from SegmentationAlgorithm import SegmentationAlgorithm


class SegmentationAlgorithmTest(unittest.TestCase):

    def test_find_neighbors_from_minimum_tree_for(self):
        switches = range(1, 7)
        weights_matrix = {1: {6: 1, 5: 15, 4: 10, 3: 20, 2: 4},
                          2: {1: 4, 3: 6, 6: 17},
                          3: {2: 6, 1: 20, 4: 15},
                          4: {3: 15, 1: 10, 5: 2},
                          5: {4: 2, 1: 15, 6: 9},
                          6: {5: 9, 1: 1, 2: 17}}
        alg = SegmentationAlgorithm(switches, weights_matrix)
        alg.minimum_tree = [(1, 6), (6, 1),
                            (1, 2), (2, 1),
                            (2, 3), (3, 2),
                            (6, 5), (5, 6),
                            (5, 4), (4, 5)]
        switch = 1
        expected = [2, 6]
        actual = alg.find_neighbors_from_minimum_tree_for(switch)
        self.assertItemsEqual(expected, actual)

    def test_compute_degree_for(self):
        switches = range(1, 7)
        weights_matrix = {1: {6: 1, 5: 15, 4: 10, 3: 20, 2: 4},
                          2: {1: 4, 3: 6, 6: 17},
                          3: {2: 6, 1: 20, 4: 15},
                          4: {3: 15, 1: 10, 5: 2},
                          5: {4: 2, 1: 15, 6: 9},
                          6: {5: 9, 1: 1, 2: 17}}
        alg = SegmentationAlgorithm(switches, weights_matrix)
        alg.minimum_tree = [(1, 6), (6, 1),
                            (1, 2), (2, 1),
                            (2, 3), (3, 2),
                            (6, 5), (5, 6),
                            (5, 4), (4, 5)]

        self.assertEqual(alg.compute_degree_for(1), 2)
        self.assertEqual(alg.compute_degree_for(3), 1)
        self.assertEqual(alg.compute_degree_for(4), 1)
        self.assertEqual(alg.compute_degree_for(5), 2)

    def test_find_island_for(self):
        switches = range(1, 7)
        weights_matrix = {1: {6: 1, 5: 15, 4: 10, 3: 20, 2: 4},
                          2: {1: 4, 3: 6, 6: 17},
                          3: {2: 6, 1: 20, 4: 15},
                          4: {3: 15, 1: 10, 5: 2},
                          5: {4: 2, 1: 15, 6: 9},
                          6: {5: 9, 1: 1, 2: 17}}
        alg = SegmentationAlgorithm(switches, weights_matrix)
        island1 = [1, 4, 5, 6]
        island2 = [2, 3]
        alg.islands = [island1, island2]
        switch = 1
        expected = island1
        actual = alg.find_island_for(switch)
        self.assertItemsEqual(expected, actual)

    def test_find_allocated_switches(self):
        switches = range(1, 7)
        islands = [[1, 2, 3], [5, 6]]
        alg = SegmentationAlgorithm(switches, None)
        alg.islands = islands
        expected = [1, 2, 3, 5, 6]
        actual = alg.find_allocated_switches()
        self.assertItemsEqual(expected, actual)

    def test_find_unallocated_switches(self):
        switches = range(1, 7)
        islands = [[1, 2, 3], [5, 6]]
        alg = SegmentationAlgorithm(switches, None)
        alg.islands = islands
        expected = [4]
        actual = alg.find_unallocated_switches()
        self.assertItemsEqual(expected, actual)

    def test_find_external_links_for(self):
        switches = range(1, 7)
        weights_matrix = {1: {6: 1, 5: 15, 4: 10, 3: 20, 2: 4},
                          2: {1: 4, 3: 6, 6: 17},
                          3: {2: 6, 1: 20, 4: 15},
                          4: {3: 15, 1: 10, 5: 2},
                          5: {4: 2, 1: 15, 6: 9},
                          6: {5: 9, 1: 1, 2: 17}}
        alg = SegmentationAlgorithm(switches, weights_matrix)
        expected = [(4, 3), (1, 3), (2, 3)]
        island = [1, 2, 4, 5, 6]
        actual = alg.find_external_links_for(island)
        self.assertItemsEqual(expected, actual)

    def test_find_internal_links_for(self):
        switches = range(1, 7)
        weights_matrix = {1: {6: 1, 5: 15, 4: 10, 3: 20, 2: 4},
                          2: {1: 4, 3: 6, 6: 17},
                          3: {2: 6, 1: 20, 4: 15},
                          4: {3: 15, 1: 10, 5: 2},
                          5: {4: 2, 1: 15, 6: 9},
                          6: {5: 9, 1: 1, 2: 17}}
        alg = SegmentationAlgorithm(switches, weights_matrix)
        expected = [(4, 5), (5, 4), (1, 5), (5, 1), (1, 4), (4, 1)]
        island = [1, 4, 5]
        actual = alg.find_internal_links_for(island)
        self.assertItemsEqual(expected, actual)

    def test_compute_connection_value_for(self):
        switches = range(1, 7)
        weights_matrix = {1: {6: 1, 5: 15, 4: 10, 3: 20, 2: 4},
                          2: {1: 4, 3: 6, 6: 17},
                          3: {2: 6, 1: 20, 4: 15},
                          4: {3: 15, 1: 10, 5: 2},
                          5: {4: 2, 1: 15, 6: 9},
                          6: {5: 9, 1: 1, 2: 17}}
        alg = SegmentationAlgorithm(switches, weights_matrix)
        island = [1, 4, 5, 6]
        expected = 5 / 4.
        actual = alg.compute_connection_value_for(island)
        self.assertEquals(expected, actual)

    def test_find_weak_connected_islands(self):
        switches = range(1, 7)
        weights_matrix = {1: {6: 1, 5: 15, 4: 10, 3: 20, 2: 4},
                          2: {1: 4, 3: 6, 6: 17},
                          3: {2: 6, 1: 20, 4: 15},
                          4: {3: 15, 1: 10, 5: 2},
                          5: {4: 2, 1: 15, 6: 9},
                          6: {5: 9, 1: 1, 2: 17}}
        alg = SegmentationAlgorithm(switches, weights_matrix)
        alg.islands = [[1, 4, 5, 6], [2, 3]]
        expected = [[2, 3]]
        actual = alg.find_weak_connected_islands()
        self.assertItemsEqual(expected, actual)

    def test_compute_connections_between_switch_and_island(self):
        switches = range(1, 7)
        weights_matrix = {1: {6: 1, 5: 15, 4: 10, 3: 20, 2: 4},
                          2: {1: 4, 3: 6, 6: 17},
                          3: {2: 6, 1: 20, 4: 15},
                          4: {3: 15, 1: 10, 5: 2},
                          5: {4: 2, 1: 15, 6: 9},
                          6: {5: 9, 1: 1, 2: 17}}
        alg = SegmentationAlgorithm(switches, weights_matrix)
        island = [1, 2, 4, 5, 6]
        switch = 3
        expected = 3
        actual = alg.compute_connections_between_switch_and_island(switch, island)
        self.assertEquals(expected, actual)

    def test_compute_connections_between_island_and_island(self):
        switches = range(1, 7)
        weights_matrix = {1: {6: 1, 5: 15, 4: 10, 3: 20, 2: 4},
                          2: {1: 4, 3: 6, 6: 17},
                          3: {2: 6, 1: 20, 4: 15},
                          4: {3: 15, 1: 10, 5: 2},
                          5: {4: 2, 1: 15, 6: 9},
                          6: {5: 9, 1: 1, 2: 17}}
        alg = SegmentationAlgorithm(switches, weights_matrix)
        island1 = [1, 4, 5, 6]
        island2 = [2, 3]
        expected = 4
        actual = alg.compute_connections_between_island_and_island(island1, island2)
        self.assertEquals(expected, actual)

    def test_form_primary_islands(self):
        switches = range(1, 7)
        weights_matrix = {1: {6: 3, 2: 2, 3: 18},
                          2: {1: 2, 3: 15},
                          3: {2: 15, 1: 18, 6: 1, 4: 20},
                          4: {3: 20, 6: 4, 5: 40},
                          5: {4: 40, 6: 5},
                          6: {5: 5, 1: 3, 3: 1, 4: 4}}
        alg = SegmentationAlgorithm(switches, weights_matrix)
        alg.minimum_tree = [(1, 2), (2, 1),
                            (1, 6), (6, 1),
                            (6, 3), (3, 6),
                            (6, 4), (4, 6),
                            (5, 6), (6, 5)]
        alg.form_primary_islands()
        expected = [[1, 2], [3, 6, 4, 5]]
        actual = alg.islands
        for i in range(len(actual)):
            self.assertItemsEqual(expected[i], actual[i])

    def test_extract_switches_from(self):
        islands = [[1, 2], [3, 4]]
        alg = SegmentationAlgorithm([], [])
        expected = [1, 2, 3, 4]
        actual = alg.extract_switches_from(islands)
        self.assertItemsEqual(expected, actual)

    def test_filter_islands_connected_to_switch_by_minimal_tree(self):
        switches = range(1, 7)
        weights_matrix = {1: {6: 1, 5: 15, 4: 10, 3: 20, 2: 4},
                          2: {1: 4, 3: 6, 6: 17},
                          3: {2: 6, 1: 20, 4: 15},
                          4: {3: 15, 1: 10, 5: 2},
                          5: {4: 2, 1: 15, 6: 9},
                          6: {5: 9, 1: 1, 2: 17}}
        alg = SegmentationAlgorithm(switches, weights_matrix)
        alg.minimum_tree = [(1, 6), (6, 1),
                            (1, 2), (2, 1),
                            (2, 3), (3, 2),
                            (6, 5), (5, 6),
                            (5, 4), (4, 5)]
        switch = 4
        island1 = [1, 5, 6]
        island2 = [2, 3]
        alg.islands = [island1, island2]
        expected = [island1]
        actual = alg.filter_islands_connected_to_switch_by_minimal_tree(switch)
        self.assertItemsEqual(expected, actual)

    def test_filter_islands_with_max_connectivity_to_switch(self):
        switches = range(1, 11)
        weights_matrix = {1: {2: 0, 4: 0, 7: 0, 8: 0, 10: 0},
                          2: {1: 0, 4: 0, 3: 0},
                          3: {2: 0, 4: 0},
                          4: {2: 0, 3: 0, 1: 0},
                          5: {7: 0, 6: 0},
                          6: {5: 0, 7: 0},
                          7: {5: 0, 6: 0, 1: 0},
                          8: {1: 0, 10: 0, 9: 0},
                          9: {8: 0, 10: 0},
                          10: {1: 0, 8: 0, 9: 0}}
        alg = SegmentationAlgorithm(switches, weights_matrix)
        switch = 1
        island1 = [2, 3, 4]
        island2 = [5, 6, 7]
        island3 = [8, 9, 10]
        islands = [island1, island2, island3]
        expected = [island1, island3]
        actual = alg.filter_islands_with_max_connectivity_to_switch(switch, islands)
        self.assertItemsEqual(expected, actual)

    def test_filter_island_connected_to_switch_by_minimum_weight(self):
        switches = range(1, 7)
        weights_matrix = {1: {6: 1, 5: 15, 4: 10, 3: 20, 2: 4},
                          2: {1: 4, 3: 6, 6: 17},
                          3: {2: 6, 1: 20, 4: 15},
                          4: {3: 15, 1: 10, 5: 2},
                          5: {4: 2, 1: 15, 6: 9},
                          6: {5: 9, 1: 1, 2: 17}}
        alg = SegmentationAlgorithm(switches, weights_matrix)
        switch = 1
        island1 = [4, 5, 6]
        island2 = [2, 3]
        alg.islands = [island1, island2]
        expected = (island1, 1)
        actual = alg.filter_island_connected_to_switch_by_minimum_weight(switch, alg.islands)
        self.assertItemsEqual(expected, actual)

    def test_form_secondary_islands(self):
        switches = range(1, 7)
        weights_matrix = {1: {6: 1, 5: 15, 4: 10, 3: 20, 2: 4},
                          2: {1: 4, 3: 6, 6: 17},
                          3: {2: 6, 1: 20, 4: 15},
                          4: {3: 15, 1: 10, 5: 2},
                          5: {4: 2, 1: 15, 6: 9},
                          6: {5: 9, 1: 1, 2: 17}}
        alg = SegmentationAlgorithm(switches, weights_matrix)
        alg.minimum_tree = [(1, 6), (6, 1),
                            (1, 2), (2, 1),
                            (2, 3), (3, 2),
                            (6, 5), (5, 6),
                            (5, 4), (4, 5)]
        island1 = [4, 5]
        island2 = [2, 3]
        alg.islands = [island1, island2]
        alg.form_secondary_islands()
        expected = [[4, 5], [2, 3, 1, 6]]
        self.assertItemsEqual(expected, alg.islands)

    def test_do(self):
        switches = range(1, 7)
        weights_matrix = {1: {6: 1, 5: 15, 4: 10, 3: 20, 2: 4},
                          2: {1: 4, 3: 6, 6: 17},
                          3: {2: 6, 1: 20, 4: 15},
                          4: {3: 15, 1: 10, 5: 2},
                          5: {4: 2, 1: 15, 6: 9},
                          6: {5: 9, 1: 1, 2: 17}}
        alg = SegmentationAlgorithm(switches, weights_matrix)
        alg.do()
        expected = [[3, 2, 1, 6, 4, 5]]
        self.assertItemsEqual(expected, alg.islands)


if __name__ == '__main__':
    unittest.main()
