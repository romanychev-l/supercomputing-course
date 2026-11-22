#!/usr/bin/env bash
#SBATCH --job-name=hpc-mpi
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --time=00:05:00
#SBATCH --output=mpi-%j.out
set -euo pipefail
cd "${SLURM_SUBMIT_DIR:?Submit with sbatch from the practicum directory}"
export OMP_NUM_THREADS=1
# Use only if this cluster documents direct srun integration with its MPI.
# Otherwise replace this launcher with the center's documented command.
srun ./build/mpi_sum_pi pi 1000000
