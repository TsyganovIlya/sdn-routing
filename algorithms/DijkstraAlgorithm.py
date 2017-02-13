from domain.Path import Path


class DijkstraAlgorithm(object):

    def __init__(self, weights):
        self.switches = []
        self.weights = weights

    def set_switches(self, value):
        self.switches = value

    def compute_shortest_path(self, src_vertex, dst_vertex):

        def find_nearest_vertex(viewed_vertices, distance):
            min_distance = float('+inf')
            nearest_vertex = None
            for vertex in viewed_vertices:
                if distance[vertex] < min_distance:
                    min_distance = distance[vertex]
                    nearest_vertex = vertex
            return nearest_vertex

        vertices = self.switches
        distance = {}
        previous = {}

        for vertex in vertices:
            distance[vertex] = float("+inf")
            previous[vertex] = None

        viewed_vertices = set(vertices)
        distance[src_vertex] = 0
        while len(viewed_vertices) > 0:
            current_vertex = find_nearest_vertex(viewed_vertices, distance)
            viewed_vertices.remove(current_vertex)
            for vertex in vertices:
                if vertex in self.weights[current_vertex]:
                    tmp_distance = distance[current_vertex] + self.weights[current_vertex][vertex]
                    if tmp_distance < distance[vertex]:
                        distance[vertex] = tmp_distance
                        previous[vertex] = current_vertex

        return Path(src_vertex, dst_vertex, previous)
