#!/bin/bash

#PBS -l select=4:ncpus=32:mem=16gb

# set max execution time
#PBS -l walltime=4:00:00

# imposta la coda di esecuzione
#PBS -q short_cpuQ

# Set number of OpenMP threads per MPI process
export OMP_NUM_THREADS=8
# Enable thread binding
export OMP_PROC_BIND=true
export OMP_PLACES=cores

module load mpich-3.2

NODES=(2 4 8 16 32 64 128)  # replace with your actual node names

for NODE in "${NODES[@]}"; do
    echo "Running $NODE"
    {   time mpirun.actual -n $NODE \
        -ppn $OMP_NUM_THREADS \
        parallel; } 2>> "time/hybrid.txt"
done
