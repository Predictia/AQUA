"""Module for teleconnection class."""
import os

import xarray as xr

from aqua.logger import log_configure
from aqua.reader import Reader
from teleconnections.index import station_based_index, regional_mean_index
from teleconnections.plots import index_plot
from teleconnections.tools import load_namelist


class Teleconnection():
    """Class for teleconnection objects."""

    def __init__(self, model: str, exp: str, source: str,
                 telecname: str, configdir=None, regrid='r100',
                 savefig=False, outputfig=None,
                 savefile=False, outputdir=None,
                 filename=None,
                 months_window: int = 3, loglevel: str = 'WARNING'):
        """Initialize teleconnection object."""

        # Configure logger
        self.loglevel = loglevel
        self.logger = log_configure(self.loglevel, 'Teleconnection')

        # Reader variables
        self.model = model
        self.exp = exp
        self.source = source
        self.logger.debug('Open dataset: {}/{}/{}'.format(self.model, self.exp, self.source))

        self.regrid = regrid
        if self.regrid is None:
            self.logger.warning('No regridding will be performed')
        self.logger.debug('Regridding resolution: {}'.format(self.regrid))

        # Teleconnection variables
        avail_telec = ['NAO', 'ENSO']
        if telecname in avail_telec:
            self.telecname = telecname
        else:
            raise ValueError('telecname must be one of {}'.format(avail_telec))

        self._load_namelist(configdir=configdir)

        # Variable to be used for teleconnection
        self.var = self.namelist[self.telecname]['field']
        self.logger.debug('Teleconnection variable: {}'.format(self.var))

        # The teleconnection type is used to select the correct function
        self.telec_type = self.namelist[self.telecname]['telec_type']
        self.logger.debug('Teleconnection type: {}'.format(self.telec_type))

        # At the moment it is used by all teleconnections
        if self.telecname == 'NAO' or self.telecname == 'ENSO':
            self.months_window = months_window

        # Output variables
        self._load_figs_options(savefig, outputfig)
        self._load_data_options(savefile, outputdir, filename)
        if self.savefile or self.savefig:
            self._filename(filename)

        # Data empty at the beginning
        self.data = None
        self.index = None

        # Initialize reader
        self._reader()

    def _load_namelist(self, configdir=None):
        """Load namelist."""

        self.namelist = load_namelist('teleconnections', configdir)
        self.logger.info('Namelist loaded')
        self.logger.debug(self.namelist)

    def _reader(self):
        """Initialize AQUA reader."""

        self.reader = Reader(model=self.model, exp=self.exp, source=self.source,
                             regrid=self.regrid, loglevel=self.loglevel)
        self.logger.info('Reader initialized')

    def retrieve(self):
        """Retrieve teleconnection data."""

        try:
            self.data = self.reader.retrieve(var=self.var)
        except ValueError:
            self.logger.warning('Variable {} not found'.format(self.var))
            self.logger.warning('Trying to retrieve without fixing')
            self.data = self.reader.retrieve(var=self.var, fix=False)
        self.logger.info('Data retrieved')

        if self.regrid:

            self.data = self.reader.regrid(self.data)
            self.logger.info('Data regridded')

    def evaluate_index(self):
        """Calculate teleconnection index."""

        if self.data is None:
            self.logger.warning('No retrieve has been performed, trying to retrieve')
            self.retrieve()

        if self.telec_type == 'station':
            self.index = station_based_index(field=self.data[self.var],
                                             namelist=self.namelist,
                                             telecname=self.telecname,
                                             months_window=self.months_window,
                                             loglevel=self.loglevel)
        elif self.telec_type == 'regional':
            self.index = regional_mean_index(field=self.data[self.var],
                                             namelist=self.namelist,
                                             telecname=self.telecname,
                                             months_window=self.months_window,
                                             loglevel=self.loglevel)

        if self.savefile:
            file = self.outputdir + '/' + self.filename + '_index.nc'
            self.index.to_netcdf(file)
            self.logger.info('Index saved to {}'.format(file))

    def evaluate_regression(self):
        """Calculate teleconnection regression."""

        self.logger.warning('Not implemented yet')
        return

        if self.savefile:
            file = self.outputdir + '/' + self.filename + '_reg.nc'
            self.reg.to_netcdf(file)
            self.logger.info('Regression saved to {}'.format(file))

    def evaluate_correlation(self):
        """Calculate teleconnection correlation."""

        self.logger.warning('Not implemented yet')
        return

        if self.savefile:
            file = self.outputdir + '/' + self.filename + '_corr.nc'
            self.corr.to_netcdf(file)
            self.logger.info('Correlation saved to {}'.format(file))

    def plot_index(self, step=False, **kwargs):
        """Plot teleconnection index."""

        if self.index is None:
            self.logger.warning('No index has been calculated, trying to calculate')
            self.evaluate_index()

        index_plot(indx=self.index, save=self.savefig, outputdir=self.outputfig,
                   loglevel=self.loglevel, step=step, **kwargs)

    def _load_figs_options(self, savefig=False, outputfig=None):
        """Load the figure options.
        Args:
            savefig (bool): whether to save the figures.
                            Default is False.
            outputfig (str): path to the figure output directory.
                             Default is None.
                             See init for the class default value.
        """
        self.savefig = savefig  # adapt or remove if you do not need it

        if self.savefig:
            self.logger.info('Figures will be saved')
            self._load_folder_info(outputfig, 'figure')

    def _load_data_options(self, savefile=False, outputdir=None, filename=None):
        """Load the data options.
        Args:
            savefile (bool): whether to save the data.
                             Default is False.
            outputdir (str): path to the data output directory.
                             Default is None.
                             See init for the class default value.
            filename (str): name of the output file.
                            Default is None.
                            See init for the class default value.
        """
        self.savefile = savefile  # adapt or remove if you do not need it

        if self.savefile:
            self.logger.info('Data will be saved')
            self._load_folder_info(outputdir, 'data')

    def _filename(self, filename=None):
        """Generate the output file name.
        Args:
            filename (str): name of the output file.
                            Default is None.
        """
        if filename is None:
            self.logger.info('No filename specified, using the teleconnection name')
            filename = self.model + '_' + self.exp + '_' + self.source + '_' + self.telecname
        self.filename = filename
        self.logger.debug('Output filename: {}'.format(filename))

    def _load_folder_info(self, folder=None, folder_type=None):
        """Load the folder information.
        Args:
            folder (str): path to the folder.
                          Default is None.
            folder_type (str): type of the folder.
                               Default is None.

        Raises:
            KeyError: if the folder_type is not recognised.
            TypeError: if the folder_type is not a string.
        """
        if folder_type not in ['figure', 'data']:
            raise KeyError('The folder_type must be either figure or data')

        if not folder:
            self.logger.warning('No {} folder specified, using the current directory'.format(folder_type))
            folder = os.getcwd()
        else:
            if not isinstance(folder, str):
                raise TypeError('The folder must be a string')
            if not os.path.isdir(folder):
                self.logger.warning('The folder {} does not exist, creating it'.format(folder))
                os.makedirs(folder)

        # Store the folder in the class
        if folder_type == 'figure':
            self.outputfig = folder
            self.logger.debug('Figure output folder: {}'.format(self.outputfig))
        elif folder_type == 'data':
            self.outputdir = folder
            self.logger.debug('Data output folder: {}'.format(self.outputdir))
