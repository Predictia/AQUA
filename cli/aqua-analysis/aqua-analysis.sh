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

machine="levante" # will change the aqua config file

# When available, use the following variables to set the loglevel
loglevel="WARNING" # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Set as true the diagnostics you want to run
# -------------------------------------------
atmglobalmean=true
dummy=false # dummy is a test diagnostic
ecmean=true
# ---------------------------------------
# Command line extra arguments for ecmean
# -c --config ecmean config file
# -i --interface custom interface file
# -l --loglevel loglevel
# ---------------------------------------
global_time_series=true
# global time series additional flags
# ---------------------------------------------------------------
# --loglevel, -l (can be DEBUG, INFO, WARNING, ERROR, CRITICAL)
# ---------------------------------------------------------------
ocean3d=true
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

# set the correct machine in the config file
if [[ "$OSTYPE" == "darwin"* ]]; then
  # Mac OSX
  sed -i '' "/^machine:/c\\
machine: $machine" "$aqua/config/config-aqua.yaml"
else
  # Linux
  sed -i "/^machine:/c\\machine: $machine" "$aqua/config/config-aqua.yaml"
fi

# print the output directory
echo "Output directory: $outputdir"

if [ "$atmglobalmean" = true ] ; then
  cd $aqua/diagnostics/atmglobalmean/cli
  python cli_atm_mean_bias.py $args_atm --outputdir $outputdir/atmglobalmean
  cd $aqua/cli/aqua-analysis
fi

if [ "$dummy" = true ] ; then
  echo "Running dummy"
  python $aqua/diagnostics/dummy/cli/cli_dummy.py $args --outputdir $outputdir/dummy
fi

if [ "$ecmean" = true ] ; then
  scriptpy="$aqua/diagnostics/ecmean/cli/ecmean_cli.py"
  python $scriptpy $args -o $outputdir/ecmean -l $loglevel
fi

if [ "$global_time_series" = true ] ; then
  echo "Running global_time_series"

  filepy="$aqua/diagnostics/global_time_series/cli/single_analysis/cli_global_time_series.py"
  conf_atm="$aqua/diagnostics/global_time_series/cli/single_analysis/config_time_series_atm.yaml"
  conf_oce="$aqua/diagnostics/global_time_series/cli/single_analysis/config_time_series_oce.yaml"

  python $filepy $args_atm --outputdir $outputdir/global_time_series --config $conf_atm -l $loglevel
  python $filepy $args_oce --outputdir $outputdir/global_time_series --config $conf_oce -l $loglevel
fi

if [ "$ocean3d" = true ] ; then
  # Moving to ocean3d directory to run the ocean3d_cli.py script
  cd $aqua/diagnostics/ocean3d/cli
  python $aqua/diagnostics/ocean3d/cli/ocean3d_cli.py $args_oce --outputdir $outputdir/ocean3d

  # Moving back to aqua-analysis directory
  cd $aqua/cli/aqua-analysis

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

  python cli_teleconnections.py $args_atm --outputdir $outputdir/teleconnections --config cli_config_atm.yaml --obs -l $loglevel
  python cli_teleconnections.py $args_oce --outputdir $outputdir/teleconnections --config cli_config_oce.yaml --obs -l $loglevel

  # Move back to the aqua-analysis directory
  cd $aqua/cli/aqua-analysis

  echo "Finished teleconnections"
fi

echo "Finished"