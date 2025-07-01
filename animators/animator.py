from matplotlib import pyplot as plt, animation
from matplotlib.animation import FuncAnimation
from typing import Optional, Tuple, List, Dict
from abc import ABC, abstractmethod
import networkx as nx
import random
import logging
import numpy as np

logger = logging.getLogger(__name__)
def init_logger(logger):
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
init_logger(logger)
MIN_ALPHA = 0.2
MAX_ALPHA = 0.8
MIN_WEIGHT = .5
MAX_WEIGHT = 2.0
MIN_RADIUS = 0.0 # MINIMUM RADIUS FOR REPRESENTING ANT QUANTITY
MAX_RADIUS = .125 # MAXIMUM RADIUS FOR REPRESENTING ANT QUANTITY
PHERO_INIT = 1.0
NODE_OPTIONS = {
    'node_color': 'red',
    'node_size': 150,
    'alpha' : 1,
}

EDGE_OPTIONS = {
    'style': 'dashed',
}
logger.info("Node options: {}".format(NODE_OPTIONS.keys()))
logger.info("Edge options: {}".format(EDGE_OPTIONS.keys()))

def graph_from_info(graph_info:dict)->nx.Graph:
    """
    Takes graph_info and initializes a networkx graph
    :param graph_info: dict containing nodes and edges
    :return: nx.Graph object
    """
    nodes = graph_info['nodes']
    G = nx.Graph()
    
    # Add nodes
    G.add_nodes_from(nodes.keys())
    for node, coords in nodes.items():
        G.add_node(node, pos=coords, color="red")
    logger.info(f"Added {len(nodes)} nodes to graph")

    # Add edges
    for i, (x0, y0) in nodes.items():
        for j, (x1, y1) in nodes.items():
            if i != j:
                dist = ((x1 - x0)**2 + (y1 - y0)**2)**0.5
                G.add_edge(i, j, 
                           weight=dist,
                           pheromones=random.random())
    logger.info(f"Added {G.number_of_edges()} edges to graph")

    return G

def read_coords(lines:List[str], start: int)->Dict[int, Tuple[float, float]]:
    """
    Reads coordinates from input file
    :param lines: list of lines from input file
    :param start: index to start reading from
    :return: dict of node: (x, y) coordinates
    """
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
    """
    Reads tsp file and returns a dict of graph info
    :param path: path to tsp file
    :param type: UNHANDLED -- type of tsp file instance to read
    :return: dict of graph info
    """
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

class Animator(ABC):
    def __init__(self, path: str):
        """
        Initializes the animator class with a TSP file.
        The animator class will read the TSP file, create a networkx graph,
        and handle drawing and updating the graph.
        """
        self.path = path
        self.tsp_info = read_tsp_file(path, 'tsp')
        self.G = graph_from_info(self.tsp_info)
        self.fig, self.ax = plt.subplots()
        self.iteration = 0

        self.pos = nx.get_node_attributes(self.G, 'pos')
        self.edge_color = nx.get_edge_attributes(self.G, 'pheromones')
        self.edge_width = nx.get_edge_attributes(self.G, 'weight')

        self.max_weight = max(nx.get_edge_attributes(self.G, 'weight').values())
        self.min_weight = min(nx.get_edge_attributes(self.G, 'weight').values())
        self.max_pheromones = max(nx.get_edge_attributes(self.G, 'pheromones').values())
        self.min_pheromones = min(nx.get_edge_attributes(self.G, 'pheromones').values())

    def get_random_init(self)->Tuple[Dict[Tuple[int, int], float], Dict[Tuple[int, int], float]]:
        """
        Randomly inits pheromones and ants for the network
        """
        pheromones = {}
        ants = {}

        for edge in self.G.edges:
            pheromones[edge] = random.random()
            ants[edge] = random.random()

        return pheromones, ants

    def graph_init(self):
        """
        Inits the graph with random pheromones and ants
        """
        for edge in self.G.edges:
            self.alpha[edge] = np.interp(PHERO_INIT, [self.min_pheromones, self.max_pheromones], [MIN_ALPHA, MAX_ALPHA])
            self.ants[edge] = 0

        self.draw_network()

    def draw_network(self):
        return self._draw_network(self.G)
    
    def load_info(self, iteration):
        """
        Loads ant and info information from ./data/ dir
        :param iteration: int of iteration to load
        :return: dict of ant and info information
        """
        with open(f'./data/ant_tours/{iteration}.txt', 'r') as f:
            ants = f.readlines()
        with open(f'./data/pheromones/{iteration}.txt', 'r') as f:
            pheromones = f.readlines()
        
        ants = [line.strip() for line in ants]
        pheromones = [line.strip().split(" ") for line in pheromones]

        ant_tours = [tour.split(" ") for tour in ants]
        ant_tours = [[int(node) for node in tour] for tour in ant_tours]

        phero, ants = {}, {}

        for edge in self.G.edges:
            u, v = edge
            phero[edge] = float(pheromones[u-1][v-1])
            ants[edge] = 0

        for i in range(len(ant_tours)):
            for j in range(len(ant_tours[i])-1):
                edge = (ant_tours[i][j]+1, ant_tours[i][j+1]+1)
                try:
                    ants[edge] += 1
                except KeyError:
                    edge = edge[::-1]
                    ants[edge] += 1
        
        return phero, ants
    
    @abstractmethod
    def update_network(self):
        """
        Updates the network internal values to be used for drawing.
        """
        pass
    
    @abstractmethod
    def draw_update(self, iteration):
        """
        Updates the network and draws the updated network.
        """
        pass

    @abstractmethod
    def _draw_network(self, G: nx.Graph):
        """
        Defines how to draw the network
        """
        pass

    @abstractmethod
    def get_graph_animation(self) -> FuncAnimation:
        """
        Returns the graph animation
        """
        pass
    
if __name__ == '__main__':
    path = 'tsplib/burma14.tsp'
    animator = Animator(path)
    anim = animator.get_graph_animation()
    # Save animation (Ensure ImageMagick is installed)
    anim.save('test.gif', writer='pillow', savefig_kwargs={'facecolor': 'white'}, fps=5)

    plt.show()