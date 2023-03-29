from aqua.util import load_yaml, create_folder

class LRA_Generator():
    """
    Class to generate LRA data at required frequency/resolution
    """

    def __init__(self, 
                 model=None, exp=None, source=None,
                 varlist=None, 
                 resolution=None, frequency=None,
                 outdir=None, nproc=1,
                 verbose=False, replace=False):
        """
        Args:
            model (string):       The model name from the catalog
            exp (string):         The experiment name from the catalog
            source (string):      The sourceid name from the catalog
            varlist (list):       The list fo variables to be processed and archived in LRA
            resolution (string):  The target resolution for the LRA
            frequency (string):   The target frequency for averaging the LRA
            outdir (string):      Where the LRA is
            nproc (int):          Number of processors to use
            verbose (bool):       True to print debug messages
            replace (bool):       True to overwrite existing files in LRA, default is False        """
        self.model = model
        self.exp = exp
        self.source = source
        self.varlist = varlist
        self.resolution = resolution
        self.frequency = frequency
        self.outdir = outdir
        self.nproc = nproc
        self.verbose = verbose
        self.replace = replace