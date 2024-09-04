import unittest
import numpy as np
from main import Node, Cluster, WSN  # Import your classes from the main code


class TestWSN(unittest.TestCase):

    def test_node_distance(self):
        """Test the Euclidean distance between two nodes."""
        node1 = Node(1, 0, 0, 5, 50, 50)
        node2 = Node(2, 3, 4, 5, 50, 50)  # Distance should be 5 (3-4-5 triangle)
        distance = node1.distance_to(node2)
        self.assertEqual(distance, 5)

    def test_cluster_head_election(self):
        """Test that the correct node is elected as the cluster head."""
        cluster = Cluster(1)
        node1 = Node(1, 5, 5, 4, 70, 40)  # F = 0.4 * 4 + 0.4 * 70 + 0.2 * 40 = 33.6
        node2 = Node(2, 6, 6, 3, 80, 50)  # F = 0.4 * 3 + 0.4 * 80 + 0.2 * 50 = 38.2
        node3 = Node(3, 7, 7, 2, 60, 20)  # F = 0.4 * 2 + 0.4 * 60 + 0.2 * 20 = 26.8
        cluster.add_node(node1)
        cluster.add_node(node2)
        cluster.add_node(node3)
        cluster.elect_clusterhead()
        self.assertEqual(cluster.clusterhead.node_id, 2)

    def test_node_generation(self):
        """Test that nodes are generated in random mode."""
        wsn = WSN(mode='random')
        self.assertGreaterEqual(len(wsn.nodes), 10)
        self.assertLessEqual(len(wsn.nodes), 100)
        for node in wsn.nodes:
            self.assertGreaterEqual(node.position[0], 0)
            self.assertLessEqual(node.position[0], 20)
            self.assertGreaterEqual(node.position[1], 0)
            self.assertLessEqual(node.position[1], 20)

    def test_cluster_assignment(self):
        """Test that nodes are correctly assigned to clusters based on their coordinates."""
        wsn = WSN(mode='random')
        wsn.assign_clusters()
        for node in wsn.nodes:
            cluster_id = wsn.get_cluster_id(node.position[0], node.position[1])
            self.assertIn(node, wsn.clusters[cluster_id].nodes)

    def test_routing(self):
        """Test that a route is found between nodes when one exists."""
        wsn = WSN(mode='random')
        # Create a scenario where nodes can be routed
        node1 = Node(1, 0, 0, 5, 50, 50)
        node2 = Node(2, 3, 4, 5, 50, 50)
        node3 = Node(3, 6, 8, 5, 50, 50)
        wsn.nodes = [node1, node2, node3]
        wsn.assign_clusters()
        route = wsn.find_route(1, 3)
        self.assertEqual(route, [1, 2, 3])

    def test_invalid_routing(self):
        """Test that no route is found when nodes are out of range."""
        wsn = WSN(mode='random')
        node1 = Node(1, 0, 0, 2, 50, 50)  # Range too small to connect
        node2 = Node(2, 10, 10, 2, 50, 50)
        wsn.nodes = [node1, node2]
        wsn.assign_clusters()
        route = wsn.find_route(1, 2)
        self.assertEqual(route, [])

    def setUp(self):
        """Create a basic WSN for testing."""
        self.wsn = WSN(mode='random')
        # Create nodes manually for predictable behavior
        node1 = Node(1, 0, 0, 5, 50, 50)  # (x, y, range, energy, processing power)
        node2 = Node(2, 3, 4, 5, 50, 50)  # Within range of node1
        node3 = Node(3, 6, 8, 5, 50, 50)  # Within range of node2
        self.wsn.nodes = [node1, node2, node3]
        self.wsn.build_kd_tree()

    def test_valid_route(self):
        """Test that a valid route is found."""
        route = self.wsn.find_route(1, 3)
        self.assertEqual(route, [1, 2, 3])

    def test_no_route(self):
        """Test that no route is found if nodes are out of range."""
        node1 = Node(1, 0, 0, 2, 50, 50)  # Small range, can't reach node2
        node2 = Node(2, 10, 10, 2, 50, 50)
        self.wsn.nodes = [node1, node2]
        self.wsn.build_kd_tree()
        route = self.wsn.find_route(1, 2)
        self.assertEqual(route, [])


if __name__ == "__main__":
    unittest.main()
