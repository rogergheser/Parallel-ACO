# Parallel-ACO
A parallel implementation of Ant Colony Optimisation for TSP with mpic.

## High performance algorithms for Ant Colony Optimisation whilst leveraging MPI, OpenMP and a Hybrid of the two
In this project we implement three algorithms to increase the performance of Ant Colony Optimisation whilst using multiple processes, threads or both.

## Table of Contents
famo dopo

## Key Features
- **Hybrid Parallelization**: Combined MPI+OpenMP implementation
- **Reference Implementation**: Serial version for comparison
- **Performance Analysis**: Comprehensive benchmarking tools
- **Visualization**: Performance metrics plotting
- **Animator**: [IN PROGRESS] A tool to animate the operations on the graph

## Project Structure
├── allACO.c    # MPI implementation
├── animate.py          # Work in progress
├── animators           # Work in progress
├── data                # Run results
│   └── results
├── discarded_implementations # Discarded implementations but working, for reference
│   └── ACO.c
│   └── parallelACO.c
├── gen_graph.py       # Script to generate graphs
├── hybrid.c           # Hybrid MPI+OpenMP implementation
├── omp.c              # OpenMP implementation
├── README.md
├── run               # Utility scripts to run the algorithms
│   ├── hybrid.sh
│   ├── parallel.sh
│   └── serial.sh
├── serial.c       # Serial ACO implementation
├── tools           # Tools for performance analysis
│   ├── plot_times.py
│   └── plotting.py
└── tsplib         # TSPLIB dataset

## Datasets
We use the following datasets for testing:
* [TSPLIB](https://github.com/mastqe/tsplib)
    This uses nodes with x and y coordinates.
Also we provide a script for graph generation by sampling nodes in a cartesian space which can be used for further exploration.

