from animators import AntAnimator, PheroAnimator
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

if __name__ == '__main__':
    path = 'tsplib/burma14.tsp'
    animator = AntAnimator(path)
    anim = animator.get_graph_animation()
    # Save animation (Ensure ImageMagick is installed)
    anim.save('ants.gif', writer='pillow', savefig_kwargs={'facecolor': 'white'}, fps=5)

    plt.show()