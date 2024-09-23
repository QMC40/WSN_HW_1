# Wireless Sensor Network (WSN) Simulation

**Author**: QMC40   
**Date**: 09/15/2024  
**Version**: 0.5

## Table of Contents
- [Project Description](#project-description)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Code Structure](#code-structure)
- [How It Works](#how-it-works)

## Project Description

This project is a simulation of a Wireless Sensor Network (WSN) that operates in a 20m x 20m area divided into clusters. Nodes within the network communicate using a **greedy routing** strategy, forwarding packets to the node closest to the destination within its transmission range.

The simulation includes two modes:
- **Random Mode**: Randomly generates nodes and their characteristics.
- **User Mode**: Reads node characteristics from an input file.

The simulation efficiently searches for nodes using a **KD Tree**, enabling nearest-neighbor searches, and features graphical visualization of the network.

## Features

- **Node Simulation**: Nodes have attributes such as position, transmission range, energy level, and processing power. They are assigned to clusters based on their coordinates.
- **Cluster Head Election**: A cluster head is elected for each cluster using a fitness formula:
  \[
  F = 0.4R + 0.4E + 0.2P
  \]
  where R is communication range, E is energy level, and P is processing power.
- **Greedy Routing**: The simulation implements greedy intuitive routing, forwarding packets to the nearest node (within range) to the destination without regard to the destination node being within that nodes range and allows for no fallback or backtracking of the route to other nodes to achieve connectivity.
- **Efficient Nearest Neighbor Search**: The implementation uses a **KD Tree** to optimize nearest-neighbor searches for routing.
- **Visualization**: The simulation visualizes node placement, transmission ranges, clusters, and packet routes using `matplotlib`.
- **Logging**: The program uses a configurable logging system to provide insights into the routing process and node generation.

## Requirements

- **Python 3.x**
- `numpy` (for numerical computations)
- `scipy` (for KD Tree implementation)
- `matplotlib` (for plotting/visualization)
- `tabulate` (for formatting tabular data)

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/QMC40/wsn-simulation.git
   cd wsn-simulation
   ```

2. **Install Required Dependencies**:
   ```bash
   pip install numpy scipy matplotlib tabulate
   ```

3. **Run the Program**:
   ```bash
   python main.py
   ```

## Usage

### Running the Simulation
**NOTE:** At the top of the main.py file there are a set of constants that may be changed before execution to modify the behavior of the simulation:

- LOGGING - turns logging during run on/off
- MAX_COORD - sets the maximal value for the sides of the cluster squares
- NUM_CLUSTERS - sets the number of clusters in the network
- CLUSTER_INDEX - sets the indexing of the clusters at zero or one
- NODE_INDEX - sets the indexing of the nodes at zero or one

When you run the program, you'll be first be asked if you want the plotting function to plot out the network of sensors and their associated ranges as well as plotting any successful packet routes as requested during the packet routing simulation. 
 
You'll then be prompted to choose a mode:
- **User Mode**: Provide an `input.txt` file containing node information (see format below).
- **Random Mode**: Randomly generates nodes and clusters.

After generating the network it will be output to the `network.txt` file in the style described below as well as displayed on the screen in table format.

### Packet Routing
After generating the network, input a source and destination node to simulate the packet route. The program will display the route and optionally plot the nodes, their transmission ranges, and the routing path.

### Input File Format (for User Mode)
The `input.txt` file should contain node details in the following format:
```
Number of nodes
x1 y1 R1 E1 P1
x2 y2 R2 E2 P2
...
```

Example:
```
3
3 1 4 40 30
2 7 5 99 55
13 14 4 45 80
```

### Network Output
The following details will be printed to the console and saved in `network.txt` following a similar format to the input file format above:
- Number of nodes
- Node positions and attributes
- Cluster assignments and elected cluster heads

Example:
```
3
3 1 4 40 30
2 7 5 99 55
13 14 4 45 80

Cluster 0:
Nodes: 3
Clusterhead: 3

Cluster 1:
Nodes: 1
Clusterhead: 2

Cluster 2:
Nodes: 1
Clusterhead: 13
```
### Packet Routing Output
During the packet routing simulation the program will either return `No valid route found.` if there is no viable way to route a packet from the entered source to the desired destination node, or a route listed as a series of hops from node to node:

Example:
```
Packet routing simulation:

Enter source node ID: 8
Enter destination node ID: 97
Route: 8 -> 56 -> 46 -> 55 -> 41 -> 66 -> 97
```

### Visualization
If requested at the beginning of the run, the simulation will generate a plot displaying the nodes, their transmission ranges, and clusters. During packet routing, the route will be visualized by connecting the nodes along the path with only the nodes used in the route displayed.

## Code Structure

- **main.py**: The main script that runs the simulation and handles node generation, clustering, routing, and visualization.

**Key Components**:
- **Node class**: Represents each sensor node with attributes like position, range, energy, and processing power. Also includes methods for calculating distances between nodes.
- **Cluster class**: Manages nodes within a cluster and elects a cluster head based on a fitness formula.
- **WSN class**: Manages the entire network, generates nodes, assigns them to clusters, builds the KD Tree, and performs routing using greedy strategy.
- **plot_nodes function**: Handles visualization of the network, including node positions, clusters, and packet routes.
- **Logging**: A configurable logging system provides detailed information on node generation, clusterhead election, and routing.

## How It Works

- **Node Generation**: In random mode, nodes are generated with random coordinates, communication range, energy, and processing power. In user mode, node information is read from an input file. The system ensures no two nodes have identical coordinates.
- **Cluster Assignment**: The network space is divided into the number of clusters set in the constant NUM_CLUSTERS, and nodes are assigned based on their coordinates. Cluster heads are elected using the fitness formula.
- **Greedy Routing**: The program routes packets using greedy routing, where a node forwards a packet to the nearest node within communication range. Using a KD Tree optimize nearest-neighbor searches to improve efficiency.
- **Visualization**: Nodes, clusters, and packet routes are visualized using `matplotlib`.
