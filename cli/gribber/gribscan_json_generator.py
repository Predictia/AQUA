import os
from aqua.util import load_yaml

class Gribber():
    """
    Class to generate a JSON file from a GRIB file.
    """

    def __init__(self,expid='tco1279',nprocs=4,
                 tmpdir='/scratch/b/b382289/gribscan',
                 jsondir='/work/bb1153/b382289/gribscan-json') -> None:
        self.expid   = expid
        self.nprocs  = nprocs
        self.tmpdir  = os.path.join(tmpdir,expid)
        self.jsondir = os.path.join(jsondir,expid)

        # Create folders
        for item in [self.tmpdir, self.jsondir]:
            print(f"Creating {item}...")
            os.makedirs(item, exist_ok=True)