# Wireless Sensor Network (WSN) Simulation

### Author: Aaron Fortner  
### Date: 09/01/2024  
### Version: 0.3

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

This project is a simulation of a **Wireless Sensor Network (WSN)** where nodes are placed in a 20m x 20m area, divided into clusters. The nodes communicate using a **greedy routing strategy**, where each node forwards packets to the node closest to the destination within its transmission range.

The simulation can run in two modes:
1. **Random Mode**: Randomly generates nodes with randomized characteristics.
2. **User Mode**: Reads node characteristics from an input file.

The program supports efficient routing using **KD Trees** for spatial searching to optimize nearest-neighbor searches.

## Features

- **Node Simulation**: Nodes have attributes like position, transmission range, energy level, processing power, and are assigned to clusters.
- **Cluster Head Election**: Each cluster elects a cluster head based on a fitness formula.
- **Greedy Routing**: A packet is forwarded to the node nearest to the destination, within the current node’s transmission range.
- **Efficient Nearest Neighbor Search**: Uses **KD Trees** to quickly find the nearest node within range.
- **Visualization**: The simulation includes a graphical visualization of the network, displaying node positions, transmission ranges, and packet routes.

## Requirements

- Python 3.x
- `numpy` (for numerical computations)
- `scipy` (for KD Tree implementation)
- `matplotlib` (for plotting/visualization)

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/wsn-simulation.git
   cd wsn-simulation
   ```

2. **Install Required Dependencies:**
   You can install the necessary libraries using pip:
   ```bash
   pip install numpy scipy matplotlib
   ```

3. **Run the Program:**
   After installation, you can run the simulation with:
   ```bash
   python main.py
   ```

## Usage

### Running the Simulation

1. Upon running the program, you'll be prompted to choose a mode:
   - **User Mode**: Provide an `input.txt` file containing node information (see format below).
   - **Random Mode**: Randomly generate nodes and clusters.

2. **Routing Packets:**
   After generating the network, you can input a source and destination node to simulate the packet route between them. The program will display the route on the screen and plot the nodes and their transmission ranges.

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

After running the simulation, the following details will be printed to the console and saved in `network.txt`:

- Number of nodes
- Node positions and attributes
- Cluster assignments and elected cluster heads
- Routes taken by packets

### Visualization
The program will generate a plot showing the nodes, their transmission ranges, and the clusters they belong to. When routing packets, the plot will display the route by connecting nodes with lines.

## Code Structure

- `main.py`: Main script that runs the simulation and handles node generation, routing, and plotting.
  
  **Key Components**:
  - **`Node` class**: Represents each sensor node with attributes like position, range, energy, etc.
  - **`Cluster` class**: Manages nodes within a cluster and elects a cluster head.
  - **`WSN` class**: Manages the network, node generation, clustering, routing, and KD Tree integration.
  - **`plot_nodes` function**: Handles the visualization of nodes, clusters, and routing paths.

## How It Works

1. **Node Generation**:
   In random mode, nodes are generated with random coordinates, communication range, energy, and processing power. In user mode, node information is read from a file.

2. **Cluster Assignment**:
   The network space is divided into 16 clusters, and each node is assigned to a cluster based on its coordinates. A cluster head is elected based on node fitness.

3. **Greedy Routing**:
   The program routes packets using a **greedy strategy**, where a node forwards packets to the node nearest to the destination within its communication range. KD Trees are used to efficiently find nearby nodes.

4. **Visualization**:
   The nodes and clusters are visualized using `matplotlib`, showing the transmission ranges and packet routes.

## Testing

Unit tests can be added to verify the correct behavior of the key components. For example, you can test:
- Node distance calculation.
- Cluster head election.
- Routing functionality (whether the correct nodes are selected in the route).

To run unit tests, use the `unittest` module. Example:

```bash
python -m unittest test_main.py
```

Ensure your `test_main.py` contains test cases for important functions like node distance, routing, etc.

## License

This project is open-source and available under the MIT License. See the LICENSE file for details.
