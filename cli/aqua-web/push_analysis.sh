#!/bin/bash

# CLI tool to push analysis results to aqua-web

collect_figures() {
    # This assumes that we are inside the aqua-web repository

    log_message INFO "Collecting figures for $2"

    indir="$1/$2"
    dstdir="./content/pdf/$2"

    # erase content and copy all files to content
    git rm -r $dstdir
    mkdir -p $dstdir

    find $indir -name "*.pdf"  -exec cp {} $dstdir/ \;

    # Remove dates from EC-mean filenames
    for file in $dstdir/PI4*_????_????.pdf
    do
        mv -- "$file" "${file%_*_*}.pdf"
    done

    echo $(date) > $dstdir/last_update.txt

    git add $dstdir
}

convert_pdf_to_png() {
    # This assumes that we are inside the aqua-web repository

    log_message INFO "Converting PDFs to PNGs for $1"

    dstdir="./content/png/$1"

    git rm -r $dstdir
    mkdir -p $dstdir
    
    IFS='/' read -r catalog model experiment <<< "$1"
    ./pdf_to_png.sh "$catalog" "$model" "$experiment"

    git add $dstdir
}

# define the aqua installation path
AQUA=$(aqua --path)/..

if [ ! -d $AQUA ]; then
    echo -e "\033[0;31mError: AQUA is not installed."
    echo -e "\x1b[38;2;255;165;0mPlease install AQUA with aqua install command"
    exit 1  # Exit with status 1 to indicate an error
fi

source "$AQUA/cli/util/logger.sh"
log_message DEBUG "Sourcing logger.sh from: $AQUA/cli/util/logger.sh"
setup_log_level 2 # 1=DEBUG, 2=INFO, 3=WARNING, 4=ERROR, 5=CRITICAL


if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 <indir> <modelexp>"
    echo
    echo "<indir>:    the directory containing the output, e.g. output"
    echo "<modelexp>: the subfolder to push, e.g IFS-NEMO/historical-1990."
    echo "            This can also be a text file containing a list of models-experiments."
    exit 1
fi

# setup a fresh local aqua-web copy
log_message INFO "Clone aqua-web"

git clone git@github.com:DestinE-Climate-DT/aqua-web.git aqua-web$$

# erase content and copy all files to content
log_message INFO "Collect and update figures in content/pdf"
cd aqua-web$$

# Check if the second argument is an actual file and use it as a list of experiments
if [ -f "$2" ]; then
    log_message INFO "Reading list of experiments from $2"

    # Loop over each line in the file
    while IFS= read -r line; do
        # Skip empty lines and lines starting with #
        if [[ -z "$line" || "$line" == "#"* ]]; then
            continue
        fi

        # Extract model, experiment, and source from the line
        catalog=$(echo "$line" | awk '{print $1}')
        model=$(echo "$line" | awk '{print $2}')
        experiment=$(echo "$line" | awk '{print $3}')

        collect_figures "$1" "$catalog/$model/$experiment"
        convert_pdf_to_png "$catalog/$model/$experiment"
    done < "$2"
else  # Otherwise, use the second argument as the experiment folder
    collect_figures "$1" "$2"
    convert_pdf_to_png "$2"
fi

# commit and push
log_message INFO "Commit and push"

commit_message="update pdfs $(date)"
git commit -m "$commit_message"
git push

## cleanup
log_message INFO "Clean up"
cd ..
rm -rf aqua-web$$
#
log_message INFO "Pushed new figures to aqua-web"
