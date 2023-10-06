#!/bin/bash

# User defined variables
# ----------------------
# The following variables can be changed by the user.
# ---------------------------------------------------
model_atm="IFS"
model_oce="NEMO"
exp="control-1950-devcon"
source="lra-r100-monthly"

outputdir="/scratch/project_465000454/nurissom/cli_outpturdir"
aqua="/users/nurissom/AQUA"

# When available, use the following variables to set the loglevel
loglevel="WARNING" # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Set as true the diagnostics you want to run
# -------------------------------------------
run_dummy=true # dummy is a diagnostic that checks if the setup is correct
run_atmglobalmean=false
run_ecmean=false
run_global_time_series=false
run_ocean3d=false
run_radiation=false
run_seaice=false
run_teleconnection=false

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

if [ "$run_dummy" = true ] ; then
  echo "Running setup checker"
  python $aqua/diagnostics/dummy/cli/cli_dummy.py $args --outputdir $outputdir/dummy
fi

if [ "$run_atmglobalmean" = true ] ; then
  echo "Running atmglobalmean"
  python $aqua/diagnostics/atmglobalmean/cli/cli_atmglobalmean.py $args_atm --outputdir $outputdir/atmglobalmean
fi

if [ "$run_ecmean" = true ] ; then
  echo "Running ecmean"
  python $aqua/diagnostics/ecmean/cli/cli_ecmean.py $args --outputdir $outputdir/ecmean
fi

if [ "$run_global_time_series" = true ] ; then
  echo "Running global_time_series"
  python $aqua/diagnostics/global_time_series/cli/cli_global_time_series.py $args_atm --outputdir $outputdir/global_time_series --config $aqua/diagnostics/global_time_series/cli/config_atm.yaml
  python $aqua/diagnostics/global_time_series/cli/cli_global_time_series.py $args_oce --outputdir $outputdir/global_time_series --config $aqua/diagnostics/global_time_series/cli/config_oce.yaml
fi

if [ "$run_ocean3d" = true ] ; then
  echo "Running ocean3d"
  python $aqua/diagnostics/ocean3d/cli/cli_ocean3d.py $args_oce --outputdir $outputdir/ocean3d
fi

if [ "$run_radiation" = true ] ; then
  echo "Running radiation"
  python $aqua/diagnostics/radiation/cli/cli_radiation.py $args_atm --outputdir $outputdir/radiation
fi

if [ "$run_seaice" = true ] ; then
  echo "Running seaice"
  python $aqua/diagnostics/seaice/cli/cli_seaice.py $args_oce --outputdir $outputdir/seaice
fi

if [ "$run_teleconnection" = true ] ; then
  echo "Running teleconnection"
  python $aqua/diagnostics/teleconnection/cli/cli_teleconnection.py $args_atm --outputdir $outputdir/teleconnection --config $aqua/diagnostics/teleconnection/cli/config_atm.yaml
  python $aqua/diagnostics/teleconnection/cli/cli_teleconnection.py $args_oce --outputdir $outputdir/teleconnection --config $aqua/diagnostics/teleconnection/cli/config_oce.yaml
fi

echo "Finished"