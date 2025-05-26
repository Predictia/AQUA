import xarray as xr
from aqua.logger import log_configure
from aqua.util import area_selection, to_list
from .base import BaseMixin

# set default options for xarray
xr.set_options(keep_attrs=True)


class MJO(BaseMixin):
    """
    MJO (Madden-Julian Oscillation) class.
    """
    def __init__(self, catalog: str = None, model: str = None,
                 exp: str = None, source: str = None,
                 regrid: str = None,
                 startdate: str = None, enddate: str = None,
                 configdir: str = None,
                 interface: str = 'teleconnections-destine',
                 loglevel: str = 'WARNING'):
        """
        Initialize the MJO class.

        Args:
            catalog (str): Catalog name.
            model (str): Model name.
            exp (str): Experiment name.
            source (str): Source name.
            regrid (str): Regrid method.
            startdate (str): Start date for data retrieval.
            enddate (str): End date for data retrieval.
            configdir (str): Configuration directory. Default is the installation directory.
            interface (str): Interface filename. Default is 'teleconnections-destine'.
            loglevel (str): Logging level. Default is 'WARNING'.
        """
        super().__init__(telecname='MJO', catalog=catalog, model=model, exp=exp, source=source,
                         regrid=regrid, startdate=startdate, enddate=enddate,
                         configdir=configdir, interface=interface,
                         loglevel=loglevel)
        self.logger = log_configure(log_name='MJO', log_level=loglevel)

        self.var = self.interface.get('field')
        self.data_hovmoller = None

        # Delete the self.index attribute if it exists
        if hasattr(self, 'index'):
            del self.index

    def retrieve(self):
        # Assign self.data, self.reader, self.catalog
        super().retrieve(var=self.var)

        self.reader.timmean(self.data, freq='D')

    def compute_hovmoller(self, day_window: int = None):
        """
        Compute the Hovmoller plot for the MJO index.
        This method prepares the data for a Hovmoller plot by selecting the MJO box,
        evaluating anomalies, and smoothing the data if required.

        Args:
            day_window (int, optional): Number of days to be used in the smoothing window.
                                        If None, no smoothing is performed. Default is None.
        """
        if self.interface.get('flip_sign', True):
            self.logger.info("Flipping the sign of the variable.")
            self.data = -self.data
        
        # Acquiring MJO box
        lat = [self.interface['latS'], self.interface['latN']]
        lon = [self.interface['lonW'], self.interface['lonE']]

        # Selecting the MJO box
        data_sel = area_selection(self.data, lat=lat, lon=lon, drop=True)

        # Evaluating anomalies
        data_mean = data_sel.mean(dim='time')
        data_anom = data_sel - data_mean

        # Smoothing the data
        if day_window:
            self.logger.info("Smoothing the data with a window of " + str(day_window) + " days.")
            self.data_hovmoller = data_anom.rolling(time=day_window, center=True).mean()
        else:
            self.data_hovmoller = data_anom


class PlotMJO:
    """
    PlotMJO class for plotting the MJO Hovmoller data.
    This class is a placeholder for future plotting methods.
    """
    def __init__(self, data, outputdir: str = './', rebuild: bool = True, loglevel: str = 'WARNING'):
        """
        Initialize the PlotMJO class.

        Args:
            data (list or xarray.DataArray): The list of data to be plot.
            outputdir (str): Directory where the plots will be saved. Default is './'.
            rebuild (bool): If True, the plots will be rebuilt. Default is True.
            loglevel (str): Logging level. Default is 'WARNING'.
        """
        # Data info initalized as empty
        self.loglevel = loglevel
        self.logger = log_configure(self.loglevel, 'PlotMJO')
        self.catalogs = None
        self.models = None
        self.exps = None

        self.data = to_list(data)
        self.len_data = len(self.data)

        self.get_data_info()

    def get_data_info(self):
        """
        We extract the data needed for labels, description etc
        from the data arrays attributes.

        The attributes are:
        - AQUA_catalog
        - AQUA_model
        - AQUA_exp
        """
        self.catalogs = [d.AQUA_catalog for d in self.data]
        self.models = [d.AQUA_model for d in self.data]
        self.exps = [d.AQUA_exp for d in self.data]

    def plot(self):
        """
        Placeholder method for plotting the MJO Hovmoller data.
        """
        raise NotImplementedError("Plotting method not implemented yet.")