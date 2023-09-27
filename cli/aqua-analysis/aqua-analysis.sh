#!/bin/bash

# User defined variables
# ----------------------
# The following variables can be changed by the user.
# ---------------------------------------------------
model="IFS"
exp="control-1950-devcon"
source="lra-r100-monthly"

outputdir="/scratch/project_465000454/nurissom/cli_outpturdir"
aqua="/users/nurissom/AQUA"

# Set as true the diagnostics you want to run
# -------------------------------------------
atmglobalmean=false
dummy=false # dummy is a test diagnostic
ecmean=false
global_time_series=false
ocean3d=false
radiation=false
seaice=false
teleconnection=false

# End of user defined variables
# -----------------------------

# use $AQUA if defined otherwise use aqua
if [[ -z "${AQUA}" ]]; then
  echo "AQUA path is not defined, using user defined aqua in the script"
else
  echo "AQUA path is defined, using $AQUA"
  aqua=$AQUA
fi

if [ "$atmglobalmean" = true ] ; then
  echo "Running atmglobalmean"
  python $aqua/diagnostics/atmglobalmean/cli/cli_atmglobalmean.py --model $model --exp $exp --source $source --outputdir $outputdir/atmglobalmean
fi

if [ "$dummy" = true ] ; then
  echo "Running dummy"
  python $aqua/diagnostics/dummy/cli/cli_dummy.py --model $model --exp $exp --source $source --outputdir $outputdir/dummy
fi

if [ "$ecmean" = true ] ; then
  echo "Running ecmean"
  python $aqua/diagnostics/ecmean/cli/cli_ecmean.py --model $model --exp $exp --source $source --outputdir $outputdir/ecmean
fi

if [ "$global_time_series" = true ] ; then
  echo "Running global_time_series"
  python $aqua/diagnostics/global_time_series/cli/cli_global_time_series.py --model $model --exp $exp --source $source --outputdir $outputdir/global_time_series
fi

if [ "$ocean3d" = true ] ; then
  echo "Running ocean3d"
  python $aqua/diagnostics/ocean3d/cli/cli_ocean3d.py --model $model --exp $exp --source $source --outputdir $outputdir/ocean3d
fi

if [ "$radiation" = true ] ; then
  echo "Running radiation"
  python $aqua/diagnostics/radiation/cli/cli_radiation.py --model $model --exp $exp --source $source --outputdir $outputdir/radiation
fi

if [ "$seaice" = true ] ; then
  echo "Running seaice"
  python $aqua/diagnostics/seaice/cli/cli_seaice.py --model $model --exp $exp --source $source --outputdir $outputdir/seaice
fi

if [ "$teleconnection" = true ] ; then
  echo "Running teleconnection"
  python $aqua/diagnostics/teleconnection/cli/cli_teleconnection.py --model $model --exp $exp --source $source --outputdir $outputdir/teleconnection
fi

echo "Finished"