from PrimAlgorithm import PrimAlgorithm


class SegmentationAlgorithm(object):

    def __init__(self, switches, weights_matrix):
        self._switches = switches
        self._weights_matrix = weights_matrix
        self.connection_value = 0.8
        self.minimum_tree = []
        self.islands = []

    def do(self):
        # Step 1: To compute a minimum tree
        prim = PrimAlgorithm(self._switches, self._weights_matrix)
        self.minimum_tree = prim.do()
        # Step 2: To form primary islands
        self.form_primary_islands()
        # Step 3: To form secondary islands
        self.form_secondary_islands()
        # Step 4: To merge weak connected islands
        self.merge_weak_connected_islands()

    def form_primary_islands(self):
        for switch in self._switches:
            switch_degree = self.compute_degree_for(switch)
            if switch_degree == 1:
                switch_parent = self.find_neighbors_from_minimum_tree_for(switch)[0]
                unallocated_switches = self.find_unallocated_switches()
                if switch_parent in unallocated_switches:
                    self.islands.append([switch, switch_parent])
                else:
                    island_of_parent = self.find_island_for(switch_parent)
                    island_of_parent.append(switch)

    def form_secondary_islands(self):
        unallocated_switches = self.find_unallocated_switches()
        while len(unallocated_switches) > 0:
            candidate_bundles = []
            for switch in unallocated_switches:
                tmp_island_group = self.filter_islands_connected_to_switch_by_minimal_tree(switch)
                tmp_island_group = self.filter_islands_with_max_connectivity_to_switch(switch, tmp_island_group)
                candidate_island, weight_to_candidate_island = self.filter_island_connected_to_switch_by_minimum_weight(
                    switch, tmp_island_group)
                if len(candidate_island) > 0 and weight_to_candidate_island > 0:
                    candidate_bundles.append((switch, weight_to_candidate_island, candidate_island))

            bundle_with_min_weight = candidate_bundles[0]
            for bundle in candidate_bundles:
                if bundle[1] < bundle_with_min_weight[1]:
                    bundle_with_min_weight = bundle
            # merge switch (index 0) and island (index 2)
            bundle_with_min_weight[2].append(bundle_with_min_weight[0])
            unallocated_switches.remove(bundle_with_min_weight[0])

    def merge_weak_connected_islands(self):
        weak_connected_islands = self.find_weak_connected_islands()
        while len(weak_connected_islands) > 0:
            candidate_bundles = []
            for island in weak_connected_islands:
                tmp_island_group = self.filter_islands_connected_to_island_by_minimal_tree(island)
                tmp_island_group = self.filter_islands_with_max_connectivity_to_island(island, tmp_island_group)
                candidate_island, weight_to_candidate_island = self.filter_island_connected_to_island_by_minimum_weight(
                    island, tmp_island_group)
                if len(candidate_island) > 0 and weight_to_candidate_island > 0:
                    candidate_bundles.append((island, weight_to_candidate_island, candidate_island))

            bundle_with_min_weight = candidate_bundles[0]
            for bundle in candidate_bundles:
                if bundle[1] < bundle_with_min_weight[1]:
                    bundle_with_min_weight = bundle
            island1 = bundle_with_min_weight[0]
            island2 = bundle_with_min_weight[2]
            island2.extend(island1)
            self.islands.remove(island1)
            weak_connected_islands.remove(island1)
            if island2 in weak_connected_islands:
                weak_connected_islands.remove(island2)

    def find_neighbors_from_minimum_tree_for(self, switch):
        neighbors_from_minimum_tree = []
        for neighbor in self._weights_matrix[switch].keys():
            if (switch, neighbor) in self.minimum_tree:
                neighbors_from_minimum_tree.append(neighbor)
        return neighbors_from_minimum_tree

    def compute_degree_for(self, switch):
        neighbors_from_minimum_tree = self.find_neighbors_from_minimum_tree_for(switch)
        return len(neighbors_from_minimum_tree)

    def find_island_for(self, switch):
        for island in self.islands:
            if switch in island:
                return island
        return []

    def find_allocated_switches(self):
        return self.extract_switches_from(self.islands)

    def find_unallocated_switches(self):
        unallocated_switches = self.find_allocated_switches()
        return list(set(self._switches) - set(unallocated_switches))

    def find_external_links_for(self, island):
        external_links = []
        for switch in island:
            for neighbor in self._weights_matrix[switch].keys():
                if neighbor not in island:
                    external_links.append((switch, neighbor))
        return external_links

    def find_internal_links_for(self, island):
        internal_links = []
        for switch in island:
            for neighbor in self._weights_matrix[switch].keys():
                if neighbor in island:
                    internal_links.append((switch, neighbor))
        return internal_links

    def compute_connection_value_for(self, island):
        internal_links_number = len(self.find_internal_links_for(island)) / 2
        external_links_number = len(self.find_external_links_for(island))
        if external_links_number == self.connection_value:  # there are only one island
            return 1
        return internal_links_number / float(external_links_number)

    def find_weak_connected_islands(self):
        weak_connected_islands = []
        for island in self.islands:
            if self.compute_connection_value_for(island) < self.connection_value:
                weak_connected_islands.append(island)
        return weak_connected_islands

    def compute_connections_between_switch_and_island(self, switch, island):
        connections_number = 0
        for neighbor in self._weights_matrix[switch].keys():
            if neighbor in island:
                connections_number += 1
        return connections_number

    def compute_connections_between_island_and_island(self, island1, island2):
        connections_number = 0
        for switch in island1:
            for neighbor in self._weights_matrix[switch].keys():
                if neighbor in island2:
                    connections_number += 1
        return connections_number

    def extract_switches_from(self, islands):
        return reduce(lambda result, island: result + island, islands, [])

    def filter_islands_connected_to_switch_by_minimal_tree(self, switch):
        filtered_islands = []
        for neighbor in self._weights_matrix[switch].keys():
            if (switch, neighbor) in self.minimum_tree:
                neighbor_island = self.find_island_for(neighbor)
                if len(neighbor_island) > 0:
                    filtered_islands.append(neighbor_island)
        return filtered_islands

    def filter_islands_with_max_connectivity_to_switch(self, switch, islands):
        filtered_islands = []
        max_connectivity = 0
        for island in islands:
            connections_number_to_switch = self.compute_connections_between_switch_and_island(switch, island)
            if connections_number_to_switch > max_connectivity:
                del filtered_islands[:]
                filtered_islands.append(island)
                max_connectivity = connections_number_to_switch
            elif connections_number_to_switch == max_connectivity:
                filtered_islands.append(island)
        return filtered_islands

    def filter_island_connected_to_switch_by_minimum_weight(self, switch, islands):
        if len(islands) == 0:
            return [], 0  # default value
        switches_from_islands = self.extract_switches_from(islands)
        min_weight = float('+inf')
        neighbor_connected_by_min_weight = -1
        for neighbor in self._weights_matrix[switch].keys():
            if neighbor in switches_from_islands and self._weights_matrix[switch][neighbor] < min_weight:
                neighbor_connected_by_min_weight = neighbor
                min_weight = self._weights_matrix[switch][neighbor]
        return self.find_island_for(neighbor_connected_by_min_weight), min_weight

    def filter_islands_connected_to_island_by_minimal_tree(self, island):
        filtered_islands = []
        for switch in island:
            for neighbor in self._weights_matrix[switch].keys():
                if neighbor not in island and (switch, neighbor) in self.minimum_tree:
                    neighbor_island = self.find_island_for(neighbor)
                    if len(neighbor_island) > 0:
                        filtered_islands.append(neighbor_island)
        return filtered_islands

    def filter_islands_with_max_connectivity_to_island(self, island, islands):
        filtered_islands = []
        max_connectivity = 0
        for other_island in islands:
            connections_number_to_island = self.compute_connections_between_island_and_island(island, other_island)
            if connections_number_to_island > max_connectivity:
                del filtered_islands[:]
                filtered_islands.append(other_island)
                max_connectivity = connections_number_to_island
            elif connections_number_to_island == max_connectivity:
                filtered_islands.append(other_island)
        return filtered_islands

    def filter_island_connected_to_island_by_minimum_weight(self, island, islands):
        if len(islands) == 0:
            return [], 0  # default value
        switches_from_islands = self.extract_switches_from(islands)
        min_weight = float('+inf')
        neighbor_connected_by_min_weight = -1
        for switch in island:
            for neighbor in self._weights_matrix[switch].keys():
                if neighbor in switches_from_islands and self._weights_matrix[switch][neighbor] < min_weight:
                    neighbor_connected_by_min_weight = neighbor
                    min_weight = self._weights_matrix[switch][neighbor]
        return self.find_island_for(neighbor_connected_by_min_weight), min_weight
