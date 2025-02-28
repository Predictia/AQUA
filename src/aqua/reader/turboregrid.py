"""New Regrid class independent from the Reader"""
import os
import xarray as xr
from aqua.logger import log_configure
from aqua.util import to_list
from smmregrid import GridType, GridInspector, CdoGenerate, Regridder

class TurboRegrid():
    
    def __init__(self, cfg_grid_dict: dict,
                 src_grid_name: str,
                 data=None, loglevel="WARNING"):
        """
        The TurboRegrid constructor.

        Args:
            cfg_grid_dict (dict): The dictionary containing the full AQUA grid configuration.
            src_grid_name (str): The name of the source grid in the AQUA convention.
            data (xarray.Dataset): The dataset to be regridded, to be provided in src_grid_path is missing.
            loglevel (str): The logging level.
        """

        self.loglevel = loglevel
        self.logger = log_configure(log_level=loglevel, log_name='TurboRegrid')

        # define basic attributes:
        self.cfg_grid_dict = cfg_grid_dict #full grid dictionary
        self.src_grid_name = src_grid_name # source grid name
        self.src_grid_dict = cfg_grid_dict['grids'][src_grid_name] # source grid dictionary
        self.regridder = {} # regridders for each vertical coordinate

        # check that a path exists
        self.src_grid_path = self.src_grid_dict.get('path', None)
        if not self.src_grid_path:
            self.logger.warning("Grid file path not found in the configuration. Need a sample data.")
            return
        
        # verify that all provided paths are valid
        if isinstance(self.src_grid_path, dict):
            for key in self.src_grid_path:
                if not os.path.exists(self.src_grid_path[key]):
                    raise FileNotFoundError(f"Grid file {self.src_grid_path} does not exist.")
        elif not os.path.exists(self.src_grid_path):
            raise FileNotFoundError(f"Grid file {self.src_grid_path} does not exist.")
        
    def load_generate_weights(self, dst_grid_name, rebuild=False, reader_kwargs=None, **kwargs):
        """
        Load or generate regridding weights.
        """
        #self._make_filename(dst_grid_name, self.grid_name, model, exp, source, **reader_kwargs)     
        for v in self.src_grid_path:

            weights_filename = f'tmp_{v}.nc'
            if rebuild or os.path.exists(weights_filename):
                weights = xr.open_dataset(weights_filename)
                
            generator = CdoGenerate(source_grid=self.src_grid_path[v],
                            target_grid=self.cfg_grid_dict['grids'][dst_grid_name],
                            cdo_download_path=None,
                            cdo_icon_grids=None,
                            cdo_extra=None,
                            cdo_options=None,
                            cdo='cdo',
                            loglevel=self.loglevel)
            if v in ['2d', '2dm']:
                weights = generator.weights(method="con", nproc=1)
            else:
                weights = generator.weights(method="con", vert_coord=v, nproc=1)
            weights.to_netcdf(weights_filename)

            self.regridder[v] = Regridder(weights=weights)
        
    # def _configure_gridtype(self, data=None):
    #     """
    #     Configure the GridType object based on the grid_dict.
    #     """

    #     # 2d and 2dm should be passed to GridType and GridInspector as extra vert_dims
    #     vertical_dims = self.src_grid_dict.get('vert_coords', None)
    #     horizontal_dims = self.src_grid_dict.get('space_coords', None)
    #     grid_dims = to_list(horizontal_dims) + to_list(vertical_dims)

    #     if grid_dims: # check on self.grid_dict
    #         grid = GridType(dims=grid_dims)
    #     elif data:  # If not, we need to guess
    #         # It is the first element of a list because I can handle with smmregrid
    #         # multiple horizontal grids.
    #         grid = GridInspector(data).get_grid_info()[0]
    #     else:
    #         return None

    #     return grid




