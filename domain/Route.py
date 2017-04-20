from domain.SwitchIterator import SwitchIterator


class Route(object):

    def __init__(self, switches):
        self._switches = switches

    @property
    def switch_iterator(self):
        return SwitchIterator(self._switches)

    @property
    def source(self):
        return self._switches[0]

    @property
    def destination(self):
        return self._switches[len(self._switches) - 1]

    def get_switches(self, start_index, end_index):
        return self._switches[start_index:end_index]

    def get_link(self, switch1, switch2):
        return self._switches[switch1], self._switches[switch2]

    def __getitem__(self, item):
        return self._switches[item]

    def __len__(self):
        return len(self._switches)

    def __str__(self):
        return "->".join(["s{0}".format(s) for s in self._switches])

    def __repr__(self):
        return ",".join([str(s) for s in self._switches])

    def __eq__(self, other):
        return self._switches == other.get_switches(0, len(other))

