import os
import xarray as xr
from aqua.diagnostics.core import Diagnostic
from aqua.util import ConfigPath, load_yaml, select_season

xr.set_options(keep_attrs=True)


class BaseMixin(Diagnostic):
    def __init__(self, telecname: str, catalog: str = None, model: str = None,
                 exp: str = None, source: str = None,
                 regrid: str = None,
                 startdate: str = None, enddate: str = None,
                 configdir: str = None,
                 interface: str = 'teleconnections-destine',
                 loglevel: str = 'WARNING'):
        """
        Initialize the Base class.
        Args:
            telecname (str): The name of the teleconnection.
            catalog (str): The catalog to be used. If None, the catalog will be determined by the Reader.
            model (str): The model to be used.
            exp (str): The experiment to be used.
            source (str): The source to be used.
            regrid (str): The target grid to be used for regridding. If None, no regridding will be done.
            startdate (str): The start date of the data to be retrieved.
                             If None, all available data will be retrieved.
            enddate (str): The end date of the data to be retrieved.
                           If None, all available data will be retrieved.
            configdir (str): The directory where the interface file is located.
                             If None, the default directory will be used.
            interface (str): The filename of the interface file.
                             Default is 'teleconnections-destine'.
            loglevel (str): The log level to be used. Default is 'WARNING'.
        """
        super().__init__(catalog=catalog, model=model, exp=exp, source=source, regrid=regrid,
                         startdate=startdate, enddate=enddate, loglevel=loglevel)

        self.interface = self.load_interface(configdir=configdir, interface=interface,
                                             telecname=telecname)
        # Initialize the possible results
        self.index = None

    def compute_regression(self, var: str = None,
                            dim: str = 'time', season: str = None):
        """
        Compute the regression of the data on the index.

        Args:
            var (str): The variable to be used. If None, the variable is the same of the index.
            dim (str): The dimension to be used for the regression. Default is 'time'.
            season (str): The season to be used. If None, no season will be selected.

        Returns:
            xr.DataArray: The regression of the data on the index.
        """
        data, index = self._prepare_statistic(var=var, season=season)
        reg = xr.cov(index, data, dim=dim)/index.var(dim=dim, skipna=True).values
        return reg

    def compute_correlation(self, var: str = None,
                             dim: str = 'time', season: str = None):
        """
        Compute the correlation of the data on the index.

        Args:
            var (str): The variable to be used. If None, the variable is the same of the index.
            dim (str): The dimension to be used for the regression. Default is 'time'.
            season (str): The season to be used. If None, no season will be selected.

        Returns:
            xr.DataArray: The regression of the data on the index.
        """
        data, index = self._prepare_statistic(var=var, season=season)
        corr = xr.corr(index, data, dim=dim, skipna=True)
        return corr
    
    def _prepare_statistic(self, var: str = None, season: str = None):
        """Hidden method to prepare the data and index for the statistic."""
        # Preparing data and index. Both have to be xr.DataArray
        if not var:
            data = self.data[self.var]
        else:
            data, _, _ = super()._retrieve(model=self.model, exp=self.exp, source=self.source,
                                           var=var, catalog=self.catalog, startdate=self.startdate,
                                           enddate=self.enddate, regrid=self.regrid, loglevel=self.loglevel)
            data = data[var]

        index = self.index
        if season:
            data = select_season(data, season)
            index = select_season(index, season)

        return data, index
        

    def load_interface(self, configdir: str = None, interface: str = 'teleconnections-destine',
                       telecname: str = None):
        """
        Load the interface for the teleconnections.

        Args:
            configdir (str): The directory where the interface file is located.
                              If None, the default directory will be used.
            interface (str): The filename of the interface file.
                             Default is 'teleconnections-destine'.
            telecname (str): The name of the teleconnection. It selects the subset of the interface.
        
        Returns:
            dict: The interface file as a dictionary.
        """
        # Add yaml to interface if not present
        if not interface.endswith('.yaml'):
            interface = f'{interface}.yaml'
        if not configdir:
            configdir = ConfigPath().get_config_dir()
            configdir = os.path.join(configdir, 'diagnostics', 'teleconnections', 'config')
        
        interface_file = os.path.join(configdir, interface)
        self.logger.debug(f'Loading interface file: {interface_file}')

        interface_dict = load_yaml(interface_file)

        return interface_dict[telecname] if telecname else interface_dict
