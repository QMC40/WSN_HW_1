"""
    File: wsn.py
    Author: Aaron Fortner
    Date: 09/22/2024
    Version: 0.6

    Description: This file contains the WSN class for the Wireless Sensor Network (WSN) simulation.

    See the main README.md file for detailed information, installation instructions, and usage.
"""
import os
import random
import numpy as np
from node import Node
from cluster import Cluster
from scipy.spatial import KDTree
from logging_config.logger import get_logger
from config.constants import CLUSTER_INDEX, CLUSTER_SIZE, MAX_COORD, NODE_INDEX, NUM_CLUSTERS

logger = get_logger()


def get_cluster_id(x: int, y: int, node_num: int) -> int:
    """
    Get the cluster ID based on the coordinates of a node.

    :param x: X-coordinate of the node
    :param y: Y-coordinate of the node
    :param node_num: current node number for logging
    :return cluster_id: Cluster ID based on the coordinates
    """

    def rank_and_file_calculator(value: int):
        """
        Calculates the correct row or column of the network grid of a node
        :param value: the relevant coordinate for the node being located
        :return: the row or column within which the node resides
        """
        # Calculate the row and column of the node based on the node's coordinates by floor division of the coordinate
        # by the cluster length.
        # Then subtract the result of the floor division of the coord by the max coord value
        # to reflect nodes on the outer edge back inside the network grid.
        result = int((value // CLUSTER_SIZE) - (value // MAX_COORD))

        # If the node is on the border between two segments, randomly assign it to one of the two adjacent segments.
        # If the node is at the outside edge of the network, keep the segment the same.
        # The adjustment is made by subtracting one from the result.
        if value % CLUSTER_SIZE == 0 and value != 0 and value != 20:
            if random.choice([True, False]):
                result -= 1
        return result

    # Call rank and file calc to determine the row and col containing the node
    col = rank_and_file_calculator(x)
    row = rank_and_file_calculator(y)

    # Return the cluster ID based on the row and column of the cluster.
    # The clusters are numbered from left to right and top to bottom starting from 0 or 1 depending on indexing,
    # so the cluster ID is calculated as row * 4 + col + CLUSTER_INDEX, where 4 is the number of columns per row:
    # so if the node is in row 0, col 0, and indexed at 0 the cluster ID is 0 (0 * 4 + 0 + 0), if its in row 3,
    # col 1, and indexed at 1 the cluster ID is 14 (3 * 4 + 1 + 1).
    cluster = row * 4 + col
    logger.debug(f"node {node_num} @ {x},{y} : {col},{row} assigned to cluster {cluster}")
    return cluster


class WSN:
    """
    Class to represent a Wireless Sensor Network (WSN).
    """

    def __init__(self, mode='random', input_file='input.txt'):
        """
        Initialize a WSN instance.

        :param mode: Mode of operation ('random' or 'user')
        :param input_file: Input file for user mode
        """
        self.mode = mode
        self.input_file = input_file
        self.nodes = []
        self.kd_tree = None  # Add an attribute for the KD Tree
        self.clusters = [Cluster(i) for i in range(NUM_CLUSTERS)]

        # Generate nodes, assign clusters and build the KD tree then elect cluster heads
        self.generate_nodes()
        self.assign_clusters()
        self.build_kd_tree()
        self.elect_clusterheads()

    def generate_nodes(self) -> None:
        """
        Generate nodes for the WSN based on the mode of operation.
        """
        if self.mode == 'random':
            # Pick random number of nodes between 10 and 100
            num_nodes = random.randint(10, 100)
            # Generate random nodes with coordinates, communication range, energy level, and processing power.
            for i in range(num_nodes):
                while True:
                    # generate coordinates for candidate node
                    x = random.randint(0, 20)
                    y = random.randint(0, 20)

                    # check for duplication of existing node at those coords, regen if found, otherwise finish
                    # construction of candidate node and save to the network
                    not_dupe = not any(node.position[0] == x and node.position[1] == y for node in self.nodes)

                    if not_dupe:
                        # If no duplicate found, generate the remaining characteristics and add the new node
                        r = random.randint(1, 8)
                        e = random.randint(1, 100)
                        p = random.randint(1, 100)
                        self.nodes.append(Node(i, x, y, r, e, p))
                        logger.debug(f"Node {i} @ ({x}, {y}) with R={r}, E={e}, P={p} added to the network.")
                        break  # Exit the loop once a valid node is added
                    else:
                        # If a duplicate is found, regenerate the coordinates and try again
                        print(f"Node @ coordinates ({x}, {y}) already exists. Regenerating...")

        elif self.mode == 'user':

            # Check if the input file exists
            if not os.path.exists(self.input_file):
                print(f"Error: The input file '{self.input_file}' does not exist.")
                return  # Exit the function if the file doesn't exist

            # Read nodes from the input file in user mode
            with open(self.input_file, 'r') as file:
                num_nodes = int(file.readline().strip())
                for i in range(num_nodes):
                    x, y, r, e, p = map(int, file.readline().strip().split())
                    # check for duplication of existing node at those coords, reject if found, otherwise finish
                    # construction of candidate node and save to the network
                    # Check for duplication of existing node at those coordinates
                    not_dupe = not any(node.position[0] == x and node.position[1] == y for node in self.nodes)

                    if not_dupe:
                        # If no duplicate found, add the new node, otherwise skip the node.
                        self.nodes.append(Node(i, x, y, r, e, p))
                        logger.debug(f"Node {i} @ ({x}, {y}) with R={r}, E={e}, P={p} added to the network.")
                    else:
                        print(f"Node @ coordinates ({x}, {y}) already exists in user input. Skipping...")

    def assign_clusters(self) -> None:
        """
        Assign nodes to clusters based on their coordinates.
        """
        # Iterate through all nodes and assign them to the appropriate cluster based on their coordinates.
        for node in self.nodes:
            cluster_id = get_cluster_id(node.position[0], node.position[1], node.node_id)
            self.clusters[cluster_id].add_node(node)

    def elect_clusterheads(self) -> None:
        """
        Elect cluster heads for all clusters.
        """
        # Iterate through all clusters and elect the cluster head for each cluster.
        for cluster in self.clusters:
            # Only elect a cluster head if the cluster has nodes
            if cluster.nodes:
                cluster.elect_clusterhead()

    def build_kd_tree(self):
        """
        Build a KD Tree using the positions of the nodes.
        """
        if self.nodes:
            positions = np.array([node.position for node in self.nodes])
            self.kd_tree = KDTree(positions)

    def find_route(self, src_id: int, dest_id: int) -> list[int]:
        """
        Find a route from the source node to the destination node.

        :param src_id: Source node ID.
        :param dest_id: Destination node ID.
        :return: List of node IDs representing the route, or an empty list if no route is found.
        """

        # Check if the network has less than two nodes, in which case no routing can be performed
        if self.kd_tree.tree.children <= 1:
            print("Network has less than two nodes in the network. No routing can be performed.")
            return []

        # Get the source and destination nodes
        src_node = self.get_node_by_id(src_id)
        dest_node = self.get_node_by_id(dest_id)

        # Start the route with the source node
        route = [src_node]
        current_node = src_node
        already_visited = set()  # Track visited nodes to avoid loops

        # Continue routing until the destination node is reached
        while current_node != dest_node:
            already_visited.add(current_node.node_id)

            # Get the nearest node to the destination within the current node's transmission range
            next_node = self.get_nearest_node_kdtree(current_node, dest_node, already_visited)

            if not next_node or next_node.node_id in already_visited:
                print("No valid route found.")
                return []  # Return an empty route if no valid next node is found or if stuck in a loop

            # Add the next node to the route and continue routing from that node
            route.append(next_node)
            current_node = next_node

        # Return the final route as a list of node IDs
        return [node.node_id for node in route]

    def get_nearest_node_kdtree(self, current_node: Node, dest_node: Node, visited: set[int]) -> Node | None:
        """
        Use KD Tree to find all nodes within the current node's communication range (radius search).
        From those nodes, find the one closest to the destination.

        :param current_node: The node currently sending the packet.
        :param dest_node: The final destination node for the packet.
        :param visited: The set of nodes already visited in path search.
        :return: The node within range closest to the destination, or None if no node is found.
        """

        # Radius search: Find all nodes within the current node's transmission range
        radius = current_node.r
        neighbors_within_range = self.kd_tree.query_ball_point(current_node.position, r=radius)

        # Check if the destination node is within the current node's transmission range, if so finish the route and
        # return the destination node as the next node in the route.
        if dest_node.node_id in neighbors_within_range:
            logger.debug(
                    f"Destination node {dest_node.node_id + NODE_INDEX} is within range of node "
                    f"{current_node.node_id + NODE_INDEX}."
                    )
            return dest_node

        logger.debug(
                    f"Neighbors within range of node {current_node.node_id + NODE_INDEX}: {
                        [neighbor + NODE_INDEX for neighbor in neighbors_within_range]
                        }"
                )

        # Remove the current node and any nodes already visited from the list of neighbors to prevent revisiting and
        # loops in the path
        neighbors_within_range = [node for node in neighbors_within_range if node not in visited]

        logger.debug(
                    f"Neighbors within range after removing current and visited nodes: {
                        [neighbor + NODE_INDEX for neighbor in neighbors_within_range]}"
                )

        # If no neighbors are within range, return None
        if not neighbors_within_range:
            return None

        # Sort neighbors by distance to the destination node and extract the nearest node
        neighbors_within_range.sort(key=lambda idx: self.nodes[idx].distance_to(dest_node))
        selected_node = self.nodes[neighbors_within_range[0]]

        logger.debug(f"Sorted neighbors within range: {[neighbor + NODE_INDEX for neighbor in neighbors_within_range]}")
        logger.debug(f"Closest node to destination: {selected_node.node_id + NODE_INDEX}")

        # return the nearest node to the destination from the list of neighbors within range
        return selected_node

    def get_node_by_id(self, node_id: int) -> Node | None:
        """
        Get a node by its ID.

        :param node_id: Node ID
        :return: Node instance with the given ID
        """
        # Iterate through all nodes and return the node with the given ID if found, otherwise return None
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        return None

    def save_network(self, output_file='network.txt') -> None:
        """
        Save the network configuration to a file.

        :param output_file: Output file name
        """
        with open(output_file, 'w') as file:
            # Write the number of nodes
            file.write(f'{len(self.nodes)}\n')
            print(f'\nNumber of nodes: {len(self.nodes)}')

            # Write details of each node
            for node in self.nodes:
                node_info = f'{int(node.position[0])}\t{int(node.position[1])}\t{node.r}\t{node.e}\t{node.p}'
                file.write(f'{node_info}\n')

            # Write cluster information
            for cluster in self.clusters:
                if cluster.nodes:
                    file.write(f'\nCluster {cluster.cluster_id + CLUSTER_INDEX}:\n')

                    node_ids = ", ".join(str(node.node_id + NODE_INDEX) for node in cluster.nodes)
                    file.write(f'Nodes: {node_ids}\n')

                    if cluster.clusterhead:
                        file.write(f'Clusterhead: {cluster.clusterhead.node_id + NODE_INDEX}\n')
