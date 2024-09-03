"""
    File: main.py
    Author: Aaron Fortner
    Date: 09/1/2024
    Version: 0.1

    Description: This file contains the main code for the Wireless Sensor Network (WSN) simulation.

    See the main README.md file for detailed information, installation instructions, and usage.
"""

import random

import numpy as np
from scipy.spatial import KDTree


class Node:
    """
    Class to represent a node in a Wireless Sensor Network (WSN).

    Each node has a unique identifier, coordinates, communication range, energy level, processing power, and
    fitness value.

    The fitness value (F) is calculated as follows:
    F = 0.4 * R + 0.4 * E + 0.2 * P
    where R is the communication range, E is the energy level, and P is the processing power.

    The node can also be assigned to a cluster and used to calculate the distance to another node.
    """

    def __init__(self, node_id, x, y, R, E, P):
        """
        Initialize a Node instance.

        :param node_id: Unique identifier for the node
        :param x: X-coordinate of the node
        :param y: Y-coordinate of the node
        :param R: Communication range of the node
        :param E: Energy level of the node
        :param P: Processing power of the node
        """
        self.node_id = node_id
        self.position = np.array([x, y])
        self.R = R
        self.E = E
        self.P = P
        self.cluster = None
        self.F = 0.4 * R + 0.4 * E + 0.2 * P

    def distance_to(self, other_node) -> np.floating:
        """
        Calculate the Euclidean distance to another node.

        :param other_node: The other node to calculate the distance to
        :return: Euclidean distance to the other node
        """
        return np.linalg.norm(self.position - other_node.position)


class Cluster:
    """
    Class to represent a cluster in a Wireless Sensor Network (WSN).
    """

    def __init__(self, cluster_id: int):
        """
        Initialize a Cluster instance.

        :param cluster_id: Unique identifier for the cluster
        """
        self.cluster_id = cluster_id
        self.nodes = []
        self.clusterhead = None

    def add_node(self, node: Node) -> None:
        """
        Add a node to the cluster.

        :param node: The node to add to the cluster
        """
        self.nodes.append(node)
        node.cluster = self

    def elect_clusterhead(self) -> Node | None:
        """
        Elect the cluster head based on the highest F value and proximity to the cluster center.

        :return: The elected cluster head node
        """
        if not self.nodes:
            return None

        self.clusterhead = max(self.nodes, key=lambda node: (node.F, -node.distance_to(self.center())))

        return self.clusterhead

    def center(self) -> Node:
        """
        Calculate the center of the cluster based on its ID.

        :return: A Node instance representing the center of the cluster
        """
        cluster_size = 5
        row = self.cluster_id // 4
        col = self.cluster_id % 4
        center_position = np.array([(col * cluster_size) + cluster_size / 2,
                                    (row * cluster_size) + cluster_size / 2])
        return Node(-1, center_position[0], center_position[1], 0, 0, 0)


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
        self.clusters = [Cluster(i) for i in range(16)]
        self.generate_nodes()
        self.assign_clusters()
        self.elect_clusterheads()

    def generate_nodes(self) -> None:
        """
        Generate nodes for the WSN based on the mode of operation.
        """
        if self.mode == 'random':
            num_nodes = random.randint(10, 100)
            for i in range(num_nodes):
                x = random.uniform(0, 20)
                y = random.uniform(0, 20)
                R = random.uniform(1, 8)
                E = random.uniform(1, 100)
                P = random.uniform(1, 100)
                self.nodes.append(Node(i + 1, x, y, R, E, P))
        elif self.mode == 'user':
            with open(self.input_file, 'r') as file:
                num_nodes = int(file.readline().strip())
                for i in range(num_nodes):
                    x, y, R, E, P = map(float, file.readline().strip().split())
                    self.nodes.append(Node(i + 1, x, y, R, E, P))

    def assign_clusters(self) -> None:
        """
        Assign nodes to clusters based on their coordinates.
        """
        for node in self.nodes:
            cluster_id = self.get_cluster_id(node.position[0], node.position[1])
            self.clusters[cluster_id].add_node(node)

    def get_cluster_id(self, x: float, y: float) -> int:
        """
        Get the cluster ID based on the coordinates of a node.

        :param x: X-coordinate of the node
        :param y: Y-coordinate of the node
        :return: Cluster ID
        """
        cluster_size = 5
        row = int(y // cluster_size)
        col = int(x // cluster_size)
        return row * 4 + col

    def elect_clusterheads(self) -> None:
        """
        Elect cluster heads for all clusters.
        """
        for cluster in self.clusters:
            cluster.elect_clusterhead()

    def find_route(self, src_id: int, dest_id: int) -> list[int]:
        """
        Find a route from the source node to the destination node.

        :param src_id: Source node ID
        :param dest_id: Destination node ID
        :return: List of node IDs representing the route
        """
        src_node = self.get_node_by_id(src_id)
        dest_node = self.get_node_by_id(dest_id)
        if not src_node or not dest_node:
            print("Invalid source or destination node.")
            return []

        route = [src_node]
        current_node = src_node
        while current_node != dest_node:
            next_node = self.get_nearest_node(current_node, dest_node)
            if not next_node:
                print("No route found.")
                return []
            route.append(next_node)
            current_node = next_node

        return [node.node_id for node in route]

    def get_nearest_node(self, current_node: int, dest_node: int) -> Node | None:
        """
        Get the nearest node to the destination node within the communication range.

        :param current_node: Current node
        :param dest_node: Destination node
        :return: Nearest node to the destination node
        """
        candidates = [node for node in self.nodes if node != current_node and current_node.distance_to(node)
                      <= current_node.R]
        if not candidates:
            return None
        return min(candidates, key=lambda node: node.distance_to(dest_node))

    def get_node_by_id(self, node_id: int) -> Node | None:
        """
        Get a node by its ID.

        :param node_id: Node ID
        :return: Node instance with the given ID
        """
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
            file.write(f'Number of nodes: {len(self.nodes)}\n')
            for node in self.nodes:
                file.write(f'{node.node_id} {node.position[0]} {node.position[1]} {node.R} {node.E} {node.P}\n')
            for cluster in self.clusters:
                if cluster.nodes:
                    file.write(f'Cluster {cluster.cluster_id + 1}:\n')
                    file.write(f'Nodes: {", ".join(str(node.node_id) for node in cluster.nodes)}\n')
                    if cluster.clusterhead:
                        file.write(f'Clusterhead: {cluster.clusterhead.node_id}\n')


def main() -> None:
    """
    Main function to run the WSN simulation.
    """
    print("Welcome to WSN Simulation!")
    while True:
        print("\nChoose mode of operation:")
        print("1. User Mode")
        print("2. Random Mode")
        print("3. Quit")

        choice = input("Enter your choice: ")
        if choice == '1':
            wsn = WSN(mode='user')
        elif choice == '2':
            wsn = WSN(mode='random')
        elif choice == '3':
            break
        else:
            print("Invalid choice, please try again.")
            continue

        wsn.save_network()

        while True:
            src_id = int(input("\nEnter source node ID: "))
            dest_id = int(input("Enter destination node ID: "))
            route = wsn.find_route(src_id, dest_id)
            if route:
                print(f'Route: {" -> ".join(map(str, route))}')
            again = input("Do you want to route another packet? (y/n): ")
            if again.lower() != 'y':
                break


if __name__ == "__main__":
    main()
