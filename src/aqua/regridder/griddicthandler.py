"""Basic grid dictionary handling."""

from smmregrid.util import is_cdo_grid
from aqua.logger import log_configure
from .regridder_util import check_existing_file


class GridDictHandler:
    """Class to handle AQUA grid dictionaries."""

    def __init__(self, cfg_grid_dict, default_dimension='2d', loglevel='WARNING'):
        self.cfg_grid_dict = cfg_grid_dict
        self.default_dimension = default_dimension
        self.loglevel = loglevel
        self.logger = log_configure(log_level=loglevel, log_name='Regridder')

    def normalize_grid_dict(self, grid_name):
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

        if not isinstance(grid_name, (str, dict)):
            raise ValueError(f"Grid name '{grid_name}' is not a valid type.")

        # if a grid name is a valid CDO grid name, return it in the format of a dictionary
        if is_cdo_grid(grid_name):
            self.logger.debug("Grid name %s is a valid CDO grid name.", grid_name)
            return {"path": {self.default_dimension: grid_name}}

        # raise error if the grid does not exist
        grid_dict = self.cfg_grid_dict['grids'].get(grid_name)
        if not grid_dict:
            raise ValueError(f"Grid name '{grid_name}' not found in the configuration.")

        # grid dict is a string: this is the case of a CDO grid name
        if isinstance(grid_dict, str):
            if is_cdo_grid(grid_dict):
                self.logger.debug("Grid definition %s is a valid CDO grid name.", grid_dict)
                return {"path": {self.default_dimension: grid_dict}}
            raise ValueError(f"Grid name '{grid_dict}' is not a valid CDO grid name.")
        if isinstance(grid_dict, dict):
            return grid_dict

    def normalize_grid_path(self, grid_dict):
        """
        Normalize the grid path to a dictionary with the self.default_dimension key.
        3 cases handled: 
            - an empty dictionary, return an empty dictionary
            - a dictionary with a path string, a CDO grid name or a file path
            - a dictionary with a dictionary of path, one for each vertical coordinate

        Args:
            path (str, dict): The grid path.
            data (xarray.Dataset): The dataset to extract grid information from.

        Returns:
            dict: The normalized grid path dictionary. "self.default_dimension" key is mandatory.
        """

        # if empty, return an empty dictionary
        path = grid_dict.get('path')
        if path is None:
            return {}

        # case path is a string: check if it is a valid CDO grid name or a file path
        if isinstance(path, str):
            if is_cdo_grid(path):
                self.logger.debug("Grid path %s is a valid CDO grid name.", path)
                return {self.default_dimension: path}
            if check_existing_file(path):
                self.logger.debug("Grid path %s is a valid file path.", path)
                return {self.default_dimension: path}
            raise FileNotFoundError(f"Grid file '{path}' does not exist.")

        # case path is a dictionary: check if the values are valid file paths
        # (could extend to CDO names?)
        if isinstance(path, dict):
            for _, value in path.items():
                if not (is_cdo_grid(value) or check_existing_file(value)):
                    raise ValueError(f"Grid path '{value}' is not a valid CDO grid name nor a file path.")
            self.logger.debug("Grid path %s is a valid dictionary of file paths.", path)
            return path

        raise ValueError(f"Grid path '{path}' is not a valid type.")
