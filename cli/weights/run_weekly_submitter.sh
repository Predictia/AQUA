#!/bin/bash
set -e

# find mamba/conda (to be refined)
whereconda=$(which mamba | rev | cut -f 3-10 -d"/" | rev)
source $whereconda/etc/profile.d/conda.sh

# activate conda environment
conda activate aqua

while true; do
    # Your commands to run your job
    /usr/bin/env python3 generate_weights_for_catalog.py
    # Sleep for one week (adjust the time as needed)
    sleep 604800  # 604800 seconds = 1 week

    # Resubmit the job to Slurm
    sbatch $0
    exit  # Exit the current instance of the script after submitting
done