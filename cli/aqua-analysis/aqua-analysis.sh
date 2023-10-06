#!/bin/bash

# User defined variables
# ----------------------
# The following variables can be changed by the user.
# ---------------------------------------------------
model_atm="IFS"
model_oce="FESOM"
exp="tco2559-ng5-cycle3"
source="lra-r100-monthly"

# LUMI
# outputdir="/scratch/project_465000454/nurissom/cli_outpturdir"
# aqua="/users/nurissom/AQUA"

# LEVANTE
outputdir="/scratch/b/b382289/cli_test"
aqua="/home/b/b382289/AQUA"

# Set as true the diagnostics you want to run
# -------------------------------------------
atmglobalmean=false
dummy=false # dummy is a test diagnostic
ecmean=false
global_time_series=false
ocean3d=false
radiation=false
seaice=false
teleconnections=true
# teleconnections additional flags
# ---------------------------------------------------------------
# --loglevel, -l (can be DEBUG, INFO, WARNING, ERROR, CRITICAL)
# --dry, -d (dry run, if set it will run without producing plots)
# --obs (if set it will run the teleconnections also for ERA5)
# ---------------------------------------------------------------

# End of user defined variables
# -----------------------------

args_atm="--model $model_atm --exp $exp --source $source"
args_oce="--model $model_oce --exp $exp --source $source"
args="--model_atm $model_atm --model_oce $model_oce --exp $exp --source $source"

# use $AQUA if defined otherwise use aqua
if [[ -z "${AQUA}" ]]; then
  echo "AQUA path is not defined, using user defined aqua in the script"
else
  echo "AQUA path is defined, using $AQUA"
  aqua=$AQUA
fi

# print the output directory
echo "Output directory: $outputdir"

if [ "$atmglobalmean" = true ] ; then
  echo "Running atmglobalmean"
  python $aqua/diagnostics/atmglobalmean/cli/cli_atmglobalmean.py $args_atm --outputdir $outputdir/atmglobalmean
fi

if [ "$dummy" = true ] ; then
  echo "Running dummy"
  python $aqua/diagnostics/dummy/cli/cli_dummy.py $args --outputdir $outputdir/dummy
fi

if [ "$ecmean" = true ] ; then
  echo "Running ecmean"
  python $aqua/diagnostics/ecmean/cli/cli_ecmean.py $args --outputdir $outputdir/ecmean
fi

if [ "$global_time_series" = true ] ; then
  echo "Running global_time_series"
  python $aqua/diagnostics/global_time_series/cli/cli_global_time_series.py $args_atm --outputdir $outputdir/global_time_series --config $aqua/diagnostics/global_time_series/cli/config_atm.yaml
  python $aqua/diagnostics/global_time_series/cli/cli_global_time_series.py $args_oce --outputdir $outputdir/global_time_series --config $aqua/diagnostics/global_time_series/cli/config_oce.yaml
fi

if [ "$ocean3d" = true ] ; then
  echo "Running ocean3d"
  python $aqua/diagnostics/ocean3d/cli/cli_ocean3d.py $args_oce --outputdir $outputdir/ocean3d
fi

if [ "$radiation" = true ] ; then
  echo "Running radiation"
  python $aqua/diagnostics/radiation/cli/cli_radiation.py $args_atm --outputdir $outputdir/radiation
fi

if [ "$seaice" = true ] ; then
  echo "Running seaice"
  python $aqua/diagnostics/seaice/cli/cli_seaice.py $args_oce --outputdir $outputdir/seaice
fi

if [ "$teleconnections" = true ] ; then
  # Move to the teleconnection CLI directory
  cd $aqua/diagnostics/teleconnections/cli/single_analysis

  python cli_teleconnections.py $args_atm --outputdir $outputdir/teleconnections --config cli_config_atm.yaml --obs
  python cli_teleconnections.py $args_oce --outputdir $outputdir/teleconnections --config cli_config_oce.yaml --obs

  # Move back to the aqua-analysis directory
  cd $aqua/cli/aqua-analysis

  echo "Finished teleconnections"
fi

echo "Finished"