#!/bin/bash
# Check if AQUA is set and the file exists
if [[ -z "$AQUA" ]]; then
    echo -e "\033[0;31mError: The AQUA environment variable is not defined, or the file does not exist."
    echo -e "Please define the AQUA environment variable with the path to your 'AQUA' directory."
    echo -e "For example: export AQUA=/path/to/aqua\033[0m"
    exit 1  # Exit with status 1 to indicate an error
else
    source "$AQUA/cli/util/logger.sh"
    log_message INFO "Sourcing logger.sh from: $AQUA/cli/util/logger.sh"
    # Your subsequent commands here
fi
setup_log_level 2 # 1=DEBUG, 2=INFO, 3=WARNING, 4=ERROR, 5=CRITICAL

file_url="https://swift.dkrz.de/v1/dkrz_a973e394-5f24-4f4d-8bbf-1a83bd387ccb/AQUA/framework/AQUA_testsv3.tar.gz?temp_url_sig=c8000103d54abee64bfbd00a90a1e602a68a025f&temp_url_expires=2024-07-16T12:57:27Z"
file_path="AQUA_testsv3.tar.gz"

if [ ! -f "$file_path" ]; then
    log_message INFO "Downloading file..."
    curl -o "$file_path" "$file_url"
    log_message INFO "File downloaded."
    log_message INFO "Extracting file..."
    tar -xzf "$file_path"
else
    log_message ERROR "File already exists."
fi
cp ./config/config-aqua.yaml ./config/config-aqua.yaml.bak

if [[ "$OSTYPE" == "darwin"* ]]; then
  # Mac OSX
  sed -i '' "/^machine:/c\\
machine: ci" "./config/config-aqua.yaml"
else
  # Linux
  sed -i "/^machine:/c\\machine: ci" "./config/config-aqua.yaml"
fi

#python -m pytest ./tests/test_basic.py
#mv ./config/config.yaml.bak ./config/config.yaml


