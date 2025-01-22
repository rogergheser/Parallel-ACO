from matplotlib import pyplot as plt, animation
import networkx as nx
import random
import logging
import numpy as np

logger = logging.getLogger(__name__)


MIN_ALPHA = 0.2
MAX_ALPHA = 0.8
MIN_WEIGHT = .5
MAX_WEIGHT = 2.0
NODE_OPTIONS = {
    'node_color': 'red',
    'node_size': 100,
    'alpha' : 1,
}

EDGE_OPTIONS = {
    'edge_color': 'gray',
    'style': 'dashed',
}

def graph_from_info(graph_info:dict)->nx.Graph:
    nodes = graph_info['nodes']
    G = nx.Graph()
    
    # Add nodes
    G.add_nodes_from(nodes.keys())
    for node, coords in nodes.items():
        G.add_node(node, pos=coords, color="red")

    # Add edges
    for i, (x0, y0) in nodes.items():
        for j, (x1, y1) in nodes.items():
            if i != j:
                dist = ((x1 - x0)**2 + (y1 - y0)**2)**0.5
                G.add_edge(i, j, 
                           weight=dist,
                           pheromones=0.1)

    return G

def read_coords(lines, start):
    logger.info("Reading node coordinates")
    nodes = {}
    for line in lines[start:]:
        try:
            node, x, y = [val for val in line.split(' ') if val]
            nodes[int(node)] = (float(x), float(y))
            logger.info(node, x, y)
        except ValueError:
            if line == 'EOF':
                logger.info("Finished reading node coordinates")
                break
    return nodes


def read_tsp_file(path, type):
    with open(path, "r") as f:
        lines = f.readlines()
        lines = [line.strip() for line in lines]
        lines = [line for line in lines if line]
    
    graph_info = {}
    for i, line in enumerate(lines):
        try:
            key, val = line.split(': ')
            graph_info[key.lower()] = val
        except ValueError:
            # We hit beginning of node section
            # Break and start loading
            graph_info['node_type'] = line
            # Start reading node values
            if graph_info['node_type'] == 'NODE_COORD_SECTION':
                graph_info['nodes'] = read_coords(lines, i)
                break
            raise ValueError("Invalid line: {}".format(line))
        
    return graph_info

def draw_network(G, pos, options):
    nx.draw_networkx_nodes(G, pos, **NODE_OPTIONS)

    # get max min weight and pheromone values
    max_weight = max([value['weight'] for key, value in G.edges.items()])
    min_weight = min([value['weight'] for key, value in G.edges.items()])
    max_pheromones = max([value['pheromones'] for key, value in G.edges.items()])
    min_pheromones = min([value['pheromones'] for key, value in G.edges.items()])

    for key, value in G.edges.items():
        weight, pheromones = value['weight'], value['pheromones']
        # map alpha between 0.2 and 0.8 based on pheromone value
        alpha = np.interp(pheromones, [min_pheromones, max_pheromones], [MIN_ALPHA, MAX_ALPHA])
        # map width between 1 and 3 based on weight value
        width = np.interp(weight, [min_weight, max_weight], [MIN_WEIGHT, MAX_WEIGHT])
        nx.draw_networkx_edges(G,
                               pos = pos,
                               edgelist=[key],
                               alpha=alpha, 
                               width=width,
                               **EDGE_OPTIONS) #loop through edges and draw them


class Animator():
    def __init__(self, path):
        self.path = path
        self.tsp_info = read_tsp_file(path, 'tsp')
        self.G = graph_from_info(self.tsp_info)
        self.pos = nx.get_node_attributes(self.G, 'pos')
        self.fig, self.ax = plt.subplots()

        self.max_weight = max([value['weight'] for key, value in self.G.edges.items()])
        self.min_weight = min([value['weight'] for key, value in self.G.edges.items()])
        self.max_pheromones = max([value['pheromones'] for key, value in self.G.edges.items()])
        self.min_pheromones = min([value['pheromones'] for key, value in self.G.edges.items()])

    def update_network(self, G: nx.Graph):
        # TODO: Implement update network
        # Update the network with new pheromone values
        # Track ant movement?
        raise NotImplementedError

    def draw_network(self):
        self._draw_network(self.G, self.pos)

    def _draw_network(self,
                      G: nx.Graph,
                      pos: dict):
        nx.draw_networkx_nodes(G, pos, **NODE_OPTIONS)

        # get max min weight and pheromone values

        for key, value in G.edges.items():
            weight, pheromones = value['weight'], value['pheromones']
            # map alpha between 0.2 and 0.8 based on pheromone value
            alpha = np.interp(pheromones, [self.min_pheromones, self.max_pheromones], [MIN_ALPHA, MAX_ALPHA])
            # map width between 1 and 3 based on weight value
            width = np.interp(weight, [self.min_weight, self.max_weight], [MIN_WEIGHT, MAX_WEIGHT])
            nx.draw_networkx_edges(G,
                                pos = pos,
                                edgelist=[key],
                                alpha=alpha, 
                                width=width,
                                **EDGE_OPTIONS) #loop through edges and draw them

if __name__ == '__main__':
    path = 'tsplib/burma14.tsp'
    tsp_info = read_tsp_file(path, 'tsp')
    G = graph_from_info(tsp_info)
    options = {
        'node_color': 'red',
        'node_size': 100,
        'width': 1,
        'edge_color': 'gray',
        'style': 'dashed',
        'alpha' : 0.5,
        'with_labels': True
    }
    draw_network(G, nx.get_node_attributes(G, 'pos'), options)
    plt.show()

