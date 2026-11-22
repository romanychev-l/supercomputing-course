#!/usr/bin/env bash
#SBATCH --job-name=hpc-omp
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=1G
#SBATCH --time=00:05:00
#SBATCH --output=omp-%j.out
# Add partition/account only as documented by the teaching cluster.
set -euo pipefail
cd "${SLURM_SUBMIT_DIR:?Submit with sbatch from the practicum directory}"
# Load the cluster's documented compiler modules here if required.
export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:?}"
export OMP_DYNAMIC=false
export OMP_SCHEDULE=static
export OMP_PLACES=cores
export OMP_PROC_BIND=close
srun --ntasks=1 ./build/kernels_omp pi 1000000
