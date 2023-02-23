#!/bin/bash
#SBATCH --partition=compute
#SBATCH --job-name=regrid_test_mon_12
#SBATCH --output=output_mon_12.txt
#SBATCH --error=error_mon_12.txt
#SBATCH --account=bb1153
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=12
#SBATCH --time=12:00:00
set -e

# find mamba/conda (to be refined)
whereconda=$(which mamba | rev | cut -f 3-10 -d"/" | rev)
source $whereconda/etc/profile.d/conda.sh

# activate conda environment
conda activate aqua

# config
#model='IFS'
#exp='tco2559-ng5'
#res='r100'
#freq='mon'
workers=12

# run the Python script
#./regridder.py -m ${model} -e ${exp} -r ${res} -f ${freq} -w ${workers} -o /work/bb1153/b3122076/IFS-lowres
./regridder.py --config config_lra.yml -w ${workers}
