"""
    File: main.py
    Author: Aaron Fortner
    Date: 09/1/2024
    Version: 0.3

    Description: This file contains the main code for the Wireless Sensor Network (WSN) simulation.

    See the main README.md file for detailed information, installation instructions, and usage.
"""

import random
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import KDTree

# Number of significant digits to round to
SIGNIFICANT_DIGITS = 2
# Dimensional length of cluster
CLUSTER_SIZE = 5
# Number of clusters in the network
NUM_CLUSTERS = 16


class Node:
    """
    Class to represent a node in a Wireless Sensor Network (WSN).

    Each node has a unique identifier, coordinates, communication range, energy level, processing power, and
    fitness to be the cluster head value (f).

    The fitness value (f) is calculated as follows:     f = 0.4 * r + 0.4 * e + 0.2 * p
    where r is the communication range, e is the energy level, and p is the processing power.

    The node can also be assigned to a cluster and used to calculate the distance to another node.
    """

    def __init__(self, node_id, x, y, r, e, p):
        """
        Initialize a Node instance.

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
        self.node_id = node_id
        self.position = np.array([x, y])
        self.r = r
        self.e = e
        self.p = p
        self.cluster = None
        self.f = 0.4 * r + 0.4 * e + 0.2 * p

    def distance_to(self, other_node) -> np.floating:
        """
        Calculate the Euclidean distance to another node using numpy's linalg norm function.

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
        Elect the cluster head based on the highest f value and proximity to the cluster center.

        :return: The elected cluster head node
        """
        # Cluster head is selected based on the highest f value with proximity to the cluster center used as a
        # tiebreaker. If cluster has no nodes, the cluster head is set to None, single occupants of clusters are
        # considered cluster heads.
        if not self.nodes:
            return None

        self.clusterhead = max(self.nodes, key=lambda node: (node.f, -node.distance_to(self.center())))

        return self.clusterhead

    def center(self) -> Node:
        """
        Calculate the center of the cluster based on its ID.

        :return: A Node instance representing the center of the cluster
        """
        # Calculate the baseline for the cluster based on the cluster ID: the cluster ID is used to determine the row by
        # dividing by 4 and the column by taking the modulo of 4. The center position is then calculated based on the
        # row and column.
        row = self.cluster_id // 4
        col = self.cluster_id % 4
        center_position = np.array(
            [(col * CLUSTER_SIZE) + CLUSTER_SIZE / 2, (row * CLUSTER_SIZE) + CLUSTER_SIZE / 2]
            )
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
        self.kd_tree = None  # Add an attribute for the KD Tree
        self.clusters = [Cluster(i) for i in range(NUM_CLUSTERS)]
        self.generate_nodes()
        self.assign_clusters()
        self.build_kd_tree()  # Build KD Tree after node generation and assignment
        self.elect_clusterheads()

    def generate_nodes(self) -> None:
        """
        Generate nodes for the WSN based on the mode of operation.
        """
        if self.mode == 'random':
            # Pick random number of nodes between 10 and 100
            num_nodes = random.randint(10, 100)
            # Generate random nodes with coordinates, communication range, energy level, and processing power.
            # Round the values to desired number of decimal places.
            for i in range(num_nodes):
                x = round(random.uniform(0, 20), SIGNIFICANT_DIGITS)
                y = round(random.uniform(0, 20), SIGNIFICANT_DIGITS)
                r = round(random.uniform(1, 8), SIGNIFICANT_DIGITS)
                e = round(random.uniform(1, 100), SIGNIFICANT_DIGITS)
                p = round(random.uniform(1, 100), SIGNIFICANT_DIGITS)
                self.nodes.append(Node(i + 1, x, y, r, e, p))
        elif self.mode == 'user':
            # Read nodes from the input file in user mode, significant digits not specified in job sheet so no rounding
            # here.
            with open(self.input_file, 'r') as file:
                num_nodes = int(file.readline().strip())
                for i in range(num_nodes):
                    x, y, r, e, p = map(float, file.readline().strip().split())
                    self.nodes.append(Node(i + 1, x, y, r, e, p))

    def assign_clusters(self) -> None:
        """
        Assign nodes to clusters based on their coordinates.
        """
        # Iterate through all nodes and assign them to the appropriate cluster based on their coordinates.
        for node in self.nodes:
            cluster_id = self.get_cluster_id(node.position[0], node.position[1])
            self.clusters[cluster_id].add_node(node)

    def get_cluster_id(self, x: float, y: float) -> int:
        """
        Get the cluster ID based on the coordinates of a node.

        :param x: X-coordinate of the node
        :param y: Y-coordinate of the node
        :return cluster_id: Cluster ID based on the coordinates
        """
        # Calculate the row and column of the cluster based on the node's coordinates
        col = int(x // CLUSTER_SIZE)
        # If the node is on the border of a cluster, randomly assign it to one of the two adjacent clusters.
        # If the node is at edge of the network, keep the column the same.
        # Column classifier
        if x % CLUSTER_SIZE == 0 and x != 0 and x != 20:
            if random.choice([True, False]):
                col += 1
            else:
                col -= 1
        # Row classifier
        row = int(y // CLUSTER_SIZE)
        # If the node is on the border of a cluster, randomly assign it to one of the two adjacent clusters.
        # If the node is at edge of the network, keep the row the same.
        if y % CLUSTER_SIZE == 0 and y != 0 and y != 20:
            if random.choice([True, False]):
                row += 1
            else:
                row -= 1
        # Return the cluster ID based on the row and column of the cluster.
        # The clusters are numbered from left to right and top to bottom starting from 0,
        # so the cluster ID is calculated as row * 4 + col, where 4 is the number of columns per row:
        # if in row 0, col 0, cluster ID is 0, if in row 3, col 1, cluster ID is 13, etc.
        return row * 4 + col

    def elect_clusterheads(self) -> None:
        """
        Elect cluster heads for all clusters.
        """
        # Iterate through all clusters and elect the cluster head for each cluster.
        for cluster in self.clusters:
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
        Find a route from the source node to the destination node using a KD Tree for nearest-neighbor search.
        """
        # Get the source and destination nodes, and check if they are valid
        src_node = self.get_node_by_id(src_id)
        dest_node = self.get_node_by_id(dest_id)
        if not src_node or not dest_node:
            print("Invalid source or destination node.")
            return []

        # Init route as a list with the source node as the starting point
        route = [src_node]

        # Set starting node as the current node and iterate until the destination node is reached
        current_node = src_node
        while current_node != dest_node:
            # Use KD Tree to find the nearest node within the communication range
            nearest_node = self.get_nearest_node_kdtree(current_node, dest_node)
            if not nearest_node:
                print("No route found.")
                return []
            # If suitable node found, add it to the route and set it as the current node
            route.append(nearest_node)
            current_node = nearest_node

        return [node.node_id for node in route]

    # TODO: remove?
    def get_nearest_node(self, current_node: Node, dest_node: Node) -> Node | None:
        """
        Get the nearest node to the destination node within the communication range.

        :param current_node: Current node
        :param dest_node: Destination node
        :return: Nearest node to the destination node
        """
        # Get all nodes within the communication range of the current node
        candidates = [node for node in self.nodes if node != current_node and current_node.distance_to(node)
                      <= current_node.r]
        # If no candidates found, no route exists, return None
        if not candidates:
            return None
        # Otherwise, return the candidate node closest to the destination node
        return min(candidates, key=lambda node: node.distance_to(dest_node))

    def get_nearest_node_kdtree(self, current_node: Node, dest_node: Node) -> Node | None:
        """
        Use KD Tree to find the node nearest to the destination within the current node's communication range.

        :param current_node: Current node
        :param dest_node: Destination node
        :return: Nearest node to the destination node
        """
        if not self.kd_tree:
            return None

        # Query the KD Tree for the k nearest neighbors to the current node (can be large enough like k=10 or more)
        distances, indices = self.kd_tree.query(current_node.position, k=10)

        # Initialize variables to track the best candidate node
        best_candidate = None
        min_dist_to_dest = float('inf')

        # Iterate over the nearest neighbors
        for dist, idx in zip(distances, indices):
            candidate_node = self.nodes[idx]

            # Check if the candidate node is within the communication range of the current node
            if dist <= current_node.r:
                # Check if this candidate node is closer to the destination than the current best candidate
                dist_to_dest = candidate_node.distance_to(dest_node)
                if dist_to_dest < min_dist_to_dest and candidate_node != current_node:
                    best_candidate = candidate_node
                    min_dist_to_dest = dist_to_dest

        # Return the node that is closest to the destination and within the communication range
        return best_candidate

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
            file.write(f'Number of nodes: {len(self.nodes)}\n')
            print(f'Number of nodes: {len(self.nodes)}')

            # Write details of each node
            for node in self.nodes:
                node_info = f'{node.node_id} {node.position[0]} {node.position[1]} {node.r} {node.e} {node.p}'
                file.write(f'{node_info}\n')
                print(node_info)

            # Write cluster information
            for cluster in self.clusters:
                if cluster.nodes:
                    file.write(f'\nCluster {cluster.cluster_id + 1}:\n')
                    print(f'\nCluster {cluster.cluster_id + 1}:')

                    node_ids = ", ".join(str(node.node_id) for node in cluster.nodes)
                    file.write(f'Nodes: {node_ids}\n')
                    print(f'Nodes: {node_ids}')

                    if cluster.clusterhead:
                        file.write(f'Clusterhead: {cluster.clusterhead.node_id}\n')
                        print(f'Clusterhead: {cluster.clusterhead.node_id}')


def plot_nodes(nodes, clusters, connect=False, title='WSN Nodes and Their Radio Ranges') -> None:
    """
    Plot the nodes and their radio ranges on a 2D grid.
    :param nodes: List of Node instances to be plotted
    :param clusters: List of Cluster instances
    :param connect: Boolean flag to connect the nodes with lines for routing plot
    :param title: Title of the plot
    """
    fig, ax = plt.subplots()

    # Set up the plot limits (assuming a 20x20 grid)
    ax.set_xlim(0, 20)
    ax.set_ylim(20, 0)  # Flip the y-axis

    # Plot horizontal and vertical lines at 5, 10, and 15
    for pos in [5, 10, 15]:
        ax.axhline(y=pos, color='green', linestyle='-', linewidth=1)
        ax.axvline(x=pos, color='green', linestyle='-', linewidth=1)

    # Store positions for line plotting if connect is True
    if connect:
        x_coords: list[float] = []
        y_coords: list[float] = []

    # Plot each node
    for node in nodes:
        # Plot the node as a point
        ax.plot(node.position[0], node.position[1], 'bo')  # 'bo' means blue circle marker

        # Plot the radio range as a circle
        circle = plt.Circle(node.position, node.r, color='r', fill=False, linestyle='--')
        ax.add_patch(circle)

        # Annotate the node with its ID
        ax.text(node.position[0] + 0.2, node.position[1] - 0.5, f'ID: {node.node_id}', fontsize=9)

        # Collect coordinates if connecting nodes
        if connect:
            x_coords.append(node.position[0])
            y_coords.append(node.position[1])

    # If connect is True, plot lines connecting the nodes in the order given
    if connect and len(nodes) > 1:
        ax.plot(x_coords, y_coords, 'b-', marker='o')  # 'b-' means blue line, 'o' markers at points

    # Add labels for each cluster at the center in green
    for cluster in clusters:
        center_node = cluster.center()
        ax.text(center_node.position[0], center_node.position[1],
                f'Cluster {cluster.cluster_id + 1}', color='green', fontsize=10, ha='center')

    ax.set_xlabel('X')
    ax.set_ylabel('Y', rotation=0)
    ax.set_title(title)

    plt.grid(True)
    plt.show()


def main() -> None:
    """
    Main function to run the WSN simulation.
    """
    print("Welcome to WSN Simulation!")
    # Inside infinite loop, Create a WSN instance based on the user's choice and save the network configuration
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

        # Save the network configuration to a file
        wsn.save_network()

        # Plot the nodes and their radio ranges, and include cluster labels
        plot_nodes(wsn.nodes, wsn.clusters)

        # Find a route for a packet based on the user's input if one exists
        while True:
            src_id = None
            dest_id = None

            # Validate source node ID
            while src_id is None:
                try:
                    src_id = int(input("\nEnter source node ID: "))
                    if wsn.get_node_by_id(src_id) is None:
                        print(f"Source node ID {src_id} is not valid. Please enter a valid node ID.")
                        src_id = None
                except ValueError:
                    print("Invalid input. Please enter a valid integer for the node ID.")
                    src_id = None

            # Validate destination node ID
            while dest_id is None:
                try:
                    dest_id = int(input("Enter destination node ID: "))
                    if wsn.get_node_by_id(dest_id) is None:
                        print(f"Destination node ID {dest_id} is not valid. Please enter a valid node ID.")
                        dest_id = None
                except ValueError:
                    print("Invalid input. Please enter a valid integer for the node ID.")
                    dest_id = None

            # Call the find_route method and print the route if one exists
            route = wsn.find_route(src_id, dest_id)
            # Print the route if it exists and ask the user if they want to route another packet or quit
            if route:
                print(f'Route: {" -> ".join(map(str, route))}')
                plot_nodes([wsn.get_node_by_id(node_id) for node_id in route],
                           wsn.clusters,
                           connect=True,
                           title=f'Packet Route from Node {src_id} to Node {dest_id}'
                           )

            # Validate input for y/n and default to 'y'
            while True:
                again = input("Do you want to route another packet? (y/n, default 'y'): ").strip().lower()
                if again == '' or again == 'y':
                    again = 'y'  # Default to 'y'
                    break
                elif again == 'n':
                    break
                else:
                    print("Invalid input. Please enter 'y' for yes or 'n' for no.")

            # If 'n', break the loop
            if again == 'n':
                break


if __name__ == "__main__":
    main()
