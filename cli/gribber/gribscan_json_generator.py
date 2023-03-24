import yaml
import os
import subprocess
from aqua.util import load_yaml
from glob import glob

class Gribber():
    """
    Class to generate a JSON file from a GRIB file.
    """

    def __init__(self,
                 model='IFS',exp='tco1279',source='ICMGG_atm2d',
                 nprocs=4,
                 dir = {'datadir': '/scratch/b/b382289/tco1279-orca025/nemo_deep/ICMGGc2',
                        'tmpdir': '/scratch/b/b382289/gribscan',
                        'jsondir': '/work/bb1153/b382289/gribscan-json',
                        'catalogdir': '/work/bb1153/b382289/AQUA/config/levante/catalog'},
                 verbose=True
                ) -> None:
        """
        Initialize class.
        """
        self.verbose = verbose
        if self.verbose:
            self.help()

        self.model = model
        self.exp = exp
        self.source = source
        self.nprocs = nprocs
        self.dir = dir

        # Create folders from dir dictionary
        self.datadir = self.dir['datadir']
        self.tmpdir = os.path.join(self.dir['tmpdir'], self.exp)
        self.jsondir = os.path.join(self.dir['jsondir'], self.exp)
        self.catalogdir = self.dir['catalogdir']

        self._create_folders()
        
        # Get gribtype and tgt_json from source
        self.gribtype = self.source.split('_')[0]
        self.tgt_json = self.source.split('_')[1]

        if self.verbose:
            print(self.gribtype)
            print(self.tgt_json)
        
        # Get gribfiles wildcard from gribtype
        self.gribfiles = self.gribtype + '????+*'
        if self.verbose:
            print(self.gribfiles)

        # Create symlinks to GRIB files
        self._create_symlinks()

        # Create indices for GRIB files
        self.indices = None
        self._create_indices()
        if self.verbose:
            print(self.indices)

    def _create_folders(self):
        """
        Create folders.
        """
        for item in [self.tmpdir, self.jsondir]:
            if self.verbose:
                print(f"Creating {item}...")
            os.makedirs(item, exist_ok=True)

    def _create_symlinks(self):
        """
        Create symlinks to GRIB files.
        """
        if self.verbose:
            print("Creating symlinks...")
            print("Searching in...")
            print(os.path.join(self.datadir, self.gribfiles))
        try:
            for file in glob(os.path.join(self.datadir, self.gribfiles)):
                try: 
                    os.symlink(file, os.path.join(self.tmpdir, os.path.basename(file)))
                except FileExistsError:
                    print(f"File {file} already exists in {self.tmpdir}")
        except FileNotFoundError:
            print(f"Directory {self.datadir} not found.")
    
    def _create_indices(self):
        """
        Create indices for GRIB files.
        """
        if self.verbose:
            print("Creating GRIB indices...")
        # to be improved without using subprocess
        cmd = ['gribscan-index', '-n', str(self.nprocs)] + glob(os.path.join(self.tmpdir, self.gribfiles))
        self.indices = subprocess.run(cmd)

    def _create_json(self):
        if self.verbose:
            print("Creating JSON file...")
        cmd = ['gribscan-build', '-o', self.jsondir, '--magician', 'ifs', 
            '--prefix', self.datadir + '/'] + glob(os.path.join(self.tmpdir, '*index'))
        json = subprocess.run(cmd)
    
    def _create_catalog(self):
        """
        Create or update catalog file
        """
        catalogfile = os.path.join(self.catalogdir,self.model,self.exp+'.yml')
        if self.verbose:
            print(f"Catalog file: {catalogfile}")
        
        # Generate the block to be added to the catalog file
        myblock = {
            'driver': 'zarr',
            'args': {
                'consolidated': False,
                'urlpath': 'reference::' + os.path.join(self.jsondir,self.tgt_json+'.json')
            }
        }
        if self.verbose:
            print("Block to be added to catalog file:")
            print(myblock)
        
        # Check if catalog file exists
        if os.path.exists(catalogfile):
            mydict = load_yaml(catalogfile)
            mydict['sources'][self.source] = myblock
        else:
            # default dict for zarr
            mydict= {'plugins': {'source': [{'module': 'intake_xarray'}, {'module': 'gribscan'}]}}
            mydict['sources'] = {}
            mydict['sources'][self.source] = myblock
        
        # Write catalog file
        with open(catalogfile, 'w') as f:
            yaml.dump(mydict, f, sort_keys=True)
    
    # def _create_json(self):
    #     """
    #     Create JSON file.
    #     """
    #     print("Creating JSON file...")
    #     cmd2 = ['gribscan-build', '-o', self.jsondir, '--magician', 'ifs', 
    #             '--prefix', datadir + '/'] + glob(os.path.join(self.tmpdir, '*index'))
    #     result2 = subprocess.run(cmd2)
    
    # def _create_catalog(self):
    #     """
    #     Create catalog file.
    #     """
    #     # Check if catalog file exists
    #     if os.path.exists(self.catalogfile):
    #         mydict = load_yaml(self.catalogfile)
    #         mydict['sources'][sourceid] = myblock
    #     else: 
    #         # Default dict for zarr
    #         mydict = {
    #             'sources': {
    #                 sourceid: myblock
    #             }
    #         }
        
    #     # Write catalog file
    #     with open(self.catalogfile, 'w') as f:
    #         yaml.dump(mydict, f, default_flow_style=False)

    def help(self):
        """
        Print help message.
        """
        print("Gribber class:")
        print("  model: model name (default: IFS)")
        print("  exp: experiment name (default: tco1279)")
        print("  source: source name (default: ICMGG_atm2d)")
        print("  nprocs: number of processors (default: 4)")
        print("  verbose: print help message (default: True)")
        print("  dir: dictionary with directories (default: see below)")
        print("  datadir: data directory (default: /scratch/b/b382289/tco1279-orca025/nemo_deep/ICMGGc2)")
        print("  tmpdir: temporary directory (default: /scratch/b/b382289/gribscan)")
        print("  jsondir: JSON directory (default: /work/bb1153/b382289/gribscan-json)")
        print("  catalogdir: catalog directory (default: /work/bb1153/b382289/AQUA/config/levante/catalog)")
        print("  griblist: dictionary with GRIB files (default: see gribber.yml)")
        print("  tgt_json: target JSON file (default: see gribber.yml)")
        print("  catalogfile: catalog file (default: see gribber.yml)")
        print("  jsonfile: JSON file (default: see gribber.yml)")