"""
Module to identify the nature of coordinates of an Xarray object.
"""
import xarray as xr
from metpy.units import units

from aqua.logger import log_configure

LATITUDE = ["latitude", "lat", "nav_lat"]
LONGITUDE = ["longitude", "lon", "nav_lon"]
TIME = ["time", "valid_time"]
ISOBARIC = ["plev"]
DEPTH = ["depth", "zlev"]

# Define the target dimensionality (pressure)
pressure_dim = units.pascal.dimensionality
#meter_dim = units.meter.dimensionality

# Function to check if a unit is a pressure unit
def is_isobaric(unit):
    """Check if a unit is a pressure unit."""
    if unit is None:
        return False
    if unit in units:
        return units(unit).dimensionality == pressure_dim
    return False

class CoordIdentifier():
    """
    Class to identify the nature of coordinates of an Xarray object.
    It aims at detecting the longitude, latitude, time and any other vertical
    by inspecting the attributes of the coordinates provided by the user.
    """

    def __init__(self, coords, loglevel='WARNING'):
        """
        Constructor of the CoordIdentifier class.
        """
        self.loglevel = loglevel
        self.logger = log_configure(self.loglevel, 'CoordIdentifier')

        if not isinstance(coords, xr.Coordinates):
            raise TypeError("coords must be an Xarray Coordinates object.")
        self.coords = coords

        # internal name definition for the coordinates
        self.coord_dict = {
            "latitude": None,
            "longitude": None,
            "time": None,
            "isobaric": None,
            "depth": None
        }

    def identify_coords(self):
        """
        Identify the coordinates of the Xarray object.
        """
        for name, coord in self.coords.items():
            self.logger.debug("Identifying coordinate: %s", name)
            if not self.coord_dict["latitude"] and self._identify_latitude(coord):
                    self.coord_dict["latitude"] = self._get_horizontal_attributes(coord)
            if not self.coord_dict["longitude"] and self._identify_longitude(coord):
                    self.coord_dict["longitude"] = self._get_horizontal_attributes(coord)
            if not self.coord_dict["isobaric"] and self._identify_isobaric(coord):
                    self.coord_dict["isobaric"] = self._get_vertical_attributes(coord)
            if not self.coord_dict["depth"] and self._identify_depth(coord):
                    self.coord_dict["depth"] = self._get_vertical_attributes(coord)
            # TODO: improve time detection
            if not self.coord_dict["time"]:
                time = self._identify_time(name)
                if time:
                    self.coord_dict["time"] = time

        return self.coord_dict
    
    def _get_horizontal_attributes(self, coord):
        """
        Get the attributes of the coordinate.
        """
        coord_range = (coord.values.min(),  coord.values.max())
        direction = "increasing" if coord.values[-1] > coord.values[0] else "decreasing"
        return {'name': coord.name,
                'units': coord.attrs.get('units', None),
                'direction': direction,
                'range': coord_range}    

    def _get_vertical_attributes(self, coord):
        """
        Get the attributes of the coordinate.
        """
        coord_range = (coord.values.min(),  coord.values.max())
        positive = coord.attrs.get('positive')
        # TODO: check how set correctly the positive attribute
        if not positive:
            positive = "down" if coord.values[0] > 0  else "up"
        return {'name': coord.name,
                'units': coord.attrs.get('units', None),
                'positive': positive,
                'range': coord_range}  

    @staticmethod
    def _identify_latitude(coord):
        """
        Identify the latitude coordinate of the Xarray object.
        """
        if coord.name in LATITUDE:
            return True
        if coord.attrs.get("axis") == "Y":
            return True
        if coord.attrs.get("units") == "degrees_north":
            return True
        return False
    
    @staticmethod
    def _identify_longitude(coord):
        """
        Identify the longitude coordinate of the Xarray object.
        """
        if coord.name in LONGITUDE:
            return True
        if coord.attrs.get("axis") == "X":
            return True
        if coord.attrs.get("units") == "degrees_east":
            return True
        return False
    
    @staticmethod
    def _identify_time(coord):
        """
        Identify the time coordinate of the Xarray object.
        """
        if coord in TIME:
            return coord
        return None
    
    @staticmethod
    def _identify_isobaric(coord):
        """
        Identify the isobaric coordinate of the Xarray object.
        """
        if coord.name in ISOBARIC:
            return True
        if coord.attrs.get("standard_name") == "air_pressure":
            return True
        if is_isobaric(coord.attrs.get("units")):
            return True
        return False
    
    @staticmethod
    def _identify_depth(coord):
        """
        Identify the depth coordinate of the Xarray object.
        """
        if coord.name in DEPTH:
            return True
        if coord.attrs.get("standard_name") == "depth":
            return True
        if "depth" in coord.attrs.get("long_name", ""):
            return True
        if coord.attrs.get("units") in ["m", "meters"]:
            return True
        return False
    
    

