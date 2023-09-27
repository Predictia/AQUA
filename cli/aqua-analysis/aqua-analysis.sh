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
atmglobalmean=true
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
  python $aqua/diagnostics/atmglobalmean/cli/cli_atmglobalmena --model $model --exp $exp --source $source --outputdir $outputdir
fi