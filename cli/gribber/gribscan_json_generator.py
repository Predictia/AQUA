import os
from aqua.util import load_yaml

class Gribber():
    """
    Class to generate a JSON file from a GRIB file.
    """

    def __init__(self,exp='IFS',expid='tco1279',nprocs=4,
                 tmpdir='/scratch/b/b382289/gribscan',
                 jsondir='/work/bb1153/b382289/gribscan-json',
                 catalogdir='/work/bb1153/b382289/AQUA/config/levante/catalog') -> None:
        self.exp = exp
        self.expid = expid
        self.nprocs = nprocs
        self.tmpdir = os.path.join(tmpdir,expid)
        self.jsondir = os.path.join(jsondir,expid)
        self.catalogdir = catalogdir

        # Create folders
        for item in [self.tmpdir, self.jsondir]:
            print(f"Creating {item}...")
            os.makedirs(item, exist_ok=True)

        # Load yaml file
        self.griblist = load_yaml('gribber.yml')
        


        #self.tgt_json = griblist[self.expid]['tgt_json']
        
        #self.catalogfile = os.path.join(self.catalogdir, self.exp, self.expid + '.yaml')
        #self.jsonfile    = os.path.join(self.jsondir, self.tgt_json + '.json')

    def _create_symlinks(self):
        """
        Create symlinks to GRIB files.
        """
        for gribtype in self.griblist[self.expid]['gribtypes']:
            gribfiles = gribtype + '????+*'
            for file in glob(os.path.join(self.datadir, gribfiles)):
                try: 
                    os.symlink(file, os.path.join(self.tmpdir, os.path.basename(file)))
                except FileExistsError:
                    pass
    
    def _create_indices(self):
        """
        Create indices for GRIB files.
        """
        print("Creating GRIB indices...")
        cmd1 = ['gribscan-index', '-n', str(self.nprocs)] + glob(os.path.join(self.tmpdir, gribfiles))
        result1 = subprocess.run(cmd1)
    
    def _create_json(self):
        """
        Create JSON file.
        """
        print("Creating JSON file...")
        cmd2 = ['gribscan-build', '-o', self.jsondir, '--magician', 'ifs', 
                '--prefix', datadir + '/'] + glob(os.path.join(self.tmpdir, '*index'))
        result2 = subprocess.run(cmd2)
    
    def _create_catalog(self):
        """
        Create catalog file.
        """
        # Check if catalog file exists
        if os.path.exists(self.catalogfile):
            mydict = load_yaml(self.catalogfile)
            mydict['sources'][sourceid] = myblock
        else: 
            # Default dict for zarr
            mydict = {
                'sources': {
                    sourceid: myblock
                }
            }
        
        # Write catalog file
        with open(self.catalogfile, 'w') as f:
            yaml.dump(mydict, f, default_flow_style=False)