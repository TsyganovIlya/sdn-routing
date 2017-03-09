from domain.VertexIterator import VertexIterator


class Path(object):

    def __init__(self, vertices):
        self._vertices = vertices

    @property
    def vertex_iterator(self):
        return VertexIterator(self._vertices)

    @property
    def source(self):
        return self._vertices[0]

    @property
    def destination(self):
        return self._vertices[len(self._vertices) - 1]

    def get_vertices(self, start_index, end_index):
        return self._vertices[start_index:end_index]

    def get_edge(self, vertex_index_1, vertex_index_2):
        return self._vertices[vertex_index_1], self._vertices[vertex_index_2]

    def __bytes__(self):
        return bytes(self.__repr__(), 'utf-8')

    def __getitem__(self, item):
        return self._vertices[item]

    def __len__(self):
        return len(self._vertices)

    def __str__(self):
        return "->".join(["s{0}".format(s) for s in self._vertices])

    def __repr__(self):
        return ",".join([str(s) for s in self._vertices])

    def __eq__(self, other):
        return self._vertices == other.get_vertices(0, len(other))

