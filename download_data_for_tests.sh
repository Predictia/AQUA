#!/bin/bash
script_dir=$(dirname "${BASH_SOURCE[0]}")
source $script_dir/cli/util/logger.sh
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


