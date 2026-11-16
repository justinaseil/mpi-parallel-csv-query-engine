#!/usr/bin/env bash

#SBATCH -p main
#SBATCH -n 7
#SBATCH --cpus-per-task=1

module purge
module load openmpi
module load python

DATA="data2.csv"
WHERE="Town==Ansonia"
GROUP="Property_Type"
AGG="Sale_Amount=count"

for P in 2 4 7
do
    echo "=== Paleidimas su $P procesais ==="
    mpirun -np $P python3 main_mpi.py \
      --input $DATA --where "$WHERE" --group-by $GROUP --agg "$AGG"
    echo "=============================="
done



