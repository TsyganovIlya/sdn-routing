from SegmentationAlgorithm import SegmentationAlgorithm
from DijkstraAlgorithm import DijkstraAlgorithm
from network.sending import Sender
from collections import defaultdict
from util.DeepCopier import DeepCopier
from algorithms.YenAlgorithm import YenAlgorithm


class RoutingController(object):

    def __init__(self, switches, weight_map, logger):
        """
        :type weight_map: defaultdict
        :type switches: dict
        """
        self._is_segmented = False
        self._islands = []
        self._switches = switches
        self._weight_map = weight_map
        self._logger = logger
        self._sender = Sender(logger)

    @property
    def is_segmented(self):
        return self._is_segmented

    def compute_islands(self):
        copier = DeepCopier(self._weight_map)
        alg = SegmentationAlgorithm(self._switches.keys(), copier.make_copy())
        alg.do()
        self._is_segmented = True
        self._islands = alg.islands
        self._sender.send_islands(self._convert_islands_to_bytes())

    def _convert_islands_to_bytes(self):
        islands_representation = []
        for island in self._islands:
            islands_representation.append(','.join([str(sw) for sw in island]))
        return bytearray(';'.join(islands_representation), 'utf-8')

    def _convert_paths_to_bytes(self, paths):
        paths_representation = []
        for path in paths:
            paths_representation.append(path.__repr__())
        return bytearray(';'.join(paths_representation), 'utf-8')

    def compute_path(self, source_switch, destination_switch):
        copier = DeepCopier(self._weight_map)
        island = self._find_island_with(source_switch, destination_switch)
        if island:
            alg = DijkstraAlgorithm(copier.make_copy(), island)
        else:
            alg = DijkstraAlgorithm(copier.make_copy(), self._switches.keys())
        path = alg.compute_shortest_path(source_switch, destination_switch)
        self._sender.send_path(path.__repr__())
        return path

    def compute_paths(self, source_switch, destination_switch):
        copier = DeepCopier(self._weight_map)
        island = self._find_island_with(source_switch, destination_switch)
        if island:
            alg = YenAlgorithm(copier.make_copy(), island, 6)
        else:
            alg = YenAlgorithm(copier.make_copy(), self._switches.keys(), 6)
        alg.compute_shortest_paths(source_switch, destination_switch)
        paths = alg.shortest_paths
        self._sender.send_paths(self._convert_paths_to_bytes(paths))
        return paths[0]

    def _find_island_with(self, dpid1, dpid2):
        for island in self._islands:
            if dpid1 in island and dpid2 in island:
                return island
        return []

