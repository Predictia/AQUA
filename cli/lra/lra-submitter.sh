#!/bin/bash
#SBATCH --partition=shared
#SBATCH --job-name=regrid_test_mon_16
#SBATCH --output=regrid_mon_16_%j.out
#SBATCH --error=regrid_mon_16_%j.err
#SBATCH --account=bb1153
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=16
#SBATCH --time=08:00:00
#SBATCH --mem=200G 
set -e

# find mamba/conda (to be refined)
whereconda=$(which mamba | rev | cut -f 3-10 -d"/" | rev)
source $whereconda/etc/profile.d/conda.sh

# activate conda environment
conda activate aqua

# set the number of dask workers
workers=2

# run the Python script
# -d to perform a definitive run
# -o to overwrite existing files
# -w for the number of dask workers
# -l to change the loglevel
./cli_lra_generator.py --config lra_config.yaml -w ${workers} -d -o
