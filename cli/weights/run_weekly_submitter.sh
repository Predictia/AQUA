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
        # Create a SLURM job script
        job_script="tmp.sh"
        echo "#!/bin/bash" > "$job_script"
        if [ "$machine" == 'levante' ]; then
            echo "#SBATCH --account=bb1153" >> "$job_script"
            echo "#SBATCH --partition=shared" >> "$job_script"
        else
            echo "#SBATCH --partition=standard" >> "$job_script"
            echo "#SBATCH --account=project_465000454" >> "$job_script"
        fi
        echo "#SBATCH --job-name=weights" >> "$job_script"
        echo "#SBATCH --output=weights_%j.out" >> "$job_script"
        echo "#SBATCH --error=weights_%j.log" >> "$job_script"
        echo "#SBATCH --nodes=1" >> "$job_script"
        echo "#SBATCH --ntasks-per-node=1" >> "$job_script" #16
        echo "#SBATCH --time=0:10:00" >> "$job_script"
        echo "#SBATCH --mem=10G" >> "$job_script"
        # Add your commands
        echo "echo 'Hello from SLURM job!'" >> "$job_script"
        echo "/usr/bin/env python3 generate_weights_for_catalog.py" >> "$job_script"
        # Submit the SLURM job
        sbatch "$job_script"
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