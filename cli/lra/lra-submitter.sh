#!/bin/bash
#SBATCH --partition=shared
#SBATCH --job-name=regrid_test_day_8
#SBATCH --output=regrid_day_8_%j.out
#SBATCH --error=regrid_day_8_%j.err
#SBATCH --account=bb1153
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --time=08:00:00
#SBATCH --mem=200G 
set -e

# find mamba/conda (to be refined)
whereconda=$(which mamba | rev | cut -f 3-10 -d"/" | rev)
source $whereconda/etc/profile.d/conda.sh

# activate conda environment
conda activate aqua

# set the number of dask workers
workers=8

# run the Python script
# -d to perform a dry run (for testing reasons)
# -r to replace the files
# -v to be verbose
./cli_lra_generator.py --config config_lra.yml -w ${workers} -d -v
