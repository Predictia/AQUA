#!/bin/bash
#SBATCH --partition=debug # compute is suggested on levante
#SBATCH --job-name=teleconnections
#SBATCH --output=teleconnections_%j.out
#SBATCH --error=teleconnections_%j.err
#SBATCH --account=project_465000454
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --time=00:30:00
#SBATCH --mem=0
set -e

configfile="${AQUA}/diagnostics/teleconnections/deliverable/config_deliverable.yaml"
scriptfile="${AQUA}/diagnostics/teleconnections/cli/cli_teleconnections.py"
outputdir="${AQUA}/diagnostics/teleconnections/deliverable/output"
workers=8

echo "Running the global time series diagnostic with $workers workers"
echo "Script: $scriptfile"
echo "Config: $configfile"

python $scriptfile -c $configfile -l DEBUG -n $workers --outputdir $outputdir --ref