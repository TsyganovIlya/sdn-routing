from PathIterator import PathIterator


class Path(object):

    def __init__(self, vertices):
        self._vertices = vertices

    @property
    def source(self):
        return self._vertices[0]

    @property
    def destination(self):
        return self._vertices[len(self._vertices) - 1]

    @property
    def vertex_number(self):
        return len(self._vertices)

    def to_byte_array(self):
        representation = ",".join([str(s) for s in self._vertices])
        return bytearray(representation, 'utf-8')

    def __repr__(self):
        return "->".join(["s{0}".format(s) for s in self._vertices])

    def get_iterator(self):
        return PathIterator(self._vertices)

