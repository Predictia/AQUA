import os
import xarray as xr
from aqua.diagnostics.core import Diagnostic
from aqua.util import ConfigPath, load_yaml

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

    def evaluate_regression(self, data: xr.Dataset = None, var: str = None,
                            dim: str = 'time', season: str = None):
        pass

    def evaluate_correlation(self, data: xr.Dataset = None, var: str = None,
                             dim: str = 'time', season: str = None):
        pass

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
