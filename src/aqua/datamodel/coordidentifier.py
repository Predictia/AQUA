"""
Module to identify the nature of coordinates of an Xarray object.
"""

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
            "time": None
        }

    def identify_coords(self):
        """
        Identify the coordinates of the Xarray object.
        """
        for coord in self.coords:
            if not self.coord_dict["latitude"]:
                if self._identify_latitude(self.coords[coord]):
                    self.coord_dict["latitude"] = self._get_horizontal_attributes(coord)
            if not self.coord_dict["longitude"]:
                if self._identify_longitude(self.coords[coord]):
                    self.coord_dict["longitude"] = self._get_horizontal_attributes(coord)
            if not self.coord_dict["time"]:
                time = self._identify_time(coord)
                if time:
                    self.coord_dict["time"] = time

        return self.coord_dict
    
    def _get_horizontal_attributes(self, coord):
        """
        Get the attributes of the coordinate.
        """

        coord_range = (self.coords[coord].values.min(),  self.coords[coord].values.max())
        direction = "increasing" if coord_range[1] > coord_range[0] else "decreasing"
        return {'name': coord,
                'units': self.coords[coord].attrs.get('units', None),
                'direction': direction,
                'range': coord_range}      

    @staticmethod
    def _identify_latitude(coord):
        """
        Identify the latitude coordinate of the Xarray object.
        """
        if coord.name in ["latitude", "lat"]:
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
        if coord.name in ["longitude", "lon"]:
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

    

