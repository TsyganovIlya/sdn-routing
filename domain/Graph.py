

class Graph(object):

    def __init__(self, edges, nodes):
        """

        :type edges: dict
        :type nodes: list
        """
        self._nodes = nodes
        self._edges = edges  # it is weights dict
        self._stored_nodes = nodes[:]
        self._stored_edges = edges.copy()

    def restore_edges(self):
        self._edges = self._stored_edges.copy()

    def restore_nodes(self):
        self._nodes = self._stored_nodes

    def count_distance_for(self, path):
        distance = 0
        for i in range(len(path) - 1):
            distance += self._edges[path[i]][path[i + 1]]
        return distance

    def remove_edge(self, edge):
        """

        :type edge: tuple
        """
        self._edges[edge[0]][edge[1]] = float('+inf')
        self._edges[edge[1]][edge[0]] = float('+inf')

    def remove_node(self, node):
        self._nodes.pop(node)
