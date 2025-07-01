import os
import logging
import random
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image
from matplotlib import transforms
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.animation import FuncAnimation
from typing import List

from animator import Animator
from animators.types import AntTours

# Initialize Logger
logger = logging.getLogger(__name__)

def init_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()]
    )

init_logger()

# Constants
MIN_ALPHA, MAX_ALPHA = 0.2, 0.8
MIN_WEIGHT, MAX_WEIGHT = 0.5, 2.0
MIN_RADIUS, MAX_RADIUS = 0.0, 0.125  # Ant quantity representation
PHERO_INIT, FPM = 1.0, 10  # Frame per movement

NODE_OPTIONS = {"node_color": "red", "node_size": 150, "alpha": 1}
EDGE_OPTIONS = {"style": "dashed"}

logger.info(f"Node options: {NODE_OPTIONS}")
logger.info(f"Edge options: {EDGE_OPTIONS}")

class AntAnimator(Animator):
    def __init__(self, path: str):
        """Initialize the AntAnimator."""
        super().__init__(path)
        self.ant_tours : list[AntTours] = self._read_ant_paths()
        self.pos = {}  # Stores node positions

        self.ant_artists = []
        self.ant_path = "ant.png"
        self.ant_im = Image.open(self.ant_path).convert("RGBA")
        self.ant_im = self.preprocess_image(self.ant_im)

    def preprocess_image(self, image):
        """Convert black background to red, but keep transparency."""
        data = np.array(image)
        
        # Make mask of black areas that are not transparent
        black_mask = (data[:, :, 0] == 0) & (data[:, :, 1] == 0) & (data[:, :, 2] == 0) & (data[:, :, 3] != 0)
        
        # Change black areas to red
        data[black_mask] = [255, 0, 0, 255]
        
        return Image.fromarray(data)

    def _read_ant_paths(self) -> List[AntTours]:
        """Read and parse ant tour paths from text files.
        
        Returns:
            List of ant tours, each tour is a list of paths.
            Each path is a list of node indices.
        """
        ant_tours = []
        tour_dir = "data/ant_tours"

        for file in sorted(os.listdir(tour_dir), key=lambda x: int(x.split('.')[0]))[:3]:
            if file.endswith(".txt"):
                with open(os.path.join(tour_dir, file), "r") as f:
                    paths = [list(map(int, line.strip().split())) for line in f.readlines()]
                    ant_tours.append(paths)

        logger.info(f"Loaded {len(ant_tours)} ant tours.")
        return ant_tours

    def _draw_network(self, G: nx.Graph):
        """Draw the network graph."""
        pos = self.pos
        return [
            nx.draw_networkx_nodes(G, pos, **NODE_OPTIONS),
            nx.draw_networkx_edges(G, pos, **EDGE_OPTIONS),
        ]

    def add_ants(self, positions: List[tuple], orientations: List[float], zoom: float = 0.02):
        """Create ant images at the specified positions and orientations."""
        new_ants = []
        for (x, y), angle in zip(positions, orientations):
            # Rotate ant image
            imagebox = OffsetImage(self.ant_im, zoom=zoom)
            trans = transforms.Affine2D().rotate_deg(angle) + self.ax.transData
            imagebox.set_transform(trans)

            ant = AnnotationBbox(imagebox, (x, y), frameon=False)
            self.ax.add_artist(ant)  # Ensure ants are visible
            new_ants.append(ant)

        return new_ants

    def draw_ants(self, frame: int):
        """Compute and return ant positions for the given frame."""
        frames_per_movement = self.G.number_of_edges() * FPM
        iteration = frame // frames_per_movement
        j = (frame%self.G.number_of_edges()// FPM)

        positions = []
        orientations = []
        for tour in self.ant_tours[iteration]:
            N = len(tour)
            start_city = tour[j] + 1
            next_city = tour[(j + 1) % N] + 1

            # Compute ant position on edge
            start_node_pos = self.pos[start_city]
            next_node_pos = self.pos[next_city]
            x = start_node_pos[0] + (next_node_pos[0] - start_node_pos[0]) * j / FPM
            y = start_node_pos[1] + (next_node_pos[1] - start_node_pos[1]) * j / FPM
            positions.append((x, y))
            orientations.append(np.arctan2(next_node_pos[1] - start_node_pos[1], next_node_pos[0] - start_node_pos[0]))

        for ant in self.ant_artists:
            ant.remove()
        self.ant_artists = self.add_ants(positions, orientations)

    def draw_update(self, frame: int):
        """Update the animation frame-by-frame."""
        # Clear old frame
        if frame % FPM == 0:
            self.update_network()
            # save the current frame in a debug folder
            plt.savefig(f"debug/frame_{frame}.png", dpi=300, bbox_inches='tight')

        self.draw_ants(frame)
        return self._draw_network(self.G) + self.ant_artists

    def get_graph_animation(self):
        """Generate and return the animation object."""
        iterations = len(self.ant_tours)
        frames = FPM * self.G.number_of_nodes() * iterations

        return FuncAnimation(
            self.fig, self.draw_update, frames=frames, interval=100, blit=False
        )

    def update_network(self):
        """Update network attributes (positions, edge properties)."""
        self.pos = nx.get_node_attributes(self.G, "pos")

if __name__ == "__main__":
    path = "tsplib/burma14.tsp"
    animator = AntAnimator(path)
    anim = animator.get_graph_animation()

    # Save animation
    anim.save("test.gif", writer="pillow", savefig_kwargs={"facecolor": "white"}, fps=5)

    plt.show()
