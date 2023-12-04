#!/bin/bash
set -e

# Check a condition (replace this with your actual condition)
should_resubmit=false
script_dir=$(dirname "${BASH_SOURCE[0]}")

# Read the machine name from the YAML file
machine=$(grep -E "^machine:" "$script_dir/../../config/config-aqua.yaml" | awk '{print $2}')
# Now $machine contains the name of the machine
echo "Machine name: $machine"

while true; do
    if [ "$machine" == 'levante' ] || [ "$machine" == 'lumi' ]; then    
        if [ "$machine" == 'levante' ]; then
            account='bb1153'
            partition='shared'
        else
            account='project_465000454'
            partition='small'
        fi
        # Submit the SLURM job directly
        sbatch <<EOL
#!/bin/bash
#SBATCH --account=$account
#SBATCH --partition=$partition
#SBATCH --job-name=weights
#SBATCH --output=weights_%j.out
#SBATCH --error=weights_%j.log
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=16
#SBATCH --time=08:00:00
#SBATCH --mem=200G

echo 'Hello from SLURM job!'
# if machine is levante use mamba/conda
if [ $machine == "levante" ]; then
    # find mamba/conda (to be refined)
    whereconda=$(which mamba | rev | cut -f 3-10 -d"/" | rev)
    source $whereconda/etc/profile.d/conda.sh
    # activate conda environment
    conda activate aqua_common
fi

function load_environment_AQUA() {
        # Load env modules on LUMI
    module purge
    module use LUMI/23.03
}
# if machine is lumi use modules
if [ $machine == "lumi" ]; then
    load_environment_AQUA
    # get username
    username=$USER
    export PATH="/users/$username/mambaforge/aqua/bin:$PATH"
fi
/usr/bin/env python3 "$script_dir/generate_weights_for_catalog.py"
EOL

    else
        /usr/bin/env python3 "$script_dir/generate_weights_for_catalog.py"
    fi
    # Use an if statement to decide whether to resubmit
    if $should_resubmit; then
        # Sleep for one week (adjust the time as needed)
        sleep 604800  # 604800 seconds = 1 week
        sbatch "$0"  # Resubmit the job to Slurm
    fi
    exit  # Exit the current instance of the script after submitting
done