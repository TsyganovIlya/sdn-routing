from domain.Path import Path
from algorithms.DijkstraAlgorithm import DijkstraAlgorithm


class PairTransitionsAlgorithm(object):

    def __init__(self, switches, weights):
        self._switches = switches
        self._weights = weights
        self.tree_edges = set()
        self.replacement_edges = set()
        self.current_route = Path([])
        self.previous = {}

    def compute_shortest_route(self, src, dst):
        dijkstra = DijkstraAlgorithm(
            self._weights, self._switches)
        self.current_route = \
            dijkstra.compute_shortest_path(src, dst)
        self.previous = dijkstra.previous
        return self.current_route

    def recompute_shortest_route(self):
        if len(self.current_route) > 1:
            return self.compute_shortest_route(
                self.current_route.source,
                self.current_route.destination)
        return self.current_route

    def count_pair_transitions(self):
        old_tree_edges = self.tree_edges
        self.collect_statistics()
        return len(self.tree_edges - old_tree_edges) / 2

    def collect_statistics(self):
        all_edges = self.unpack_edges_from_weights(
            self._weights)
        self.tree_edges = self.unpack_edges_from_previous(
            self.previous)
        self.replacement_edges = \
            all_edges - self.tree_edges

    def unpack_edges_from_weights(self, weights):
        all_edges = set()
        for v1 in weights.keys():
            for v2 in weights[v1].keys():
                all_edges.add((v1, v2))
        return all_edges

    def unpack_edges_from_previous(self, previous):
        tree_edges = set()
        for item in previous:
            if previous[item]:
                tree_edges.add((item, previous[item]))
                tree_edges.add((previous[item], item))
        return tree_edges
