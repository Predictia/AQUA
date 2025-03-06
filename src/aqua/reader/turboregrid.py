"""New Regrid class independent from the Reader"""
import os
import xarray as xr
from smmregrid import CdoGenerate, Regridder, GridInspector
from aqua.logger import log_configure

class TurboRegrid():
    """Refactor of regridder class"""
    
    def __init__(self, cfg_grid_dict: dict, 
                 src_grid_name: str, 
                 data: xr.Dataset = None, 
                 loglevel: str = "WARNING"):
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
        self.src_grid_dict = cfg_grid_dict['grids'].get(src_grid_name) # source grid dictionary

        if not self.src_grid_dict:
            raise ValueError(f"Source grid '{src_grid_name}' not found in the configuration.")

        self.regridder = {} # regridders for each vertical coordinate
        self.src_grid_area = None # source grid area
        self.dst_grid_area = None # destination grid area

        # Set up grid path
        self.src_grid_path = self._initialize_grid_path(data)

        self.logger.info("Grid name: %s", self.src_grid_name)
        self.logger.info("Grid file path: %s", self.src_grid_path)

    
    def _initialize_grid_path(self, data):
        """Initializes and validates the source grid path."""

        src_grid_path = self.src_grid_dict.get("path")

        if not src_grid_path:
            if data is not None:
                self.logger.info("Using provided dataset for grid path.")
                return {"2d": data}  # Expand for other grid types if needed

            self.logger.warning("Grid file path missing in config and no sample data provided.")
            return None

        # Convert to dictionary if necessary
        if isinstance(src_grid_path, str):
            src_grid_path = {"2d": src_grid_path}

        # Verify paths
        for key, path in src_grid_path.items():
            if not os.path.exists(path):
                raise FileNotFoundError(f"Grid file '{path}' does not exist for key '{key}'.")

        return src_grid_path

    def _check_existing_file(self, filename):
        """
        Checks if an area/weights file exists and is valid.
        Return true if the file has some records.
        """
        return os.path.exists(filename) and os.path.getsize(filename) > 0

    def load_generate_areas(self, dst_grid_name=None, rebuild=False, reader_kwargs=None, **kwargs):
        """
        Load or generate regridding areas calling smmregrid
        """

        # get the grid name for logging
        area_logname = "target" if dst_grid_name else "source"

        if dst_grid_name:
            # get the target from the configuration: HACK need to be homogenized for `2d` cases
            dst_grid_dict = self.cfg_grid_dict['grids'].get(dst_grid_name)
            dst_grid_path = self.cfg_grid_dict['grids'].get(dst_grid_name)
            #if isinstance(dst_grid_dict, dict):
            #    cdo_extra = dst_grid_dict.get('cdo_extra')
            #    cdo_options = dst_grid_dict.get('cdo_options')
        else:
            dst_grid_path = None
            # get the cdo options from the configuration
        
        cdo_extra = self.src_grid_dict.get('cdo_extra')
        cdo_options = self.src_grid_dict.get('cdo_options')
        
        area_filename = f'tmp_areas.nc'
        #weights_filename = self._make_filename(dst_grid_name, self.grid_name, **reader_kwargs)
        #keep fallback option for filename when weights/areas block is not present in the configuration

        # check if weights already exist, if not, generate them
        if rebuild or self._check_existing_file(area_filename):
  
            # smmregrid call
            generator = CdoGenerate(source_grid=self.src_grid_path['2d'],
                            target_grid=dst_grid_path,
                            cdo_download_path=None,
                            cdo_icon_grids=None,
                            cdo_extra=cdo_extra,
                            cdo_options=cdo_options,
                            cdo='cdo',
                            loglevel=self.loglevel)
            
            # if target_grid is not None, will generate the areas for the target grid
            grid_area = generator.areas(target=bool(dst_grid_name))
            grid_area.to_netcdf(area_filename)
            self.logger.info("Saved %s area to %s.", area_logname, area_filename)
        else:
            self.logger.info("Loading existing %s area from %s.", area_logname, area_filename)
            grid_area = xr.open_dataset(area_filename)

        # assign to the object
        if dst_grid_name is None:
            self.src_grid_area = grid_area
        else:
            self.dst_grid_area = grid_area
        
    def load_generate_weights(self, dst_grid_name, rebuild=False, reader_kwargs=None, **kwargs):
        """
        Load or generate regridding weights calling smmregrid
        """

        # get the cdo options from the configuration 
        cdo_extra = self.src_grid_dict.get('cdo_extra', None)
        cdo_options = self.src_grid_dict.get('cdo_options', None)

        # loop over the vertical coordinates: 2d, 2dm, or any other
        for vertical_dim in self.src_grid_path:

            weights_filename = f'tmp_{vertical_dim}.nc'
            #weights_filename = self._make_filename(dst_grid_name, self.grid_name, **reader_kwargs)
            #keep fallback option for filename when weights/areas block is not present in the configuration

            # check if weights already exist, if not, generate them
            if rebuild or not os.path.exists(weights_filename):
                
                # smmregrid call
                generator = CdoGenerate(source_grid=self.src_grid_path[vertical_dim],
                                target_grid=self.cfg_grid_dict['grids'][dst_grid_name],
                                cdo_download_path=None,
                                cdo_icon_grids=None,
                                cdo_extra=cdo_extra,
                                cdo_options=cdo_options,
                                cdo='cdo',
                                loglevel=self.loglevel)
                
                # define the vertical coordinate in the smmregrid world
                smm_vert_coord = None if vertical_dim in ['2d', '2dm'] else vertical_dim

                # generate and save the weights
                weights = generator.weights(method="con", vert_coord=smm_vert_coord, nproc=1)
                weights.to_netcdf(weights_filename)

            else:
                # load the weights
                weights = xr.open_dataset(weights_filename)

            # initialize the regridder
            self.regridder[vertical_dim] = Regridder(weights=weights)
        
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




