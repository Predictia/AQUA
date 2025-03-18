"""AQUA class for field statitics"""
import xarray as xr

from aqua.logger import log_configure, log_history
from aqua.util import area_selection

class FldStat():
    """AQUA class for field statitics"""

    def __init__(self, area, horizontal_dims=None, grid_name=None, loglevel='WARNING'):
        """
        Initialize the FldStat.

        Args:
            area (str): The area to calculate the statistics for.
            loglevel (str): The logging level.
        """

        self.loglevel = loglevel
        self.logger = log_configure(log_level=loglevel, log_name='FldStat')
        self.area = area

        if self.area is None:
            self.logger.warning("No area provided, no weighted area can be provided.")
            return

        # safety checks
        if not isinstance(area, (xr.DataArray, xr.Dataset)):
            raise ValueError("Area must be an xarray DataArray or Dataset.")
        
        # TODO: add a guess with smmregrid GridInspector
        if horizontal_dims is None:
            self.logger.warning("No horizontal coordinates provided, using default ['lon', 'lat'].")
            horizontal_dims = ['lon', 'lat']
        self.horizontal_dims = horizontal_dims
        self.logger.debug('Space coordinates are %s', self.horizontal_dims)
        self.grid_name = grid_name

        
    def fldmean(self, data, lon_limits=None, lat_limits=None, **kwargs):
        """
        Perform a weighted global average.
        If a subset of the data is provided, the average is performed only on the subset.

        Arguments:
            data (xr.DataArray or xarray.DataDataset):  the input data
            lon_limits (list, optional):  the longitude limits of the subset
            lat_limits (list, optional):  the latitude limits of the subset

        Kwargs:
            - box_brd (bool,opt): choose if coordinates are comprised or not in area selection.
                                  Default is True

        Returns:
            the value of the averaged field
        """

        if not isinstance(data, (xr.DataArray, xr.Dataset)):
            raise ValueError("Data must be an xarray DataArray or Dataset.")

        if self.area is None:
            return data.mean(dim=self.horizontal_dims)

        if lon_limits is not None or lat_limits is not None:
            data = area_selection(data, lon=lon_limits, lat=lat_limits,
                                  loglevel=self.loglevel, **kwargs)

        # cleaning coordinates which have "multiple" coordinates in their own definition
        # grid_area = self._clean_spourious_coords(grid_area, name = "area")
        # data = self._clean_spourious_coords(data, name = "data")

        # check if coordinates are aligned
        try:
            xr.align(self.area, data, join='exact')
        except ValueError as err:
            raise ValueError('Coordinates are not aligned!') from err
            # # check in the dimensions what is wrong
            # for coord in grid_area.coords:
            #     if coord in space_coord:
            #         xcoord = data.coords[coord]

            #         # first case: shape different
            #         if len(grid_area[coord]) != len(xcoord):
            #             raise ValueError(f'{coord} has different shape between area files and your dataset.'
            #                              'If using the LRA, try setting the regrid=r100 option') from err
            #         # shape are ok, but coords are different
            #         if not grid_area[coord].equals(xcoord):
            #             # if they are fine when sorted, there is a sorting mismatch
            #             if grid_area[coord].sortby(coord).equals(xcoord.sortby(coord)):
            #                 self.logger.warning('%s is sorted in different way between area files and your dataset. Flipping it!',
            #                                     coord)
            #                 grid_area = grid_area.reindex({coord: list(reversed(grid_area[coord]))})
            #             else:
            #                 raise ValueError(f'{coord} has a mismatch in coordinate values!') from err

        self.logger.debug('Computing the weighted average over f{self.horizontal_dims}')
        out = data.weighted(weights=self.area.fillna(0)).mean(dim=self.horizontal_dims)

        if self.grid_name is not None:
            log_history(data, f"Spatially averaged by fldmean from {self.grid_name} grid")

        return out
