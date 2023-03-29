from aqua.reader import Reader
from aqua.util import load_yaml, create_folder
import os

class LRA_Generator():
    """
    Class to generate LRA data at required frequency/resolution
    """

    def __init__(self, 
                 model=None, exp=None, source=None,
                 varlist=None, 
                 resolution=None, frequency=None,fix=True,
                 outdir=None, nproc=1,
                 verbose=False, replace=False, dry=False):
        """
        Initialize the LRA_Generator class

        Args:
            model (string):       The model name from the catalog
            exp (string):         The experiment name from the catalog
            source (string):      The sourceid name from the catalog
            varlist (list):       The list of variables to be processed and archived in LRA
            resolution (string):  The target resolution for the LRA
            frequency (string):   The target frequency for averaging the LRA
            fix (bool, opt):      True to fix the data, default is True
            outdir (string):      Where the LRA is
            nproc (int, opt):     Number of processors to use. default is 1
            verbose (bool, opt):  True to print logging messages, default is False
            replace (bool, opt):  True to overwrite existing files in LRA, default is False
            dry (bool, opt):      False to create the output file, 
                                  True to just explore the reader operations, default is False        
        """
        # General settings
        self.verbose = verbose
        self.replace = replace
        if self.replace:
            if self.verbose:
                print('File will be replaced if already existing.')
        self.dry = dry
        if self.dry:
            if self.verbose:
                print('IMPORTANT: no file will be created, this is a dry run')
        self.nproc = nproc
        if self.nproc > 1:
            self.dask = True
            if self.verbose:
                print(f'Running dask.distributed with {self.nproc} workers')
        else:
            self.dask = False
        
        # Data settings
        if model:
            self.model = model
        else:
            raise Exception('Please specify model.')

        if exp:
            self.exp = exp
        else:
            raise Exception('Please specify experiment.')
        
        if source:
            self.source = source
        else:
            raise Exception('Please specify source.')
        
        self.varlist = varlist
        if not self.varlist:
            raise Exception('Please specify variable list.')
        if self.verbose:
            print(f'Variables to be processed: {self.varlist}')

        self.resolution = resolution
        if not self.resolution:
            raise Exception('Please specify resolution.')

        self.frequency = frequency
        if not self.frequency:
            if self.verbose:
                print('Frequency not specified, streaming mode')
        
        self.fix = fix
        if self.verbose:
            print(f'Fixing data: {self.fix}')

        # Create LRA folder
        if self.frequency:
            self.outdir = os.path.join(outdir, self.exp, self.resolution, self.frequency)
        else:
            self.outdir = os.path.join(outdir, self.exp, self.resolution)
        create_folder(self.outdir,verbose=self.verbose)

        # Initialize the reader
        self.retrieve_data()

        

    def retrieve_data(self):
        """
        Retrieve data from the catalog
        """
        if self.verbose:
            print(f'Accessing catalog for {self.model}-{self.exp}-{self.source}...')
            print(f'I am going to produce LRA at {self.resolution} resolution and {self.frequency} frequency...')

        # Initialize the reader
        self.reader = Reader(model=self.model, exp=self.exp, source=self.source,
                             regrid=self.resolution, freq=self.frequency, configdir="../../config")
        
        if self.verbose:
            print('Retrieving data...')
        self.data = self.reader.retrieve(fix=self.fix)
        if self.verbose:
            print(self.data)