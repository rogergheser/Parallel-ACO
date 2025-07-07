#!/bin/bash
NODES=$1
PROCESSES=$2
STRATEGY=$3
EXECUTABLE=$4
OUT_FILE=$5
#PBS -l select=$NODES:ncpus=$PROCESSES:mem=16gb
#PBS -l place=$STRATEGY

#PBS -l walltime=1:00:00

#PBS -q short_cpuQ

module load mpich-3.2
NODES=(2 4 8 16 32 64)
for NODE in "${NODES[@]}"; do
    {
        mpiexec -n $NODE ./src/$EXECUTABLE;} >> "$OUT_FILE"
done
echo " " >> "$5"