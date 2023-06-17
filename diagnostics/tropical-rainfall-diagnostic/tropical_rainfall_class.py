from datetime import datetime
import numpy as np
import xarray as xr
import pickle
import re

from os import listdir
from os.path import isfile, join

import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.ticker import PercentFormatter

import fast_histogram 
import boost_histogram as bh #pip
import dask.array as da
import dask_histogram as dh # pip
import dask_histogram.boost as dhb
import dask
 


"""The module contains Tropical Precipitation Diagnostic:

.. moduleauthor:: AQUA team <natalia.nazarova@polito.it>

"""

class TR_PR_Diagnostic:
    """This class is a minimal version of the Tropical Precipitation Diagnostic.
    """
    def class_attributes_update(self,   trop_lat = None,  s_time = None, f_time = None,  
                          s_year = None, f_year = None, s_month = None, f_month = None, 
                          num_of_bins = None, first_edge = None, width_of_bin = None, bins=0):
        """ Function to update the class attributes.
        
        :param trop_lat: the latitude of the tropical zone
        :type trop_lat: int or float
        
        :param s_time: the start time of the time interval
        :type s_time: int or str
        
        :param f_time: the end time of the time interval
        :type f_time: int or str
        
        :param s_year: the start year of the time interval
        :type s_year: int
        
        :param f_year: the end year of the time interval
        :type f_year: int
        
        :param s_month: the start month of the time interval
        :type s_month: int
        
        :param f_month: the end month of the time interval
        :type f_month: int
        
        :param num_of_bins: the number of bins
        :type num_of_bins: int
        
        :param first_edge: the first edge of the bin
        :type first_edge: int or float"""
        
        if trop_lat is not None and isinstance(trop_lat, (int, float)):        
            self.trop_lat = trop_lat
        elif trop_lat is not None and not isinstance(trop_lat, (int, float)):
            raise Exception("trop_lat must to be integer or float")
        
        if s_time is not None and isinstance(s_time, (int, str)):          
            self.s_time = s_time
        elif s_time is not None and not isinstance(s_time, (int, str)):
            raise Exception("s_time must to be integer or string")
        
        if f_time is not None and isinstance(f_time, (int, str)):          
            self.f_time = f_time
        elif f_time is not None and not isinstance(f_time, (int, str)):
            raise Exception("f_time must to be integer or string")
        
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
        
        if num_of_bins is not None and isinstance(num_of_bins, int):
            self.num_of_bins = num_of_bins
        elif num_of_bins is not None and not isinstance(num_of_bins, int):
            raise Exception("num_of_bins must to be integer")
        
        if first_edge is not None and isinstance(first_edge, (int, float)):
            self.first_edge = first_edge
        elif first_edge is not None and not isinstance(first_edge, (int, float)):
            raise Exception("first_edge must to be integer or float") 
        
        if width_of_bin is not None and isinstance(width_of_bin, (int, float)):
            self.width_of_bin = width_of_bin
        elif width_of_bin is not None and not isinstance(width_of_bin, (int, float)):
            raise Exception("width_of_bin must to be integer or float")

        if bins!=0 and isinstance(bins, np.ndarray):
            self.bins = bins            
        elif bins!=0 and not isinstance(bins, (np.ndarray, list)):
            raise Exception("bins must to be array")


    def __init__(self,
            trop_lat = 10, 
            s_time      = None, 
            f_time      = None, 
            s_year      = None,
            f_year      = None, 
            s_month     = None,
            f_month     = None, 
            num_of_bins = None, 
            first_edge  = None, 
            width_of_bin= None,
            bins        = 0):
        
        
        """ The constructor of the class.

        Args:
            trop_lat (int or float, optional):      The latitude of the tropical zone. Defaults to 10.
            s_time (int or str, optional):          The start time of the time interval. Defaults to None.
            f_time (int or str, optional):          The end time of the time interval. Defaults to None.
            s_year (int, optional):                 The start year of the time interval. Defaults to None.
            f_year (int, optional):                 The end year of the time interval. Defaults to None.
            s_month (int, optional):                The start month of the time interval. Defaults to None.
            f_month (int, optional):                The end month of the time interval. Defaults to None.
            num_of_bins (int, optional):            The number of bins. Defaults to None.
            first_edge (int or float, optional):    The first edge of the bin. Defaults to None.
            width_of_bin (int or float, optional):  The width of the bin. Defaults to None.
            bins (np.ndarray, optional):            The bins. Defaults to 0."""

        

        self.trop_lat   = trop_lat  
        self.s_time     = s_time
        self.f_time     = f_time  
        self.s_year     = s_year
        self.f_year     = f_year   
        self.s_month    = s_month
        self.f_month    = f_month         
        self.num_of_bins    = num_of_bins
        self.first_edge     = first_edge
        self.width_of_bin   = width_of_bin
        self.bins           = bins
    
    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ 
    def coordinate_names(self, data):
        """ Function to get the names of the coordinates."""
        coord_lat, coord_lon = None, None

        if 'Dataset' in str(type(data)): 
            for i in data._coord_names:
                if 'lat' in i:
                    coord_lat = i
                if 'lon' in i:
                    coord_lon = i 
        elif 'DataArray' in str(type(data)):
            for i in data.coords:
                if 'lat' in i:
                    coord_lat = i
                if 'lon' in i:
                    coord_lon = i 
        return coord_lat, coord_lon

    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ 
    def precipitation_units_converter(self, data, variable_1 ='tprate', new_unit='m s**-1'):
        """ Function to convert the units of precipitation.

        Args:
            data (xarray):                  The Dataset
            variable_1 (str, optional):     The name of the variable to be converted. Defaults to 'tprate'.
            new_unit (str, optional):       The new unit of the variable. Defaults to 'm s**-1'.

        Returns:
            xarray: The Dataset with converted units.
        """    
        if data[variable_1].units==new_unit:
            return data
        else:
            if data[variable_1].units=='m':
                if new_unit=='m s**-1':
                    data_copy=data.copy(deep=True)
                    data_copy[variable_1].values = data_copy[variable_1].values/(60*60*24)
            elif data[variable_1].units=='m s**-1':
                if new_unit=='m':
                    data_copy=data.copy(deep=True)
                    data_copy[variable_1].values = data_copy[variable_1].values*(60*60*24)
                
            data_copy[variable_1].attrs['units']=new_unit
            return data_copy
    
        
    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ 
    def latitude_band(self, data, trop_lat=None): 
        """ Function to select the Dataset for specified latitude range

        Args:
            data (xarray):                  The Dataset
            trop_lat (int/float, optional): The maximumal and minimal tropical latitude values in Dataset.  Defaults to None.

        Raises:
            Exception: "trop_lat must to be integer"

        Returns:
            xarray: The Dataset only for selected latitude range. 
        """    
        
        
        self.class_attributes_update( trop_lat=trop_lat )
        
        coord_lat, coord_lon = self.coordinate_names(data)
        self.class_attributes_update( trop_lat=trop_lat )
        return data.where(abs(data[coord_lat]) <= self.trop_lat, drop=True)  
    


    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ 
    def time_band(self, data,  s_time = None, f_time = None, s_year = None, f_year = None,
        s_month = None, f_month = None): 
        """ Function to select the Dataset for specified time range

        Args:
            data (xarray):                  The Dataset
            s_time (str, optional):         The starting time of the Dataset.  Defaults to None.
            f_time (str, optional):         The ending time of the Dataset.  Defaults to None.
            s_year (str, optional):         The starting year of the Dataset.  Defaults to None.
            f_year (str, optional):         The ending year of the Dataset.  Defaults to None.
            s_month (str, optional):        The starting month of the Dataset.  Defaults to None.
            f_month (str, optional):        The ending month of the Dataset.  Defaults to None.

        Raises:
            Exception: "s_time and f_time must to be integer"
            Exception: "s_year and f_year must to be integer"
            Exception: "s_month and f_month must to be integer"

        Returns:
            xarray: The Dataset only for selected time range. 
        """          
        self.class_attributes_update( s_time=s_time,  f_time=f_time, s_year=s_year, f_year=f_year, s_month=s_month, f_month=f_month)

        if isinstance(self.s_time, int) and isinstance(self.f_time, int): 
            if self.s_time != None and self.f_time != None:
                data = data.isel(time=slice(self.s_time, self.f_time))
        elif self.s_year != None and self.f_year == None:
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
        
        if isinstance(self.s_time, str) and isinstance(self.f_time, str):
            if  s_time != None and f_time != None:
                _s = re.split(r"[^a-zA-Z0-9\s]", s_time)
                _f = re.split(r"[^a-zA-Z0-9\s]", f_time)  
                if len(_s)==1:
                    s_time=_s[0]
                elif len(_f)==1:
                    f_time=_f[0]

                elif len(_s)==2:
                    s_time=_s[0]+'-'+_s[1]
                elif len(_f)==2:
                    f_time=_f[0]+'-'+_f[1]

                elif len(_s)==3:
                    s_time=_s[0]+'-'+  _s[1] +'-'+_s[2]
                elif len(_f)==3:
                    f_time=_f[0]+'-'+  _f[1] +'-'+ _f[2] 

                elif len(_s)==4:
                    s_time=_s[0]+'-'+  _s[1] +'-'+_s[2]+'-'+_s[3]
                elif len(_f)==4:
                    f_time=_f[0]+'-'+  _f[1] +'-'+ _f[2] +'-'+ _f[3]

                elif len(_s)==5:
                    s_time=_s[0] +'-'+  _s[1] +'-'+_s[2]+'-'+_s[3] +'-'+_s[4]
                elif len(_f)==5:
                    f_time=_f[0] +'-'+  _f[1] +'-'+ _f[2] +'-'+ _f[3] +'-'+ _f[4]  
                else:
                    raise Exception("Sorry, unknown format of time. Try one more time")  
            data=data.sel(time=slice(s_time, f_time))    
        elif self.s_time != None and  self.f_time == None:
            if isinstance(s_year, str): 
                _temp = re.split(r"[^a-zA-Z0-9\s]", s_time)
                if len(_temp)==1:
                    time=_temp[0]
                elif len(_temp)==2:
                    time=_temp[0]+'-'+_temp[1]
                elif len(_temp)==3:
                    time=_temp[0]+'-'+_temp[1]+'-'+_temp[2]
                elif len(_temp)==3:
                    time=_temp[0]+'-'+_temp[1]+'-'+_temp[2]+'-'+_temp[3] 
                elif len(_temp)==4:
                    time=_temp[0]+'-'+_temp[1]+'-'+_temp[2]+'-'+_temp[3]+'-'+_temp[4]  
                elif len(_temp)==5:
                    time=_temp[0]+'-'+_temp[1]+'-'+_temp[2]+'-'+_temp[3]+'-'+_temp[4]+'-'+_temp[5]  
                else:
                    raise Exception("Sorry, unknown format of time. Try one more time")    
                data=data.sel(time=slice(time))
        return data

    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ 
    def dataset_into_1d(self, data, variable_1 = 'tprate', sort = False): 
        """ Function to convert Dataset into 1D array.

        Args:
            data (xarray):                  The Dataset
            variable_1 (str, optional):     The variable of the Dataset. Defaults to 'tprate'.
            sort (bool, optional):          The flag to sort the array. Defaults to False.

        Returns:
            xarray: The 1D array.
        """ 
           
        coord_lat, coord_lon = self.coordinate_names(data)

        try: 
            data = data[variable_1]
        except KeyError:
            data = data 

        try:
            data_1d  = data.stack(total=['time', coord_lat, coord_lon])  # 
        except KeyError:
            data_1d  = data.stack(total=[coord_lat, coord_lon])
        if sort == True:
            data_1d  = data_1d.sortby(data_1d)
        return data_1d

  
    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """
    def preprocessing(self, data, preprocess = True,  variable_1="tprate", trop_lat=None, 
                       s_time = None, f_time = None,  
                       s_year = None, f_year = None, s_month = None, f_month = None, sort = False, dask_array = False):
        """Preprocessing the Dataset

        Args:
            data (xarray):                  The Dataset.
            preprocess (bool, optional):    If sort is True, the functiom preprocess Dataset. Defaults to True.
            variable_1 (str, optional):     The variable of the Dataset. Defaults to 'tprate'.
            trop_lat (float, optional):     The maximumal and minimal tropical latitude values in Dataset.  Defaults to None.
            s_time (str/int, optional):     The starting time value/index in Dataset. Defaults to None.
            f_time (str/int, optional):     The final time value/index in Dataset. Defaults to None.
            s_year (int, optional):         The starting year in Dataset. Defaults to None.
            f_year (int, optional):         The final year in Dataset. Defaults to None.
            s_month (int, optional):        The starting month in Dataset. Defaults to None.
            f_month (int, optional):        The final month in Dataset. Defaults to None.
            sort (bool, optional):          If sort is True, the DataArray is sorted. Defaults to False.
            dask_array (bool, optional):    If sort is True, the function return daskarray. Defaults to False.

        Returns:
            xarray: Preprocessed Dataset according to the arguments of the function
        """        
        
        self.class_attributes_update(trop_lat=trop_lat,  s_time=s_time, f_time=f_time,  
                               s_year=s_year, f_year=f_year, s_month=s_month, f_month=f_month)
        if preprocess == True:
            if 'time' in data.coords:
                data_per_time_band = self.time_band(data, s_time=self.s_time, f_time=self.f_time, 
                                        s_year=self.s_year, f_year=self.f_year, s_month=self.s_month, f_month=self.f_month)
            else:
                data_per_time_band = data
            
            try: 
                data_variable = data_per_time_band[variable_1]
            except KeyError: 
                data_variable = data_per_time_band

            data_per_lat_band = self.latitude_band(data_variable, trop_lat=self.trop_lat)
            
            if dask_array == True:
                data_1d = self.dataset_into_1d(data_per_lat_band)
                dask_data = da.from_array(data_1d)
                return dask_data
            else:
                return data_per_lat_band
        else:
            return data
    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ 
    def histogram(self, data, preprocess = True,   trop_lat = 10, variable_1 = 'tprate',   weights = None, 
                  data_with_global_atributes=None,
                  s_time = None, f_time = None, s_year = None, f_year = None, s_month = None, f_month = None, 
                  num_of_bins = None, first_edge = None,  width_of_bin  = None,   bins=0, 
                  dask = False, lazy=False, create_xarray=True, path_to_save=None):
        """Function to create a histogram of the Dataset

        Args:
            data (xarray):                  The Dataset.
            preprocess (bool, optional):    If sort is True, the functiom preprocess Dataset. Defaults to True.
            trop_lat (float, optional):     The maximumal and minimal tropical latitude values in Dataset.  Defaults to 10.
            variable_1 (str, optional):     The variable of the Dataset. Defaults to 'tprate'.
            weights (array, optional):      The weights of the data. Defaults to None.
            data_with_global_atributes (xarray, optional): The Dataset with global atributes. Defaults to None.
            s_time (str/int, optional):     The starting time value/index in Dataset. Defaults to None.
            f_time (str/int, optional):     The final time value/index in Dataset. Defaults to None.
            s_year (int, optional):         The starting year in Dataset. Defaults to None.
            f_year (int, optional):         The final year in Dataset. Defaults to None.

        Returns:
            xarray: Histogram of the Dataset
        """
               
        if lazy:
            if weights is not None:
                hist_counts=self.dask_factory_weights(data=data, weights=weights, preprocess=preprocess,  
                                                      trop_lat=trop_lat,  variable_1=variable_1,  
                                                      s_time=s_time, f_time=f_time,
                                                      s_year=s_year, f_year=f_year, s_month=s_month, f_month=f_month, 
                                                      num_of_bins=num_of_bins, first_edge=first_edge,  
                                                      width_of_bin=width_of_bin,  bins=bins,   
                                                      lazy=lazy)
            else:
                hist_counts=self.dask_factory(data=data, preprocess = preprocess,   
                                                  trop_lat = trop_lat,  variable_1 = variable_1,  
                                                  s_time = s_time , f_time = f_time, 
                                                  s_year = s_year, f_year = f_year, s_month = s_month, f_month = f_month, 
                                                  num_of_bins = num_of_bins, first_edge = first_edge,  
                                                  width_of_bin  = width_of_bin,   bins =bins, 
                                                  lazy=lazy)


        elif weights is not None:
            if bins!=0 or self.bins!=0: #dask:
                hist_counts=self.hist1d_np(data=data, weights=weights, preprocess=preprocess,   
                                            trop_lat=trop_lat, variable_1=variable_1,  
                                            s_time=s_time, f_time = f_time,   
                                            s_year = s_year, f_year =f_year, s_month = s_month, f_month = f_month, 
                                            num_of_bins=num_of_bins, first_edge=first_edge,  
                                            width_of_bin=width_of_bin,  bins=bins)
            else:
                hist_counts=self.dask_factory_weights(data=data, weights=weights, preprocess=preprocess,  
                                                      trop_lat=trop_lat,  variable_1=variable_1,  
                                                      s_time=s_time, f_time=f_time,
                                                      s_year=s_year, f_year=f_year, s_month=s_month, f_month=f_month, 
                                                      num_of_bins=num_of_bins, first_edge=first_edge,  
                                                      width_of_bin=width_of_bin,  bins=bins,   
                                                      lazy=lazy)
        else:
            if dask:
                #if lazy:
                #    hist_counts=self.dask_factory(data=data, preprocess = preprocess,   
                #                                  trop_lat = trop_lat,  variable_1 = variable_1,  
                #                                  s_time = s_time , f_time = f_time, 
                #                                  s_year = s_year, f_year = f_year, s_month = s_month, f_month = f_month, 
                #                                  num_of_bins = num_of_bins, first_edge = first_edge,  
                #                                  width_of_bin  = width_of_bin,   bins =bins, 
                #                                  lazy=lazy)
                #else:
                hist_counts=self.dask_boost(data=data, preprocess=preprocess, 
                                            trop_lat=trop_lat,  variable_1=variable_1,  
                                            s_time=s_time, f_time=f_time, 
                                            s_year=s_year, f_year=f_year, s_month=s_month, f_month=f_month, 
                                            num_of_bins=num_of_bins, first_edge=first_edge, 
                                            width_of_bin=width_of_bin,  bins=bins)
            elif bins!=0 or self.bins!=0:
                hist_counts=self.hist1d_np(data=data, weights=weights, preprocess=preprocess,   
                                           trop_lat=trop_lat, variable_1=variable_1,  
                                           s_time=s_time, f_time = f_time,   
                                           s_year = s_year, f_year =f_year, s_month = s_month, f_month = f_month, 
                                           num_of_bins=num_of_bins, first_edge=first_edge,  
                                           width_of_bin=width_of_bin,  bins=bins)
            else:
                hist_counts=self.hist1d_fast(data=data, preprocess=preprocess,   
                                             trop_lat=trop_lat, variable_1=variable_1,  
                                             s_time=s_time, f_time=f_time, 
                                             s_year=s_year, f_year=f_year, s_month=s_month, f_month=f_month, 
                                             num_of_bins=num_of_bins, first_edge=first_edge,  
                                             width_of_bin=width_of_bin,  bins=bins)
                
        if data_with_global_atributes is None:
            data_with_global_atributes=data

        if not lazy and create_xarray:
            tprate_dataset = self.histogram_to_xarray(hist_counts=hist_counts, path_to_save=path_to_save, data_with_global_atributes=data_with_global_atributes)
            
            data_with_final_grid=self.preprocessing(data=data, preprocess=preprocess,   trop_lat=trop_lat, variable_1=variable_1, 
                                                    s_time=s_time, f_time=f_time, 
                                                    s_year=s_year, f_year=f_year, s_month=s_month, f_month=f_month, 
                                                    sort = False, dask_array = False)
            for variable in (None, 'counts', 'frequency', 'pdf'):
                tprate_dataset=self.grid_attributes(data=data_with_final_grid, tprate_dataset=tprate_dataset, variable=variable)
            return tprate_dataset
        else:
            return hist_counts
        
    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ 
    def save_histogram(self, dataset=None, path_to_save=None, name_of_file=None):
        """ Function to save the histogram.

        Args:
            dataset (xarray, optional): The Dataset with the histogram. Defaults to None.
            path_to_save (str, optional): The path to save the histogram. Defaults to None.

        Returns:
            str: The path to save the histogram.
        """
        if path_to_save is not None and name_of_file is not None:
            time_band=dataset.counts.attrs['time_band']
            try:
                name_of_file = name_of_file +'_'+ re.split(":", re.split(", ", time_band)[0])[0]+'_' + re.split(":", re.split(", ", time_band)[1])[0]
            except IndexError:
                name_of_file = name_of_file +'_'+ re.split("'", re.split(":", time_band)[0])[1]
            path_to_save = path_to_save + name_of_file + '_histogram.pkl'
        
        if path_to_save is not None:
            with open(path_to_save, 'wb') as output:
                pickle.dump(dataset, output)
        return path_to_save
    
    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ 
    def grid_attributes(self, data=None, tprate_dataset=None, variable=None):
        """ Function to add the attributes with information about the space and time grid to the Dataset.

        Args:
            data (xarray, optional):    . Defaults to None.
            dataset (xarray, optional): . Defaults to None.
            variable (str, optional):   . Defaults to None.

        Returns:
            xarray: The xarray with the grid.
        """
        if data.time.size>1:
            time_band = str(data.time[0].values)+', '+str(data.time[-1].values)+', freq='+str(time_interpreter(data))
        else:
            time_band = str(data.time.values)
        if data.lat.size>1:
            latitude_step  = data.lat[1].values - data.lat[0].values
            lat_band = str(data.lat[0].values)+', '+str(data.lat[-1].values)+', freq='+str(latitude_step)
        else:
            lat_band = data.lat.values
            latitude_step = data.lat.values
        if data.lon.size>1:
            longitude_step = data.lon[1].values - data.lon[0].values
            lon_band = str(data.lon[0].values)+', '+str(data.lon[-1].values)+', freq='+str(longitude_step)
        else:   
            longitude_step = data.lon.values 
            lon_band = data.lon.values 

        
        
        if variable is None:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            history_update=str(current_time)+' histogram is calculated for time_band: ['+str(time_band)+']; lat_band: ['+str(lat_band)+']; lon_band: ['+str(lon_band)+'];\n '
            try:
                history_attr  = tprate_dataset.attrs['history'] + history_update
                tprate_dataset.attrs['history'] = history_attr
            except KeyError:
                print("The obtained xarray.Dataset doesn't have global attributes. Consider adding global attributes manually to the dataset.")
        else:
            tprate_dataset[variable].attrs['time_band']=time_band
            tprate_dataset[variable].attrs['lat_band'] =lat_band
            tprate_dataset[variable].attrs['lon_band'] =lon_band

        return tprate_dataset
    
    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ 
    def histogram_to_xarray(self,  hist_counts=None, path_to_save=None, data_with_global_atributes=None):
        """ Function to convert the histogram to xarray.Dataset.

        Args:
            hist_counts (xarray, optional):     The histogram with counts. Defaults to None.
            path_to_save (str, optional):       The path to save the histogram. Defaults to None.

        Returns:
            xarray: The xarray.Dataset with the histogram.
        """
        tprate_dataset = hist_counts.to_dataset(name="counts")
        
        hist_frequency = self.convert_counts_to_frequency(hist_counts)
        tprate_dataset['frequency'] = hist_frequency

        hist_pdf = self.convert_counts_to_pdf(hist_counts)
        tprate_dataset['pdf'] = hist_pdf

        if data_with_global_atributes is not None:  
            tprate_dataset.attrs = data_with_global_atributes.attrs

        if path_to_save is not None:
            self.save_histogram(dataset=tprate_dataset, path_to_save=path_to_save)
        return tprate_dataset

    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ 
    def load_histogram(self, path_to_dataset=None, multi=None, all=None):
        """ Function to load/open the histogram from the storage."""
        with open(path_to_dataset, 'rb') as data:
            dataset = pickle.load(data)
        return dataset
    
    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ 
    def merge_two_datasets(self, tprate_dataset_1=None, tprate_dataset_2=None):
        """ Function to merge two datasets.

        Args:
            tprate_dataset_1 (xarray, optional): The first dataset. Defaults to None.
            tprate_dataset_2 (xarray, optional): The second dataset. Defaults to None.

        Returns:
            xarray: The xarray.Dataset with the merged data.
        """
        
        if isinstance(tprate_dataset_1, xr.Dataset) and isinstance(tprate_dataset_2, xr.Dataset):
            dataset_3 = tprate_dataset_1.copy(deep=True)

            dataset_3.attrs = {**tprate_dataset_1.attrs, **tprate_dataset_2.attrs}
            for attribute in tprate_dataset_1.attrs:
                if tprate_dataset_1.attrs[attribute]!=tprate_dataset_2.attrs[attribute]:
                    dataset_3.attrs[attribute] = str(tprate_dataset_1.attrs[attribute])+';\n '+str(tprate_dataset_2.attrs[attribute])


            dataset_3.counts.values = tprate_dataset_1.counts.values+tprate_dataset_2.counts.values
            dataset_3.frequency.values = self.convert_counts_to_frequency(dataset_3.counts)
            dataset_3.pdf.values = self.convert_counts_to_pdf(dataset_3.counts)

            for variable in ('counts', 'frequency', 'pdf'):
                for attribute in tprate_dataset_1.counts.attrs:
                    dataset_3[variable].attrs ={**tprate_dataset_1[variable].attrs, **tprate_dataset_2[variable].attrs}
                    if tprate_dataset_1[variable].attrs[attribute]!=tprate_dataset_2[variable].attrs[attribute]:
                        dataset_3[variable].attrs[attribute] = str(tprate_dataset_1[variable].attrs[attribute])+';\n '+str(tprate_dataset_2[variable].attrs[attribute])

            return dataset_3
        
    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ 
    def merge_list_of_histograms(self, path_to_histograms=None, multi=None, all=False):
        """ Function to merge list of histograms.

        Args:
            path_to_histograms (str, optional):     The path to the list of histograms. Defaults to None.
            multi (int, optional):                  The number of histograms to merge. Defaults to None.
            all (bool, optional):                   If True, all histograms in the repository will be merged. Defaults to False.

        Returns:
            xarray: The xarray.Dataset with the merged data.
        """

        histogram_list = [f for f in listdir(path_to_histograms) if isfile(join(path_to_histograms, f))]
        histogram_list.sort()

        if all:
            histograms_to_load = [str(path_to_histograms)+str(histogram_list[i]) for i in range(0, len(histogram_list))]
        elif multi is not None:
            histograms_to_load = [str(path_to_histograms)+str(histogram_list[i]) for i in range(0, multi)]

        for i in range(0, len(histograms_to_load)):
            if i==0:
                dataset = self.load_histogram(path_to_dataset=histograms_to_load[i])
            else:
                dataset = self.merge_two_datasets(tprate_dataset_1=dataset, tprate_dataset_2=self.load_histogram(path_to_dataset=histograms_to_load[i]))

        return dataset
    
        

    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ 
    def hist1d_fast(self, data, preprocess = True,   trop_lat = 10, variable_1 = 'tprate',  
                    s_time = None, f_time = None, s_year = None, f_year = None, s_month = None, f_month = None, 
                    num_of_bins = None, first_edge = None,  width_of_bin  = None,   bins = 0):
        """Calculating the histogram with the use of fast_histogram.histogram1d (***fast_histogram*** package)

        Args:
            data (xarray):                  The Dataset.
            preprocess (bool, optional):    If sort is True, the functiom preprocess Dataset. Defaults to True.
            variable_1 (str, optional):     The variable of the Dataset. Defaults to 'tprate'.
            trop_lat (float, optional):     The maximumal and minimal tropical latitude values in Dataset.  Defaults to None.
            s_time (str/int, optional):     The starting time value/index in Dataset. Defaults to None.
            f_time (str/int, optional):     The final time value/index in Dataset. Defaults to None.
            s_year (int, optional):         The starting year in Dataset. Defaults to None.
            f_year (int, optional):         The final year in Dataset. Defaults to None.
            s_month (int, optional):        The starting month in Dataset. Defaults to None.
            f_month (int, optional):        The final month in Dataset. Defaults to None.
            sort (bool, optional):          If sort is True, the DataArray is sorted. Defaults to False.
            dask_array (bool, optional):    If sort is True, the function return daskarray. Defaults to False.
            
            num_of_bins (int, optional):    The number of bins in the histogram. Defaults to None.
            first_edge (float, optional):   The first edge of the histogram. Defaults to None.
            width_of_bin (float, optional): The width of the bins in the histogram. Defaults to None.
            bins (array, optional):         The array of bins in the histogram. Defaults to 0.

        Returns:
            xarray: The frequency histogram of the specified variable in the Dataset
        """        
        self.class_attributes_update(s_time = s_time, f_time = f_time, trop_lat = trop_lat, 
                               s_year = s_year, f_year = f_year, s_month = s_month, f_month = f_month, 
                               first_edge = first_edge, num_of_bins = num_of_bins, width_of_bin = width_of_bin, bins = bins)


        if preprocess == True:
            data = self.preprocessing(data, preprocess=preprocess,  variable_1=variable_1, trop_lat=trop_lat, 
                                      s_time = self.s_time, f_time = self.f_time,
                                      s_year=s_year, f_year=f_year, s_month=s_month, f_month=f_month,  
                                      sort = False, dask_array = False)
        if isinstance(self.bins, int):
            width_table = [self.width_of_bin for j in range(0, self.num_of_bins)]  
            center_of_bin = [self.first_edge + self.width_of_bin*(j+0.5) for j in range(0, self.num_of_bins)]
            hist_fast   = fast_histogram.histogram1d(data, 
                                                   range=[self.first_edge, self.first_edge + (self.num_of_bins)*self.width_of_bin], 
                                                   bins = self.num_of_bins)
        else: 
            bin_table = self.bins
            width_table = [bin_table[i+1]-bin_table[i] for i in range(0, len(self.bins)-1)]
            center_of_bin = [bin_table[i] + 0.5*width_table[i] for i in range(0, len(self.bins)-1)]
            hist_fast = fast_histogram.histogram1d(data, 
                                                   range=[min(self.bins),max(self.bins)], bins = len(self.bins)-1)   
        
        
        counts_per_bin =  xr.DataArray(hist_fast, coords=[center_of_bin], dims=["center_of_bin"])
        counts_per_bin = counts_per_bin.assign_coords(width=("center_of_bin", width_table))
        counts_per_bin.attrs = data.attrs
        return  counts_per_bin 
    
    
    
    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ 
    def hist1d_np(self, data, weights=None, preprocess = True,   trop_lat = 10, variable_1 = 'tprate',  
                  s_time = None, f_time = None, s_year = None, f_year = None, s_month = None, f_month = None, 
                  num_of_bins = None, first_edge = None,  width_of_bin  = None,  bins = 0):
        """ Function to calculate the histogram with the use of numpy.histogram.

        Args:
            data (xarray):                  The Dataset.
            preprocess (bool, optional):    If sort is True, the functiom preprocess Dataset. Defaults to True.
            variable_1 (str, optional):     The variable of the Dataset. Defaults to 'tprate'.
            trop_lat (float, optional):     The maximumal and minimal tropical latitude values in Dataset.  Defaults to None.
            s_time (str/int, optional):     The starting time value/index in Dataset. Defaults to None.
            f_time (str/int, optional):     The final time value/index in Dataset. Defaults to None.
            s_year (int, optional):         The starting year in Dataset. Defaults to None.
            f_year (int, optional):         The final year in Dataset. Defaults to None.
            s_month (int, optional):        The starting month in Dataset. Defaults to None.
            f_month (int, optional):        The final month in Dataset. Defaults to None.
            
        Returns:"""
        self.class_attributes_update(s_time = s_time, f_time = f_time,  trop_lat = trop_lat, 
                               s_year = s_year, f_year = f_year, s_month = s_month, f_month = f_month, 
                               first_edge = first_edge, num_of_bins = num_of_bins, width_of_bin = width_of_bin, bins = bins)
        
        if preprocess == True:
            data = self.preprocessing(data, preprocess=preprocess, variable_1=variable_1, trop_lat=self.trop_lat, 
                                      s_time = self.s_time, f_time = self.f_time, 
                                      s_year=self.s_year, f_year=self.f_year, s_month=self.s_month, f_month=self.f_month,  
                                      sort = False, dask_array = False)
            
            #weights = self.preprocessing(weights, preprocess=preprocess, variable_1=variable_1, trop_lat=self.trop_lat, 
            #                          s_time = self.s_time, f_time = self.f_time, 
            #                          s_year=self.s_year, f_year=self.f_year, s_month=self.s_month, f_month=self.f_month,  
            #                          sort = False, dask_array = False)
        if 'DataArray' in str(type(weights)):
            weights = self.latitude_band(weights, trop_lat=self.trop_lat)
            hist_np=0
            for i in range(0, len(data.time)):
                data_element = data.isel(time=i)
                if isinstance(self.bins, int):
                    hist_np = np.histogram(data_element, weights=weights, \
                                           range=[self.first_edge, self.first_edge + (self.num_of_bins )*self.width_of_bin], \
                                           bins = (self.num_of_bins))
                else:
                    hist_np = np.histogram(data_element,  weights=weights, bins = self.bins) 
                width_table = [hist_np[1][i+1]-hist_np[1][i] for i in range(0, len(hist_np[1])-1)]
                center_of_bin = [hist_np[1][i] + 0.5*width_table[i] for i in range(0, len(hist_np[1])-1)]
                counts_per_bin =+  xr.DataArray(hist_np[0], coords=[center_of_bin], dims=["center_of_bin"])
                counts_per_bin = counts_per_bin.assign_coords(width=("center_of_bin", width_table))
        else: 
            if isinstance(self.bins, int):
                hist_np = np.histogram(data, weights=weights, 
                                       range=[self.first_edge, self.first_edge + (self.num_of_bins )*self.width_of_bin], 
                                       bins = (self.num_of_bins))
            else:
                hist_np = np.histogram(data,  weights=weights, bins = self.bins) 
            
            width_table = [hist_np[1][i+1]-hist_np[1][i] for i in range(0, len(hist_np[1])-1)]
            center_of_bin = [hist_np[1][i] + 0.5*width_table[i] for i in range(0, len(hist_np[1])-1)]
            counts_per_bin =  xr.DataArray(hist_np[0], coords=[center_of_bin], dims=["center_of_bin"])
            counts_per_bin = counts_per_bin.assign_coords(width=("center_of_bin", width_table))
       
        counts_per_bin.attrs = data.attrs
        return  counts_per_bin
        
    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ 
    def hist1d_pyplot(self, data, weights=None,preprocess = True,  trop_lat = 10,  variable_1 = 'tprate',  
                      s_time = None, f_time = None,  s_year = None, f_year = None, s_month = None, f_month = None, 
                      num_of_bins = None, first_edge = None,  width_of_bin  = None,  bins = 0):
        """ Function to create a 1D histogram of the specified variable in the Dataset using 
        (***matplotlib*** package)
        Args:
            data (xarray):                  The Dataset.
            preprocess (bool, optional):    If sort is True, the functiom preprocess Dataset. Defaults to True.
            variable_1 (str, optional):     The variable of the Dataset. Defaults to 'tprate'.
            trop_lat (float, optional):     The maximumal and minimal tropical latitude values in Dataset.  Defaults to None.
            s_time (str/int, optional):     The starting time value/index in Dataset. Defaults to None.
            f_time (str/int, optional):     The final time value/index in Dataset. Defaults to None.
            s_year (int, optional):         The starting year in Dataset. Defaults to None.
            f_year (int, optional):         The final year in Dataset. Defaults to None.
            s_month (int, optional):        The starting month in Dataset. Defaults to None.
            f_month (int, optional):        The final month in Dataset. Defaults to None.""" 
        self.class_attributes_update(s_time = s_time, f_time = f_time,  trop_lat = trop_lat, 
                               s_year = s_year, f_year = f_year, s_month = s_month, f_month = f_month, 
                               first_edge = first_edge, num_of_bins = num_of_bins, width_of_bin = width_of_bin, bins=bins)  

        if preprocess == True:
            data = self.preprocessing(data, preprocess=preprocess, variable_1=variable_1, trop_lat=trop_lat, 
                                      s_time = self.s_time, f_time = self.f_time, 
                                      s_year=s_year, f_year=f_year, s_month=s_month, f_month=f_month,  
                                      sort = False, dask_array = False)

        if isinstance(self.bins, int):
            bins = [self.first_edge  + i*self.width_of_bin for i in range(0, self.num_of_bins+1)]
            left_edges_table   = [self.first_edge + self.width_of_bin*j for j in range(0, self.num_of_bins)]  
            width_table = [self.width_of_bin for j in range(0, self.num_of_bins)]  
            center_of_bin = [bins[i] + 0.5*width_table[i] for i in range(0, len(bins)-1)]
        else:
            bins = self.bins
            left_edges_table =[self.bins[i] for i in range(0, len(self.bins)-1)]
            width_table = [self.bins[i+1]-self.bins[i] for i in range(0, len(self.bins)-1)]
            center_of_bin = [self.bins[i] + 0.5*width_table[i] for i in range(0, len(self.bins)-1)]
            

        coord_lat, coord_lon = self.coordinate_names(data)

        if 'DataArray' in str(type(weights)):
            weights = self.latitude_band(weights, trop_lat=self.trop_lat)
            weights=weights.stack(total=[coord_lat, coord_lon])
            for i in range(0, len(data.time)):
                data_element = data.isel(time=i)
                data_element=data_element.stack(total=[coord_lat, coord_lon])
                hist_pyplt = plt.hist(x = data_element, bins = bins, weights=weights)
                counts_per_bin =+  xr.DataArray(hist_pyplt[0], coords=[center_of_bin], dims=["center_of_bin"])
        else:    
            data_element=data.stack(total=['time', coord_lat, coord_lon])
            hist_pyplt = plt.hist(x = data_element, bins = bins)
            counts_per_bin =  xr.DataArray(hist_pyplt[0], coords=[center_of_bin], dims=["center_of_bin"])
        plt.close()

        counts_per_bin = counts_per_bin.assign_coords(width=("center_of_bin", width_table))
        counts_per_bin.attrs = data.attrs
        return  counts_per_bin

        
         
    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ 
    def dask_factory(self, data, weights=None, preprocess = True,   trop_lat = 10,  variable_1 = 'tprate',  
                     s_time = None, f_time = None, s_year = None, f_year = None, s_month = None, f_month = None, 
                     num_of_bins = None, first_edge = None,  width_of_bin  = None,   bins = 0, 
                     lazy=False):
        """ Function to create a dask array of the frequency histogram of the specified variable in the Dataset.
        Args:
            data (xarray):                 The Dataset.
            preprocess (bool, optional):    If preprocess is True, the function preprocess the Dataset. Defaults to True.
            variable_1 (str, optional):     The variable of the Dataset. Defaults to 'tprate'.
            trop_lat (float, optional):     The maximumal and minimal tropical latitude values in Dataset.  Defaults to None.
            s_time (str/int, optional):     The starting time value/index in Dataset. Defaults to None.
            f_time (str/int, optional):     The final time value/index in Dataset. Defaults to None.
            s_year (int, optional):         The starting year in Dataset. Defaults to None.
            f_year (int, optional):         The final year in Dataset. Defaults to None.
            s_month (int, optional):        The starting month in Dataset. Defaults to None.
            f_month (int, optional):        The final month in Dataset. Defaults to None.
            
        Returns:"""
        self.class_attributes_update(s_time = s_time, f_time = f_time, trop_lat = trop_lat, 
                               s_year = s_year, f_year = f_year, s_month = s_month, f_month = f_month, first_edge = first_edge, 
                               num_of_bins = num_of_bins, width_of_bin = width_of_bin)

        last_edge = self.first_edge  + self.num_of_bins*self.width_of_bin
        

        if preprocess == True:
            data_dask = self.preprocessing(data, preprocess=preprocess, variable_1=variable_1, trop_lat=trop_lat, 
                                      s_time = self.s_time, f_time = self.f_time, 
                                      s_year=s_year, f_year=f_year, s_month=s_month, f_month=f_month,  
                                      sort=False, dask_array=True)
            if weights is not None:
                weights_dask = self.preprocessing(weights, preprocess=preprocess, variable_1=variable_1, trop_lat=trop_lat, 
                                      s_time = self.s_time, f_time = self.f_time,
                                      s_year=s_year, f_year=f_year, s_month=s_month, f_month=f_month,  
                                      sort=False, dask_array=True)
        else:
            data_dask=data
            weights_dask= weights
        if weights is None:
            h = dh.factory(data_dask, 
                axes=(bh.axis.Regular(self.num_of_bins, self.first_edge, last_edge),))   
        else: 
            h = dh.factory(data_dask, weights_dask, 
                axes=(bh.axis.Regular(self.num_of_bins, self.first_edge, last_edge),))  
        counts, edges = h.to_dask_array()
        if not lazy: 
            counts = counts.compute()
            edges = edges.compute()
        
        width_table = [self.width_of_bin for j in range(0, self.num_of_bins)]  
        center_of_bin = [self.first_edge + self.width_of_bin*(j+0.5) for j in range(0, self.num_of_bins)]
        counts_per_bin =  xr.DataArray(counts, coords=[center_of_bin], dims=["center_of_bin"])
        counts_per_bin = counts_per_bin.assign_coords(width=("center_of_bin", width_table))
        counts_per_bin.attrs = data[variable_1].attrs  
        return  counts_per_bin


    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ 
    def dask_factory_weights(self, data, weights=None, preprocess = True,  trop_lat = 10,  variable_1 = 'tprate',  
                             s_time = None, f_time = None, s_year = None, f_year = None, s_month = None, f_month = None, 
                             num_of_bins = None, first_edge = None,  width_of_bin  = None,  bins = 0,   
                             lazy=False):
        """ Function to calculate the histogram with weights.
        Args:
            data (xarray):                  The Dataset.
            preprocess (bool, optional):    If sort is True, the functiom preprocess Dataset. Defaults to True.
            variable_1 (str, optional):     The variable of the Dataset. Defaults to 'tprate'.
            trop_lat (float, optional):     The maximumal and minimal tropical latitude values in Dataset.  Defaults to None.
            s_time (str/int, optional):     The starting time value/index in Dataset. Defaults to None.
            f_time (str/int, optional):     The final time value/index in Dataset. Defaults to None.
            s_year (int, optional):         The starting year in Dataset. Defaults to None.
            f_year (int, optional):         The final year in Dataset. Defaults to None.
            s_month (int, optional):        The starting month in Dataset. Defaults to None.
            f_month (int, optional):        The final month in Dataset. Defaults to None.
            
        Returns:"""
        self.class_attributes_update(s_time = s_time, f_time = f_time, trop_lat = trop_lat, 
                               s_year = s_year, f_year = f_year, s_month = s_month, f_month = f_month, first_edge = first_edge, 
                               num_of_bins = num_of_bins, width_of_bin = width_of_bin)    

        last_edge = self.first_edge  + self.num_of_bins*self.width_of_bin

        if preprocess == True:
            data = self.preprocessing(data, preprocess=preprocess, variable_1=variable_1, trop_lat=trop_lat, 
                                      s_time = self.s_time, f_time = self.f_time,
                                      s_year=s_year, f_year=f_year, s_month=s_month, f_month=f_month,  
                                      sort=False, dask_array=False)
            
            #weights = self.preprocessing(weights, preprocess=preprocess, variable_1=variable_1, trop_lat=trop_lat, 
            #                          s_time = self.s_time, f_time = self.f_time,
            #                          s_year=s_year, f_year=f_year, s_month=s_month, f_month=f_month,  
            #                          sort=False, dask_array=False)


            weights = self.latitude_band(weights, trop_lat=self.trop_lat)

        ref = bh.Histogram(bh.axis.Regular(self.num_of_bins, self.first_edge, last_edge), storage=bh.storage.Weight())
        counts=0
        for i in range(0, data.time.size):
            data_dask = data.isel(time=i)
            data_dask = da.from_array(data_dask.stack(total=['lat', 'lon']))
            weights_dask=da.from_array(weights.stack(total=['lat', 'lon']))
        
            h = dh.factory(data_dask, weights=weights_dask, histref=ref)
            _counts, edges = h.to_dask_array()
            counts=+_counts
        if not lazy: 
            counts = counts.compute()
            edges = edges.compute()
        
        width_table = [self.width_of_bin for j in range(0, self.num_of_bins)]  
        center_of_bin = [self.first_edge + self.width_of_bin*(j+0.5) for j in range(0, self.num_of_bins)]
        counts_per_bin =  xr.DataArray(counts, coords=[center_of_bin], dims=["center_of_bin"])
        counts_per_bin = counts_per_bin.assign_coords(width=("center_of_bin", width_table))
        counts_per_bin.attrs = data.attrs        
        return  counts_per_bin


    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ 
    def dask_boost(self, data, preprocess = True, trop_lat = 10,  variable_1 = 'tprate',  
                   s_time = None, f_time = None, s_year = None, f_year = None, s_month = None, f_month = None, 
                   num_of_bins = None, first_edge = None,  width_of_bin  = None,  bins = 0):
        """ Function to calculate the histogram of the specified variable in the Dataset.
        Args:
            data (xarray):                  The Dataset.
            preprocess (bool, optional):    If sort is True, the functiom preprocess Dataset. Defaults to True.
            variable_1 (str, optional):     The variable of the Dataset. Defaults to 'tprate'.
            trop_lat (float, optional):     The maximumal and minimal tropical latitude values in Dataset.  Defaults to None.
            s_time (str/int, optional):     The starting time value/index in Dataset. Defaults to None.
            f_time (str/int, optional):     The final time value/index in Dataset. Defaults to None.
            s_year (int, optional):         The starting year in Dataset. Defaults to None.
            f_year (int, optional):         The final year in Dataset. Defaults to None.
            s_month (int, optional):        The starting month in Dataset. Defaults to None.
            f_month (int, optional):        The final month in Dataset. Defaults to None.
        Returns: the counts histogram."""
        self.class_attributes_update(s_time = s_time, f_time = f_time,  trop_lat = trop_lat, 
                               s_year = s_year, f_year = f_year, s_month = s_month, f_month = f_month, first_edge = first_edge, 
                               num_of_bins = num_of_bins, width_of_bin = width_of_bin) 

        last_edge = self.first_edge  + self.num_of_bins*self.width_of_bin

        if preprocess == True:
            data_dask = self.preprocessing(data, preprocess=preprocess, variable_1=variable_1, trop_lat=trop_lat, 
                                      s_time = self.s_time, f_time = self.f_time, 
                                      s_year=s_year, f_year=f_year, s_month=s_month, f_month=f_month,  
                                      sort = False, dask_array=True)
        else:
            data_dask=data

        h = dhb.Histogram(dh.axis.Regular(self.num_of_bins, self.first_edge, last_edge),  storage=dh.storage.Double(), )
        h.fill(data_dask)
        
        counts, edges = h.to_dask_array()
        print(counts, edges)
        counts =  dask.compute(counts)
        edges = dask.compute(edges[0]) 
        
        width_table = [self.width_of_bin for j in range(0, self.num_of_bins)]  
        center_of_bin = [self.first_edge + self.width_of_bin*(j+0.5) for j in range(0, self.num_of_bins)]
        counts_per_bin =  xr.DataArray(counts[0], coords=[center_of_bin], dims=["center_of_bin"])
        counts_per_bin = counts_per_bin.assign_coords(width=("center_of_bin", width_table))
        counts_per_bin.attrs = data[variable_1].attrs
        return  counts_per_bin

    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ 
    def convert_counts_to_frequency(self, data):
        """ Function to convert the counts to the frequency.

        Args:
            data (xarray): The counts.

        Returns:
            xarray: The frequency.
        """
        sum_of_counts = sum(data[:]) 
        frequency = data[0:]/sum_of_counts
        frequency_per_bin =  xr.DataArray(frequency, coords=[data.center_of_bin], dims=["center_of_bin"])
        frequency_per_bin = frequency_per_bin.assign_coords(width=("center_of_bin", data.width.values))
        frequency_per_bin.attrs = data.attrs
        sum_of_frequency=sum(frequency_per_bin[:]) 
        if abs(sum_of_frequency -1) < 10**(-4):
            return frequency_per_bin
        else:
            raise Exception("Test failed")


        
    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ 
    def convert_counts_to_pdf(self, data):
        """ Function to convert the counts to the pdf.

        Args:
            data (xarray): The counts.

        Returns:
            xarray: The pdf.
        """
        sum_of_counts = sum(data[:]) 
        pdf =  data[0:]/(sum_of_counts*data.width[0:])
        pdf_per_bin =  xr.DataArray(pdf, coords=[data.center_of_bin], dims=["center_of_bin"])
        pdf_per_bin = pdf_per_bin.assign_coords(width=("center_of_bin", data.width.values))
        pdf_per_bin.attrs = data.attrs
        sum_of_pdf=sum(pdf_per_bin[:]*data.width[0:]) 
        if abs(sum_of_pdf-1.) < 10**(-4):
            return pdf_per_bin
        else:
            raise Exception("Test failed")


    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """
    def hist_figure(self,  data, weights=None, frequency = False, pdf = True, smooth = True, step = False, color_map = False,  \
                    ls = '-', ylogscale=True, xlogscale = False, color = 'tab:blue',  figsize=1, legend='_Hidden', 
                    varname = 'Precipitation', plot_title = None,  add = None, fig=None, path_to_save = None):
        """ Function to plot the histogram.

        Args:
            data (xarray): The counts."""
        if add is None and fig is None:
            fig, ax = plt.subplots( figsize=(8*figsize,5*figsize) )
        elif add is not None: 
            fig, ax = add
        elif fig is not None:
            fig, ax = fig

        if not pdf and not frequency:
            try:
                data=data['counts']
            except KeyError:
                data=data
        elif pdf and not frequency:
            try: 
                data=data['pdf']
            except KeyError:
                try:
                    data=data['counts']
                    data = self.convert_counts_to_pdf(data)
                except KeyError:    
                    data = self.convert_counts_to_pdf(data)

        elif not pdf and frequency:
            try: 
                data=data['frequency']
            except KeyError:
                try:
                    data=data['counts']
                    data = self.convert_counts_to_frequency(data)
                except KeyError:    
                    data = self.convert_counts_to_frequency(data)
            data = self.convert_counts_to_frequency(data)
        
        if smooth:
            plt.plot(data.center_of_bin, data, 
                linewidth=3.0, ls = ls, color = color, label=legend )
            plt.grid(True)
        elif step:
            plt.step(data.center_of_bin, data, 
                linewidth=3.0, ls = ls, color = color, label=legend )
            plt.grid(True)
        elif color_map:
            if weights is None: 
                N, bins, patches = plt.hist(x= data.center_of_bin, bins = data.center_of_bin, weights=data,  label=legend)  
            else:
                N, bins, patches = plt.hist(x= data.center_of_bin, bins = data.center_of_bin, weights=weights,  label=legend)  
            fracs = ((N**(1 / 5)) / N.max())
            norm = colors.Normalize(fracs.min(), fracs.max())

            for thisfrac, thispatch in zip(fracs, patches):
                if color_map is True:
                    color = plt.cm.get_cmap('viridis')(norm(thisfrac))
                elif isinstance(color_map, str):
                    color = plt.cm.get_cmap(color_map)(norm(thisfrac))
                thispatch.set_facecolor(color)
            
        plt.xlabel(varname+", "+str(data.attrs['units']), fontsize=14)
        if ylogscale:
            plt.yscale('log')
        if xlogscale:
            plt.xscale('log') 

        if pdf and not frequency:
            plt.ylabel('PDF', fontsize=14)
        elif not pdf and frequency:
            plt.ylabel('Frequency', fontsize=14)
        else:
            plt.ylabel('Counts', fontsize=14)
        
        plt.title(plot_title, fontsize=16)


        if legend!='_Hidden':
            plt.legend(loc='upper right', fontsize=12)
        # set the spacing between subplots
        plt.tight_layout()
        if path_to_save is not None and isinstance(path_to_save, str):
            plt.savefig(path_to_save)
        return {fig, ax}   





def time_interpreter(dataset):
    """Identifying unit of timestep in the Dataset

    Args:
        dataset (xarray): The Dataset

    Returns:
        str: The unit of timestep in input Dataset
    """

    if dataset['time'].size==1:
        return 'False. Load more timesteps then one'
    try:
        if np.count_nonzero(dataset['time.second'] == dataset['time.second'][0]) == dataset.time.size:
            if np.count_nonzero(dataset['time.minute'] == dataset['time.minute'][0]) == dataset.time.size:
                if  np.count_nonzero(dataset['time.hour'] == dataset['time.hour'][0]) == dataset.time.size:
                    if np.count_nonzero(dataset['time.day'] == dataset['time.day'][0] ) == dataset.time.size or \
                        np.count_nonzero([dataset['time.day'][i] in [1, 28, 29, 30, 31] for i in range(0, len(dataset['time.day']))]) == dataset.time.size:

                        if np.count_nonzero(dataset['time.month'] == dataset['time.month'][0]) == dataset.time.size:
                            return 'Y'
                        else:
                            return 'M'
                    else:
                        return 'D'
                else:
                    timestep = dataset.time[1] - dataset.time[0]
                    n_hours = int(timestep/(60 * 60 * 10**9) )
                    return str(n_hours)+'H'
            else:
                timestep = dataset.time[1] - dataset.time[0]
                n_minutes = int(timestep/(60  * 10**9) )
                return str(n_minutes)+'m'
                # separate branch, PR, not part of this diagnostic
        else:
            return 1

    except KeyError and AttributeError:
        timestep = dataset.time[1] - dataset.time[0]
        if timestep >=28 and timestep <=31:
            return 'M'