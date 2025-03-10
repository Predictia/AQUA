"""New Regrid class independent from the Reader"""
import os
import re
import xarray as xr
from smmregrid import CdoGenerate, Regridder
from smmregrid.util import is_cdo_grid, check_gridfile
from aqua.logger import log_configure

# parameters which will affect the weights and areas name
DEFAULT_WEIGHTS_AREAS_PARAMETERS = ['zoom']

# please notice: is_cdo_grid and check_gridfile are functions from smmregrid.util
# to check if a string is a valid CDO grid name and if a grid is a cdo grid, 
# file on the disk or xarray dataset. Possible inclusion of CDOgrid object is considered
# but should be developed on the smmregrid side.

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
            data (xarray.Dataset, optional): The dataset to be regridded, 
                                   to be provided in src_grid_path is missing.
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
        
        # we want all the grid dictionary to be real dictionaries
        self.src_grid_dict = self._normalize_grid_dict(self.src_grid_dict)

        self.regridder = {} # regridders for each vertical coordinate
        self.src_grid_area = None # source grid area
        self.dst_grid_area = None # destination grid area

        # we want all the grid path dictionary to be real dictionaries
        self.src_grid_path = self.src_grid_dict.get('path')
        self._normalize_grid_path(self.src_grid_path, data)

        self.logger.info("Grid name: %s", self.src_grid_name)
        self.logger.info("Grid file path: %s", self.src_grid_path)
    
    def _normalize_grid_dict(self, grid):
        """
        Normalize the grid dictionary to a dictionary with the 2d key.
        """

        # grid dict is a string: this is the case of a CDO grid name
        if isinstance(grid, str):
            if is_cdo_grid(grid):
                self.logger.info("Grid definition %s is a valid CDO grid name.", grid)
                return {"path": {"2d": grid}}
            raise ValueError(f"Grid '{grid}' is not a valid CDO grid name.")
        if isinstance(grid, dict):
            return grid
        raise ValueError(f"Grid definition '{grid}' is not a valid type")

    def _normalize_grid_path(self, path, data=None):
        """
        Normalize the grid path to a dictionary with the 2d key.
        3 cases handled: 
            - a dictionary with a path string, a CDO grid name or a file path
            - a dictionary with a dictionary of path, one for each vertical coordinate
            - a dictionary without path with data provided, to get info from the dataset

        Args:
            path (str, dict): The grid path.
            data (xarray.Dataset): The dataset to extract grid information from.
        
        Returns:
            dict: The normalized grid path dictionary. "2d" key is mandatory.
        """

        # case path is a string: check if it is a valid CDO grid name or a file path
        if isinstance(path, str):
            if is_cdo_grid(path):
                self.logger.info("Grid path %s is a valid CDO grid name.", path)
                return {"2d": path}
            if self._check_existing_file(path):
                self.logger.info("Grid path %s is a valid file path.", path)
                return {"2d": path}
            raise FileNotFoundError(f"Grid file '{path}' does not exist.")

        # case path is a dictionary: check if the values are valid file paths
        # (could extend to CDO names?)
        if isinstance(path, dict):
            for _, value in path.items():
                if not (is_cdo_grid(value) or self._check_existing_file(value)):
                    raise ValueError(f"Grid path '{value}' is not a valid CDO grid name nor a file path.")
            self.logger.info("Grid path %s is a valid dictionary of file paths.", path)
            return path

        # grid path is None: check if data is provided to extract information for CDO
        if path is None:
            if data is not None:
                self.logger.info("Using provided dataset for grid path.")
                return {"2d": data}
            raise ValueError("Grid path missing in config and no sample data provided.")

        raise ValueError(f"Grid path '{path}' is not a valid type.")
    
    def load_generate_areas(self, dst_grid_name=None, rebuild=False, reader_kwargs=None):
        """
        Load or generate regridding areas by calling the appropriate function.
        """
        if dst_grid_name:
            return self._generate_target_areas(dst_grid_name, rebuild, reader_kwargs)
        return self._generate_source_areas(rebuild, reader_kwargs)
        
    def _generate_source_areas(self, rebuild=False, reader_kwargs=None):
        """
        Generate or load source grid areas.

        Args:
            rebuild (bool): If True, rebuild the areas.
            reader_kwargs (dict): The reader kwargs, including info on model, exp, source, etc.
        """
        area_filename = self._area_filename(None, reader_kwargs)

        if not rebuild and self._check_existing_file(area_filename):
            self.logger.info("Loading existing source area from %s.", area_filename)
            self.src_grid_area = xr.open_dataset(area_filename)
            return

        # if cell ino are provide in the grid dictionary, use them
        cellareas = self.src_grid_dict.get('cellareas')
        cellareas_var = self.src_grid_dict.get('cellareas_var')
        if cellareas and cellareas_var:
            self.logger.info("Using cellareas from variable %s in file %s", cellareas_var, cellareas)
            grid_area = xr.open_mfdataset(cellareas)[cellareas_var].rename("cell_area").squeeze()

        # otherwise, generate the areas with smmregrid
        else:
            self.logger.info("Generating source area for %s", self.src_grid_name)
            generator = CdoGenerate(
                source_grid=self._get_grid_path(self.src_grid_path), # get the 2d grid path
                target_grid=None,
                cdo_extra=self.src_grid_dict.get('cdo_extra'),
                cdo_options=self.src_grid_dict.get('cdo_options'),
                cdo='cdo',
                loglevel=self.loglevel
            )
            grid_area = generator.areas(target=False)

        grid_area.to_netcdf(area_filename)
        self.logger.info("Saved source area to %s.", area_filename)
        self.src_grid_area = grid_area

    def _generate_target_areas(self, dst_grid_name, rebuild=False, reader_kwargs=None):
        """
        Generate or load target grid areas.

        Args:
            dst_grid_name (str): The destination grid name.
            rebuild (bool): If True, rebuild the areas.
            reader_kwargs (dict): The reader kwargs, including info on model, exp, source, etc.
        """

        # normalize the dst grid dictionary and path
        dst_grid_dict = self._normalize_grid_dict(self.cfg_grid_dict['grids'].get(dst_grid_name))
        dst_grid_path = self._normalize_grid_path(dst_grid_dict.get('path'))

        area_filename = self._area_filename(dst_grid_name, reader_kwargs)

        if not rebuild and self._check_existing_file(area_filename):
            self.logger.info("Loading existing target area from %s.", area_filename)
            self.dst_grid_area = xr.open_dataset(area_filename)
            return

        self.logger.info("Generating target area for %s", dst_grid_name)
        generator = CdoGenerate(
            source_grid=None,
            target_grid=self._get_grid_path(dst_grid_path),
            cdo_extra=dst_grid_dict.get('cdo_extra'),
            cdo_options=dst_grid_dict.get('cdo_options'),
            cdo='cdo',
            loglevel=self.loglevel
        )
        grid_area = generator.areas(target=True)

        grid_area.to_netcdf(area_filename)
        self.logger.info("Saved target area to %s.", area_filename)
        self.dst_grid_area = grid_area
        
    def load_generate_weights(self, dst_grid_name, regrid_method="con", nproc=1,
                              rebuild=False, reader_kwargs=None):
        """
        Load or generate regridding weights calling smmregrid

        Args:
            dst_grid_name (str): The destination grid name.
            regrid_method (str): The regrid method.
            nproc (int): The number of processors to use.
            rebuild (bool): If True, rebuild the weights.
            reader_kwargs (dict): The reader kwargs, including info on model, exp, source, etc.
        """

        # get the cdo options from the configuration
        cdo_extra = self.src_grid_dict.get('cdo_extra', None)
        cdo_options = self.src_grid_dict.get('cdo_options', None)

        # loop over the vertical coordinates: 2d, 2dm, or any other
        for vertical_dim in self.src_grid_path:

            weights_filename = self._weights_filename(dst_grid_name, regrid_method, 
                                                      vertical_dim, reader_kwargs)

            # check if weights already exist, if not, generate them
            if rebuild or not self._check_existing_file(weights_filename):
                
                self.logger.info("Generating weights for %s grid: %s", dst_grid_name, vertical_dim)
                # smmregrid call
                generator = CdoGenerate(source_grid=self.src_grid_path[vertical_dim],
                                target_grid=self.cfg_grid_dict['grids'][dst_grid_name],
                                cdo_extra=cdo_extra,
                                cdo_options=cdo_options,
                                cdo='cdo',
                                loglevel=self.loglevel)
                
                # define the vertical coordinate in the smmregrid world
                smm_vert_coord = None if vertical_dim in ['2d', '2dm'] else vertical_dim

                # generate and save the weights
                weights = generator.weights(method=regrid_method,
                                            vert_coord=smm_vert_coord,
                                            nproc=nproc)
                weights.to_netcdf(weights_filename)

            else:
                self.logger.info("Loading existing weights from %s.", weights_filename)
                # load the weights
                weights = xr.open_dataset(weights_filename)

            # initialize the regridder
            self.regridder[vertical_dim] = Regridder(weights=weights)

    def _area_filename(self, dst_grid_name, reader_kwargs):
        """"
        Generate the area filename.
        
        Args:
            dst_grid_name (str): The destination grid name.
            reader_kwargs (dict): The reader kwargs, including info on model, exp, source, etc.
        """

        area_dict = self.cfg_grid_dict.get('areas')

        # destination grid name is provided, use grid template
        if dst_grid_name:
            filename = area_dict["template_grid"].format(grid=dst_grid_name)
            self.logger.debug("Using grid-based template for target grid. Filename: %s", filename)
        # source grid name is provided, check if it is data
        else:
            if check_gridfile(self.src_grid_path['2d']) != 'xarray':
                filename = area_dict["template_grid"].format(grid=self.src_grid_name)
                self.logger.debug("Using grid-based template for source grid. Filename: %s", filename)
            else:
                filename =  area_dict["template_default"].format(model=reader_kwargs["model"],
                                                                 exp=reader_kwargs["exp"],
                                                                 source=reader_kwargs["source"])
                self.logger.debug("Using source-based template for source grid. Filename: %s", filename)

        filename = self._insert_kwargs(filename, reader_kwargs)
        filename = self._filename_prepend_path(filename, kind="areas")
        return filename

    def _weights_filename(self, dst_grid_name, regrid_method, vertical_dim, reader_kwargs):
        """
        Generate the weights filename.

        Args:
            dst_grid_name (str): The destination grid name.
            regrid_method (str): The regrid method.
            vertical_dim (str): The vertical dimension.
            reader_kwargs (dict): The reader kwargs, including info on model, exp, source, etc.
        """

        levname = vertical_dim if vertical_dim in ["2d", "2dm"] else f"3d-{vertical_dim}"

        weights_dict = self.cfg_grid_dict.get('weights')

        # destination grid name is provided, use grid template
        if check_gridfile(self.src_grid_path[vertical_dim]) != 'xarray':
            filename = weights_dict["template_grid"].format(
                sourcegrid=self.src_grid_name,
                method=regrid_method,
                targetgrid=dst_grid_name,
                level=levname)
            self.logger.debug("Using grid-based template for target grid. Filename: %s", filename)
        else:
            filename = weights_dict["weights"]["template_default"].format(
                model=reader_kwargs["model"],
                exp=reader_kwargs["exp"],
                source=reader_kwargs["source"],
                method=regrid_method,
                targetgrid=dst_grid_name,
                level=levname)
            self.logger.debug("Using source-based template for target grid. Filename: %s", filename)

        filename = self._insert_kwargs(filename, reader_kwargs)
        filename = self._filename_prepend_path(filename, kind="weights")
        return filename
    
    def _filename_prepend_path(self, filename, kind="weights"):
        """
        Prepend the path to the filename with some fall back option
        """
        if not self.cfg_grid_dict.get("paths"):
            self.logger.warning("Paths block not found in the configuration file, using present directory.")
        else:
            if not self.cfg_grid_dict["paths"].get(kind):
                self.logger.warning("%s block not found in the paths block, using present directory.", kind)
            else:
                filename = os.path.join(self.cfg_grid_dict["paths"][kind], filename)
        return filename

    @staticmethod
    def _insert_kwargs(filename, reader_kwargs):
        """
        Insert the DEFAULT_WEIGHTS_AREAS_PARAMETERS in the filename template.
        """
        # add the kwargs naming in the template file
        if isinstance(reader_kwargs, dict):
            for parameter in DEFAULT_WEIGHTS_AREAS_PARAMETERS:
                if parameter in reader_kwargs:
                    filename = re.sub(r'\.nc',
                                    '_' + parameter + str(reader_kwargs[parameter]) + r'\g<0>',
                                    filename)

        return filename
    
    @staticmethod
    def _get_grid_path(grid_path):
        """
        Get the grid path from the grid dictionary.
        This looks for `2d` key, otherwise takes the first available value.
        """
        return grid_path.get('2d', next(iter(grid_path.values()), None))
    
    @staticmethod
    def _check_existing_file(filename):
        """
        Checks if an area/weights file exists and is valid.
        Return true if the file has some records.
        """
        return os.path.exists(filename) and os.path.getsize(filename) > 0
        
        
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




