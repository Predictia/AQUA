script_dir=$(dirname "${BASH_SOURCE[0]}")
source $script_dir/../util/bash_util.sh
log_message "INFO" "The aqua utilities for bash scripts are imported."


# Function to create a job script
function slurm_job() {
    local nodes=${1:-1}             # Default to 1 node if not specified
    local nproc=${2:-1}             # Default to 1 processor if not specified
    local walltime=${3:-"02:30:00"} # Default walltime if not specified
    local memory=${4:-"10G"}        # Default memory if not specified
    local queue=${5:-""}            # Queue, to be determined based on machine_name
    local account=${6:-""}          # The account to which SLURM charges the job
    local additional_commands=$(cat)  # Read additional commands from standard input


    local JOB_NAME="job"

    machine=$(get_machine)            # Assuming get_machine is defined
    log_message "INFO" "Machine name: $machine"

    # Submitting the SLURM job
    log_message INFO "Submitting the SLURM job"
    # Setting default values for the queue and account
    if [ -z "$queue" ]; then
        if [ $machine == "levante" ]; then
            queue="compute"
        elif [ $machine == "lumi" ]; then
            queue="small"
        else
            log_message CRITICAL "The queue is not defined. Please, define the queue manually."
            return 1  # Exit the function with an error status
        fi
    fi
    if [ -z "$account" ]; then
        if [ $machine == "levante" ]; then
            account="bb1153"
        elif [ $machine == "lumi" ]; then
            account="project_465000454"
        else
            log_message CRITICAL "The account is not defined. Please, define the account manually."
            return 1  # Exit the function with an error status
        fi
    fi

    if [ "$machine" == 'levante' ] || [ "$machine" == 'lumi' ]; then
        # Submit the SLURM job with submission_time variable
        sbatch <<EOL
#!/bin/bash
#SBATCH --account=$account
#SBATCH --partition=$queue
#SBATCH --job-name=$JOB_NAME
#SBATCH --output=$JOB_NAME_%j.out
#SBATCH --error=$JOB_NAME_%j.log
#SBATCH --nodes=$nodes
#SBATCH --ntasks-per-node=$nproc
#SBATCH --time=$walltime
#SBATCH --mem=$memory

# Load function to log messages with colored output
source $script_dir/../util/bash_util.sh

activate_aqua

log_message INFO 'Hello from SLURM job!'
log_message INFO "Number of processes (nproc): $nproc"
log_message INFO "Number of nodes: $nodes"
log_message INFO "Walltime: $walltime"
log_message INFO "Memory: $memory"
log_message INFO "Account: $account"
log_message INFO "Partition: $queue"

# Additional commands passed to the function
$additional_commands
EOL
        return 0
    fi
}