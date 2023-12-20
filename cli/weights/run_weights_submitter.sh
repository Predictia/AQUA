#!/bin/bash
set -e

script_dir=$(dirname "${BASH_SOURCE[0]}")

# Read the machine name from the YAML file
machine=$(python -c "
import yaml
with open('$script_dir/../../config/config-aqua.yaml') as f:
    config = yaml.safe_load(f)
    print(config['machine'])
")
echo "Machine Name: $machine"

read -r nproc nodes walltime memory lumi_version account partition run_on_sunday < <(python -c "
import yaml
with open('$script_dir/config/weights_config.yml') as f:
    config = yaml.safe_load(f)['compute_resources']
    print(config['nproc'], config['nodes'], config['walltime'], config['memory'], config['lumi_version'], \
    config['account']['$machine'], config['partition']['$machine'], config['run_on_sunday'])
")

if [ "$run_on_sunday" == "True" ]; then
    begin_time=$(date -d "next Sunday 21:00" +"%Y-%m-%dT%H:%M:%S")
else
    begin_time=$(date -d "now + 1 minute" +"%Y-%m-%dT%H:%M:%S")
fi
echo "Begin run time: $begin_time"
echo "Number of processes (nproc): $nproc"
echo "Number of nodes: $nodes"
echo "Walltime: $walltime"
echo "Memory: $memory"
echo "Account: $account"
echo "Partition: $partition"

# if machine is levante use mamba/conda
if [ $machine == "levante" ]; then
    # find mamba/conda (to be refined)
    whereconda=$(which mamba | rev | cut -f 3-10 -d"/" | rev)
    source $whereconda/etc/profile.d/conda.sh
    conda init
    # activate conda environment
    conda activate aqua_common
fi

function load_environment_AQUA() {
        # Load env modules on LUMI
    module purge
    module use LUMI/$lumi_version
}

if [ "$machine" == 'levante' ] || [ "$machine" == 'lumi' ]; then
    # Submit the SLURM job with submission_time variable
    sbatch --begin="$begin_time" <<EOL
#!/bin/bash
#SBATCH --account=$account
#SBATCH --partition=$partition
#SBATCH --job-name=weights
#SBATCH --output=weights_%j.out
#SBATCH --error=weights_%j.log
#SBATCH --nodes=$nodes
#SBATCH --ntasks-per-node=$nproc
#SBATCH --time=$walltime
#SBATCH --mem=$memory

echo "Submission time: $submission_time"
echo 'Hello from SLURM job!'

# if machine is lumi use modules
if [ $machine == "lumi" ]; then
    load_environment_AQUA
    # get username
    username=$USER
    export PATH="/users/$username/mambaforge/aqua/bin:$PATH"
fi
/usr/bin/env python3 "$script_dir/generate_weights.py" --nproc=$nproc
EOL

else
    /usr/bin/env python3 "$script_dir/generate_weights.py" --nproc=$nproc
fi