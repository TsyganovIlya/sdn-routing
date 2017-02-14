from DijkstraAlgorithm import DijkstraAlgorithm
from domain.Graph import Graph


class YenAlgorithm(object):

    def __init__(self, switches, adjacency, weights):
        self._graph = Graph(weights, switches)
        self._adjacency = adjacency
        self._K = len(switches) / 2  # TODO: Костыль
        self._dijkstra = DijkstraAlgorithm(adjacency, weights)

    def compute_shortest_paths(self, src_vertex, dst_vertex):
        dijkstra = lambda source, sink: self._dijkstra.compute_shortest_path(source, sink).convert_to_ordered_sequence()
        paths = [dijkstra(src_vertex, dst_vertex)]
        potential_paths = []
        for k in range(1, self._K):
            for i in range(0, len(paths[k - 1])):
                spur_node = paths[k - 1][i]
                root_path = paths[k - 1][:i]
                for path in paths:
                    if root_path == path[:i]:
                        edge = (paths[k - 1][i], paths[k - 1][i + 1])
                        self._graph.remove_edge(edge)
                for root_path_node in [node for node in root_path if node is not spur_node]:
                    self._graph.remove_vertex(root_path_node)
                spur_path = dijkstra(spur_node, dst_vertex)
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
