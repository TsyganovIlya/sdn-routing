class SwitchIterator(object):

    def __init__(self, switches):
        self._switches = switches
        self._current = 0

    def move_next(self):
        if self._current < len(self._switches) - 1:
            self._current += 1
            return True
        return False

    @property
    def current(self):
        return self._switches[self._current]
