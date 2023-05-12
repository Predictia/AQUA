#!/bin/bash

file_url="https://link/to/your/file/"
file_path="filename.tar.gz"

if [ ! -f "$file_path" ]; then
    echo "Downloading file..."
    curl -o "$file_path" "$file_url"
    echo "File downloaded."
    echo "Extracting file..."
    tar -xzf "$file_path"
else
    echo "File already exists."
fi

cp ./config/config.yaml ./config/config.yaml.bak
sed -i "/^machine:/c\\machine: ci" "./config/config.yaml"