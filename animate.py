from matplotlib import pyplot as plt, animation
from typing import Optional, Tuple, List, Dict

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

class Animator():
    def __init__(self, path: str):
        """
        Inits the animator class with a tsp file
        The animator class will read the tsp file and create a networkx graph 
        and take care of drawing and updating the graph
        :param path: path to tsp file
        """
        self.path = path
        self.tsp_info = read_tsp_file(path, 'tsp')
        self.G = graph_from_info(self.tsp_info)
        
        self.pos = nx.get_node_attributes(self.G, 'pos')
        self.edge_color = nx.get_edge_attributes(self.G, 'pheromones')
        self.edge_width = nx.get_edge_attributes(self.G, 'weight')
        self.alpha = nx.get_edge_attributes(self.G, 'alpha')
        self.ants = nx.get_edge_attributes(self.G, 'ants')

        self.max_weight = max([value['weight'] for key, value in self.G.edges.items()])
        self.min_weight = min([value['weight'] for key, value in self.G.edges.items()])
        self.max_pheromones = max([value['pheromones'] for key, value in self.G.edges.items()])
        self.min_pheromones = min([value['pheromones'] for key, value in self.G.edges.items()])

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

    def update_network(self,
        pheromones: Dict[Tuple[int, int], float],
        ants: Optional[Dict]):
        """
        Updates the network with the new pheromone and ant values.
        Both dictionaries are accessed by edge key e.g. (0, 1)
        :param pheromones: dict of edge:pheromone values
        :param ants: dict of edge:ant values
        """
        # TODO: Implement update network
        # Update the network with new pheromone values
        # Track ant movement?
        # alpha = np.interp(pheromones, [self.min_pheromones, self.max_pheromones], [MIN_ALPHA, MAX_ALPHA])
        #     # map width between 1 and 3 based on weight value
        # width = np.interp(weight, [self.min_weight, self.max_weight], [MIN_WEIGHT, MAX_WEIGHT])
        # Get edge color based on the red scale. white for 0 pheromones, red for max pheromones
        self.min_pheromones = np.min(list(pheromones.values()))
        self.max_pheromones = np.max(list(pheromones.values()))
        
        if ants:
            self.min_ants = np.min(list(ants.values()))
            self.max_ants = np.max(list(ants.values()))
        
        for key in self.G.edges:
            value = self.G.edges[key]
            # set edge_color, alpha, edge_width
            alpha = np.interp(pheromones[key], [self.min_pheromones, self.max_pheromones], [MIN_ALPHA, MAX_ALPHA])
            normalised_width = np.interp(value['weight'], [self.min_weight, self.max_weight], [MIN_WEIGHT, MAX_WEIGHT])
            new_pheromone = pheromones[key]

            # update edge values
            self.G.edges[key]['pheromones'] = new_pheromone
            self.G.edges[key]['alpha'] = alpha
            self.G.edges[key]['weight'] = normalised_width
            
            if ants:
                self.G.edges[key]['ants'] = np.interp(ants[key], [self.min_ants, self.max_ants], [MIN_RADIUS, MAX_RADIUS])
            else:
                self.G.edges[key]['ants'] = 0
        
        self.pos = nx.get_node_attributes(self.G, 'pos')
        self.edge_color = nx.get_edge_attributes(self.G, 'pheromones')
        self.edge_width = nx.get_edge_attributes(self.G, 'weight')
        self.alpha = nx.get_edge_attributes(self.G, 'alpha')
        self.ants = nx.get_edge_attributes(self.G, 'ants')

    def draw_network(self):
        self._draw_network(self.G)

    def _draw_network(self,
                      G: nx.Graph):
        nx.draw_networkx_nodes(G, self.pos, **NODE_OPTIONS)
 
        logger.info("Drawing network")
        #loop through edges and draw them
        for key, value in G.edges.items():
            edge_color = self.edge_color[key]
            alpha = self.alpha[key]
            edge_width = self.edge_width[key]
            # map alpha between 0.2 and 0.8 based on pheromone value
            cmap = plt.get_cmap('Blues')
            norm = plt.Normalize(vmin=self.min_pheromones, vmax=self.max_pheromones)
            edge_color_mapped = cmap(norm(edge_color))
            
            nx.draw_networkx_edges(G,
                                edgelist = [key],
                                pos = self.pos,
                                edge_color = edge_color_mapped,
                                alpha = alpha, 
                                width = edge_width,
                                **EDGE_OPTIONS) #loop through edges and draw them
            # draw ants
            # Draw a circle of radius ants[key] at the midpoint of the edge
            # Get the midpoint of the edge
            x0, y0 = self.pos[key[0]]
            x1, y1 = self.pos[key[1]]
            mid_x = (x0 + x1) / 2
            mid_y = (y0 + y1) / 2
            radius = value['ants']
            dx, dy = x1 - x0, y1 - y0
            angle = np.degrees(np.arctan2(dy, dx))
            width = radius * edge_width * 4
            height = radius * 1
            ellipse = plt.matplotlib.patches.Ellipse(
                (mid_x, mid_y), width, height, angle=angle, color='green', alpha=0.8
            )
            plt.gca().add_patch(ellipse)



if __name__ == '__main__':
    path = 'tsplib/burma14.tsp'
    # tsp_info = read_tsp_file(path, 'tsp')
    # G = graph_from_info(tsp_info)
    # options = {
    #     'node_color': 'red',
    #     'node_size': 100,
    #     'width': 1,
    #     'edge_color': 'gray',
    #     'style': 'dashed',
    #     'alpha' : 0.5,
    #     'with_labels': True
    # }
    animator = Animator(path)
    phero, ants = animator.get_random_init()
    animator.update_network(
        pheromones=phero,
        ants=ants
    )
    animator.draw_network()
    
    # draw_network(G,
    #     nx.get_node_attributes(G, 'pos'),
    #     nx.get_edge_attributes(G, 'weight')
    # )
    plt.show()

