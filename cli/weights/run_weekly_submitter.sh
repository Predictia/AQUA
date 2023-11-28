#!/bin/bash
set -e

# Check a condition (replace this with your actual condition)
should_resubmit=false

# find mamba/conda (to be refined)
whereconda=$(which mamba | rev | cut -f 3-10 -d"/" | rev)
source $whereconda/etc/profile.d/conda.sh

# activate conda environment
conda activate aqua_common

machine=$(python get_machine.py)
echo "Machine name: $machine"

while true; do
    if [ "$machine" == 'levante' ] || [ "$machine" == 'lumi' ]; then    
        if [ "$machine" == 'levante' ]; then
            account='bb1153'
            partition='shared'
        else
            account='project_465000454'
            partition='standard'
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
/usr/bin/env python3 generate_weights_for_catalog.py
EOL

    else
        /usr/bin/env python3 generate_weights_for_catalog.py
    fi

    
    # Use an if statement to decide whether to resubmit
    if $should_resubmit; then
        # Sleep for one week (adjust the time as needed)
        sleep 604800  # 604800 seconds = 1 week
        sbatch "$0"  # Resubmit the job to Slurm
    fi
    exit  # Exit the current instance of the script after submitting
done