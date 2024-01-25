source logger.sh

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
