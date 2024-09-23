"""
    File: cluster.py
    Author: Aaron Fortner
    Date: 09/22/2024
    Version: 0.6

    Description: This file contains the Cluster class for the Wireless Sensor Network (WSN) simulation.

    See the main README.md file for detailed information, installation instructions, and usage.
"""
import random
import numpy as np
from node import Node
from config.constants import CLUSTER_SIZE


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
        node.cluster = self.cluster_id

    def elect_clusterhead(self) -> Node | None:
        """
        Elect the cluster head based on the highest fitness score (f), proximity to the cluster center,
        and in case of a further tie, picks randomly from the tied nodes.

        :return: The elected cluster head node
        """
        # Find the maximum fitness score among all nodes
        max_fitness = max(node.f for node in self.nodes)

        # Filter nodes with the highest fitness score
        top_nodes = [node for node in self.nodes if node.f == max_fitness]

        if len(top_nodes) == 1:
            # Only one node with the highest fitness score, so it becomes the cluster head
            self.clusterhead = top_nodes[0]
        else:
            # If there is a tie in fitness scores, compare distances to the cluster center
            center_node = self.center()
            min_distance = min(node.distance_to(center_node) for node in top_nodes)

            # Filter the top nodes by distance to the center
            closest_nodes = [node for node in top_nodes if node.distance_to(center_node) == min_distance]

            if len(closest_nodes) == 1:
                # Only one node closest to the center, so it becomes the cluster head
                self.clusterhead = closest_nodes[0]
            else:
                # If there's still a tie, pick a random node from the closest ones
                self.clusterhead = random.choice(closest_nodes)

        return self.clusterhead

    def center(self) -> Node:
        """
        Calculate the center of the cluster based on its ID.

        :return: A Node instance representing the center of the cluster
        """
        # Calculate the baseline for the cluster based on the cluster ID: the cluster ID is used to determine the row by
        # dividing by 4 and the column by taking the modulo of 4. The center position is then calculated based on the
        # row and column.
        # The center position is calculated as follows: Column is determined by cluster ID modulo 4, and row is the
        # cluster ID divided by 4. The center position is the column number times the cluster size plus half the
        # cluster size for the x-coordinate, and the row number times the cluster size plus half the cluster size for
        # the y-coordinate.
        # Calculate the column and row of the cluster
        col = self.cluster_id % 4
        row = self.cluster_id // 4
        center_position = np.array(
                [(col * CLUSTER_SIZE) + CLUSTER_SIZE / 2,
                 (row * CLUSTER_SIZE) + CLUSTER_SIZE / 2]
                )
        return Node(-1, float(center_position[0]), float(center_position[1]), 0, 0, 0)
