#!/bin/bash
script_dir=$(dirname "${BASH_SOURCE[0]}")
source $script_dir/cli/util/logger.sh
setup_log_level 2 # 1=DEBUG, 2=INFO, 3=WARNING, 4=ERROR, 5=CRITICAL

file_url="https://swift.dkrz.de/v1/dkrz_a973e394-5f24-4f4d-8bbf-1a83bd387ccb/AQUA/framework/AQUA_testsv2.tar.gz?temp_url_sig=129efdbed5a4f57e8437083aca893236db7377c8&temp_url_expires=2025-10-22T17:37:39Z"
file_path="AQUA_testsv2.tar.gz"

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


