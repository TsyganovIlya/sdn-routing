from DijkstraAlgorithm import DijkstraAlgorithm
from domain.Graph import Graph
from domain.Path import Path


class YenAlgorithm(object):

    def __init__(self, weight_map, vertices, k):
        self._graph = Graph(weight_map, vertices)
        self._k = k
        self._dijkstra = DijkstraAlgorithm(weight_map, vertices)

    def compute_shortest_paths(self, src_vertex, dst_vertex):
        paths = [self._dijkstra.compute_shortest_path(src_vertex, dst_vertex)]
        potential_paths = []
        for k in range(1, self._k + 1):
            for i in range(paths[k - 1].size - 1):
                spur_vertex = paths[k - 1].get_vertex(i)
                root_path = paths[k - 1].get_vertices(0, i)  # 'i' is not included. It is index of spur vertex
                for path in paths:
                    if root_path == Path(path.get_vertices(0, i)):
                        self._graph.remove_edge(path.get_edge(i, i + 1))
                for root_path_vertex in root_path:
                    self._graph.remove_vertex(root_path_vertex)
                spur_path = self._dijkstra.compute_shortest_path(spur_vertex, dst_vertex)
                total_path = root_path + spur_path
                potential_paths.append(total_path)
                self._graph.restore_vertices()
                self._graph.restore_edges()
            if len(potential_paths) is 0:
                break
            potential_paths.sort(key=lambda p: self._graph.count_distance_for(p))
            paths.append(potential_paths.pop(0))
        return paths
