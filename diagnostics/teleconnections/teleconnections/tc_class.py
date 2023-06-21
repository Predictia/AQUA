"""Module for teleconnection class."""
from aqua.logger import log_configure
from aqua.reader import Reader
from teleconnections.index import station_based_index, regional_mean_index
from teleconnections.tools import load_namelist


class Teleconnection():
    """Class for teleconnection objects."""

    def __init__(self, model=None, exp=None, source=None,
                 telecname=None, configdir=None, regrid='r100',
                 months_window=3, loglevel='WARNING'):
        """Initialize teleconnection object."""

        # Configure logger
        self.loglevel = loglevel
        self.logger = log_configure(self.loglevel, 'Teleconnection')

        # Reader variables
        if model:
            self.model = model
        else:
            raise ValueError('model must be specified')

        if exp:
            self.exp = exp
        else:
            raise ValueError('exp must be specified')

        if source:
            self.source = source
        else:
            raise ValueError('source must be specified')

        self.regrid = regrid
        if self.regrid is None:
            self.logger.warning('No regridding will be performed')
        self.logger.debug('Regridding resolution: {}'.format(self.regrid))

        # Teleconnection variables
        if telecname:
            self.telecname = telecname
        else:
            raise ValueError('telecname must be specified')

        if configdir:
            self.configdir = configdir
        else:
            self.configdir = None

        self._load_namelist()

        self.var = self.namelist[self.telecname]['field']
        self.logger.debug('Teleconnection variable: {}'.format(self.var))
        self.telec_type = self.namelist[self.telecname]['telec_type']
        self.logger.debug('Teleconnection type: {}'.format(self.telec_type))

        self.months_window = months_window

        # Initialize reader
        self._reader()

    def _load_namelist(self):
        """Load namelist."""

        self.namelist = load_namelist('teleconnections', self.configdir)
        self.logger.info('Namelist loaded')
        self.logger.debug(self.namelist)

    def _reader(self):
        """Initialize AQUA reader."""

        self.reader = Reader(model=self.model, exp=self.exp, source=self.source,
                             regrid=self.regrid, loglevel=self.loglevel)
        self.logger.info('Reader initialized')
        self.logger.debug(self.reader)

    def retrieve(self):
        """Retrieve teleconnection data."""

        try:
            self.data = self.reader.retrieve(var=self.var)
        except ValueError:
            self.logger.warning('Variable {} not found'.format(self.var))
            self.logger.warning('Trying to retrieve without fixing')
            self.data = self.reader.retrieve(var=self.var, fix=False)
        self.logger.info('Data retrieved')

    def index(self):
        """Calculate teleconnection index."""

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
