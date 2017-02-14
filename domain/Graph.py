from util.DeepCopier import DeepCopier
from collections import defaultdict


class Graph(object):

    def __init__(self, weight_map, vertices):
        """
        :type weight_map: defaultdict
        :type vertices: list
        """
        self._vertices = vertices
        self._weight_map = weight_map
        self._stored_vertices = vertices[:]
        self._stored_weight_map = DeepCopier(weight_map).make_copy()

    def restore_edges(self):
        self._weight_map = DeepCopier(self._stored_weight_map).make_copy()

    def restore_vertices(self):
        self._vertices = self._stored_vertices[:]

    def count_distance_for(self, path):
        distance = 0
        for i in range(len(path) - 1):
            distance += self._weight_map[path[i]][path[i + 1]]
        return distance

    def remove_edge(self, edge):
        self._weight_map[edge[0]][edge[1]] = float('+inf')
        self._weight_map[edge[1]][edge[0]] = float('+inf')

    def remove_vertex(self, vertex):
        self._vertices.pop(vertex)
