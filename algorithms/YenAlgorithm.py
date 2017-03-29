from algorithms.DijkstraAlgorithm import DijkstraAlgorithm
from domain.Graph import Graph


class YenAlgorithm(object):

    def __init__(self, weight_map, vertices, k):
        self._graph = Graph(weight_map, vertices)
        self._k = k
        self._dijkstra_alg = DijkstraAlgorithm(weight_map, vertices)
        self._shortest_paths = []

    @property
    def shortest_paths(self):
        return self._shortest_paths

    def _compute_shortest_path(self, src, dst):
        return self._dijkstra_alg.compute_shortest_path(src, dst)

    def compute_shortest_paths(self, src, dst):
        shortest_path = self._compute_shortest_path(src, dst)
        self._shortest_paths.append(shortest_path)
        for _ in range(self._k - 1):
            min_distance = float('+inf')
            new_shortest_path = None
            removed_edge = None
            for edge in [shortest_path.get_edge(i, i + 1) for i in range(len(shortest_path) - 1)]:
                self._graph.remove(edge)
                intermediate_shortest_path = self._compute_shortest_path(src, dst)
                if self._graph.count_distance_for(intermediate_shortest_path) <= min_distance:
                    min_distance = self._graph.count_distance_for(intermediate_shortest_path)
                    new_shortest_path = intermediate_shortest_path
                    removed_edge = edge
                self._graph.recover_last_deleted_edge()
            if new_shortest_path:
                self._shortest_paths.append(new_shortest_path)
                self._graph.remove(removed_edge)
                shortest_path = new_shortest_path
            else:
                return

    def convert_paths_to_bytes(self):
        paths_representation = []
        for path in self._shortest_paths :
            paths_representation.append(path.__repr__())
        return bytearray(';'.join(paths_representation), 'utf-8')

