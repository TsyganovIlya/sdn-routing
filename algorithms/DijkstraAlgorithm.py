from domain.Path import Path


class DijkstraAlgorithm(object):

    def __init__(self, weight_map, vertices):
        self._vertices = []
        self._weight_map = weight_map
        self._source_vertex = 0
        self._destination_vertex = 0
        self._distance = {}
        self._previous = {}
        self._viewed_vertices = []
        self._vertices = vertices

    def compute_shortest_path(self, source_vertex, destination_vertex):
        self._source_vertex = source_vertex
        self._destination_vertex = destination_vertex

        for vertex in self._vertices:
            self._distance[vertex] = float("+inf")
            self._previous[vertex] = None

        self._viewed_vertices = set(self._vertices)
        self._distance[self._source_vertex] = 0
        while len(self._viewed_vertices) > 0:
            current_vertex = self._find_nearest_vertex()
            if not current_vertex:
                break
            self._viewed_vertices.remove(current_vertex)
            for vertex in self._vertices:
                if vertex in self._weight_map[current_vertex]:
                    tmp_distance = self._distance[current_vertex] + self._weight_map[current_vertex][vertex]
                    if tmp_distance < self._distance[vertex]:
                        self._distance[vertex] = tmp_distance
                        self._previous[vertex] = current_vertex

        ordered_vertices = self._recover_path()
        return Path(ordered_vertices)

    def _find_nearest_vertex(self):
        min_distance = float('+inf')
        nearest_vertex = None
        for vertex in self._viewed_vertices:
            if self._distance[vertex] < min_distance:
                min_distance = self._distance[vertex]
                nearest_vertex = vertex
        return nearest_vertex

    def _recover_path(self):
        ordered_vertices = [self._destination_vertex]
        current_vertex = self._previous[self._destination_vertex]
        while current_vertex is not None:
            ordered_vertices.append(current_vertex)
            current_vertex = self._previous[current_vertex]
        ordered_vertices.reverse()
        return ordered_vertices
