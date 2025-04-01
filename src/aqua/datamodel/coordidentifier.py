"""
Module to identify the nature of coordinates of an Xarray object.
"""

from metpy.units import units

# Define the target dimensionality (pressure)
pressure_dim = units.pascal.dimensionality

# Function to check if a unit is a pressure unit
def is_isobaric(unit):
    """Check if a unit is a pressure unit."""
    if unit is None:
        return False
    if unit in units:
        return units(unit).dimensionality == pressure_dim

class CoordIdentifier():
    """
    Class to identify the nature of coordinates of an Xarray object.
    It aims at detecting the longitude, latitude, time and any other vertical
    by inspecting the attributes of the coordinates provided by the user.
    """

    def __init__(self, coords):
        """
        Constructor of the CoordIdentifier class.
        """
        self.coords = coords

        # internal name definition for the coordinates
        self.coord_dict = {
            "latitude": None,
            "longitude": None,
            "time": None,
            "isobaric": None
        }

    def identify_coords(self):
        """
        Identify the coordinates of the Xarray object.
        """
        for name, coord in self.coords.items():
            if not self.coord_dict["latitude"]:
                if self._identify_latitude(coord):
                    self.coord_dict["latitude"] = self._get_attributes(coord)
            if not self.coord_dict["longitude"]:
                if self._identify_longitude(coord):
                    self.coord_dict["longitude"] = self._get_attributes(coord)
            if not self.coord_dict["isobaric"]:
                if self._identify_isobaric(coord):
                    self.coord_dict["isobaric"] = self._get_attributes(coord)
            if not self.coord_dict["time"]:
                time = self._identify_time(name)
                if time:
                    self.coord_dict["time"] = time

        return self.coord_dict
    
    def _get_attributes(self, coord):
        """
        Get the attributes of the coordinate.
        """
        coord_range = (coord.values.min(),  coord.values.max())
        direction = "increasing" if coord.values[-1] > coord.values[0] else "decreasing"
        return {'name': coord.name,
                'units': coord.attrs.get('units', None),
                'direction': direction,
                'range': coord_range}      

    @staticmethod
    def _identify_latitude(coord):
        """
        Identify the latitude coordinate of the Xarray object.
        """
        if coord.name in ["latitude", "lat", "nav_lat"]:
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
        if coord.name in ["longitude", "lon", "nav_lon"]:
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
        if coord in ["time", "valid_time"]:
            return coord
        return None
    
    @staticmethod
    def _identify_isobaric(coord):
        """
        Identify the isobaric coordinate of the Xarray object.
        """
        if coord.name in ["plev"]:
            return True
        if is_isobaric(coord.attrs.get("units")):
            return True
        return False
    
    

