class VertexIterator(object):

    def __init__(self, vertices):
        self._vertices = vertices
        self._current = 0

    def move_next(self):
        if self._current < len(self._vertices) - 1:
            self._current += 1
            return True
        return False

    @property
    def current(self):
        return self._vertices[self._current]
