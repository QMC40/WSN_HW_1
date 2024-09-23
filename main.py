"""
    File: main.py
    Author: Aaron Fortner
    Date: 09/22/2024
    Version: 0.6

    Description: This file contains the main code for the Wireless Sensor Network (WSN) simulation.

    See the main README.md file for detailed information, installation instructions, and usage.
"""
import matplotlib.pyplot as plt
from wsn import WSN
from tabulate import tabulate
from logging_config.logger import get_logger
from config.constants import LOGGING, CLUSTER_INDEX, NODE_INDEX


# If logging is enabled, configure the logger
if LOGGING:
    logger = get_logger()


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
                        node.node_id + NODE_INDEX,
                        node.position[0],
                        node.position[1],
                        node.r,
                        node.e,
                        node.p
                        ]
                )

    # Define headers for node table
    node_headers = ['Node ID', 'X Position', 'Y Position', 'Range (R)', 'Energy (E)', 'Processing Power (P)']

    print("\nNode Information:")
    print(tabulate(node_data, headers=node_headers, tablefmt="grid"))

    # Display cluster information
    cluster_data = []
    for cluster in wsn.clusters:
        if cluster.nodes:
            cluster_nodes = ", ".join(str(node.node_id + NODE_INDEX) for node in cluster.nodes)
            clusterhead = cluster.clusterhead.node_id + NODE_INDEX if cluster.clusterhead else "None"
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
        ax.text(node.position[0] + 0.3, node.position[1], f'ID: {node.node_id + NODE_INDEX}', fontsize=9)

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

        if len(wsn.nodes) > 1:

            print("Packet routing simulation:")

            # Find a route for a packet based on the user's input if one exists
            while True:
                src_id = None
                dest_id = None

                # Validate source node ID, note the subtraction of the NODE_INDEX to the input to align displayed node
                # IDs with the displayed node_ids based on the 1 or 0 indexing setting.
                while src_id is None:
                    try:
                        src_id = int(input("\nEnter source node ID: "))
                        if wsn.get_node_by_id(src_id - NODE_INDEX) is None:
                            print(f"The network does not contain a node  with the ID:{src_id}. Please "
                                  f"enter a valid node ID.")
                            src_id = None
                    except ValueError:
                        print("Invalid input. Please enter a valid integer for the node ID.")
                        src_id = None

                # Validate destination node ID, note the subtraction of the NODE_INDEX to the input to align displayed
                # node IDs with the displayed node_ids based on the 1 or 0 indexing setting.
                while dest_id is None:
                    try:
                        dest_id = int(input("Enter destination node ID: "))
                        if wsn.get_node_by_id(dest_id - NODE_INDEX) is None:
                            print(f"The network does not contain a node  with the ID:{dest_id}. Please "
                                  f"enter a valid node ID.")
                            dest_id = None
                    except ValueError:
                        print("Invalid input. Please enter a valid integer for the node ID.")
                        dest_id = None

                # Call the find_route method and print the route if one exists
                route = wsn.find_route(src_id - NODE_INDEX, dest_id - NODE_INDEX)
                # Print the route if it exists and ask the user if they want to route another packet or quit
                if route:
                    print(f'Route: {" -> ".join(f"{node + NODE_INDEX}" for node in route)}')
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
        else:
            print("Network has less than two nodes in the network. No routing can be performed.")

    print("Thank you for using WSN Simulation!")
    plt.ioff()  # Disable interactive mode to close plots properly
    plt.show()  # Keep plots open until the user closes them


if __name__ == "__main__":
    main()
