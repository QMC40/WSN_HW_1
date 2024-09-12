Here's an updated version of your README that reflects the current state of your code base:

---

# Wireless Sensor Network (WSN) Simulation

**Author**: Aaron Fortner  
**Date**: 09/08/2024  
**Version**: 0.4

## Table of Contents
- [Project Description](#project-description)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Code Structure](#code-structure)
- [How It Works](#how-it-works)
- [Testing](#testing)
- [License](#license)

## Project Description

This project is a simulation of a Wireless Sensor Network (WSN) that operates in a 20m x 20m area divided into clusters. Nodes within the network communicate using a **greedy routing** strategy, forwarding packets to the node closest to the destination within its transmission range.

The simulation includes two modes:
- **Random Mode**: Randomly generates nodes and their characteristics.
- **User Mode**: Reads node characteristics from an input file.

The simulation efficiently searches for nodes using **KD Trees**, enabling nearest-neighbor searches, and features graphical visualization of the network.

## Features

- **Node Simulation**: Nodes have attributes such as position, transmission range, energy level, and processing power. They are assigned to clusters based on their coordinates.
- **Cluster Head Election**: A cluster head is elected for each cluster using a fitness formula:
  \[
  F = 0.4R + 0.4E + 0.2P
  \]
  where R is communication range, E is energy level, and P is processing power.
- **Greedy Routing**: The simulation implements greedy routing, forwarding packets to the nearest node (within range) to the destination.
- **Efficient Nearest Neighbor Search**: The implementation uses **KD Trees** to optimize nearest-neighbor searches for routing.
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
   git clone https://github.com/yourusername/wsn-simulation.git
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
When you run the program, you'll be prompted to choose a mode:
- **User Mode**: Provide an `input.txt` file containing node information (see format below).
- **Random Mode**: Randomly generates nodes and clusters.

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

### Sample Output
The following details will be printed to the console and saved in `network.txt`:
- Number of nodes
- Node positions and attributes
- Cluster assignments and elected cluster heads
- Routes taken by packets

### Visualization
The simulation will generate a plot displaying the nodes, their transmission ranges, and clusters. During packet routing, the route will be visualized by connecting the nodes along the path.

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
- **Cluster Assignment**: The network space is divided into 16 clusters, and nodes are assigned based on their coordinates. Cluster heads are elected using the fitness formula.
- **Greedy Routing**: The program routes packets using greedy routing, where a node forwards a packet to the nearest node within communication range. KD Trees optimize nearest-neighbor searches.
- **Visualization**: Nodes, clusters, and packet routes are visualized using `matplotlib`.

## Testing

You can add unit tests to verify the correctness of key functions, such as:
- Node distance calculation.
- Cluster head election.
- Routing functionality.

To run unit tests:
```bash
python -m unittest test_main.py
```

## License

This project is open-source and available under the MIT License. See the LICENSE file for details.

---

This README is designed to reflect your current code base, including logging, the use of KD Trees, and node visualization. Feel free to adjust as your project evolves!