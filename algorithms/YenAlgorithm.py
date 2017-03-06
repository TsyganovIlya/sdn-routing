from DijkstraAlgorithm import DijkstraAlgorithm
from domain.Graph import Graph


class YenAlgorithm(object):

    def __init__(self, weight_map, vertices, k):
        self._graph = Graph(weight_map, vertices)
        self._k = k
        self._dijkstra_alg = DijkstraAlgorithm(weight_map, vertices)
        self._shortest_paths = []

    def _compute_shortest_path(self, source_vertex, destination_vertex):
        return self._dijkstra_alg.compute_shortest_path(source_vertex, destination_vertex)

    def compute_shortest_paths(self, source_vertex, destination_vertex):
        shortest_path = self._compute_shortest_path(source_vertex, destination_vertex)
        self._shortest_paths.append(shortest_path)
        for _ in range(self._k - 1):
            min_distance = float('+inf')
            new_shortest_path = None
            removed_edge = None
            for edge in [shortest_path.get_edge(i, i + 1) for i in range(shortest_path.length - 1)]:
                self._graph.remove(edge)
                intermediate_shortest_path = self._compute_shortest_path(source_vertex, destination_vertex)
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

