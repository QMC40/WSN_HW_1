"""
    File: test_main.py
    Author: Aaron Fortner
    Date: 09/8/2024
    Version: 0.4

    Description: This file contains the unit testing code for the Wireless Sensor Network (WSN) simulation.

    See the main README.md file for detailed information, installation instructions, and usage.
"""
import unittest
import numpy as np
from main import Node, Cluster, WSN, get_cluster_id


class TestWSN(unittest.TestCase):

    def setUp(self):
        """Create a basic WSN for testing."""
        self.wsn = WSN(mode='user', input_file='testing/single_input.txt')
        self.wsn.nodes.clear()
        self.wsn.kd_tree = None

    def test_wsn_setup(self):
        """Test that the WSN is set up correctly."""
        # Create nodes manually for predictable behavior
        node0 = Node(0, 0, 0, 5, 50, 50)  # (x, y, range, energy, processing power)
        node1 = Node(1, 3, 4, 5, 50, 50)  # Within range of node1
        node2 = Node(2, 6, 8, 5, 50, 50)  # Within range of node2

        self.wsn.nodes = [node0, node1, node2]
        self.wsn.build_kd_tree()

        self.assertEqual(len(self.wsn.nodes), 3)
        self.assertEqual(len(self.wsn.clusters), 16)
        self.assertEqual(self.wsn.kd_tree.data.shape, (3, 2))
        self.assertEqual(self.wsn.nodes[0].node_id, 0)
        self.assertEqual(self.wsn.nodes[1].node_id, 1)
        self.assertEqual(self.wsn.nodes[2].node_id, 2)
        self.assertEqual(self.wsn.nodes[0].position[0], 0)
        self.assertEqual(self.wsn.nodes[0].position[1], 0)
        self.assertEqual(self.wsn.nodes[1].position[0], 3)
        self.assertEqual(self.wsn.nodes[1].position[1], 4)
        self.assertEqual(self.wsn.nodes[2].position[0], 6)
        self.assertEqual(self.wsn.nodes[2].position[1], 8)
        self.assertEqual(self.wsn.nodes[0].r, 5)
        self.assertEqual(self.wsn.nodes[1].r, 5)
        self.assertEqual(self.wsn.nodes[2].r, 5)
        self.assertEqual(self.wsn.nodes[0].e, 50)
        self.assertEqual(self.wsn.nodes[1].e, 50)
        self.assertEqual(self.wsn.nodes[2].e, 50)
        self.assertEqual(self.wsn.nodes[0].p, 50)
        self.assertEqual(self.wsn.nodes[1].p, 50)
        self.assertEqual(self.wsn.nodes[2].p, 50)

    def test_node_generation(self):
        """Test that nodes are generated in random mode."""
        self.wsn = WSN(mode='random')
        self.assertGreaterEqual(len(self.wsn.nodes), 10)
        self.assertLessEqual(len(self.wsn.nodes), 100)
        for node in self.wsn.nodes:
            self.assertGreaterEqual(node.position[0], 0)
            self.assertLessEqual(node.position[0], 20)
            self.assertGreaterEqual(node.position[1], 0)
            self.assertLessEqual(node.position[1], 20)

    def test_node_distance(self):
        """Test the Euclidean distance between two nodes."""
        node0 = Node(0, 0, 0, 5, 50, 50)
        node1 = Node(1, 3, 4, 5, 50, 50)  # Distance should be 5 (3-4-5 triangle)
        node2 = Node(2, 6, 8, 5, 50, 50)
        node3 = Node(3, 9, 12, 5, 50, 50)
        node4 = Node(4, 8, 0, 5, 50, 50)
        node5 = Node(5, 3, 15, 5, 50, 50)
        distance1 = node0.distance_to(node1)
        distance2 = node0.distance_to(node2)
        distance3 = node0.distance_to(node3)
        distance4 = node0.distance_to(node4)
        distance5 = round(node0.distance_to(node5), 8)
        distance6 = node1.distance_to(node5)
        self.assertEqual(distance1, 5)
        self.assertEqual(distance2, 10)
        self.assertEqual(distance3, 15)
        self.assertEqual(distance4, 8)
        self.assertEqual(distance5, 15.29705854)
        self.assertEqual(distance6, 11)

    def test_cluster_assignment(self):
        """Test that nodes are correctly assigned to clusters based on their coordinates."""
        self.wsn.assign_clusters()
        for node in self.wsn.nodes:
            cluster_id = get_cluster_id(node.position[0], node.position[1], node.node_id)
            self.assertIn(node, self.wsn.clusters[cluster_id].nodes)

    def test_cluster_head_election(self):
        """Test that the correct node is elected as the cluster head."""
        cluster = Cluster(5)
        node0 = Node(0, 5, 5, 4, 70, 40)  # F = 0.4 * 4 + 0.4 * 70 + 0.2 * 40 = 37.6
        node1 = Node(1, 6, 6, 3, 80, 50)  # F = 0.4 * 3 + 0.4 * 80 + 0.2 * 50 = 43.2
        node2 = Node(2, 7, 7, 2, 60, 20)  # F = 0.4 * 2 + 0.4 * 60 + 0.2 * 20 = 28.8
        node3 = Node(3, 5, 9, 3, 80, 50)  # F = 0.4 * 3 + 0.4 * 80 + 0.2 * 50 = 43.2
        cluster.add_node(node0)
        cluster.add_node(node1)
        cluster.add_node(node2)
        cluster.add_node(node3)
        cluster.elect_clusterhead()
        print(f'Clusterhead before adding node 5: {cluster.clusterhead.node_id}')
        self.assertEqual(cluster.clusterhead.node_id, 1)
        node4 = Node(4, 9, 9, 3, 80, 50)  # F = 0.4 * 3 + 0.4 * 80 + 0.2 * 50 = 43.2
        cluster.add_node(node4)
        cluster.elect_clusterhead()
        print(f'Clusterhead: {cluster.clusterhead.node_id}')
        self.assertTrue(cluster.clusterhead.node_id in [1, 4])

    def test_routing(self):
        """Test that a route is found between nodes when one exists."""
        # Create a scenario where nodes can be routed
        node0 = Node(0, 0, 0, 5, 50, 50)
        node1 = Node(1, 3, 4, 5, 50, 50)
        node2 = Node(2, 6, 8, 5, 50, 50)
        self.wsn.nodes = [node0, node1, node2]
        self.wsn.assign_clusters()
        self.wsn.build_kd_tree()
        self.wsn.elect_clusterheads()
        route = self.wsn.find_route(0, 2)
        self.assertEqual(route, [0, 1, 2])

    def test_invalid_routing(self):
        """Test that no route is found when nodes are out of range."""
        node0 = Node(0, 0, 0, 2, 50, 50)  # Range too small to connect
        node1 = Node(1, 10, 10, 2, 50, 50)
        self.wsn.nodes = [node0, node1]
        self.wsn.assign_clusters()
        self.wsn.build_kd_tree()
        self.wsn.elect_clusterheads()
        route = self.wsn.find_route(0, 1)
        self.assertEqual(route, [])


if __name__ == "__main__":
    unittest.main()
