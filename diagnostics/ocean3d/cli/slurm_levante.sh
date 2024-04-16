#!/bin/bash
#SBATCH --partition=compute
#SBATCH --job-name=ocean3d
#SBATCH --output=output_%j.out
#SBATCH --error=output_%j.err
#SBATCH --account=bb1153
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --time=08:00:00
#SBATCH --mem=0 
set -e

# conda actiavte aqua
# python cli_ocean3d.py
python cli_ocean3d.py --model IFS-NEMO --exp ssp370 --source lra-r100-monthly --loglevel debug
# python cli_ocean3d.py --model ICON --exp historical-1990 --source lra-r100-monthly --loglevel debug