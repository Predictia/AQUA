script_dir=$(dirname "${BASH_SOURCE[0]}")
source $script_dir/logger.sh
source $script_dir/get_machine.sh

lumi_version=23.03
# Function to activate aqua
function install_aqua() {
    machine=$(get_machine)
    log_message INFO "Machine Name: $machine"

    # if machine is lumi use modules
    if [ $machine == "lumi" ]; then
        # clean up environment
        module --force purge
        log_message INFO "Environment has been cleaned up."

        # load modules
        module load LUMI/$lumi_version
        module load lumi-container-wrapper
        log_message INFO "Modules have been loaded."

        
        # install AQUA framework and diagnostics
        conda-containerize new --mamba --prefix "${INSTALLATION_PATH}" "${AQUA}/config/machines/lumi/installation/environment_lumi_common.yml"
        conda-containerize update "${INSTALLATION_PATH}" --post-install "${AQUA}/config/machines/lumi/installation/pip_lumi_common.txt"
        log_message INFO "AQUA framework and diagnostics have been installed."
    else
        #elif [ $machine == "levante" ]; then
        # find mamba/conda (to be refined)
        whereconda=$(which mamba | rev | cut -f 3-10 -d"/" | rev)
        source $whereconda/etc/profile.d/conda.sh
        conda init
        # activate conda environment
        conda activate aqua_common
        log_message DEBUG "AQUA successfully imported on LEVANTE"
    fi
    log_message INFO "AQUA successfully imported"
}
