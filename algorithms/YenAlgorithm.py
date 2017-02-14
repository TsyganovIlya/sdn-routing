from DijkstraAlgorithm import DijkstraAlgorithm
from domain.Graph import Graph


class YenAlgorithm(object):

    def __init__(self, weight_map, vertices, k):
        self._graph = Graph(weight_map, vertices)
        self._k = k
        self._dijkstra = DijkstraAlgorithm(weight_map, vertices)

    def get_shortest_path(self, source, sink):
        return self._dijkstra.compute_shortest_path(source, sink)

    def compute_shortest_paths(self, src_vertex, dst_vertex):
        paths = [self.get_shortest_path(src_vertex, dst_vertex)]
        potential_paths = []
        for k in range(1, self._k):
            for i in range(0, paths[k - 1].count):
                spur_node = paths[k - 1].get_vertex(i)
                root_path = paths[k - 1].get_vertices(0, i)
                for path in paths:
                    if root_path == path.get_vertices(0, i):
                        self._graph.remove_edge(paths[k - 1].get_edge(i, i + 1))
                for root_path_node in [node for node in root_path if node is not spur_node]:
                    self._graph.remove_vertex(root_path_node)
                spur_path = self.get_shortest_path(spur_node, dst_vertex)
                total_path = root_path + spur_path
                potential_paths.append(total_path)
                self._graph.restore_vertices()
                self._graph.restore_edges()
            if len(potential_paths) is 0:
                break
            potential_paths.sort(key=lambda p: self._graph.count_distance_for(p))
            paths.append(potential_paths[0])
            potential_paths.remove(potential_paths[0])
        return paths
