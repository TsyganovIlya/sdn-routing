from VertexIterator import VertexIterator


class Path(object):

    def __init__(self, vertices):
        self._vertices = vertices

    def get_vertex(self, index):
        return self._vertices[index]

    def get_vertices(self, start_index, end_index):
        return self._vertices[start_index:end_index]

    def get_edge(self, vertex_index_1, vertex_index_2):
        return self._vertices[vertex_index_1], self._vertices[vertex_index_2]

    @property
    def source(self):
        return self._vertices[0]

    @property
    def destination(self):
        return self._vertices[len(self._vertices) - 1]

    def __len__(self):
        return len(self._vertices)

    def to_byte_array(self):
        representation = ",".join([str(s) for s in self._vertices])
        return bytearray(representation, 'utf-8')

    def __str__(self):
        return "->".join(["s{0}".format(s) for s in self._vertices])

    def __repr__(self):
        return ",".join([str(s) for s in self._vertices])

    @property
    def vertex_iterator(self):
        return VertexIterator(self._vertices)

    def __eq__(self, other):
        """
        :type other: Path
        """
        return self._vertices == other.get_vertices(0, other.length)

    def __add__(self, other):
        """
        :type other: Path
        """
        return Path(self._vertices + other.get_vertices(0, other.length))

