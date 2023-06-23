""" The module contains a simple example of the class for Tier 2 dummy diagnostic. 

.. moduleauthor:: AQUA team <dummy_developer>

"""

class DummyDiagnostic:
    """This class is a minimal version of the Dummy Diagnostic.
    """
    def __init__(self,
            trop_lat = 10, 
            s_year      = None,
            f_year      = None, 
            s_month     = None,
            f_month     = None):
        
        
        """ The constructor of the class.

        Args:
            trop_lat (int or float, optional):      The latitude of the tropical zone. Defaults to 10.
            s_year (int, optional):                 The start year of the time interval. Defaults to None.
            f_year (int, optional):                 The end year of the time interval. Defaults to None.
            s_month (int, optional):                The start month of the time interval. Defaults to None.
            f_month (int, optional):                The end month of the time interval. Defaults to None."""

        

        self.trop_lat   = trop_lat  
        self.s_year     = s_year
        self.f_year     = f_year   
        self.s_month    = s_month
        self.f_month    = f_month    

    def class_attributes_update(self, trop_lat = None, 
                          s_year = None, f_year = None, s_month = None, f_month = None):
        """ Function to update the class attributes.
        
        :param trop_lat: the latitude of the tropical zone
        :type trop_lat: int or float
        
        :param s_year: the start year of the time interval
        :type s_year: int
        
        :param f_year: the end year of the time interval
        :type f_year: int
        
        :param s_month: the start month of the time interval
        :type s_month: int
        
        :param f_month: the end month of the time interval
        :type f_month: int"""
        
        if trop_lat is not None and isinstance(trop_lat, (int, float)):        
            self.trop_lat = trop_lat
        elif trop_lat is not None and not isinstance(trop_lat, (int, float)):
            raise Exception("trop_lat must to be integer or float")
        
        if s_year is not None and isinstance(s_year, int):          
            self.s_year = s_year
        elif s_year is not None and not isinstance(s_year, int):
            raise Exception("s_year must to be integer")
        
        if f_year is not None and isinstance(f_year, int):          
            self.f_year = f_year
        elif f_year is not None and not isinstance(f_year, int):
            raise Exception("f_year must to be integer")
        
        if s_month is not None and isinstance(s_month, int):         
            self.s_month = s_month
        elif s_month is not None and not isinstance(s_month, int):
            raise Exception("s_month must to be integer")
        
        if f_month is not None and isinstance(f_month, int):         
            self.f_month = f_month
        elif f_month is not None and not isinstance(f_month, int):
            raise Exception("f_month must to be integer")     

    
    def latitude_band(self, data, trop_lat=None): 
        """ Function to select the Dataset for specified latitude range

        Args:
            data (xarray):                  The Dataset
            trop_lat (int/float, optional): The maximumal and minimal tropical latitude values in Dataset.  Defaults to None.

        Returns:
            xarray: The Dataset only for selected latitude range. 
        """    
        
        
        self.class_attributes_update( trop_lat=trop_lat )
        return data.where(abs(data.lat) <= self.trop_lat, drop=True)  
    
    def time_band(self, data, s_year = None, f_year = None, s_month = None, f_month = None): 
        """ Function to select the Dataset for specified time range

        Args:
            data (xarray):                  The Dataset
            s_year (str, optional):         The starting year of the Dataset.  Defaults to None.
            f_year (str, optional):         The ending year of the Dataset.  Defaults to None.
            s_month (str, optional):        The starting month of the Dataset.  Defaults to None.
            f_month (str, optional):        The ending month of the Dataset.  Defaults to None.

        Raises:
            Exception: "s_year and f_year must to be integer"
            Exception: "s_month and f_month must to be integer"

        Returns:
            xarray: The Dataset only for selected time range. 
        """   

        self.class_attributes_update(s_year=s_year, f_year=f_year, s_month=s_month, f_month=f_month)

        if self.s_year != None and self.f_year == None:
            if isinstance(s_year, int):
                data= data.where(data['time.year'] == self.s_year, drop=True)
            else:
                raise Exception("s_year must to be integer")
        elif self.s_year != None and self.f_year != None:
            if isinstance(s_year, int) and isinstance(f_year, int): 
                data = data.where(data['time.year'] >= self.s_year, drop=True)
                data = data.where(data['time.year'] <= self.f_year, drop=True)
            else:
                raise Exception("s_year and f_year must to be integer") 
        if self.s_month != None and self.f_month != None:
            if isinstance(s_month, int) and isinstance(f_month, int): 
                data = data.where(data['time.month'] >= self.s_month, drop=True)
                data = data.where(data['time.month'] <= self.f_month, drop=True)  
            else:
                raise Exception("s_month and f_month must to be integer") 
        return data 