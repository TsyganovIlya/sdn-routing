class Path(object):

    def __init__(self, src_vertex, dst_vertex, previous_sequence):
        self._source = src_vertex
        self._destination = dst_vertex
        self._previous_sequence = previous_sequence

    @property
    def previous_sequence(self):
        return self._previous_sequence

    @property
    def source(self):
        return self._source

    @property
    def destination(self):
        return self._destination

    def to_byte_array(self):
        representation = ",".join([str(s) for s in self.convert_to_ordered_sequence()])
        return bytearray(representation, 'utf-8')

    def __repr__(self):
        return "->".join(["s{0}".format(s) for s in self.convert_to_ordered_sequence()])

    def convert_to_ordered_sequence(self):
        ordered_sequence = [self.destination]
        u = self.previous_sequence[self.destination]
        while u is not None:
            ordered_sequence.insert(0, u)
            u = self.previous_sequence[u]
        return ordered_sequence


