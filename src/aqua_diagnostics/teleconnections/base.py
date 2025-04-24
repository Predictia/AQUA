import xarray as xr
from aqua.diagnostics.core import Diagnostic
from .tools import TeleconnectionsConfig

xr.set_options(keep_attrs=True)


class BaseMixin(Diagnostic):
    def __init__(self, catalog: str = None, model: str = None,
                 exp: str = None, source: str = None,
                 regrid: str = None,
                 startdate: str = None, enddate: str = None,
                 loglevel: str = 'WARNING'):
        """
        Initialize the Base class.
        Args:
            catalog (str): The catalog to be used. If None, the catalog will be determined by the Reader.
            model (str): The model to be used.
            exp (str): The experiment to be used.
            source (str): The source to be used.
            regrid (str): The target grid to be used for regridding. If None, no regridding will be done.
            startdate (str): The start date of the data to be retrieved.
                             If None, all available data will be retrieved.
            enddate (str): The end date of the data to be retrieved.
                           If None, all available data will be retrieved.
            loglevel (str): The log level to be used. Default is 'WARNING'.
        """
        super().__init__(catalog=catalog, model=model, exp=exp, source=source, regrid=regrid,
                         startdate=startdate, enddate=enddate, loglevel=loglevel)

        # Initialize the possible results
        self.index = None

    def evaluate_regression(self, data: xr.Dataset = None, var: str = None,
                            dim: str = 'time', season: str = None):
        pass

    def evaluate_correlation(self, data: xr.Dataset = None, var: str = None,
                             dim: str = 'time', season: str = None):
        pass

    def load_namelist(self, configdir: str = None, interface: str = None):
        config = TeleconnectionsConfig(configdir=configdir, interface=interface)

        self.namelist = config.load_namelist()
        self.logger.info('Namelist loaded')