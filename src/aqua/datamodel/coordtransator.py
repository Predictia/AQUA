"""Module to transform coordinates of an Xarray object."""

import xarray as xr
from aqua.logger import log_configure
from .coordidentifier import CoordIdentifier



TGT_COORDS = {
    "latitude": {
        "name": "lat",
        "direction": "decreasing",
    },
    "longitude": {
        "name": "lon",
        "direction": "increasing",
    }
}

ATTR_LIST = {
    "latitude": {
        "axis": "Y"
    },
    "longitude": {
        "axis": "X"
    },
    "time": {
        "axis": "T"
    }
}

class CoordTransator():
    """
    Class to transform coordinates of an Xarray object.
    It aims at transforming the coordinates provided by the user into
    a standard format.
    """

    def __init__(self, data, loglevel='WARNING'):
        """
        Constructor of the CoordTransator class.
        """
        if not isinstance(data, (xr.Dataset, xr.DataArray)):
            raise TypeError("data must be an Xarray Dataset or DataArray object.")
        self.loglevel = loglevel
        self.logger = log_configure(self.loglevel, 'CoordTransator')
        self.data = data
        self.src_coords = CoordIdentifier(data.coords).identify_coords()
        #self.logger.info("Source coordinates: %s", self.src_coords)
        self.tgt_coords = None
        self.gridtype = self._info_grid(data.coords)
        self.logger.info("Grid type: %s", self.gridtype)

    def _info_grid(self, coords):
        """
        Identify the grid type of the Xarray object.
        Regular, Curvilinear or Unstructured can be identified.
        """

        latname = self.src_coords.get('latitude', {}).get('name', None)
        lonname = self.src_coords.get('longitude', {}).get('name', None)
        if not latname in coords or not lonname in coords:
            return "Unknown"
        lat = coords[latname]
        lon = coords[lonname]
        if lon.ndim == 2 and lat.ndim == 2:
            return "Curvilinear"
        if lon.dims != lat.dims:
            return "Regular"
        return "Unstructured"
    
    def transform_coords(self, tgt_coords=None):
        """
        Trasforma le coordinate dell'oggetto Xarray.

        Args:
            tgt_coords (dict, optional): Dizionario delle coordinate target. Defaults to None.

        Returns:
            xr.Dataset or xr.DataArray: Il dataset o dataarray trasformato.
        """
        if tgt_coords is None:
            self.logger.info("No target coordinates provided. Using default coordinates.")
            tgt_coords = TGT_COORDS
        elif not isinstance(tgt_coords, dict):
            raise TypeError("tgt_coords must be a dictionary.")
        self.tgt_coords = tgt_coords

        data = self.data

        for coord in self.tgt_coords:
            tgt_coord = self.tgt_coords[coord]
            if coord in self.src_coords and self.src_coords[coord]:
                src_coord = self.src_coords[coord]      
                data = self.rename_coordinate(data, src_coord, tgt_coord)
                data = self.reverse_coordinate(data, src_coord, tgt_coord)
                data = self.assign_attributes(data, coord, tgt_coord)
            else:
                self.logger.warning("Coordinate %s not found in source coordinates.", coord)

        return data
    
    def rename_coordinate(self, data, src_coord, tgt_coord):
        """
        Rename coordinate if necessary.
        """
        if src_coord['name'] != tgt_coord['name']:
            self.logger.info("Renaming coordinate %s to %s",
                            src_coord['name'], tgt_coord['name'])
            data = data.rename({src_coord['name']: tgt_coord['name']})
        return data

    def reverse_coordinate(self, data, src_coord, tgt_coord):
        """
        Reverse coordinate if necessary.
        """
        if tgt_coord['direction'] not in ["increasing", "decreasing"]:
            raise ValueError("tgt_coord['direction'] must be 'increasing' or 'decreasing'.")
        if src_coord['direction'] not in ["increasing", "decreasing"]:
            self.logger.warning("src_coord['direction'] is not 'increasing' or 'decreasing'. Disabling reverse")
            return data
        if src_coord['direction'] != tgt_coord['direction']:
            if self.gridtype == "Regular":
                self.logger.info("Reversing coordinate %s from %s to %s",
                                tgt_coord['name'], src_coord['direction'], tgt_coord['direction'])
                data = data.isel({tgt_coord['name']: slice(None, None, -1)})
            else:
                self.logger.warning("Cannot reverse coordinate %s. Grid type is %s.",
                                    tgt_coord['name'], self.gridtype)
        return data

    def assign_attributes(self, data, coord, tgt_coord):
        """
        Assign attributes to the coordinate.
        """
        for attr in ATTR_LIST[coord]:
            if attr not in data.coords[tgt_coord['name']].attrs:
                self.logger.info("Adding attribute %s to coordinate %s", attr, tgt_coord['name'])
                data.coords[tgt_coord['name']].attrs[attr] = ATTR_LIST[coord][attr]
        return data
    