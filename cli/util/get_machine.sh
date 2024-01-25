script_dir=$(dirname "${BASH_SOURCE[0]}")
source $script_dir/logger.sh

function get_machine() {
    # Assuming the YAML structure is simple and looks something like:
    # machine: value

    # Use grep and awk to extract the value
    local machine_value=$(grep '^machine:' "$script_dir/../../config/config-aqua.yaml" | awk '{ print $2 }')

    echo $machine_value
}