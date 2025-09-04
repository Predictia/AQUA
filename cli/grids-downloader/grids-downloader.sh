#!/bin/bash
set -e

# define the aqua installation path
AQUA=$(aqua --path)/../..

echo $AQUA
if [ ! -d $AQUA ]; then
    echo -e "\033[0;31mError: AQUA is not installed."
    echo -e "\x1b[38;2;255;165;0mPlease install AQUA with aqua install command"
    exit 1
fi

source "$AQUA/cli/util/logger.sh"
log_message DEBUG "Sourcing logger.sh from: $AQUA/cli/util/logger.sh"
setup_log_level 2 # 1=DEBUG, 2=INFO, 3=WARNING, 4=ERROR, 5=CRITICAL

usage() {
   echo "Usage: $0 [-o outputdir] dataset-name|all"
   echo
   echo "Examples:"
   echo "   $0 -o /path/to/grids ERA5"
   echo "   $0 -o /path/to/grids all"
   echo
}

# Default outputdir (can be overridden with -o)
outputdir="./grids"
# Legacy paths:
# for LUMI
# outputdir="/appl/local/climatedt/data/AQUA/grids"
# for Levante
# outputdir="/work/bb1153/b382075/aqua/grids"
# for Leonardo
# outputdir="/leonardo_work/DestE_330_24/AQUA/grids"
# for HPC202
# outputdir="/ec/res4/hpcperm/ccjh/aqua_data/grids"

# Parse options
while [[ $# -gt 0 ]]; do
  case $1 in
    -o|--output)
      outputdir="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      model="$1"
      shift
      ;;
  esac
done

# Check if model is given
if [ -z "$model" ]; then
    usage
    exit 1
fi

if [[ $model == "all" ]]; then
	models=("EC-EARTH4" "EN4" "ERA5" "FESOM" "HealPix" "ICON" "IFS" "lonlat" "NEMO" "OSI-SAF" "PSC" "WAGHC" "WOA18")
else
	models=( "$model" )
fi

log_message INFO "Creating output directory $outputdir"
mkdir -p "$outputdir"

# Download grids
for model in "${models[@]}"; do
    log_message INFO "Downloading grid for $model"

    # links (unchanged)
    if [ "$model" == "EC-EARTH4" ]; then
        path="https://swift.dkrz.de/.../EC-EARTH4.tar.gz"
    fi
    # (other links here...)

    wget -O "$outputdir/$model.tar.gz" "$path"

    log_message INFO "Unpacking grid for $model"
    tar -xzf "$outputdir/$model.tar.gz" -C "$outputdir"

    log_message INFO "Removing tar.gz file for $model"
    rm -f "$outputdir/$model.tar.gz"
done

log_message INFO "Download complete"