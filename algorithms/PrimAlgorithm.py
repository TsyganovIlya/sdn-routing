from collections import defaultdict


class PrimAlgorithm(object):

    def __init__(self, switches, weights_matrix):
        self._switches = switches
        self._weights_matrix = weights_matrix

    def do(self):
        is_viewed = {s: False for s in self._switches}
        is_viewed[self._switches[0]] = True
        minimum_tree_links = []
        for _ in range(len(self._switches) - 1):
            min_weight = float('+inf')
            tmp_link = (self._switches[0], self._switches[1])
            for s1 in self._weights_matrix.keys():
                for s2 in self._weights_matrix[s1].keys():
                    if (is_viewed[s1] is not is_viewed[s2]) and (self._weights_matrix[s1][s2] < min_weight):
                        min_weight = self._weights_matrix[s1][s2]
                        tmp_link = (s1, s2)
            is_viewed[tmp_link[0]] = is_viewed[tmp_link[1]] = True
            minimum_tree_links.append((tmp_link[0], tmp_link[1]))
            minimum_tree_links.append((tmp_link[1], tmp_link[0]))
        return minimum_tree_links
