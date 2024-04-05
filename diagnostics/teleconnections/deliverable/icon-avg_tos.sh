#!/bin/bash
# Check if AQUA is set and the file exists
if [[ -z "$AQUA" ]]; then
    echo -e "\033[0;31mError: The AQUA environment variable is not defined."
    echo -e "\x1b[38;2;255;165;0mPlease define the AQUA environment variable with the path to your 'AQUA' directory."
    echo -e "For example: export AQUA=/path/to/aqua\033[0m"
    exit 1  # Exit with status 1 to indicate an error
else
    source "${AQUA}/cli/util/logger.sh"
    log_message INFO "Sourcing logger.sh from: ${AQUA}/cli/util/logger.sh"
    # Your subsequent commands here
fi
setup_log_level 2 # 1=DEBUG, 2=INFO, 3=WARNING, 4=ERROR, 5=CRITICAL

# This script will create the avg_tos files from the avg_thetao files,
# selecting the first level of the temperature data.
# If you need, add here the module load cdo command.

model="ICON"
exp="historical-1990"

log_message INFO "Creating avg_tos files from avg_thetao files for ${model} ${exp} LRA."

LRA_folder="/projappl/project_465000454/data/AQUA/LRA"
source_folder="${LRA_folder}/${model}/${exp}/r100/monthly"

log_message INFO "Source folder: ${source_folder}"

# moving to the source folder
cd "${source_folder}"

for file in avg_thetao*.nc; do
    # Extract the filename without the extension
    filename=$(basename -- "$file")

    log_message INFO "Processing file: ${filename}"

    # Cut 'avg_thetao' from the beginning of each filename
    filename_novar="${filename#avg_thetao}"

    # Add 'avg_tos' to the beginning of each filename
    tmp_filename="avg_tos_tmp.nc"
    new_filename="avg_tos${filename_novar}"

    log_message INFO "New filename: ${new_filename}"

    cdo -setname,avg_tos -sellevel,1 "$file" "${tmp_filename}"
    cdo -setzaxis,surface "${tmp_filename}" "${new_filename}"
    rm -rf "${tmp_filename}"
done

# Moving back to the original directory
cd -
