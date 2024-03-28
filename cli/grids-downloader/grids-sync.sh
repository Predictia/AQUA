#!/bin/bash
# This script synchronizes the grids from the Levante server to the LUMI server
# It may be generalized to synchronize grids between any two servers
# and for other folders (e.g. LRA created from an high-res experiment
# available only on one cluster)

# Usage: ./grids-sync.sh [levante_to_lumi | lumi_to_levante]

# Set the path to the grids on the servers
LEVANTE_GRID_PATH="/work/bb1153/b382075/aqua/grids"
LUMI_GRID_PATH="/pfs/lustrep3/projappl/project_465000454/data/AQUA/grids"

# Set the paths for the grids on levante and lumi
LEVANTE_SSH="user@levante:$LEVANTE_GRID_PATH"
LUMI_SSH="user@lumi:$LUMI_GRID_PATH"

# Function to synchronize grids from levante to lumi
sync_levante_to_lumi() {
    echo "Syncing grids from levante to lumi..."
    rsync -avz --progress -e ssh $LEVANTE_SSH/ $LUMI_SSH/
}

# Function to synchronize grids from lumi to levante
sync_lumi_to_levante() {
    echo "Syncing grids from lumi to levante..."
    rsync -avz --progress -e ssh $LUMI_SSH/ $LEVANTE_SSH/
}

# Main script
if [ "$1" == "levante_to_lumi" ]; then
    sync_to_lumi
elif [ "$1" == "lumi_to_levante" ]; then
    sync_to_levante
else
    echo "Usage: $0 [levante_to_lumi | lumi_to_levante]"
    exit 1
fi

echo "Done."
