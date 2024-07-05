#!/bin/bash
# This script runs the diagnostics for the AQUA project.

# Trap Ctrl-C to clean up and kill the entire process group
trap 'kill 0' SIGINT

# define the aqua installation path
AQUA=$(aqua --path)/..

aqua_config=$AQUA/cli/aqua-analysis/config.aqua-analysis.yaml

parse_yaml() {
   echo $(eval echo $(python $AQUA/cli/util/parse_yaml.py $1 $aqua_config))
}

if [ ! -d $AQUA ]; then
    echo -e "\033[0;31mError: AQUA is not installed."
    echo -e "\x1b[38;2;255;165;0mPlease install AQUA with aqua install command"
    exit 1  # Exit with status 1 to indicate an error
fi

source "$AQUA/cli/util/logger.sh"
log_message DEBUG "Sourcing logger.sh from: $AQUA/cli/util/logger.sh"

setup_log_level 2 # 1=DEBUG, 2=INFO, 3=WARNING, 4=ERROR, 5=CRITICAL

outputdir=$(parse_yaml .job.outputdir)
model=$(parse_yaml .job.model)
exp=$(parse_yaml .job.exp)
source=$(parse_yaml .job.source)
catalog=$(parse_yaml .job.catalog)  # Ignored at the moment

loglevel=$(parse_yaml .job.loglevel)
max_threads=$(parse_yaml .job.max_threads)  # Set to the desired maximum number of threads, or leave it as 0 for no limit

script_path_base=$(parse_yaml .job.script_path_base)  # Set the base path for the diagnostics scripts
if [ -z "$script_path_base" ]; then
  script_path_base="${AQUA}/diagnostics"
fi

# Define the arrays diagnostics, add more if needed or available
all_diagnostics=($(parse_yaml .diagnostics.run))

log_message DEBUG "Running diagnostics: ${all_diagnostics[@]}"

run_dummy=$(parse_yaml .job.run_dummy)

# Command line arguments

# Define accepted log levels
accepted_loglevels=("info" "debug" "error" "warning" "critical" "INFO" "DEBUG" "ERROR" "WARNING" "CRITICAL")
distributed=0

# Parse command-line options
while [[ $# -gt 0 ]]; do
  case "$1" in
    -a|--model_atm)
      model="$2"
      shift 2
      ;;
    -o|--model_oce)
      model="$2"
      shift 2
      ;;
    -e|--exp)
      exp="$2"
      shift 2
      ;;
    -s|--source)
      source="$2"
      shift 2
      ;;
    -d|--outputdir)
      outputdir="$2"
      shift 2
      ;;
    -c|--catalog)
      catalog="$2"
      shift 2
      ;;
    -p|--parallel)
      distributed=1
      shift 1
      ;;
    -t|--threads)
      max_threads="$2"
      shift 2
      ;;
    -l|--loglevel)
      # Check if the specified log level is in the accepted list
      if [[ " ${accepted_loglevels[@]} " =~ " $2 " ]]; then
        loglevel="$2"
      else
        log_message ERROR "Invalid log level. Accepted values are: ${accepted_loglevels[@]}"
        # Setting loglevel to WARNING
        loglevel="WARNING"
      fi
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

log_message INFO "Setting loglevel to $loglevel"
log_message INFO "Model: $model"
log_message INFO "Experiment: $exp"
log_message INFO "Source: $source"
log_message INFO "Catalog: $catalog"
log_message INFO "Output directory: $outputdir"

# Define an associative array for atmospheric extra arguments
declare -A extra_args
declare -A script_path
declare -A outname

# Set default value for all keys in atmospheric extra arguments
for diagnostic in ${all_diagnostics[@]}; do
  extra_args["$diagnostic"]="--model $model --exp $exp --source $source"
  outname["$diagnostic"]=$diagnostic
done
# ECmean has not-standard arguments
extra_args["ecmean"]="--model_atm $model --model_oce $model --exp $exp --source $source"

OUTPUT="$outputdir/$model/$exp"

# Iterate over all diagnostics and set the default script path and extra arguments
for diagnostic in ${all_diagnostics[@]}; do
  script_path["$diagnostic"]="$diagnostic/cli/cli_$diagnostic.py"

  script=$(parse_yaml .diagnostics.$diagnostic.script_path)
  if [ ! -z "$script" ]; then
    script_path["$diagnostic"]="$script"
  fi

  extra=$(parse_yaml .diagnostics.$diagnostic.extra)
  if [ ! -z "$extra" ]; then
    extra_args["$diagnostic"]="${extra_args["$diagnostic"]} $extra"
  fi

  out=$(parse_yaml .diagnostics.$diagnostic.outname)
  if [ ! -z "$out" ]; then
    outname["$diagnostic"]="$out"
  fi

  if [ $distributed -eq 1 ]; then
    nworkers=$(parse_yaml .diagnostics.$diagnostic.nworkers)
    if [ ! -z "$nworkers" ]; then
      extra_args["$diagnostic"]="${extra_args["$diagnostic"]} --nworkers $nworkers"
    fi
  fi
done

# Create output directory if it does not exist
log_message INFO "Creating output directory $OUTPUT"
mkdir -p "$OUTPUT"

cd $AQUA
if [ "$run_dummy" = true ] ; then
  log_message INFO "Running setup checker"
  scriptpy="${AQUA}/diagnostics/dummy/cli/cli_dummy.py"
  python $scriptpy $args -l $loglevel > "$OUTPUT/setup_checker.log" 2>&1
  
  # Store the error code of the dummy script
  dummy_error=$?

  # exit if dummy fails in finding both atmospheric and oceanic model
  if [ $dummy_error -ne 0 ]; then
    if [ $dummy_error -eq 1 ]; then # if error code is 1, then the setup checker failed
      log_message CRITICAL "Setup checker failed, exiting"
      exit 1
    fi
    # if error code is 2 or 3, then the setup checker
    # passed but there are some warnings
    if [ $dummy_error -eq 2 ]; then
      log_message ERROR "Atmospheric model is not found, it will be skipped"
    fi
    if [ $dummy_error -eq 3 ]; then
      log_message ERROR "Oceanic model is not found, it will be skipped"
    fi
  fi
  log_message INFO "Finished setup checker"
fi

thread_count=0
# Run diagnostics in parallel
for diagnostic in "${all_diagnostics[@]}"; do
  log_message INFO "Running $diagnostic"
  log_message DEBUG "Script path: ${script_path[$diagnostic]}"
  log_message DEBUG "Arguments:  ${extra_args[$diagnostic]} -l $loglevel --outputdir $OUTPUT/$diagnostic"

  python "$script_path_base/${script_path[$diagnostic]}" ${extra_args[$diagnostic]} \
  -l $loglevel --outputdir $OUTPUT/${outname[$diagnostic]} > "$OUTPUT/$diagnostic.log" 2>&1 &
 
  if [ $max_threads -gt 0 ]; then
    ((thread_count++))
    # Check if the maximum number of threads has been reached
    if [ $thread_count -ge $max_threads ]; then
      wait   # Wait for the background processes to finish
      thread_count=0  # Reset the thread count
    fi
  fi
done
wait  # Wait for all background processes to finish
log_message INFO "Finished all diagnostics"
