"""
    File: node.py
    Author: Aaron Fortner
    Date: 09/22/2024
    Version: 0.6

    Description: This file contains the Node class for the Wireless Sensor Network (WSN) simulation.

    See the main README.md file for detailed information, installation instructions, and usage.
"""
import numpy as np


class Node:
    """
    Class to represent a node in a Wireless Sensor Network (WSN).

    Each node has a unique identifier, coordinates, communication range, energy level, processing power, and
    fitness to be the cluster head value (f).

    The fitness value (f) is calculated as follows:     f = 0.4 * r + 0.4 * e + 0.2 * p
    where r is the communication range, e is the energy level, and p is the processing power.

    The node is also assigned to a cluster and the node class includes the ability to  calculate the distance to
    another node.
    """

    def __init__(self, node_id: int, x: float, y: float, r: int, e: int, p: int):
        """
        Initialize a Node instance.  Note: all characteristics are integers w/ the exception to the coordinates to
        allow for accurate determination and comparison of distances as well as determine actual center of clusters for
        clusterhead election processing, in general usage throughout the program they are treated as integers.  Also,
        the cluster head fitness score is a float to allow for more accurate comparison of cluster head candidates.

        :param node_id: Unique identifier for the node
        :param x: X-coordinate of the node
        :param y: Y-coordinate of the node
        :param r: Communication range of the node
        :param e: Energy level of the node
        :param p: Processing power of the node

        additional fields:
        cluster: Cluster the node belongs to
        f: Fitness value to be the cluster head
        """
        self.node_id: int = node_id
        self.position: np.ndarray = np.array([x, y], dtype=float)
        self.r: int = r
        self.e: int = e
        self.p: int = p
        self.cluster: int | None = None
        self.f: float = 0.4 * r + 0.4 * e + 0.2 * p

    def distance_to(self, other_node: 'Node') -> float:
        """
        Calculate the Euclidean distance to another node using numpy's linear algebra norm function.

        :param other_node: The other node to calculate the distance to
        :return: Euclidean distance to the other node
        """
        return float(np.linalg.norm(self.position - other_node.position))
