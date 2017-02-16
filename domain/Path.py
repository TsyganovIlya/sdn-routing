from PathIterator import PathIterator


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

    @property
    def size(self):
        return len(self._vertices)

    def to_byte_array(self):
        representation = ",".join([str(s) for s in self._vertices])
        return bytearray(representation, 'utf-8')

    def __repr__(self):
        return "->".join(["s{0}".format(s) for s in self._vertices])

    def get_iterator(self):
        return PathIterator(self._vertices)

    def __eq__(self, other):
        """
        :type other: Path
        """
        return self._vertices == other.get_vertices(0, other.size)

    def __add__(self, other):
        return Path(self._vertices + other.get_vertices(0, other.size))

