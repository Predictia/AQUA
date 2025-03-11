"""New Regrid class independent from the Reader"""
import os
import re
import shutil
import xarray as xr
from smmregrid import CdoGenerate, GridInspector
from smmregrid import Regridder as SMMRegridder
from smmregrid.util import is_cdo_grid, check_gridfile
from aqua.logger import log_configure

# parameters which will affect the weights and areas name
DEFAULT_WEIGHTS_AREAS_PARAMETERS = ['zoom']

# default CDO regrid method
DEFAULT_GRID_METHOD = 'ycon'

# default dimension for the weights and areas
DEFAULT_DIMENSION = '2d'
DEFAULT_DIMENSION_MASK = '2dm' #masked grid

# please notice: is_cdo_grid and check_gridfile are functions from smmregrid.util
# to check if a string is a valid CDO grid name and if a grid is a cdo grid,
# file on the disk or xarray dataset. Possible inclusion of CDOgrid object is considered
# but should be likely developed on the smmregrid side.

class Regridder():
    """AQUA Regridder class"""

    def __init__(self, cfg_grid_dict: dict,
                 src_grid_name: str = None,
                 data: xr.Dataset = None,
                 loglevel: str = "WARNING"):
        """
        The TurboRegrid constructor. Can be initialized with a dataset or a grid name

        Args:
            cfg_grid_dict (dict): The dictionary containing the full AQUA grid configuration.
            src_grid_name (str, optional): The name of the source grid in the AQUA convention.
            data (xarray.Dataset, optional): The dataset to be regridded, 
                                   to be provided in src_grid_path is missing.
            loglevel (str): The logging level.
        """

        if src_grid_name is None and data is None:
            raise ValueError("Either src_grid_name or data must be provided.")

        self.loglevel = loglevel
        self.logger = log_configure(log_level=loglevel, log_name='Regridder')

        # define basic attributes:
        self.cfg_grid_dict = cfg_grid_dict  # full grid dictionary
        self.src_grid_name = src_grid_name  # source grid name

        # we want all the grid dictionary to be real dictionaries
        self.src_grid_dict = self._normalize_grid_dict(self.src_grid_name)
        self.src_grid_path = self._normalize_grid_path(self.src_grid_dict)

        # grid path is None: check if data is provided to extract information for CDO
        if data is not None:
            self.logger.info("Using provided dataset as a grid path.")
            self.src_grid_path = {DEFAULT_DIMENSION: data}

        # check if the grid path has been defined
        if not self.src_grid_path:
            # self.error can be used by the Reader to check if the grid is valid
            self.error = "Source grid path not found. Please provide a dataset or a grid name."
            self.logger.info(self.error)
            return

        # check if CDO is available
        self.cdo = self._set_cdo()

        self.regridder = {}  # regridders for each vertical coordinate
        self.src_grid_area = None  # source grid area
        self.tgt_grid_area = None  # destination grid area

        # configure the masked fields
        self.masked_attrs, self.masked_vars = self._configure_masked_fields(
            self.src_grid_dict)

        self.logger.info("Grid name: %s", self.src_grid_name)
        self.logger.info("Grid dictionary: %s", self.src_grid_dict)
        self.logger.debug("Grid file path dictionary: %s", self.src_grid_path)

    def _set_cdo(self):
        """
        Check information on CDO to set the correct version
        """

        cdo = shutil.which("cdo")
        if cdo:
            self.logger.debug("Found CDO path: %s", cdo)
        else:
            self.logger.error(
                "CDO not found in path: Weight and area generation will fail.")

        return cdo

    def _normalize_grid_dict(self, grid_name):
        """
        Validate the grid name and return the grid dictionary.
        4 cases handled:
            - None, return an empty dictionary
            - a valid CDO grid name
            - a grid name in the configuration, again a valid CDO grid name
            - a grid dictionary in the configuration

        Args:
            grid_name (str): The grid name.

        Returns:
            dict: The normalized grid dictionary.
        """

        # if empty, return an empty dictionary
        if grid_name is None:
            return {}

        # if a grid name is a valid CDO grid name, return it in the format of a dictionary
        if is_cdo_grid(grid_name):
            self.logger.debug(
                "Grid name %s is a valid CDO grid name.", grid_name)
            return {"path": {DEFAULT_DIMENSION: grid_name}}

        # raise error if the grid does not exist
        grid_dict = self.cfg_grid_dict['grids'].get(
            grid_name)  # source grid dictionary
        if not grid_dict:
            raise ValueError(
                f"Grid '{grid_name}' not found in the configuration.")

        # grid dict is a string: this is the case of a CDO grid name
        if isinstance(grid_dict, str):
            if is_cdo_grid(grid_dict):
                self.logger.debug(
                    "Grid definition %s is a valid CDO grid name.", grid_dict)
                return {"path": {DEFAULT_DIMENSION: grid_dict}}
            raise ValueError(
                f"Grid '{grid_dict}' is not a valid CDO grid name.")
        if isinstance(grid_dict, dict):
            return grid_dict

        raise ValueError(f"Grid dict '{grid_dict}' is not a valid type")

    def _normalize_grid_path(self, grid_dict):
        """
        Normalize the grid path to a dictionary with the DEFAULT_DIMENSION key.
        3 cases handled: 
            - an empty dictionary, return an empty dictionary
            - a dictionary with a path string, a CDO grid name or a file path
            - a dictionary with a dictionary of path, one for each vertical coordinate

        Args:
            path (str, dict): The grid path.
            data (xarray.Dataset): The dataset to extract grid information from.

        Returns:
            dict: The normalized grid path dictionary. "DEFAULT_DIMENSION" key is mandatory.
        """

        # if empty, return an empty dictionary
        path = grid_dict.get('path')
        if path is None:
            return {}

        # case path is a string: check if it is a valid CDO grid name or a file path
        if isinstance(path, str):
            if is_cdo_grid(path):
                self.logger.debug(
                    "Grid path %s is a valid CDO grid name.", path)
                return {DEFAULT_DIMENSION: path}
            if self._check_existing_file(path):
                self.logger.debug("Grid path %s is a valid file path.", path)
                return {DEFAULT_DIMENSION: path}
            raise FileNotFoundError(f"Grid file '{path}' does not exist.")

        # case path is a dictionary: check if the values are valid file paths
        # (could extend to CDO names?)
        if isinstance(path, dict):
            for _, value in path.items():
                if not (is_cdo_grid(value) or self._check_existing_file(value)):
                    raise ValueError(
                        f"Grid path '{value}' is not a valid CDO grid name nor a file path.")
            self.logger.debug(
                "Grid path %s is a valid dictionary of file paths.", path)
            return path

        raise ValueError(f"Grid path '{path}' is not a valid type.")

    def load_generate_areas(self, tgt_grid_name=None, rebuild=False, reader_kwargs=None):
        """
        Load or generate regridding areas by calling the appropriate function.
        """
        if tgt_grid_name:

            # normalize the tgt grid dictionary and path
            tgt_grid_dict = self._normalize_grid_dict(tgt_grid_name)
            tgt_grid_path = self._normalize_grid_path(tgt_grid_dict)
            self.tgt_grid_area = self._load_generate_areas(
                tgt_grid_name, tgt_grid_path, tgt_grid_dict,
                reader_kwargs, target=True, rebuild=rebuild)
        else:

            self.src_grid_area = self._load_generate_areas(
                self.src_grid_name, self.src_grid_path, self.src_grid_dict,
                reader_kwargs, target=False, rebuild=rebuild)

    def _load_generate_areas(self, grid_name, grid_path, grid_dict, reader_kwargs,
                             target=False, rebuild=False):
        """"
        Load or generate the grid area.

        Args:
            grid_name (str): The grid name.
            grid_path (dict): The normalized grid path dictionary.
            grid_dict (dict): The normalized grid dictionary.
            reader_kwargs (dict): The reader kwargs, including info on model, exp, source, etc.
            target (bool): If True, the target grid area is generated. If false, the source grid area is generated.
            rebuild (bool): If True, rebuild the area.

        Returns:
            xr.Dataset: The grid area.
        """

        area_filename = self._area_filename(
            grid_name if target else None, reader_kwargs)
        area_logname = "target" if target else "source"

        if not rebuild and self._check_existing_file(area_filename):
            self.logger.info("Loading existing %s area from %s.",
                             area_logname, area_filename)
            grid_area = xr.open_dataset(area_filename)
            return grid_area

        # if cellares are provided in the grid dictionary, use them
        cellareas = grid_dict.get('cellareas')
        cellareas_var = grid_dict.get('cellareas_var')
        if cellareas and cellareas_var:
            self.logger.info("Using cellareas from variable %s in file %s",
                             cellareas_var, cellareas)
            grid_area = xr.open_mfdataset(
                cellareas)[cellareas_var].rename("cell_area").squeeze()

        # otherwise, generate the areas with smmregrid
        else:
            self.logger.info("Generating %s area for %s",
                             area_logname, grid_name)
            generator = CdoGenerate(
                # get the DEFAULT_DIMENSION grid path if available, otherwise the first available, only if source grid
                source_grid=None if target else self._get_grid_path(grid_path),
                # get the DEFAULT_DIMENSION grid path if available, otherwise the first available, only if target grid
                target_grid=self._get_grid_path(grid_path) if target else None,
                cdo_extra=grid_dict.get('cdo_extra'),
                cdo_options=grid_dict.get('cdo_options'),
                cdo=self.cdo,
                loglevel=self.loglevel
            )
            grid_area = generator.areas(target=target)

        grid_area.to_netcdf(area_filename)
        self.logger.info("Saved %s area to %s.", area_logname, area_filename)

        return grid_area

    def load_generate_weights(self, tgt_grid_name, regrid_method=DEFAULT_GRID_METHOD, nproc=1,
                              rebuild=False, reader_kwargs=None):
        """
        Load or generate regridding weights calling smmregrid

        Args:
            tgt_grid_name (str): The destination grid name.
            regrid_method (str): The regrid method.
            nproc (int): The number of processors to use.
            rebuild (bool): If True, rebuild the weights.
            reader_kwargs (dict): The reader kwargs for filename definition, 
                                  including info on model, exp, source, etc.
        """

        # define regrid method
        if regrid_method is not DEFAULT_GRID_METHOD:
            self.logger.info("Regrid method: %s", regrid_method)

        # normalize the tgt grid dictionary and path
        tgt_grid_dict = self._normalize_grid_dict(tgt_grid_name)
        tgt_grid_path = self._normalize_grid_path(tgt_grid_dict)

        # get the cdo options from the configuration
        cdo_extra = self.src_grid_dict.get('cdo_extra', None)
        cdo_options = self.src_grid_dict.get('cdo_options', None)

        # loop over the vertical coordinates: DEFAULT_DIMENSION, DEFAULT_DIMENSION_MASK, or any other
        for vertical_dim in self.src_grid_path:

            weights_filename = self._weights_filename(tgt_grid_name, regrid_method,
                                                      vertical_dim, reader_kwargs)

            # check if weights already exist, if not, generate them
            if rebuild or not self._check_existing_file(weights_filename):

                # clean if necessary
                if os.path.exists(weights_filename):
                    self.logger.warning(
                        "Weights file %s exists. Regenerating.", weights_filename)
                    os.remove(weights_filename)

                self.logger.info(
                    "Generating weights for %s grid: %s", tgt_grid_name, vertical_dim)
                # smmregrid call
                generator = CdoGenerate(source_grid=self.src_grid_path[vertical_dim],
                                        # this seems counterintuitive, 
                                        # but CDO-based target grids are defined with DEFAULT_DIMENSION
                                        target_grid=self._get_grid_path(tgt_grid_path),
                                        cdo_extra=cdo_extra,
                                        cdo_options=cdo_options,
                                        cdo=self.cdo,
                                        loglevel=self.loglevel)

                # define the vertical coordinate in the smmregrid world
                smm_vert_coord = None if vertical_dim in [
                    DEFAULT_DIMENSION, DEFAULT_DIMENSION_MASK] else vertical_dim

                # minimum time warning
                if smm_vert_coord:
                    self.logger.warning(
                        'Vertical coordinate detected, computation of weights may take longer.')

                # generate and save the weights
                weights = generator.weights(method=regrid_method,
                                            vert_coord=smm_vert_coord,
                                            nproc=nproc)
                weights.to_netcdf(weights_filename)

            else:
                self.logger.info(
                    "Loading existing weights from %s.", weights_filename)
                # load the weights
                weights = xr.open_dataset(weights_filename)

            # initialize the regridder
            self.regridder[vertical_dim] = SMMRegridder(weights=weights)

    def _area_filename(self, tgt_grid_name, reader_kwargs):
        """"
        Generate the area filename.

        Args:
            tgt_grid_name (str): The destination grid name.
            reader_kwargs (dict): The reader kwargs, including info on model, exp, source, etc.
        """

        area_dict = self.cfg_grid_dict.get('areas')

        # destination grid name is provided, use grid template
        if tgt_grid_name:
            filename = area_dict["template_grid"].format(grid=tgt_grid_name)
            self.logger.debug(
                "Using grid-based template for target grid. Filename: %s", filename)
        # source grid name is provided, check if it is data
        else:
            if check_gridfile(self._get_grid_path(self.src_grid_path)) != 'xarray':
                filename = area_dict["template_grid"].format(
                    grid=self.src_grid_name)
                self.logger.debug(
                    "Using grid-based template for source grid. Filename: %s", filename)
            else:
                reader_kwargs = self._validate_reader_kwargs(reader_kwargs)
                filename = area_dict["template_default"].format(model=reader_kwargs["model"],
                                                                exp=reader_kwargs["exp"],
                                                                source=reader_kwargs["source"])
                self.logger.debug(
                    "Using source-based template for source grid. Filename: %s", filename)

        filename = self._insert_kwargs(filename, reader_kwargs)
        filename = self._filename_prepend_path(filename, kind="areas")
        return filename

    def _weights_filename(self, tgt_grid_name, regrid_method, vertical_dim, reader_kwargs):
        """
        Generate the weights filename.

        Args:
            tgt_grid_name (str): The destination grid name.
            regrid_method (str): The regrid method.
            vertical_dim (str): The vertical dimension.
            reader_kwargs (dict): The reader kwargs, including info on model, exp, source, etc.
        """

        levname = vertical_dim if vertical_dim in [
            DEFAULT_DIMENSION, DEFAULT_DIMENSION_MASK] else f"3d-{vertical_dim}"

        weights_dict = self.cfg_grid_dict.get('weights')

        # destination grid name is provided, use grid template
        if check_gridfile(self.src_grid_path[vertical_dim]) != 'xarray':
            filename = weights_dict["template_grid"].format(
                sourcegrid=self.src_grid_name,
                method=regrid_method,
                targetgrid=tgt_grid_name,
                level=levname)
            self.logger.debug(
                "Using grid-based template for target grid. Filename: %s", filename)
        else:
            reader_kwargs = self._validate_reader_kwargs(reader_kwargs)
            filename = weights_dict["template_default"].format(
                model=reader_kwargs["model"],
                exp=reader_kwargs["exp"],
                source=reader_kwargs["source"],
                method=regrid_method,
                targetgrid=tgt_grid_name,
                level=levname)
            self.logger.debug(
                "Using source-based template for target grid. Filename: %s", filename)

        filename = self._insert_kwargs(filename, reader_kwargs)
        filename = self._filename_prepend_path(filename, kind="weights")
        return filename

    def _filename_prepend_path(self, filename, kind="weights"):
        """
        Prepend the path to the filename with some fall back option
        """
        if not self.cfg_grid_dict.get("paths"):
            self.logger.warning(
                "Paths block not found in the configuration file, using present directory.")
        else:
            if not self.cfg_grid_dict["paths"].get(kind):
                self.logger.warning(
                    "%s block not found in the paths block, using present directory.", kind)
            else:
                filename = os.path.join(
                    self.cfg_grid_dict["paths"][kind], filename)
        return filename
    
    def _group_shared_dims(self, data):
        """
        Groups variables in a dataset that share the same dimension.
        Built on GridInspector and GridType classes from smmregrid.
        It is a sort of overkill of what smmregrid do internally.
        """
        gridtype = GridInspector(data).get_grid_info()
        shared_vars = {}
        for grid in gridtype:
            variables = list(grid.variables.keys())
            
            # Ensure masked variables are stored
            if self.masked_vars:
                shared_vars[DEFAULT_DIMENSION_MASK] = self.masked_vars

            # Get the masked variables safely
            masked_vars = shared_vars.get(DEFAULT_DIMENSION_MASK, [])

            if grid.vertical_dim:
                shared_vars[grid.vertical_dim] = [var for var in variables if var not in masked_vars]
            else:
                shared_vars[DEFAULT_DIMENSION] = [var for var in variables if var not in masked_vars]

        return shared_vars

    def regrid(self, data):
        """
        Actual regridding core function. Regrid the dataset or dataarray using common gridtypes

        Args:
            data (xarray.Dataset, xarray.DataArray): The dataset to be regridded.
        """

        # get which variables share the same dimensions
        shared_vars = self._group_shared_dims(data)

        # compact regridding on all dataset with map
        # not working with vertical coordinates subselection
        if isinstance(data, xr.Dataset):
            out = data.map(self._apply_regrid, shared_vars=shared_vars)
        else:
            out = self._apply_regrid(data, shared_vars)
        return out

    def _apply_regrid(self, data, shared_vars):
        """
        Core regridding function. 
        Apply regridding on the different vertical coordinates, including 2dm
        """

        for vertical, variables in shared_vars.items():
            if data.name in variables:
                return self.regridder[vertical].regrid(data)
        return data

    # this static method can be moved to an external module or downgraded to functions
    @staticmethod
    def _insert_kwargs(filename, reader_kwargs):
        """
        Insert the DEFAULT_WEIGHTS_AREAS_PARAMETERS in the filename template.
        """
        # add the kwargs naming in the template file
        if isinstance(reader_kwargs, dict):
            for parameter in DEFAULT_WEIGHTS_AREAS_PARAMETERS:
                if parameter in reader_kwargs:
                    filename = re.sub(
                        r'\.nc', '_' + parameter +
                        str(reader_kwargs[parameter]) + r'\g<0>',
                        filename)

        return filename

    @staticmethod
    def _validate_reader_kwargs(reader_kwargs):
        """
        Validate the reader kwargs.
        """
        if not reader_kwargs:
            raise ValueError("reader_kwargs must be provided.")
        for key in ["model", "exp", "source"]:
            if key not in reader_kwargs:
                raise ValueError(f"reader_kwargs must contain key '{key}'.")
        return reader_kwargs

    @staticmethod
    def _get_grid_path(grid_path):
        """
        Get the grid path from the grid dictionary.
        This looks for `DEFAULT_DIMENSION` key, otherwise takes the first available value in the dict.
        """
        return grid_path.get(DEFAULT_DIMENSION, next(iter(grid_path.values()), None))

    @staticmethod
    def _check_existing_file(filename):
        """
        Checks if an area/weights file exists and is valid.
        Return true if the file has some records.
        """
        return os.path.exists(filename) and os.path.getsize(filename) > 0

    @staticmethod
    def _configure_masked_fields(src_grid_dict):
        """
        if the grids has the 'masked' option, this can be based on
        generic attribute or alternatively of a series of specific variables using the 'vars' key

        Args:
            source_grid (dict): Dictionary containing the grid information

        Returns:
            masked_attr (dict): Dict with name and proprierty of the attribute to be used for masking
            masked_vars (list): List of variables to mask
        """
        masked_info = src_grid_dict.get("masked")
        if masked_info is None:
            return None, None

        masked_vars = masked_info.get("vars")
        masked_attrs = {k: v for k, v in masked_info.items() if k !=
                       "vars"} or None

        return masked_attrs, masked_vars

    # def _configure_gridtype(self, data=None):
    #     """
    #     Configure the GridType object based on the grid_dict.
    #     """

    #     # DEFAULT_DIMENSION and DEFAULT_DIMENSION_MASK should be passed to GridType and GridInspector as extra vert_dims
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
