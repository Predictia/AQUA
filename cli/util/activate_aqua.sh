source logger.sh
source get_machine.sh

lumi_version=23.03
# Function to load environment on LUMI
function load_environment_AQUA() {
    # Load env modules on LUMI
    module purge
    module use LUMI/$lumi_version
}

# Function to activate aqua
function activate_aqua() {
    machine=$(get_machine)
    log_message INFO "Machine Name: $machine"

    # if machine is lumi use modules
    if [ $machine == "lumi" ]; then
        $(load_environment_AQUA)
        # get username
        username=$USER
        log_message INFO "username $USER"
        export PATH="/users/$username/mambaforge/aqua/bin:$PATH"
        log_message INFO "path $PATH"
        log_message DEBUG "AQUA successfully imported on LUMI"
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
