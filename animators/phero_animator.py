from .animator import Animator
from matplotlib import pyplot as plt, animation
from matplotlib.animation import FuncAnimation
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

class PheroAnimator(Animator):
    def __init__(self, path: str):
        super().__init__(path)

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


    def _draw_network(self, G: nx.Graph):
        artists = []  # List to store artists

        # Draw nodes and store artist
        node_artists = nx.draw_networkx_nodes(G, self.pos, **NODE_OPTIONS)
        if isinstance(node_artists, list):
            artists.extend(node_artists)  # Sometimes draw functions return lists
        else:
            artists.append(node_artists)

        logger.info("Drawing network")

        # Loop through edges and draw them
        cmap = plt.get_cmap('Blues')
        norm = plt.Normalize(vmin=self.min_pheromones, vmax=self.max_pheromones)

        for key, value in G.edges.items():
            edge_color = self.edge_color[key]
            alpha = self.alpha[key]
            edge_width = self.edge_width[key]

            edge_color_mapped = cmap(norm(edge_color))

            edge_artists = nx.draw_networkx_edges(
                G, edgelist=[key], pos=self.pos,
                edge_color=[edge_color_mapped], alpha=alpha,
                width=edge_width, **EDGE_OPTIONS
            )

            if isinstance(edge_artists, list):
                artists.extend(edge_artists)
            else:
                artists.append(edge_artists)

            # Draw ants as ellipses
            x0, y0 = self.pos[key[0]]
            x1, y1 = self.pos[key[1]]
            mid_x, mid_y = (x0 + x1) / 2, (y0 + y1) / 2
            radius = self.ants[key]
            dx, dy = x1 - x0, y1 - y0
            angle = np.degrees(np.arctan2(dy, dx))
            width = radius * edge_width * 4
            height = radius * 1

            ellipse = plt.matplotlib.patches.Ellipse(
                (mid_x, mid_y), width, height, angle=angle, color='green', alpha=0.8
            )
            plt.gca().add_patch(ellipse)
            artists.append(ellipse)

        return artists

    def draw_update(self, iteration):
        """
        Updates the network visualization for animation.
        Must return a sequence of Artist objects.
        """
        self.ax.clear()
        phero, ants = self.load_info(iteration)
        self.update_network(pheromones=phero, ants=ants)
        
        # Draw nodes and edges
        artists = self.draw_network()
        
        self.ax.set_title(f"Iteration {iteration}")
        
        return artists
    
    def get_graph_animation(self):
        """
        Creates and returns an animation object.
        """
        ani = FuncAnimation(self.fig, self.draw_update, frames=40, interval=200, blit=False)
        return ani

if __name__ == '__main__':
    path = 'tsplib/burma14.tsp'
    animator = PheroAnimator(path)
    anim = animator.get_graph_animation()
    # Save animation (Ensure ImageMagick is installed)
    anim.save('test.gif', writer='pillow', savefig_kwargs={'facecolor': 'white'}, fps=5)

    plt.show()