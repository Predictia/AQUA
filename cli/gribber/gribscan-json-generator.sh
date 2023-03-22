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
expid=tco399-orca025-kai

# define folder and grib files
tmpdir=/pfs/lustrep1/scratch/project_462000048/davini/gribscan/$expid
jsondir=/pfs/lustrep1/projappl/project_462000048/davini/gribscan-json/$expid
datadir=/pfs/lustrep1/scratch/project_462000048/kaikeller/rundir/tco399l137/hvvy/hres/cce.lumi.craympich/lum.cce.sp/h8304.N24.T1536xt2xh1.nextgems_6h.i16r0w24.ORCA025_Z75.htco399-2870646
#datadir=/users/padavini/scratch/testrun
gribfiles='ICMGG????+*'

# number of parallel procs
nprocs=4

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
gribscan-build -o $jsondir --magician ifs --prefix ${datadir}/ *.index

# clean tmpdir
echo "Cleaning..."
rm $tmpdir/$gribfiles
#rm $tmpdir/*.index
rmdir $tmpdir

echo "Good job my friend, have yourself an icecream!"