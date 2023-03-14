# This script tries to create a json entry using gribscan to access 
# IFS files from catalog using a zarr interface

#!/bin/bash
set -e

# find mamba/conda (to be refined)
whereconda=$(which mamba | rev | cut -f 3-10 -d"/" | rev)
source $whereconda/etc/profile.d/conda.sh

# activate AQUA environment
conda activate aqua

# expid
expid=pippo

# define folder and grib files
tmpdir=/home/b/b382076/scratch/gribscan/$expid
jsondir=/home/b/b382076/work/gribscan-json/$expid
datadir=/home/b/b382076/smmregrid/tests/data
gribfiles='*.grb'

# number of parallel procs
nprocs=1

# create folders
mkdir -p $jsondir $tmpdir

# create file links to avoid messing with original data
echo "Linking files..."
for file in $(ls $datadir/$gribfiles) ; do
    ln -sf $file $tmpdir/
done

# creating the indices
echo "Creating GRIB indices..."
cd $tmpdir
gribscan-index $tmpdir/$gribfiles -n $nprocs

# running the json creation
echo "Building JSON file..."
gribscan-build -o $jsondir --magician ifs --prefix $datadir *.index

# clean tmpdir
echo "Cleaning..."
rm $tmpdir/$gribfiles
rm $tmpdir/*.index
rmdir $tmpdir

echo "Good job my friend, have yourself an icecream!"