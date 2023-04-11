import os
from time import time
import dask
from aqua.logger import log_configure
from aqua.reader import Reader
from aqua.util import create_folder, generate_random_string
from dask.distributed import Client, LocalCluster, progress
from dask.diagnostics import ProgressBar


class LRA_Generator():
    """
    Class to generate LRA data at required frequency/resolution
    """
    def __init__(self,
                 model=None, exp=None, source=None,
                 var=None, vars=None,
                 resolution=None, frequency=None, fix=True,
                 outdir=None, tmpdir=None, nproc=1,
                 loglevel=None, overwrite=False, dry=True):
        """
        Initialize the LRA_Generator class

        Args:
            model (string):          The model name from the catalog
            exp (string):            The experiment name from the catalog
            source (string):         The sourceid name from the catalog
            var (str, list):         Variable(s) to be processed and archived
                                     in LRA,vars in a synonim
            resolution (string):     The target resolution for the LRA
            frequency (string,opt):  The target frequency for averaging the
                                     LRA, if no frequency is specified,
                                     no time average is performed
            fix (bool, opt):         True to fix the data, default is True
            outdir (string):         Where the LRA is
            tmpdir (string):         Where to store temporary files,
                                     default is None.
                                     Necessary for dask.distributed
            nproc (int, opt):        Number of processors to use. default is 1
            loglevel (string, opt):  Logging level
            overwrite (bool, opt):   True to overwrite existing files in LRA,
                                     default is False
            dry (bool, opt):         False to create the output file,
                                     True to just explore the reader
                                     operations, default is True
        """
        # General settings
        self.logger = log_configure(loglevel, 'lra_generator')

        self.overwrite = overwrite
        if self.overwrite:
            self.logger.info('File will be overwritten if already existing.')

        self.dry = dry
        if self.dry:
            self.logger.warning('IMPORTANT: no file will be created, this is a dry run')

        self.nproc = nproc
        self.tmpdir = tmpdir
        if self.nproc > 1:
            self.dask = True
            self.logger.info(f'Running dask.distributed with {self.nproc} workers')
            if not self.tmpdir:
                raise Exception('Please specify tmpdir for dask.distributed.')
            else:
                self.tmpdir = os.path.join(self.tmpdir,
                                           generate_random_string(10))
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

        # Initialize variable(s)
        self.var = None
        if vars:
            self.var = vars
        else:
            self.var = var
        if not self.var:
            raise Exception('Please specify variable string or list.')
        self.logger.info(f'Variable(s) to be processed: {self.var}')

        self.resolution = resolution
        if not self.resolution:
            raise Exception('Please specify resolution.')

        self.frequency = frequency
        if not self.frequency:
            self.logger.info('Frequency not specified, streaming mode')

        # option for time encoding, defined once for all
        self.time_encoding = {
            'units': 'days since 1970-01-01',
            'calendar': 'standard',
            'dtype': 'float64'
            }

        self.fix = fix
        self.logger.info(f'Fixing data: {self.fix}')

        # Create LRA folder
        if self.frequency:
            self.outdir = os.path.join(outdir, self.exp, self.resolution,
                                       self.frequency)
        else:
            self.outdir = os.path.join(outdir, self.exp, self.resolution)
        create_folder(self.outdir, verbose=self.verbose)

        # Initialize variables used by methods
        self.data = None
        self.reader = None
        self.cluster = None
        self.client = None

    def retrieve(self):
        """
        Retrieve data from the catalog
        """
        self.logger.info(f'Accessing catalog for {self.model}-{self.exp}-{self.source}...')
        if self.frequency:
            self.logger.info(f'I am going to produce LRA at {self.resolution} resolution and {self.frequency} frequency...')
        else:
            self.logger.info(f'I am going to produce LRA at {self.resolution} resolution...')

        # Initialize the reader
        self.reader = Reader(model=self.model, exp=self.exp,
                             source=self.source, var=self.var,
                             regrid=self.resolution, freq=self.frequency,
                             configdir="../../config")

        self.logger.info('Retrieving data...')
        self.data = self.reader.retrieve(fix=self.fix)
        self.logger.info(self.data)

    def generate_lra(self):
        """
        Generate LRA data
        """
        self.logger.info('Generating LRA data...')

        # Set up dask cluster
        self._set_dask()

        if isinstance(self.var, list):
            for var in self.var:
                self._write_var(var)
        else:  # Only one variable
            self._write_var(self.var)

        # Cleaning
        self.data.close()
        self._close_dask()
        self._remove_tmpdir()

        self.logger.info('Finished generating LRA data.')

    def _set_dask(self):
        """
        Set up dask cluster
        """
        if self.dask:  # self.nproc > 1
            self.logger.info(f'Setting up dask cluster with {self.nproc} workers')
            dask.config.set({'temporary_directory': self.tmpdir})
            if self.verbose:
                print(f'Temporary directory: {self.tmpdir}')
            self.cluster = LocalCluster(n_workers=self.nproc,
                                        threads_per_worker=1)
            self.client = Client(self.cluster)
        else:
            self.client = None
            dask.config.set(scheduler='synchronous')

    def _close_dask(self):
        """
        Close dask cluster
        """
        if self.dask:  # self.nproc > 1
            self.client.shutdown()
            self.cluster.close()
            self.logger.info('Dask cluster closed')

    def _remove_tmpdir(self):
        """
        Remove temporary directory
        """
        if self.dask:  # self.nproc > 1
            self.logger.warning(f'Removing temporary directory {self.tmpdir}')
            os.removedirs(self.tmpdir)

    def _write_var(self, var):
        """
        Write variable to file

        Args:
            var (str): variable name
        """
        t_beg = time()

        self.logger.info(f'Processing variable {var}...')
        temp_data = self.data[var]
        if self.frequency:
            temp_data = self.reader.timmean(temp_data)
        temp_data = self.reader.regrid(temp_data)

        # Splitting data into yearly files
        years = set(temp_data.time.dt.year.values)
        for year in years:
            year_data = temp_data.sel(time=temp_data.time.dt.year == year)
            self.logger.info(f'Processing year {year}...')
            # Splitting data into monthly files
            months = set(year_data.time.dt.month.values)
            for month in months:
                self.logger.info(f'Processing month {month}...')
                month_data = year_data.sel(time=year_data.time.dt.month
                                           == month)

                if not self.dry:
                    # Create output file
                    outfile = os.path.join(self.outdir,
                                           f'{var}_{self.exp}_\
                                           {self.resolution}_\
                                           {self.frequency}_\
                                           {year}{str(month).zfill(2)}.nc')
                    if os.path.isfile(outfile) and not self.overwrite:
                        self.logger.warning(f'File {outfile} already exists, skipping...')
                    else:  # File to be written
                        if os.path.exists(outfile):
                            os.remove(outfile)
                            self.logger.warning(f'File {outfile} already exists,\
                                             overwriting...')
                        if self.verbose:
                            self.logger.warning(f'Writing file {outfile}...')

                        # Write data to file, lazy evaluation
                        write_job =\
                            month_data.to_netcdf(outfile,
                                                 encoding={'time':
                                                           self.time_encoding},
                                                 compute=False)

                        if self.dask:
                            w_job = write_job.persist()
                            progress(w_job)
                            del w_job
                        else:
                            with ProgressBar():
                                write_job.compute()

                        del write_job
                del month_data
            del year_data
        del temp_data

        t_end = time()
        self.logger.info('Process took {:.4f} seconds'.format(t_end-t_beg))
