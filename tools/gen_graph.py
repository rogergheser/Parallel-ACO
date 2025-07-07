import sys
import argparse
from itertools import product
import random

def generate_graph(size, num_nodes):
    nodes = list(product(range(size), repeat=2))
    
    selected_nodes = random.sample(nodes, k=num_nodes)
    selected_nodes = sorted(
        selected_nodes, key=lambda x: (x[1], x[0])  # Sort by y, then x coordinate
    )
    assert len(set(selected_nodes)) == num_nodes, "Duplicate nodes were selected"
    return selected_nodes

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a random graph for TSP.")
    parser.add_argument('-s', '--size', type=int, default=10, help='Size of the grid (default: 10)')
    parser.add_argument('-n', '--num_nodes', type=int, default=5, help='Number of nodes to select (default: 5)')
    parser.add_argument('-o', '--output', type=str, default='custom_graph.tsp', help='Output file name (default: custom_graph.tsp)')
    args = parser.parse_args()

    graph_size = args.size
    num_nodes = args.num_nodes
    output_file = args.output
    if graph_size <= 0 or num_nodes <= 0:
        print("Size and number of nodes must be positive integers.")
        sys.exit(1)
    selected_nodes = generate_graph(graph_size, num_nodes)


    with open(output_file, 'w') as output_file:
        output_file.write(
            "NAME : custom_graph\n"
            "COMMENT : Generated graph with random nodes\n"
            "TYPE : TSP\n"
            f"DIMENSION : {len(selected_nodes)}\n"
            "EDGE_WEIGHT_TYPE : EUC_2D\n"
            "NODE_COORD_SECTION\n"
        )
        for i, node in enumerate(selected_nodes):
            output_file.write(f"{i+1}  {node[0]}  {node[1]}\n")