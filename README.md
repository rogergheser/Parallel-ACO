# Parallel-ACO
A parallel implementation of Ant Colony Optimisation for TSP with mpic.

## High performance algorithms for Ant Colony Optimisation whilst leveraging MPI, OpenMP and a Hybrid of the two
In this project we implement three algorithms to increase the performance of Ant Colony Optimisation whilst using multiple processes, threads or both.

## Table of Contents
- [Key Features](#key-features)
- [Project Structure](#project-structure)
- [Datasets](#datasets)
- [Dependencies](#dependencies)
- [Cluster Configuration](#cluster-configuration)
- [How to Run](#how-to-run)
- [Performance Analysis](#performance-analysis)
- [Scripts](#scripts)
- [Future Improvements](#future-improvements)

## Key Features
- **Hybrid Parallelization**: Combined MPI+OpenMP implementation
- **Reference Implementation**: Serial version for comparison
- **Performance Analysis**: Comprehensive benchmarking tools
- **Visualization**: Performance metrics plotting
- **Animator**: [IN PROGRESS] A tool to animate the operations on the graph

## Project Structure
```bash
├── animators           # Work in progress
├── data                # Run results
│   └── results
├── discarded_implementations # Discarded implementations but working, for reference
│   └── ACO.c
│   └── parallelACO.c
├── src # Working implementations
│   ├── hybrid.c         # Hybrid MPI+OpenMP implementation
│   ├── mpi.c            # Parallel MPI implementation
│   ├── omp.c            # OpenMP implementation
│   └── serial.c         # Serial ACO implementation
├── README.md
├── run               # Utility scripts to run the algorithms
│   ├── hybrid.sh
│   ├── parallel.sh
│   └── serial.sh
├── tools           # Tools for performance analysis
│   ├── animate.py      # Work in progress
│   ├── gen_graph.py    # Script to generate graphs
│   ├── plot_times.py   # Script to plot execution times
│   └── plotting.py     # Script to plotting performance metrics
└── tsplib         # TSPLIB dataset
```

## Datasets
We use the following datasets for testing:
* [TSPLIB](https://github.com/mastqe/tsplib)
    This uses nodes with x and y coordinates.
Also we provide a script for graph generation by sampling nodes in a cartesian space which can be used for further exploration.


## Dependencies

![MPI](https://img.shields.io/badge/MPI-MPICH%203.2-blue?style=flat-square)
![OpenMP](https://img.shields.io/badge/OpenMP-Enabled-green?style=flat-square)
![PBS](https://img.shields.io/badge/PBS-Scheduler-orange?style=flat-square)

## Cluster Configuration

| Resource | Specification |
|----------|---------------|
| Nodes | 1-4 compute nodes |
| Memory | 16GB per node |
| Queue | short_cpuQ |
| Wall Time | 4:00 hour max |
| MPI Processes | 1-64 per node |
| OpenMP Threads | 1-64 per process |

## Build and Run

To compile and run the different versions of the program, use the following commands:

**Serial Version**
```bash
gcc serial.c -o serial -lm
```

**MPI Version**
```bash
mpicc -g -Wall -o mpi mpi.c -lm
```

**OpenMP Version**
```bash
gcc -fopenmp -o omp omp.c -lm
```

**Hybrid MPI + OpenMP Version**
```bash
mpicc -g -Wall -fopenmp -o hybrid hybrid.c -lm
```

### Run Examples

In the shell script to submit the jobs to the cluster, the resulting commands to run the files will be:

**Serial Version**
  ```bash
  mpirun -n 1 ./serial
  ```

**MPI Version** (e.g., using 4 processes)
  ```bash
  mpirun -n 4 ./mpi
  ```

**OpenMP Version** (e.g., using 4 threads)
  ```bash
  export OMP_NUM_THREADS=4 
  mpirun -n 1 
  ```

**Hybrid Version** (e.g., 2 MPI processes, each with 4 threads)
  ```bash
  export OMP_NUM_THREADS=4 
  mpirun.actual -n 2 -ppn 4 ./hybrid
  ```


## Performance Analysis

The project includes comprehensive performance analysis tools:
- Speedup measurements
- Efficiency calculations
- Scalability analysis
- Resource utilization metrics

## Scripts

| Script | Description |
|--------|-------------|
| `run.sh` | Runs the specified algorithm |

## Future Improvements

- Animator for visualizing the results
- Optimize communication overhead with multiple threads
