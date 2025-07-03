#!/bin/bash

#PBS -l select=1:ncpus=1:mem=16gb

# set max execution time
#PBS -l walltime=4:00:00

# imposta la coda di esecuzione
#PBS -q short_cpuQ

module load mpich-3.2

NODES=(2 4 8 16 32 64 128)  # replace with your actual node names

for NODE in "${NODES[@]}"; do
    echo "Running on $NODE"
    mpirun -n $NODE serial
done