#!/usr/bin/env python
import sys
from aqua.util import load_yaml
import os
from glob import glob
import subprocess
import yaml

# expid
expid = "tco399-orca025-python"

# define folder and grib files - this has to be moved to a configuration file
tmpdir = os.path.join('/pfs/lustrep1/scratch/project_462000048/davini/gribscan', expid)
jsondir = os.path.join('/pfs/lustrep1/projappl/project_462000048/davini/gribscan-json', expid)
datadir = '/pfs/lustrep1/scratch/project_462000048/kaikeller/rundir/tco399l137/hvvy/hres/cce.lumi.craympich/lum.cce.sp/h8304.N24.T1536xt2xh1.nextgems_6h.i16r0w24.ORCA025_Z75.htco399-2870646'
gribtype = 'ICMGG'

# number of parallel procs - need a command line parser
nprocs=4

# option for the catalog entry, to be improved
if gribtype == 'ICMGG': 
    tgt_json = 'atm2d'
elif gribtype == 'ICMUA':
    tgt_json = 'atm3d'
else:
    sys.exit('Something is wrong!')

# create folders
for item in [tmpdir, jsondir]:
    print(f"Creating {item}...")
    os.makedirs(item, exist_ok=True)

# wildcard string
gribfiles = gribtype + '????+*'
# loop for symlinks
for file in glob(os.path.join(datadir, gribfiles)):
    try: 
        os.symlink(file, os.path.join(tmpdir, os.path.basename(file)))
    except FileExistsError:
        pass

# create the indices
print("Creating GRIB indices...")
cmd1 = ['gribscan-index', '-n', str(nprocs)] + glob(os.path.join(tmpdir, gribfiles))
#cmd_str = subprocess.list2cmdline(cmd)
result1 = subprocess.run(cmd1)

print("Creating JSON file...")
cmd2 = ['gribscan-build', '-o', jsondir, '--magician', 'ifs', 
        '--prefix', datadir + '/'] + glob(os.path.join(tmpdir, '*index'))
result2 = subprocess.run(cmd2)

# where is your catalog
catalogdir = '/users/padavini/AQUA/config/lumi/catalog'


# this to be expanded to automatically create the catalog entry
catalog_file = os.path.join(catalogdir, 'IFS', expid + '.yaml')
json_file = os.path.join(jsondir, tgt_json + '.json')
sourceid =  gribtype + '_' + tgt_json

# the block to create the json
myblock = {
            'driver': 'zarr',
            'args': {
                'consolidated': False,
                'urlpath': 'reference::' + os.path.join(jsondir, tgt_json + '.json')
            }
        }


# check if exist and append/create the catalog entry
if os.path.exists(catalog_file):
    mydict = load_yaml(catalog_file)
    mydict['sources'][sourceid] = myblock
else: 
    # default dict for zarr
    mydict= {'plugins': {'source': [{'module': 'intake_xarray'}, {'module': 'gribscan'}]}}
    mydict['sources'] = {}
    mydict['sources'][sourceid] = myblock

# store the new catalog object
with open(catalog_file, 'w') as yaml_file:
    yaml.dump(mydict, yaml_file, sort_keys=True)

