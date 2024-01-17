lumi_version=23.03

# Global log level
# 1=DEBUG, 2=INFO, 3=WARNING, 4=ERROR, 5=CRITICAL
LOG_LEVEL=2

# Function to log messages with colored output
function log_message() {
    local msg_type=$1
    local message=$2
    local color
    local no_color="\033[0m" # Reset to default terminal color
    local msg_level

    # Check if only one argument is provided
    if [ $# -eq 1 ]; then
        message=$1
        color=$no_color  # Use default terminal color for unspecified message types
    else
        # Set color based on message type
        case $msg_type in
            DEBUG) color="\x1b[37m" ; msg_level=1 ;;                # Grey for DEBUG
            INFO) color="\033[0;32m" ; msg_level=2 ;;               # Green for INFO
            WARNING) color="\x1b[38;2;255;165;0m" ; msg_level=3 ;;  # Orange for WARNING
            ERROR) color="\033[0;31m" ; msg_level=4 ;;              # Red for ERROR
            CRITICAL) color="\x1b[31;1m" ; msg_level=5 ;;           # Bold red for CRITICAl
            *) color=$no_color ; msg_level=0 ;;                     # Default terminal color
        esac
    fi

    # If no message type was provided, shift arguments
    if [ $# -eq 1 ]; then
        message=$msg_type
        msg_type="INFO" # Default to INFO level for single-argument calls
        msg_level=2
    fi

    # Check if the message should be printed based on the log level
    if [ $msg_level -ge $LOG_LEVEL ]; then
        # If no message type was provided, shift arguments
        if [ $# -eq 1 ]; then
            message=$1
        fi
        echo -e "${color}$(date '+%Y-%m-%d %H:%M:%S'): $message${no_color}"
    fi
}

function get_machine() {
    # Determine the directory of the current script
    script_dir=$(dirname "${BASH_SOURCE[0]}")
    machine=$(python -c "
try:
    # Read and log the machine name from the YAML configuration file
    import yaml
    with open('$script_dir/../../config/config-aqua.yaml') as f:
        config = yaml.safe_load(f)
        print(config['machine'])
except Exception as e:
    print('Error:', e)
")
    if [[ $machine == Error:* ]]; then
        log_message ERROR "Error reading machine name: ${machine#Error: }"
    fi
    echo $machine
}

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
