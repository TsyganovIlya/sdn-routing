from SegmentationAlgorithm import SegmentationAlgorithm
from DijkstraAlgorithm import DijkstraAlgorithm
from network.Sender import Sender
from collections import defaultdict


class RoutingController(object):

    def __init__(self, switches, adjacency, weights, logger):
        """

        :type weights: defaultdict
        :type adjacency: defaultdict
        :type switches: dict
        """
        self._is_segmented = False
        self._islands = []
        self._switches = switches
        self._adjacency = adjacency
        self._weights = weights
        self._logger = logger
        self._sender = Sender(logger)

    @property
    def is_segmented(self):
        return self._is_segmented

    def compute_islands(self):
        alg = SegmentationAlgorithm(self._switches, self._weights.copy())
        alg.do()
        self._is_segmented = True
        self._islands = alg.islands
        self._sender.send_islands(self._convert_islands_to_bytes())

    def _convert_islands_to_bytes(self):
        islands_representation = []
        for island in self._islands:
            islands_representation.append(','.join([str(sw) for sw in island]))
        return bytearray(';'.join(islands_representation), 'utf-8')

    def compute_path(self, src_dpid, dst_dpid):
        alg = DijkstraAlgorithm(self._weights.copy())
        island = self._find_island_with(src_dpid, dst_dpid)
        if len(island) > 0:
            alg.set_switches(island)
            print "Dijkstra in island"
        else:
            alg.set_switches(self._switches.keys())
            print "Dijkstra in whole network"
        path = alg.compute_shortest_path(src_dpid, dst_dpid)
        self._sender.send_path(path.to_byte_array())
        return path

    def _find_island_with(self, dpid1, dpid2):
        for island in self._islands:
            if dpid1 in island and dpid2 in island:
                return island
        return []

