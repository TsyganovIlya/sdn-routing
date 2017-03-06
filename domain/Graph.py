from collections import defaultdict


class Graph(object):

    def __init__(self, weight_map, vertices):
        """
        :type weight_map: defaultdict
        :type vertices: list
        """
        self._vertices = vertices
        self._weight_map = weight_map
        self._deleted_edge = ()

    @property
    def weight_map(self):
        return self._weight_map

    def count_distance_for(self, path):
        distance = 0
        for i in range(len(path) - 1):
            distance += self._weight_map[path[i]][path[i + 1]]
        return distance

    def remove(self, edge):
        """
        :param edge: tuple <v1, v2>
        """
        self._deleted_edge = edge[0], edge[1], self._weight_map[edge[0]][edge[1]]
        del self._weight_map[edge[1]][edge[0]]
        del self._weight_map[edge[0]][edge[1]]

    def recover_last_deleted_edge(self):
        edge = self._deleted_edge
        weight = edge[2]
        self._weight_map[edge[1]][edge[0]] = weight
        self._weight_map[edge[0]][edge[1]] = weight
