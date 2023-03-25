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
                 model='IFS',exp='tco1279-orca025',source='ICMGG_atm2d',
                 nprocs=4,
                 dir = {'datadir': '/scratch/b/b382289/tco1279-orca025/nemo_deep/ICMGGc2',
                        'tmpdir': '/scratch/b/b382289/gribscan',
                        'jsondir': '/work/bb1153/b382289/gribscan-json',
                        'catalogdir': '/work/bb1153/b382289/AQUA/config/levante/catalog'},
                 verbose=False,
                 replace=False
                ) -> None:
        """
        Initialize class.

        Parameters
        ----------
        model : str, optional
            Model name, by default 'IFS'
        exp : str, optional
            Experiment name, by default 'tco1279-orca025'
        source : str, optional
            Source name, by default 'ICMGG_atm2d'
        nprocs : int, optional
            Number of processors, by default 4
        dir : dict, optional
            Dictionary with directories, by default 
            {'datadir': '/scratch/b/b382289/tco1279-orca025/nemo_deep/ICMGGc2',
             'tmpdir': '/scratch/b/b382289/gribscan',
             'jsondir': '/work/bb1153/b382289/gribscan-json',
             'catalogdir': '/work/bb1153/b382289/AQUA/config/levante/catalog'}
        verbose : bool, optional
            Verbose mode, by default False
        replace : bool, optional
            Replace JSON file and indices if they exist, by default False
        
        Methods
        -------
        create_entry()
            Create catalog entry.
        
        _create_folders()
            Create folders.
        
        _create_symlinks()
            Create symlinks to GRIB files.
        
        _create_indices()
            Create indices for GRIB files.
        
        _create_json()
            Create JSON file.
        
        _create_catalog_entry()
            Create catalog entry.
        
        help()
            Print help.
        """
        self.verbose = verbose
        self.replace = replace

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

        if self.verbose:
            print(f"Data directory: {self.datadir}")
            print(f"JSON directory: {self.jsondir}")
            print(f"Catalog directory: {self.catalogdir}")
        
        # Get gribtype and tgt_json from source
        self.gribtype = self.source.split('_')[0]
        self.tgt_json = self.source.split('_')[1]
        self.indices = None
        
        # Get gribfiles wildcard from gribtype
        self.gribfiles = self.gribtype + '????+*'
        if self.verbose:
            print(f"Gribfile wildcard: {self.gribfiles}")

        # Get catalog filename
        self.catalogfile = os.path.join(self.catalogdir,
                                        self.model,self.exp+'.yaml')
        if self.verbose:
            print(f"Catalog file: {self.catalogfile}")

        # Get JSON filename
        self.jsonfile = os.path.join(self.jsondir, self.tgt_json+'.json')
        if self.verbose:
            print(f"JSON file: {self.jsonfile}")

        self.flag = [False, False, False]
        self._check_steps()
    
    def create_entry(self):
        """
        Create catalog entry.
        """
        # Create folders
        self._create_folders()

        # Create symlinks to GRIB files
        self._create_symlinks()

        # Create indices for GRIB files
        if self.flag[0]:
            self._create_indices()
        
        # Create JSON file
        if self.flag[1]:
            self._create_json()

        # Create catalog entry
        self._create_catalog_entry()

    def _check_steps(self):
        """
        Check if indices and JSON file have to be created.
        Check if catalog file exists.
        """
        # Check if indices have to be created
        # True if indices have to be created, 
        # False otherwise
        self.flag[0] = self._check_indices()

        # Check if JSON file has to be created
        # True if JSON file has to be created,
        # False otherwise
        self.flag[1] = self._check_json()

        # Check if catalog file exists
        # True if catalog file exists,
        # False otherwise
        self.flag[2] = self._check_catalog()

    def _check_indices(self):
        """
        Check if indices already exist.

        Returns:
            bool: True if indices have to be created, False otherwise.
        """
        if self.verbose:
            print("Checking if indices already exist...")
        if len(glob(os.path.join(self.tmpdir, '*.index'))) > 0:
            if self.replace:
                if self.verbose:
                    print("Indices already exist. Removing them...")
                for file in glob(os.path.join(self.tmpdir, '*.index')):
                    os.remove(file)
                return True
            else:
                if self.verbose:
                    print("Indices already exist.")
                return False
        else: # Indices do not exist
            return True
    
    def _check_json(self):
        """
        Check if JSON file already exists.

        Returns:
            bool: True if JSON file has to be created, False otherwise.
        """
        if self.verbose:
            print("Checking if JSON file already exists...")
        if os.path.exists(self.jsonfile):
            if self.replace:
                if self.verbose:
                    print("JSON file already exists. Removing it...")
                os.remove(self.jsonfile)
                return True
            else:
                if self.verbose:
                    print("JSON file already exists.")
                return False
        else: # JSON file does not exist
            return True

    def _check_catalog(self):
        """
        Check if catalog entry already exists.

        Returns:
            bool: True if catalog file exists, False otherwise.
        """
        if self.verbose:
            print("Checking if catalog file already exists...")
        if os.path.exists(self.catalogfile):
            if self.verbose:
                print(f"Catalog file {self.catalogfile} already exists.")
        else: # Catalog file does not exist
            if self.verbose:
                print(f"Catalog file {self.catalogfile} does not exist and will be generated.")
            return False

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
        if self.verbose:
                print(self.indices)

    def _create_json(self):
        if self.verbose:
            print("Creating JSON file...")
        
        # to be improved without using subprocess
        cmd = ['gribscan-build', '-o', self.jsondir, '--magician', 'ifs', 
            '--prefix', self.datadir + '/'] + glob(os.path.join(self.tmpdir, '*index'))
        json = subprocess.run(cmd)
    
    def _create_catalog_entry(self):
        """
        Create or update catalog file
        """
        
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
        
        if self.flag[2]: # Catalog file exists
            mydict = load_yaml(self.catalogfile)
            mydict['sources'][self.source] = myblock
        else: # Catalog file does not exist
            # default dict for zarr
            mydict= {'plugins': {'source': [{'module': 'intake_xarray'}, {'module': 'gribscan'}]}}
            mydict['sources'] = {}
            mydict['sources'][self.source] = myblock
        
        # Check if source already exists
        if self.source in mydict['sources'].keys():
            if self.replace:
                if self.verbose:
                    print(f"Source {self.source} already exists in {self.catalogfile}. Replacing it...")
                mydict['sources'][self.source] = myblock
            else:
                if self.verbose:
                    print(f"Source {self.source} already exists in {self.catalogfile}. Skipping...")
                return

        # Write catalog file
        with open(self.catalogfile, 'w') as f:
            yaml.dump(mydict, f, sort_keys=False)
    
    def help(self):
        """
        Print help message.
        """
        print("Gribber class:")
        print("  model: model name (default: IFS)")
        print("  exp: experiment name (default: tco1279-orca025)")
        print("  source: source name (default: ICMGG_atm2d)")
        print("  nprocs: number of processors (default: 4)")
        print("  verbose: print help message (default: False)")
        print("  replace: replace existing files (default: False)")
        print("  dir: dictionary with directories (default: see below)")
        print("  datadir: data directory (default: /scratch/b/b382289/tco1279-orca025/nemo_deep/ICMGGc2)")
        print("  tmpdir: temporary directory (default: /scratch/b/b382289/gribscan)")
        print("  jsondir: JSON directory (default: /work/bb1153/b382289/gribscan-json)")
        print("  catalogdir: catalog directory (default: /work/bb1153/b382289/AQUA/config/levante/catalog)")