"""
    File: main.py
    Author: Aaron Fortner
    Date: 09/8/2024
    Version: 0.4

    Description: This file contains the main code for the Wireless Sensor Network (WSN) simulation.

    See the main README.md file for detailed information, installation instructions, and usage.
"""
import logging
import random
from multiprocessing.util import debug

import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import KDTree
from tabulate import tabulate

# TODO: move display functions to HTML/JS?

# Max limits of coordinates
MAX_COORD = 20
# Dimensional length of cluster sides
CLUSTER_SIZE = 5
# Number of clusters in the network
NUM_CLUSTERS = 16
# Clusters index at 0 or 1? Set to match zero element index
CLUSTER_INDEX = 0

# # Configure logging
# logger = logging.getLogger('WSN')
# logging.basicConfig(
#         level=logging.DEBUG,  # Set the logging level to DEBUG to capture all log messages
#         format='%(asctime)s - %(levelname)s - %(message)s'
#         )  # Customize the format


class Node:
    """
    Class to represent a node in a Wireless Sensor Network (WSN).

    Each node has a unique identifier, coordinates, communication range, energy level, processing power, and
    fitness to be the cluster head value (f).

    The fitness value (f) is calculated as follows:     f = 0.4 * r + 0.4 * e + 0.2 * p
    where r is the communication range, e is the energy level, and p is the processing power.

    The node can also be assigned to a cluster and used to calculate the distance to another node.
    """

    def __init__(self, node_id: int, x: int, y: int, r: int, e: int, p: int):
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
        self.node_id: int = node_id
        self.position: np.array(int) = np.array([x, y])
        self.r: int = r
        self.e: int = e
        self.p: int = p
        self.cluster: int | None = None
        self.f = 0.4 * r + 0.4 * e + 0.2 * p

    def distance_to(self, other_node: 'Node') -> np.floating:
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
        node.cluster = self.cluster_id

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
        # The center position is calculated as follows: Column is determined by cluster ID modulo 4, and row is the
        # cluster ID divided by 4. The center position is the column number times the cluster size plus half the
        # cluster size for the x-coordinate, and the row number times the cluster size plus half the cluster size for
        # the y-coordinate.
        col = self.cluster_id % 4
        row = self.cluster_id // 4
        center_position = np.array(
                [(col * CLUSTER_SIZE) + CLUSTER_SIZE / 2, (row * CLUSTER_SIZE) + CLUSTER_SIZE / 2]
                )
        return Node(-1, center_position[0], center_position[1], 0, 0, 0)


class WSN:
    """
    Class to represent a Wireless Sensor Network (WSN).
    """

    # TODO: something is wrong in cluster assignment
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

        # Generate nodes and build the KD tree
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
            for i in range(num_nodes):
                x = random.randint(0, 20)
                y = random.randint(0, 20)
                r = random.randint(1, 8)
                e = random.randint(1, 100)
                p = random.randint(1, 100)
                self.nodes.append(Node(i + 1, x, y, r, e, p))
        elif self.mode == 'user':
            # Read nodes from the input file in user mode
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
            cluster_id = get_cluster_id(node.position[0], node.position[1])
            self.clusters[cluster_id].add_node(node)

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

    # TODO: check routing in same cluster, doesn't seem to work
    def find_route(self, src_id: int, dest_id: int) -> list[int]:
        """
        Find a route from the source node to the destination node.

        :param src_id: Source node ID.
        :param dest_id: Destination node ID.
        :return: List of node IDs representing the route, or an empty list if no route is found.
        """
        src_node = self.get_node_by_id(src_id)
        dest_node = self.get_node_by_id(dest_id)

        if not src_node or not dest_node:
            print("Invalid source or destination node.")
            return []

        # Start the route with the source node
        route = [src_node]
        current_node = src_node
        last_node = None
        visited = set()  # Track visited nodes to avoid loops

        while current_node != dest_node:
            visited.add(current_node.node_id)

            # Get the nearest node to the destination within the current node's transmission range
            next_node = self.get_nearest_node_kdtree(current_node, dest_node, last_node)

            if not next_node:
                # if not next_node or next_node.node_id in visited:
                print("No valid route found.")
                return []  # Return an empty route if no valid next node is found or if stuck in a loop

            # Add the next node to the route and continue routing from that node
            route.append(next_node)
            last_node = current_node
            current_node = next_node

        # Return the final route as a list of node IDs
        return [node.node_id for node in route]

    def get_nearest_node_kdtree(self, current_node: Node, dest_node: Node, last_node: Node) -> Node | None:
        """
        Use KD Tree to find all nodes within the current node's communication range (radius search).
        From those nodes, find the one closest to the destination.

        :param current_node: The node currently sending the packet.
        :param dest_node: The final destination node for the packet.
        :param last_node: The last node visited in the route.
        :return: The node within range closest to the destination, or None if no node is found.
        """
        if not self.kd_tree:
            return None

        # Radius search: Find all nodes within the current node's transmission range
        radius = current_node.r
        neighbors_within_range = self.kd_tree.query_ball_point(current_node.position, r=radius)

        # Initialize variables to track the best candidate node
        best_candidate = None
        min_dist_to_dest = float('inf')

        # Iterate over all neighboring nodes within the radius
        for idx in neighbors_within_range:
            candidate_node = self.nodes[idx]

            # Ignore the current node itself and the last node visited
            if candidate_node == current_node:
                # if candidate_node == current_node or candidate_node == last_node:
                continue

            # Check the distance from the candidate node to the destination
            dist_to_dest = candidate_node.distance_to(dest_node)

            # If this candidate is closer to the destination, select it
            if dist_to_dest < min_dist_to_dest:
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
            file.write(f'{len(self.nodes)}\n')
            print(f'\nNumber of nodes: {len(self.nodes)}')

            # Write details of each node
            for node in self.nodes:
                node_info = f'{node.position[0]}\t{node.position[1]}\t{node.r}\t{node.e}\t{node.p}'
                file.write(f'{node_info}\n')
                # print(node_info)

            # Write cluster information
            for cluster in self.clusters:
                if cluster.nodes:
                    file.write(f'\nCluster {cluster.cluster_id + CLUSTER_INDEX}:\n')
                    # print(f'\nCluster {cluster.cluster_id + CLUSTER_INDEX}:')

                    node_ids = ", ".join(str(node.node_id) for node in cluster.nodes)
                    file.write(f'Nodes: {node_ids}\n')
                    # print(f'Nodes: {node_ids}')

                    if cluster.clusterhead:
                        file.write(f'Clusterhead: {cluster.clusterhead.node_id}\n')
                        # print(f'Clusterhead: {cluster.clusterhead.node_id}')


def rank_and_file_calculator(value: float):
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


def get_cluster_id(x: float, y: float) -> int:
    """
    Get the cluster ID based on the coordinates of a node.

    :param x: X-coordinate of the node
    :param y: Y-coordinate of the node
    :return cluster_id: Cluster ID based on the coordinates
    """
    # Call rank and file calc to determine the row and col containing the node
    col = rank_and_file_calculator(x)
    row = rank_and_file_calculator(y)

    # Return the cluster ID based on the row and column of the cluster.
    # The clusters are numbered from left to right and top to bottom starting from 0 or 1 depending on indexing,
    # so the cluster ID is calculated as row * 4 + col + CLUSTER_INDEX, where 4 is the number of columns per row:
    # so if the node is in row 0, col 0, and indexed at 0 the cluster ID is 0 (0 * 4 + 0 + 0), if its in row 3,
    # col 1, and indexed at 1 the cluster ID is 14 (3 * 4 + 1 + 1).
    cluster = row * 4 + col
    # logger.debug(f"node @ {x},{y} : {col},{row} assigned to cluster {cluster}")
    return cluster


def display_network_info(wsn):
    """
    Display the nodes and cluster information in a table format using the tabulate library.
    :param wsn: The WSN object containing network details.
    """

    # Display node information
    node_data = []
    for node in wsn.nodes:
        node_data.append(
                [
                        node.node_id,
                        node.position[0],
                        node.position[1],
                        node.r,
                        node.e,
                        node.p,
                        node.f
                        ]
                )

    # Define headers for node table
    node_headers = ['Node ID', 'X Position', 'Y Position', 'Range (R)', 'Energy (E)', 'Processing Power (P)',
                    'Fitness (F)']

    print("\nNode Information:")
    print(tabulate(node_data, headers=node_headers, tablefmt="grid"))

    # Display cluster information
    cluster_data = []
    for cluster in wsn.clusters:
        if cluster.nodes:
            cluster_nodes = ", ".join(str(node.node_id) for node in cluster.nodes)
            clusterhead = cluster.clusterhead.node_id if cluster.clusterhead else "None"
            cluster_data.append(
                    [
                            cluster.cluster_id + CLUSTER_INDEX,
                            cluster_nodes,
                            clusterhead
                            ]
                    )

    # Define headers for cluster table
    cluster_headers = ['Cluster ID', 'Nodes in Cluster', 'Clusterhead']

    print("\nCluster Information:")
    print(tabulate(cluster_data, headers=cluster_headers, tablefmt="grid"))


def plot_nodes(nodes, clusters, connect=False, title='WSN Nodes and Their Radio Ranges') -> None:
    """
    Plot the nodes and their radio ranges on a 2D grid.
    :param nodes: List of Node instances to be plotted
    :param clusters: List of Cluster instances
    :param connect: Boolean flag to connect the nodes with lines for routing plot
    :param title: Title of the plot
    """
    # plt.ion()  # Enable interactive mode for non-blocking plots

    fig, ax = plt.subplots()

    # Set up the plot limits (assuming a 20x20 grid)
    ax.set_xlim(0, 20)
    ax.set_ylim(20, 0)  # Flip the y-axis

    # Plot horizontal and vertical lines at 5, 10, and 15
    for pos in [5, 10, 15]:
        ax.axhline(y=pos, color='green', linestyle='-', linewidth=1)
        ax.axvline(x=pos, color='green', linestyle='-', linewidth=1)

    # Store positions for line plotting if connect is True
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
        ax.text(
                center_node.position[0], center_node.position[1],
                f'Cluster {cluster.cluster_id + CLUSTER_INDEX}', color='green', fontsize=10, ha='center'
                )

    ax.set_xlabel('X')
    ax.set_ylabel('Y', rotation=0)
    ax.set_title(title)

    plt.grid(True)
    plt.draw()  # Draw the plot but don't block
    plt.pause(0.001)  # Pause briefly to ensure the plot is updated but non-blocking


def main() -> None:
    """
    Main function to run the WSN simulation.
    """
    print("Welcome to WSN Simulation!")

    # Ask the user if they want to plot the nodes and their radio ranges
    plot = input("Do you want to plot the nodes and their radio ranges? (y/n, default 'n'): ").strip().lower() == 'y'

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

        # Display network information in table format
        display_network_info(wsn)

        if plot:
            # Plot the nodes and their radio ranges, and include cluster labels
            plot_nodes(wsn.nodes, wsn.clusters)

        print("Packet routing simulation:")

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
                if plot:
                    # Plot the nodes and their radio ranges with the route connected
                    plot_nodes(
                            [wsn.get_node_by_id(node_id) for node_id in route],
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
