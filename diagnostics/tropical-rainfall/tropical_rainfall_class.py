from   datetime import datetime
import numpy as np
import xarray as xr
import re

from os import listdir
from os.path import isfile, join

import matplotlib.pyplot as plt
from   matplotlib import colors
from   matplotlib.colors import LogNorm

import dask.array as da
import dask_histogram as dh # pip

from aqua.util import create_folder
 
import cartopy.crs as ccrs

from aqua import Reader
from aqua.util import create_folder

from tropical_rainfall_func import time_interpreter, convert_24hour_to_12hour_clock, convert_monthnumber_to_str
from tropical_rainfall_func import mirror_dummy_grid, data_size
from tropical_rainfall_func import convert_length, convert_time, unit_splitter, extract_directory_path

"""The module contains Tropical Precipitation Diagnostic:

.. moduleauthor:: AQUA team <natalia.nazarova@polito.it>

"""


class TR_PR_Diagnostic:
    """This class is a minimal version of the Tropical Precipitation Diagnostic.
    """


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
            trop_lat (int or float, optional):      The latitude of the tropical zone.      Defaults to 10.
            s_time (int or str, optional):          The start time of the time interval.    Defaults to None.
            f_time (int or str, optional):          The end time of the time interval.      Defaults to None.
            s_year (int, optional):                 The start year of the time interval.    Defaults to None.
            f_year (int, optional):                 The end year of the time interval.      Defaults to None.
            s_month (int, optional):                The start month of the time interval.   Defaults to None.
            f_month (int, optional):                The end month of the time interval.     Defaults to None.
            num_of_bins (int, optional):            The number of bins.                     Defaults to None.
            first_edge (int or float, optional):    The first edge of the bin.              Defaults to None.
            width_of_bin (int or float, optional):  The width of the bin.                   Defaults to None.
            bins (np.ndarray, optional):            The bins.                               Defaults to 0."""

        self.trop_lat       = trop_lat
        self.s_time         = s_time
        self.f_time         = f_time
        self.s_year         = s_year
        self.f_year         = f_year
        self.s_month        = s_month
        self.f_month        = f_month     
        self.num_of_bins    = num_of_bins
        self.first_edge     = first_edge
        self.width_of_bin   = width_of_bin
        self.bins           = bins
    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ 
    def class_attributes_update(self,       trop_lat = None,    s_time = None,       f_time = None,
                          s_year = None,    f_year = None,      s_month = None,      f_month = None,
                        num_of_bins = None, first_edge = None,  width_of_bin = None, bins = 0):
        """ Function to update the class attributes.
        
        Args:
            trop_lat (int or float, optional):      The latitude of the tropical zone.      Defaults to 10.
            s_time (int or str, optional):          The start time of the time interval.    Defaults to None.
            f_time (int or str, optional):          The end time of the time interval.      Defaults to None.
            s_year (int, optional):                 The start year of the time interval.    Defaults to None.
            f_year (int, optional):                 The end year of the time interval.      Defaults to None.
            s_month (int, optional):                The start month of the time interval.   Defaults to None.
            f_month (int, optional):                The end month of the time interval.     Defaults to None.
            num_of_bins (int, optional):            The number of bins.                     Defaults to None.
            first_edge (int or float, optional):    The first edge of the bin.              Defaults to None.
            width_of_bin (int or float, optional):  The width of the bin.                   Defaults to None.
            bins (np.ndarray, optional):            The bins.                               Defaults to 0. """
        if trop_lat is not None     and     isinstance(trop_lat, (int, float)):     
            self.trop_lat = trop_lat
        elif trop_lat is not None   and not isinstance(trop_lat, (int, float)):
            raise Exception("trop_lat must to be integer or float")
        
        if s_time is not None       and     isinstance(s_time, (int, str)):        
            self.s_time = s_time
        elif s_time is not None     and not isinstance(s_time, (int, str)):
            raise Exception("s_time must to be integer or string")
        
        if f_time is not None       and     isinstance(f_time, (int, str)):       
            self.f_time = f_time
        elif f_time is not None     and not isinstance(f_time, (int, str)):
            raise Exception("f_time must to be integer or string")
        
        if s_year is not None       and     isinstance(s_year, int):    
            self.s_year = s_year
        elif s_year is not None     and not isinstance(s_year, int):
            raise Exception("s_year must to be integer")
        
        if f_year is not None       and     isinstance(f_year, int):
            self.f_year = f_year
        elif f_year is not None     and not isinstance(f_year, int):
            raise Exception("f_year must to be integer")
        
        if s_month is not None      and     isinstance(s_month, int):   
            self.s_month = s_month
        elif s_month is not None    and not isinstance(s_month, int):
            raise Exception("s_month must to be integer")
        
        if f_month is not None      and     isinstance(f_month, int):     
            self.f_month = f_month
        elif f_month is not None    and not isinstance(f_month, int):
            raise Exception("f_month must to be integer")
        
        if bins!=0                  and     isinstance(bins, np.ndarray):
            self.bins = bins
        elif bins!=0                and not isinstance(bins, (np.ndarray, list)):
            raise Exception("bins must to be array")
        
        if num_of_bins is not None          and     isinstance(num_of_bins, int):
            self.num_of_bins = num_of_bins
        elif num_of_bins is not None        and not isinstance(num_of_bins, int):
            raise Exception("num_of_bins must to be integer")
        
        if first_edge is not None           and     isinstance(first_edge, (int, float)):
            self.first_edge = first_edge
        elif first_edge is not None         and not isinstance(first_edge, (int, float)):
            raise Exception("first_edge must to be integer or float")
        
        if width_of_bin is not None         and     isinstance(width_of_bin, (int, float)):
            self.width_of_bin = width_of_bin
        elif width_of_bin is not None       and not isinstance(width_of_bin, (int, float)):
            raise Exception("width_of_bin must to be integer or float")

        
        
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
    def precipitation_rate_units_converter(self, data, model_variable = 'tprate', new_unit = 'kg m**-2 s**-1'):
        """ Function to convert the units of precipitation rate.

        Args:
            data (xarray):                  The Dataset
            model_variable (str, optional): The name of the variable to be converted.   Defaults to 'tprate'.
            new_unit (str, optional):       The new unit of the variable.               Defaults to 'm s**-1'.

        Returns:
            xarray: The Dataset with converted units.
        """    
        try:
            data        = data[model_variable]
        except KeyError:
            data        = data

        if data.units == new_unit:
            return data
        else:
            from_mass_unit, from_space_unit, from_time_unit = unit_splitter(data.units)
            to_mass_unit, to_space_unit,   to_time_unit     = unit_splitter(new_unit)

            if data.units == 'kg m**-2 s**-1':
                data            = 0.001 * data
                data            = convert_length(data,   from_space_unit, to_space_unit)
                data            = convert_time(data,     from_time_unit,  to_time_unit)
            elif from_mass_unit is None and new_unit == 'kg m**-2 s**-1':
                data            = convert_length(data,   from_space_unit, 'm')
                data            = convert_time(data,     from_time_unit,  's')
                data            = 1000 * data
            else:
                data            = convert_length(data,   from_space_unit, to_space_unit)
                data            = convert_time(data,     from_time_unit,  to_time_unit)

            data.attrs['units'] = new_unit
            current_time        = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            history_update      = str(current_time)+' the units of precipitation are converted from ' + str(data.units) + ' to ' + str(new_unit) + ';\n '
            try:
                history_attr                    = data.attrs['history'] + history_update
                data.attrs['history']           = history_attr
            except AttributeError:
                data.attrs['history']           = history_update
            return data
    
        
    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ 
    def latitude_band(self, data, trop_lat = None):
        """ Function to select the Dataset for specified latitude range

        Args:
            data (xarray):                  The Dataset
            trop_lat (int/float, optional): The maximumal and minimal tropical latitude values in Dataset.  Defaults to None.

        Returns:
            xarray: The Dataset only for selected latitude range. 
        """    
        
        
        self.class_attributes_update(trop_lat = trop_lat)
        
        coord_lat, coord_lon = self.coordinate_names(data)
        self.class_attributes_update(trop_lat = trop_lat)
        return data.where(abs(data[coord_lat]) <= self.trop_lat, drop = True)

    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ 
    def time_band(self, data,
                  s_time = None,        f_time = None,
                  s_year = None,        f_year = None,
                  s_month = None,       f_month = None):
        """ Function to select the Dataset for specified time range

        Args:
            data (xarray):                  The Dataset
            s_time (str, optional):         The starting time of the Dataset.       Defaults to None.
            f_time (str, optional):         The ending time of the Dataset.         Defaults to None.
            s_year (str, optional):         The starting year of the Dataset.       Defaults to None.
            f_year (str, optional):         The ending year of the Dataset.         Defaults to None.
            s_month (str, optional):        The starting month of the Dataset.      Defaults to None.
            f_month (str, optional):        The ending month of the Dataset.        Defaults to None.

        Returns:
            xarray: The Dataset only for selected time range. 
        """          
        self.class_attributes_update(s_time=s_time,         f_time=f_time,
                                     s_year=s_year,         f_year=f_year, 
                                     s_month=s_month,       f_month=f_month)

        if isinstance(self.s_time, int)     and isinstance(self.f_time, int):
            if self.s_time != None          and self.f_time != None:
                data = data.isel(time=slice(self.s_time, self.f_time))

        elif self.s_year != None            and self.f_year == None:
            data = data.where(data['time.year'] == self.s_year, drop = True)

        elif self.s_year != None            and self.f_year != None:
            data = data.where(data['time.year'] >= self.s_year, drop = True)
            data = data.where(data['time.year'] <= self.f_year, drop = True)

        if self.s_month != None             and self.f_month != None:
            data = data.where(data['time.month'] >= self.s_month, drop = True)
            data = data.where(data['time.month'] <= self.f_month, drop = True) 
        
        if isinstance(self.s_time, str)     and isinstance(self.f_time, str):
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
        elif self.s_time != None            and  self.f_time == None:
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
    def dataset_into_1d(self, data, model_variable = 'tprate', sort = False): 
        """ Function to convert Dataset into 1D array.

        Args:
            data (xarray):                      The Dataset
            model_variable (str, optional):     The variable of the Dataset.    Defaults to 'tprate'.
            sort (bool, optional):              The flag to sort the array.     Defaults to False.

        Returns:
            xarray: The 1D array.
        """ 
           
        coord_lat, coord_lon = self.coordinate_names(data)

        try:
            data        = data[model_variable]
        except KeyError:
            data        = data

        try:
            data_1d     = data.stack(total=['time', coord_lat, coord_lon])
        except KeyError:
            data_1d     = data.stack(total=[coord_lat, coord_lon])
        if sort == True:
            data_1d     = data_1d.sortby(data_1d)
        return data_1d

  
    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """
    def preprocessing(self, data,
                        preprocess = True,      model_variable = "tprate",      trop_lat = None,
                        s_time  = None,         f_time  = None,
                        s_year  = None,         f_year  = None,
                        s_month = None,         f_month = None,
                        sort = False,           dask_array = False):
        """ Function to preprocess the Dataset according to provided arguments and attributes of the class.

        Args:
            data (xarray):                  The Dataset.
            preprocess (bool, optional):    If sort is True, the functiom preprocess Dataset.   Defaults to True.
            model_variable (str, optional): The variable of the Dataset.                        Defaults to 'tprate'.
            trop_lat (float, optional):     The maximumal and minimal tropical latitude values in Dataset.  Defaults to None.
            s_time (str/int, optional):     The starting time value/index in Dataset.           Defaults to None.
            f_time (str/int, optional):     The final time value/index in Dataset.              Defaults to None.
            s_year (int, optional):         The starting year in Dataset.                       Defaults to None.
            f_year (int, optional):         The final year in Dataset.                          Defaults to None.
            s_month (int, optional):        The starting month in Dataset.                      Defaults to None.
            f_month (int, optional):        The final month in Dataset.                         Defaults to None.
            sort (bool, optional):          If sort is True, the DataArray is sorted.           Defaults to False.
            dask_array (bool, optional):    If sort is True, the function return daskarray.     Defaults to False.

        Returns:
            xarray: Preprocessed Dataset according to the arguments of the function
        """        
        
        self.class_attributes_update(trop_lat = trop_lat,
                                     s_time = s_time,       f_time = f_time,
                                     s_year = s_year,       f_year = f_year,        s_month = s_month,      f_month = f_month)
        if preprocess == True:
            if 'time' in data.coords:
                data_per_time_band  = self.time_band(data,
                                                    s_time  = self.s_time,       f_time  = self.f_time,
                                                    s_year  = self.s_year,       f_year  = self.f_year,
                                                    s_month = self.s_month,      f_month = self.f_month)
            else:
                data_per_time_band  = data
            
            try:
                data_variable       = data_per_time_band[model_variable]
            except KeyError:
                data_variable       = data_per_time_band

            data_per_lat_band       = self.latitude_band(data_variable, trop_lat = self.trop_lat)
            
            if dask_array == True:
                data_1d             = self.dataset_into_1d(data_per_lat_band)
                dask_data           = da.from_array(data_1d)
                return dask_data
            else:
                return data_per_lat_band
        else:
            return data
    
    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ 
    def histogram(self, data,           data_with_global_atributes = None,
                  weights = None,       preprocess = True,      trop_lat = 10,              model_variable = 'tprate',
                  s_time = None,        f_time = None,          s_year = None,              f_year = None,      s_month = None,     f_month = None,
                  num_of_bins = None,   first_edge = None,      width_of_bin  = None,       bins = 0,
                  lazy = False,         create_xarray = True,   path_to_histogram = None):
        """ Function to calculate a histogram of the Dataset.

        Args:
            data (xarray.Dataset):          The input Dataset.
            preprocess (bool, optional):    If True, preprocesses the Dataset.              Defaults to True.
            trop_lat (float, optional):     The maximum absolute value of tropical latitude in the Dataset. Defaults to 10.
            model_variable (str, optional): The variable of interest in the Dataset.        Defaults to 'tprate'.
            weights (array-like, optional): The weights of the data.                        Defaults to None.
            data_with_global_attributes (xarray.Dataset, optional): The Dataset with global attributes. Defaults to None.
            s_time (str/int, optional):     The starting time value/index in the Dataset.   Defaults to None.
            f_time (str/int, optional):     The final time value/index in the Dataset.      Defaults to None.
            s_year (int, optional):         The starting year in the Dataset.               Defaults to None.
            f_year (int, optional):         The final year in the Dataset.                  Defaults to None.
            s_month (int, optional):        The starting month in the Dataset.              Defaults to None.
            f_month (int, optional):        The final month in the Dataset.                 Defaults to None.
            num_of_bins (int, optional):    The number of bins for the histogram.           Defaults to None.
            first_edge (float, optional):   The starting edge value for the bins.           Defaults to None.
            width_of_bin (float, optional): The width of each bin.                          Defaults to None.
            bins (int, optional):           The number of bins for the histogram (alternative argument to 'num_of_bins'). Defaults to 0.
            lazy (bool, optional):          If True, delays computation until necessary.    Defaults to False.
            create_xarray (bool, optional): If True, creates an xarray dataset from the histogram counts. Defaults to True.
            path_to_histogram (str, optional):   The path to save the xarray dataset.       Defaults to None.

        Returns:
            xarray.Dataset or numpy.ndarray: The histogram of the Dataset.
        """
        self.class_attributes_update(trop_lat = trop_lat,
                                     s_time  = s_time,           f_time  = f_time,
                                     s_year  = s_year,           f_year  = f_year,
                                     s_month = s_month,          f_month = f_month, 
                                     first_edge = first_edge,    num_of_bins = num_of_bins,      width_of_bin = width_of_bin)

        coord_lat, coord_lon = self.coordinate_names(data)

        if isinstance(self.bins, int):
            bins            = [self.first_edge  + i*self.width_of_bin for i in range(0, self.num_of_bins+1)]
            width_table     = [self.width_of_bin for j in range(0, self.num_of_bins)]
            center_of_bin   = [bins[i] + 0.5*width_table[i] for i in range(0, len(bins)-1)]
        else:
            bins            = self.bins
            width_table     = [self.bins[i+1]-self.bins[i] for i in range(0, len(self.bins)-1)]
            center_of_bin   = [self.bins[i] + 0.5*width_table[i] for i in range(0, len(self.bins)-1)]


        data_original=data
        if preprocess == True:
            data = self.preprocessing(data, preprocess = preprocess,
                                      model_variable   = model_variable,     trop_lat= self.trop_lat,
                                      s_time  = self.s_time,                 f_time  = self.f_time,
                                      s_year  = self.s_year,                 f_year  = self.f_year,           
                                      s_month = self.s_month,                f_month = self.f_month,
                                      sort = False,                          dask_array = False)
            
        data_with_final_grid=data

        if weights is not None:

            weights         = self.latitude_band(weights, trop_lat = self.trop_lat)
            data, weights   = xr.broadcast(data, weights)
            weights         = weights.stack(total=['time', coord_lat, coord_lon])
            weights_dask    = da.from_array(weights)
    

        data_dask           = da.from_array(data.stack(total=['time', coord_lat, coord_lon]))
        
        if weights is not None:
            counts, edges   = dh.histogram(data_dask, bins = bins,   weights = weights_dask,    storage = dh.storage.Weight())
        else:
            counts, edges   = dh.histogram(data_dask, bins = bins,   storage = dh.storage.Weight())
        if not lazy:
            counts          = counts.compute()
            edges           = edges.compute()

        width_table         = [edges[i+1]-edges[i] for i in range(0, len(edges)-1)]
        center_of_bin       = [edges[i] + 0.5*width_table[i] for i in range(0, len(edges)-1)]
        counts_per_bin      =  xr.DataArray(counts, coords=[center_of_bin], dims=["center_of_bin"])
        
        counts_per_bin      = counts_per_bin.assign_coords(width=("center_of_bin", width_table))
        counts_per_bin.attrs= data.attrs
        
        if data_with_global_atributes is None:
            data_with_global_atributes = data_original

        if not lazy and create_xarray:
            tprate_dataset      = counts_per_bin.to_dataset(name="counts")
            tprate_dataset.attrs= data_with_global_atributes.attrs
            tprate_dataset      = self.add_frequency_and_pdf(tprate_dataset = tprate_dataset, path_to_histogram = path_to_histogram)
            
            
            for variable in (None, 'counts', 'frequency', 'pdf'):
                tprate_dataset  = self.grid_attributes(data = data_with_final_grid, tprate_dataset = tprate_dataset, variable = variable)
            return tprate_dataset
        else:
            tprate_dataset      = counts_per_bin.to_dataset(name="counts")
            tprate_dataset.attrs= data_with_global_atributes.attrs
            counts_per_bin      = self.grid_attributes(data = data_with_final_grid, tprate_dataset = tprate_dataset, variable='counts')
            tprate_dataset      = self.grid_attributes(data = data_with_final_grid, tprate_dataset = tprate_dataset)
            return counts_per_bin
        
        
    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ 
    def dataset_to_netcdf(self, dataset = None, path_to_netcdf = None, name_of_file = None):
        """ Function to save the histogram.

        Args:
            dataset (xarray, optional):         The Dataset with the histogram.     Defaults to None.
            path_to_netcdf (str, optional):  The path to save the histogram.     Defaults to None.

        Returns:
            str: The path to save the histogram.
        """
        if path_to_netcdf is not None:
            create_folder(folder    = str(path_to_netcdf), loglevel = 'WARNING')

            if name_of_file is None:
                name_of_file    = '_'
            time_band           = dataset.counts.attrs['time_band']
            try:
                name_of_file    = name_of_file +'_'+ re.split(":", re.split(", ", time_band)[0])[0] +'_'+ re.split(":", re.split(", ", time_band)[1])[0]
            except IndexError:
                name_of_file    = name_of_file +'_'+ re.split("'", re.split(":", time_band)[0])[1]

            path_to_netcdf      = path_to_netcdf + name_of_file + '_histogram.nc'
        
        if path_to_netcdf is not None:
            dataset.to_netcdf(path = path_to_netcdf)
        return path_to_netcdf
    
    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ 
    def grid_attributes(self, data = None, tprate_dataset = None, variable = None):
        """ Function to add the attributes with information about the space and time grid to the Dataset.

        Args:
            data (xarray, optional):            The Dataset with a final time and space grif, for which calculations were performed.    Defaults to None.
            tprate_dataset (xarray, optional):  Created Dataset by the diagnostics, which we would like to populate with attributes.    Defaults to None.
            variable (str, optional):           The name of the Variable objects (not a physical variable) of the created Dataset.      Defaults to None.

        Returns:
            xarray.Dataset: The updated dataset with grid attributes. The grid attributes include time_band, lat_band, and lon_band.

        Raises:
            KeyError: If the obtained xarray.Dataset doesn't have global attributes.
        """
        coord_lat, coord_lon= self.coordinate_names(data)

        if data.time.size>1:
            time_band       = str(data.time[0].values)+', '+str(data.time[-1].values)+', freq='+str(time_interpreter(data))
        else:
            time_band       = str(data.time.values)
        if data[coord_lat].size>1:
            latitude_step   = data[coord_lat][1].values - data[coord_lat][0].values
            lat_band        = str(data[coord_lat][0].values)+', '+str(data[coord_lat][-1].values)+', freq='+str(latitude_step)
        else:
            lat_band        = data[coord_lat].values
            latitude_step   = data[coord_lat].values
        if data[coord_lon].size>1:
            longitude_step  = data[coord_lon][1].values - data[coord_lon][0].values
            lon_band        = str(data[coord_lon][0].values)+', '+str(data[coord_lon][-1].values)+', freq='+str(longitude_step)
        else:
            longitude_step  = data[coord_lon].values
            lon_band        = data[coord_lon].values 

        if variable is None:
            current_time    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            history_update  = str(current_time)+' histogram is calculated for time_band: ['+str(time_band)+']; lat_band: ['+str(lat_band)+']; lon_band: ['+str(lon_band)+'];\n '
            try:
                history_attr                    = tprate_dataset.attrs['history'] + history_update
                tprate_dataset.attrs['history'] = history_attr
            except KeyError:
                print("The obtained xarray.Dataset doesn't have global attributes. Consider adding global attributes manually to the dataset.")
        else:
            tprate_dataset[variable].attrs['time_band'] = time_band
            tprate_dataset[variable].attrs['lat_band']  = lat_band
            tprate_dataset[variable].attrs['lon_band']  = lon_band

        return tprate_dataset
    
    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ 
    def add_frequency_and_pdf(self,  tprate_dataset = None, path_to_histogram = None):
        """ Function to convert the histogram to xarray.Dataset.

        Args:
            hist_counts (xarray, optional):     The histogram with counts.      Defaults to None.
            path_to_histogram (str, optional):  The path to save the histogram. Defaults to None.

        Returns:
            xarray: The xarray.Dataset with the histogram.
        """        
        #create_folder(folder=path_to_histogram, loglevel='WARNING')
        hist_frequency                  = self.convert_counts_to_frequency(tprate_dataset.counts)
        tprate_dataset['frequency']     = hist_frequency

        hist_pdf                        = self.convert_counts_to_pdf(tprate_dataset.counts)
        tprate_dataset['pdf']           = hist_pdf

        if path_to_histogram is not None:
            self.dataset_to_netcdf(dataset = tprate_dataset, path_to_netcdf = path_to_histogram)
        return tprate_dataset

    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ 
    def open_dataset(self, path_to_netcdf = None):
        """ Function to load a histogram dataset from a file using pickle.

        Args:
            path_to_netcdf (str):       The path to the dataset file.

        Returns:
            object:                     The loaded histogram dataset.

        Raises:
            FileNotFoundError:          If the specified dataset file is not found.
        
        """
        try:
            dataset = xr.open_dataset(path_to_netcdf)
            return dataset
        except FileNotFoundError:
            raise FileNotFoundError("The specified dataset file was not found.")
    
    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ 
    def merge_two_datasets(self, tprate_dataset_1 = None, tprate_dataset_2 = None):
        """ Function to merge two datasets.

        Args:
            tprate_dataset_1 (xarray, optional):    The first dataset.     Defaults to None.
            tprate_dataset_2 (xarray, optional):    The second dataset.    Defaults to None.

        Returns:
            xarray:     The xarray.Dataset with the merged data.
        """
        
        if isinstance(tprate_dataset_1, xr.Dataset) and isinstance(tprate_dataset_2, xr.Dataset):
            dataset_3       = tprate_dataset_1.copy(deep = True)
            dataset_3.attrs = {**tprate_dataset_1.attrs, **tprate_dataset_2.attrs}
            
            for attribute in tprate_dataset_1.attrs:
                if tprate_dataset_1.attrs[attribute]    != tprate_dataset_2.attrs[attribute]:
                    dataset_3.attrs[attribute]          = str(tprate_dataset_1.attrs[attribute])+';\n '+str(tprate_dataset_2.attrs[attribute])


            dataset_3.counts.values     = tprate_dataset_1.counts.values + tprate_dataset_2.counts.values
            dataset_3.frequency.values  = self.convert_counts_to_frequency(dataset_3.counts)
            dataset_3.pdf.values        = self.convert_counts_to_pdf(dataset_3.counts)

            for variable in ('counts', 'frequency', 'pdf'):
                for attribute in tprate_dataset_1.counts.attrs:
                    dataset_3[variable].attrs                       = {**tprate_dataset_1[variable].attrs, **tprate_dataset_2[variable].attrs}
                    if tprate_dataset_1[variable].attrs[attribute]  != tprate_dataset_2[variable].attrs[attribute]:
                        dataset_3[variable].attrs[attribute]        = str(tprate_dataset_1[variable].attrs[attribute])+';\n ' + str(tprate_dataset_2[variable].attrs[attribute])

            return dataset_3
        
    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ 
    def merge_list_of_histograms(self, path_to_histograms = None, multi = None, all = False):
        """ Function to merge list of histograms.

        Args:
            path_to_histograms (str, optional):     The path to the list of histograms.     Defaults to None.
            multi (int, optional):                  The number of histograms to merge.      Defaults to None.
            all (bool, optional):                   If True, all histograms in the repository will be merged. Defaults to False.

        Returns:
            xarray: The xarray.Dataset with the merged data.
        """

        histogram_list          = [f for f in listdir(path_to_histograms) if isfile(join(path_to_histograms, f))]
        histogram_list.sort()

        if all:
            histograms_to_load  = [str(path_to_histograms) + str(histogram_list[i]) for i in range(0, len(histogram_list))]
        elif multi is not None:
            histograms_to_load  = [str(path_to_histograms) + str(histogram_list[i]) for i in range(0, multi)]

        if len(histograms_to_load) > 0:
            for i in range(0, len(histograms_to_load)):
                if i == 0:
                    dataset     = self.open_dataset(path_to_netcdf = histograms_to_load[i])
                else:
                    dataset     = self.merge_two_datasets(tprate_dataset_1 = dataset,
                                                      tprate_dataset_2 = self.open_dataset(path_to_netcdf = histograms_to_load[i]))
            return dataset
        else:
            raise Exception('The specified repository is empty.')

    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ 
    def convert_counts_to_frequency(self, data):
        """ Function to convert the counts to the frequency.

        Args:
            data (xarray): The counts.

        Returns:
            xarray: The frequency.
        """
        sum_of_counts           = sum(data[:])
        frequency               = data[0:]/sum_of_counts
        frequency_per_bin       = xr.DataArray(frequency, coords=[data.center_of_bin],    dims=["center_of_bin"])
        frequency_per_bin       = frequency_per_bin.assign_coords(width=("center_of_bin", data.width.values))
        frequency_per_bin.attrs = data.attrs
        sum_of_frequency        = sum(frequency_per_bin[:])
        
        if abs(sum_of_frequency -1) < 10**(-4):
            return frequency_per_bin
        else:
            raise Exception("Test failed.")

    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ 
    def convert_counts_to_pdf(self, data):
        """ Function to convert the counts to the pdf.

        Args:
            data (xarray): The counts.

        Returns:
            xarray: The pdf.
        """
        sum_of_counts       = sum(data[:])
        pdf                 = data[0:]/(sum_of_counts*data.width[0:])
        pdf_per_bin         = xr.DataArray(pdf, coords=[data.center_of_bin],    dims=["center_of_bin"])
        pdf_per_bin         = pdf_per_bin.assign_coords(width=("center_of_bin", data.width.values))
        pdf_per_bin.attrs   = data.attrs
        sum_of_pdf          = sum(pdf_per_bin[:]*data.width[0:])
        
        if abs(sum_of_pdf-1.) < 10**(-4):
            return pdf_per_bin
        else:
            raise Exception("Test failed.")


    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """
    def histogram_plot(self, data, \
                       weights = None,      frequency = False,      pdf = True, \
                       smooth  = True,      step = False,           color_map = False, \
                       ls = '-',            ylogscale = True,       xlogscale = False, \
                       color = 'tab:blue',  figsize = 1,            legend = '_Hidden', \
                       plot_title = None,   loc = 'upper right',    varname = 'Precipitation',  \
                       add = None,          fig = None,             path_to_figure = None):
        """ Function to generate a histogram figure based on the provided data.

        Args:
            data:                           The data for the histogram.
            weights (optional):             An array of weights for the data.       Default is None.
            frequency (bool, optional):     Whether to plot frequency.              Default is False.
            pdf (bool, optional):           Whether to plot the probability density function (PDF). Default is True.
            smooth (bool, optional):        Whether to plot a smooth line.          Default is True.
            step (bool, optional):          Whether to plot a step line.            Default is False.
            color_map (bool or str, optional): Whether to apply a color map to the histogram bars.
                If True, uses the 'viridis' color map. If a string, uses the specified color map. Default is False.
            ls (str, optional):             The line style for the plot.            Default is '-'.
            ylogscale (bool, optional):     Whether to use a logarithmic scale for the y-axis. Default is True.
            xlogscale (bool, optional):     Whether to use a logarithmic scale for the x-axis. Default is False.
            color (str, optional):          The color of the plot.                  Default is 'tab:blue'.
            figsize (float, optional):      The size of the figure.                 Default is 1.
            legend (str, optional):         The legend label for the plot.          Default is '_Hidden'.
            varname (str, optional):        The name of the variable for the x-axis label. Default is 'Precipitation'.
            plot_title (str, optional):     The title of the plot.                  Default is None.
            loc(str, optional):             The location of the legend.             Default to 'upper right'. 
            add (tuple, optional):          Tuple of (fig, ax) to add the plot to an existing figure.
            fig (object, optional):         The figure object to plot on. If provided, ignores the 'add' argument.
            path_to_figure (str, optional): The path to save the figure. If provided, saves the figure at the specified path.


        Returns:
            A tuple (fig, ax) containing the figure and axes objects.
            """
        if fig is not None:
                fig, ax  = fig
                if color == 'tab:blue': color   = 'tab:orange'
        elif add is None and fig is None:
            fig, ax = plt.subplots( figsize=(8*figsize, 5*figsize) )
        elif add is not None:
            fig, ax  = add 
            if color == 'tab:blue': color   = 'tab:orange'

        if not pdf and not frequency:
            try:
                data = data['counts']
            except KeyError:
                data = data
        elif pdf and not frequency:
            try:
                data = data['pdf']
            except KeyError:
                try:
                    data = data['counts']
                    data = self.convert_counts_to_pdf(data)
                except KeyError:
                    data = self.convert_counts_to_pdf(data)

        elif not pdf and frequency:
            try:
                data = data['frequency']
            except KeyError:
                try:
                    data = data['counts']
                    data = self.convert_counts_to_frequency(data)
                except KeyError:
                    data = self.convert_counts_to_frequency(data)
            data = self.convert_counts_to_frequency(data)
        
        if smooth:
            plt.plot(data.center_of_bin, data,
                linewidth=3.0, ls = ls, color = color, label = legend)
            plt.grid(True)
        elif step:
            plt.step(data.center_of_bin, data,
                linewidth=3.0, ls = ls, color = color, label = legend)
            plt.grid(True)
        elif color_map:
            if weights is None:
                N, bins, patches = plt.hist(x = data.center_of_bin, bins = data.center_of_bin, weights = data,    label = legend)
            else:
                N, bins, patches = plt.hist(x = data.center_of_bin, bins = data.center_of_bin, weights = weights, label = legend)
            
            fracs   = ((N**(1 / 5)) / N.max())
            norm    = colors.Normalize(fracs.min(), fracs.max())

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
            plt.ylabel('PDF',       fontsize=14)
        elif not pdf and frequency:
            plt.ylabel('Frequency', fontsize=14)
        else:
            plt.ylabel('Counts',    fontsize=14)
        
        plt.title(plot_title,       fontsize=16)


        if legend!='_Hidden':
            plt.legend(loc=loc,     fontsize=12)

        # set the spacing between subplots
        plt.tight_layout()
        if path_to_figure is not None and isinstance(path_to_figure, str):
            create_folder(folder    = extract_directory_path(path_to_figure), loglevel = 'WARNING')
            plt.savefig(path_to_figure)
        return {fig, ax}
    

    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ 
    def mean_along_coordinate(self, data,           model_variable = 'tprate',      preprocess=True,
                              trop_lat = None,      coord   = 'time',               glob=False,
                              s_time   = None,      f_time  = None,
                              s_year   = None,      f_year  = None,
                              s_month  = None,      f_month = None):
        """ Function to calculate the mean value of variable in Dataset.

        Args:
            data (xarray):                      The Dataset
            model_variable (str, optional):     The variable of the Dataset.            Defaults to 'tprate'.
            trop_lat (float, optional):         The maximumal and minimal tropical latitude values in Dataset.  Defaults to None.
            coord (str, optional):              The coordinate of the Dataset.          Defaults to 'time'.
            s_time (str, optional):             The starting time of the Dataset.       Defaults to None.
            f_time (str, optional):             The ending time of the Dataset.         Defaults to None.
            s_year (str, optional):             The starting year of the Dataset.       Defaults to None.
            f_year (str, optional):             The ending year of the Dataset.         Defaults to None.
            s_month (str, optional):            The starting month of the Dataset.      Defaults to None.
            f_month (str, optional):            The ending month of the Dataset.        Defaults to None.

        Returns:
            xarray:         The mean value of variable.
        """
        if preprocess == True:
            data = self.preprocessing(data,                                  preprocess = preprocess,
                                      model_variable   = model_variable,     trop_lat= self.trop_lat,
                                      s_time  = self.s_time,                 f_time  = self.f_time,
                                      s_year  = self.s_year,                 f_year  = self.f_year,   
                                      s_month = self.s_month,                f_month = self.f_month,
                                      sort = False,                          dask_array = False)
        coord_lat, coord_lon = self.coordinate_names(data)
        if coord in data.dims:
            
            self.class_attributes_update(trop_lat = trop_lat,
                                         s_time   = s_time,          f_time  = f_time,
                                         s_year   = s_year,          f_year  = f_year,
                                         s_month  = s_month,         f_month = f_month)
            if glob:
                return data.mean()
            else:
                if coord    == 'time':
                    return data.mean(coord_lat).mean(coord_lon)
                elif coord  == coord_lat:
                    return data.mean('time').mean(coord_lon)
                elif coord  == coord_lon:
                    return data.mean('time').mean(coord_lat)
        else:
            for i in data.dims:
                coord = i
            return data.median(coord)



    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """
    def median_along_coordinate(self, data,                 trop_lat = None,        preprocess = True,
                                model_variable = 'tprate',  coord    = 'time',      glob       = False,
                                s_time  = None,             f_time   = None,
                                s_year  = None,             f_year   = None,
                                s_month = None,             f_month  = None):
        """ Function to calculate the median value of variable in Dataset.

        Args:
            data (xarray):                      The Dataset
            model_variable (str, optional):     The variable of the Dataset.            Defaults to 'tprate'.
            trop_lat (float, optional):         The maximumal and minimal tropical latitude values in Dataset.  Defaults to None.
            coord (str, optional):              The coordinate of the Dataset.          Defaults to 'time'.
            s_time (str, optional):             The starting time of the Dataset.       Defaults to None.
            f_time (str, optional):             The ending time of the Dataset.         Defaults to None.
            s_year (str, optional):             The starting year of the Dataset.       Defaults to None.
            f_year (str, optional):             The ending year of the Dataset.         Defaults to None.
            s_month (str, optional):            The starting month of the Dataset.      Defaults to None.
            f_month (str, optional):            The ending month of the Dataset.        Defaults to None.

        Returns:
            xarray: The median value of variable.
        """      
        if preprocess == True:
            data = self.preprocessing(data,                                  preprocess = preprocess,
                                      model_variable   = model_variable,     trop_lat= self.trop_lat,
                                      s_time  = self.s_time,                 f_time  = self.f_time,
                                      s_year  = self.s_year,                 f_year  = self.f_year,    
                                      s_month = self.s_month,                f_month = self.f_month,
                                      sort = False,                          dask_array = False)

        coord_lat, coord_lon = self.coordinate_names(data)
        if coord in data.dims:
            self.class_attributes_update(trop_lat = trop_lat,
                                         s_time   = s_time,         f_time  = f_time,
                                         s_year   = s_year,         f_year  = f_year,
                                         s_month  = s_month,        f_month = f_month)
        
            if glob:
                return data.median(coord_lat).median(coord_lon).mean('time')
            else:
                if coord    == 'time':
                    return data.median(coord_lat).median(coord_lon)
                elif coord  == coord_lat:
                    return data.median('time').median(coord_lon)
                elif coord  == coord_lon:
                    return data.median('time').median(coord_lat)
            
        else:
            for i in data.dims:
                coord = i
            return data.median(coord)
        
    
    
    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """
    def mean_and_median_plot(self, data,                        glob=False,                     preprocess=True,
                             model_variable = 'tprate',         variability = False,            coord      = 'time',  
                             trop_lat       = None,             get_mean    = True,             get_median = False,
                             s_time         = None,             f_time      = None,             s_year     = None,    
                             f_year         = None,             s_month     = None,             f_month    = None,
                             legend         = '_Hidden',        figsize     = 1,                ls         = '-',
                             maxticknum     = 12,               color       = 'tab:blue',       varname    = 'Precipitation',
                             ylogscale      = False,            xlogscale   = False,            loc        = 'upper right',
                             add            = None,             fig         = None,             plot_title = None,   
                             path_to_figure = None):
        """ Function to plot the mean or median value of variable in Dataset.

        Args:
            data (xarray):                  The Dataset
            model_variable (str, optional): The variable of the Dataset.            Defaults to 'tprate'.
            coord (str, optional):          The coordinate of the Dataset.          Defaults to 'time'.
            trop_lat (float, optional):     The maximumal and minimal tropical latitude values in Dataset.  Defaults to None.
            variability (bool, optional):   The flag to calculate the variability of the variable.  Defaults to False.
            get_mean (bool, optional):      The flag to calculate the mean of the variable.  Defaults to True.
            get_median (bool, optional):    The flag to calculate the median of the variable.  Defaults to False.
            s_time (str, optional):         The starting time of the Dataset.       Defaults to None.
            f_time (str, optional):         The ending time of the Dataset.         Defaults to None.
            s_year (str, optional):         The starting year of the Dataset.       Defaults to None."""

        if fig is not None:
            fig, ax  = fig
            if color == 'tab:blue': color   = 'tab:orange'
        elif add is None and fig is None:
            fig, ax = plt.subplots( figsize=(8*figsize, 5*figsize) )
        elif add is not None:
            fig, ax  = add
            if color == 'tab:blue': color   = 'tab:orange'
        
        self.class_attributes_update(trop_lat = trop_lat, 
                                     s_time   = s_time,         f_time  = f_time,
                                     s_year   = s_year,         f_year  = f_year,
                                     s_month  = s_month,        f_month = f_month)
            

        if preprocess == True:
            data_with_final_grid = self.preprocessing(data,                                    preprocess = preprocess,
                                                        model_variable   = model_variable,     trop_lat= self.trop_lat,
                                                        s_time  = self.s_time,                 f_time  = self.f_time,
                                                        s_year  = self.s_year,                 f_year  = self.f_year,     
                                                        s_month = self.s_month,                f_month = self.f_month,
                                                        sort = False,                          dask_array = False)

        if get_mean:
            data_average = self.mean_along_coordinate(data,                                     preprocess=preprocess,
                                                        glob       = glob,                      model_variable = model_variable,
                                                        trop_lat   = trop_lat,                  coord    = coord,
                                                        s_time  = self.s_time,                  f_time  = self.f_time,
                                                        s_year  = self.s_year,                  f_year  = self.f_year,     
                                                        s_month = self.s_month,                 f_month = self.f_month)
        if get_median:
            data_average = self.median_along_coordinate(data,                                   preprocess=preprocess,
                                                        glob       = glob,                      model_variable = model_variable,
                                                        trop_lat   = trop_lat,                  coord    = coord,
                                                        s_time  = self.s_time,                 f_time  = self.f_time,
                                                        s_year  = self.s_year,                 f_year  = self.f_year,     
                                                        s_month = self.s_month,                f_month = self.f_month)
        
        
        if variability      and get_mean:
            data_variability_from_average               = data_average.copy(deep=True)
            data_variability_from_average.values        = (data_average.values -  data_average.mean(coord).values)/data_average.values
        coord_lat, coord_lon= self.coordinate_names(data)

        if data[coord].size<=1:
            raise Exception("The length of the coordinate should be more than 1.")
        
        # make a plot with different y-axis using second axis object
        if coord            == 'time':
            if 'm' in time_interpreter(data_with_final_grid):
                labels      = [str(data_with_final_grid['time.hour'][i].values) + ':'+str(data_with_final_grid['time.minute'][i].values)
                                                                                    for i in range(0, data_with_final_grid.time.size)]
                labels_int  = [float(data_with_final_grid['time.hour'][i].values)   for i in range(0, data_with_final_grid.time.size)]
            elif 'H' in time_interpreter(data_with_final_grid):
                labels      = [convert_24hour_to_12hour_clock(data_with_final_grid, i)
                                                                                    for i in range(0, data_with_final_grid.time.size)]
                labels_int  = [float(data_with_final_grid['time.hour'][i].values)   for i in range(0, data_with_final_grid.time.size)]
            elif time_interpreter(data_with_final_grid) == 'D':
                labels      = [str(data_with_final_grid['time.day'][i].values + convert_monthnumber_to_str(data_with_final_grid, i))
                                                                                    for i in range(0, data_with_final_grid.time.size)]
                labels_int  = [float(data_with_final_grid['time.day'][i].values)    for i in range(0, data_with_final_grid.time.size)]
            elif time_interpreter(data_with_final_grid) == 'M':
                labels      = [convert_monthnumber_to_str(data_with_final_grid, i)
                                                                                    for i in range(0, data_with_final_grid.time.size)]
                labels_int  = [float(data_with_final_grid['time.month'][i].values)  for i in range(0, data_with_final_grid.time.size)]
            else:
                labels      = [None for i in range(0, data_with_final_grid.time.size)]
                labels_int  = [None for i in range(0, data_with_final_grid.time.size)]

        elif coord          == coord_lat:
            labels_int      = data_with_final_grid[coord_lat]
        elif coord          == coord_lon:
            labels_int      = data_with_final_grid[coord_lon]

        if data_average.size== 1:
            if variability:
                plt.axhline(y=float(data_variability_from_average),         color = color,  label = legend)
            else:
                plt.axhline(y=float(data_average.values),                   color = color,  label = legend)
        else:
            if variability:
                plt.plot(labels_int,        data_variability_from_average,  color = color,  label = legend)
            else:
                if coord == 'time':
                    plt.scatter(labels_int, data_average,                   color = color,  label = legend)
                else:
                    plt.plot(labels_int,    data_average,                   color = color,  label = legend) 

        if coord == 'time':
            plt.gca().set_xticks(labels_int,  labels)

        plt.gca().xaxis.set_major_locator(plt.MaxNLocator(maxticknum))
        plt.gca().tick_params(axis = 'both',   which = 'major',    pad = 10)
        plt.xlim([min(labels_int),    max(labels_int)])
        
        plt.grid(True)

        if coord   == 'time':
            plt.xlabel('Timestep index',                        fontsize=12)
            if data['time.year'][0].values  == data['time.year'][-1].values:
                plt.xlabel(str(data['time.year'][0].values),    fontsize=12)
            else:
                plt.xlabel(str(data['time.year'][0].values)+' - '+str(data['time.year'][-1].values),
                                                                fontsize=12)
        elif coord == coord_lat:
            plt.xlabel('Latitude',                              fontsize=12)
        elif coord == coord_lon:
            plt.xlabel('Longitude',                             fontsize=12)
        try:
            plt.ylabel(str(varname)+', '+str(data[model_variable].attrs['units']),
                                                                fontsize=12)
        except KeyError:
            plt.ylabel(str(varname),                            fontsize=12)

        if plot_title is None:
            if variability:
                plt.title('Bias of '         +str(varname),     fontsize=17,    pad=15)
            elif not variability        and get_mean:
                plt.title('Mean values of '  +str(varname),     fontsize=17,    pad=15)
            elif not variability        and get_median:
                plt.title('Median values of '+str(varname),     fontsize=17,    pad=15)
        else:
            plt.title(plot_title,                               fontsize=17,    pad=15)
        
        if legend!='_Hidden':
            plt.legend(loc=loc,                                 fontsize=12,    ncol=2)
        if ylogscale:
            plt.yscale('log')
        if xlogscale:
            plt.xscale('log')

        # set the spacing between subplots
        plt.tight_layout()
        if path_to_figure is not None and isinstance(path_to_figure, str):

            create_folder(folder    = extract_directory_path(path_to_figure), loglevel = 'WARNING')

            plt.savefig(path_to_figure,
                        bbox_inches  = "tight",
                        pad_inches   = 1,
                        transparent  = True,
                        facecolor    = "w",
                        edgecolor    = 'w',
                        orientation  = 'landscape')
        return {fig, ax}

    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """
    def twin_data_and_observations(self, data,                          dummy_data = None,                    trop_lat = 10,                      
                                    model_variable = 'tprate',
                                    s_time  = None,                     f_time   = None,                    s_year  = None,               
                                    f_year   = None,                    s_month = None,                     f_month  = None,
                                    model = 'era5',                     source = 'monthly',                 plev = 0,
                                    space_grid_factor = None,           time_freq = None,                   preprocess = True,
                                    time_length = None,                 time_grid_factor = None):
        
        """ Function to regride the data and observations to the same grid. """

        self.class_attributes_update(trop_lat = trop_lat,
                                    s_time   = s_time,                  f_time  = f_time,
                                    s_year   = s_year,                  f_year  = f_year,
                                    s_month  = s_month,                 f_month = f_month)
        try:
            data                    = data[model_variable]
        except KeyError:
            data                    = data
        new_unit = data.units
        if dummy_data is None:
            if model                    == 'era5':
                reader                  = Reader(model="ERA5", exp="era5", source=source)
                observations            = reader.retrieve()
                observations            = self.precipitation_rate_units_converter(observations.isel(plev = plev), 
                                                                                model_variable = model_variable, 
                                                                                new_unit = new_unit)

            elif model                  == 'mswep':
                reader                  = Reader(model="MSWEP", exp="past", source=source)
                observations            = reader.retrieve()
                observations            = self.precipitation_rate_units_converter(observations,  
                                                                                model_variable = model_variable, 
                                                                                new_unit = new_unit)
            dummy_data                  = observations
    
        else:
            dummy_data                  = self.precipitation_rate_units_converter(dummy_data,  
                                                                                model_variable = model_variable, 
                                                                                new_unit = new_unit)

        if preprocess == True:
            data            = self.preprocessing(               data,                                       preprocess = preprocess,
                                                                model_variable = model_variable,            trop_lat   = self.trop_lat,
                                                                s_time  = self.s_time,                      f_time     = self.f_time,
                                                                s_year  = self.s_year,                      f_year     = self.f_year,
                                                                s_month = self.s_month,                     f_month    = self.f_month,
                                                                sort    = False,                            dask_array = False)
            dummy_data      = self.preprocessing(               dummy_data,                                 preprocess = preprocess,
                                                                model_variable = model_variable,            trop_lat   = self.trop_lat,
                                                                s_time  = self.s_time,                      f_time     = self.f_time,
                                                                s_year  = self.s_year,                      f_year     = self.f_year,
                                                                s_month = self.s_month,                     f_month    = self.f_month,
                                                                sort    = False,                            dask_array = False)

        
        data_regrided,  dummy_data_regrided = mirror_dummy_grid(data = data,                                dummy_data = dummy_data,
                                                                space_grid_factor = space_grid_factor,      time_freq  = time_freq,
                                                                time_length = time_length,                  time_grid_factor = time_grid_factor)
        return data_regrided, dummy_data_regrided
    

    

    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """
    def normilized_forecast_metric(self, data,                          dummy_data = None,
                                    trop_lat = 10,                      model_variable = 'tprate',
                                    model     = 'era5',                 source = 'monthly',                 plev = 0,
                                    s_time    = None,                   f_time   = None,                    s_year  = None,                
                                    f_year    = None,                   s_month = None,                     f_month  = None,
                                    time_isel = None,                   time_length = None,                 space_grid_factor = None,
                                    time_freq = None,                   time_grid_factor = None):
        
        """  """
        self.class_attributes_update(trop_lat = trop_lat,
                                    s_time   = s_time,                  f_time  = f_time,
                                    s_year   = s_year,                  f_year  = f_year,
                                    s_month  = s_month,                 f_month = f_month)

        data_regrided, dummy_data_regrided =  self.twin_data_and_observations(data = data,                
                                                                        dummy_data = dummy_data,            model_variable = model_variable,   
                                                                        model = model,                      source = source,
                                                                        plev = plev,                        trop_lat = self.trop_lat,
                                                                        s_time   = self.s_time,             f_time  = self.f_time,
                                                                        s_year   = self.s_year,             f_year  = self.f_year,
                                                                        s_month  = self.s_month,            f_month = self.f_month,
                                                                        time_length = time_length,          space_grid_factor = space_grid_factor,
                                                                        time_freq = time_freq,              time_grid_factor = time_grid_factor)
        if time_isel is None:
            nfm             = data_regrided.copy(deep=True)
            nfm.values      = (data_regrided.values - dummy_data_regrided.values) /  (data_regrided.values + dummy_data_regrided.values)
        else:
            nfm             = data_regrided.isel(time=time_isel).copy(deep=True)
            nfm.values      = (data_regrided.values - dummy_data_regrided.values) /  (data_regrided.values + dummy_data_regrided.values)
        return nfm

    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """
    def mean_absolute_percent_error(self, data,                         trop_lat = None,                  
                                    model = 'era5',                     source = 'monthly',            
                                    s_time  = None,                     f_time   = None,                    s_year  = None,               
                                    f_year   = None,                    s_month = None,                     f_month  = None,
                                    time_isel = None,                   plev = 0,                           space_grid_factor = None,
                                    time_freq = None,                   time_length = None,                 time_grid_factor = None):
        """ Function to calculate the mean absolute percent error. """
        
        self.class_attributes_update(trop_lat = trop_lat,
                                    s_time   = s_time,                  f_time  = f_time,
                                    s_year   = s_year,                  f_year  = f_year,
                                    s_month  = s_month,                 f_month = f_month)

        data_regrided, observations_regrided =  self.twin_data_and_observations(data = data,                model = model,  source = source,
                                                                        plev=plev,                          trop_lat = self.trop_lat,
                                                                        s_time   = self.s_time,             f_time  = self.f_time,
                                                                        s_year   = self.s_year,             f_year  = self.f_year,
                                                                        s_month  = self.s_month,            f_month = self.f_month,
                                                                        time_length = time_length,          space_grid_factor = space_grid_factor,
                                                                        time_freq = time_freq,              time_grid_factor = time_grid_factor)
        if time_isel is None:
            mape            = data_regrided.copy(deep=True)
            mape.values     = 100 * (observations_regrided.values - data_regrided.values) /  observations_regrided.values
        else:
            mape            = data_regrided.isel(time=time_isel).copy(deep=True)
            mape.values     = 100 * (observations_regrided.values - data_regrided.values) /  observations_regrided.values
        return mape

    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """    
    def snapshot_plot(self,     data,                               preprocess=True,                    model = 'era5',              
                                source = 'monthly',                 plev = 0,                           model_variable = 'tprate',                
                                trop_lat       = None,              mape = False,                       nfm = False,              
                                s_time         = None,              f_time      = None,                 s_year     = None,
                                f_year         = None,              s_month     = None,                 f_month    = None,
                                figsize     = 1,                    maxticknum     = 12,                colorbarname    = 'Precipitation',       
                                vmin = None,                        vmax = None,                        contour  = True,
                                plot_title = None,                  log = False,                        time_isel = None,
                                space_grid_factor = None,           time_freq = None,                   time_length = None,                
                                time_grid_factor = None,            path_to_figure = None,              resol = '110m'):
        
        """ Function to plot the mean or median value of variable in Dataset.

        Args:"""

        self.class_attributes_update(trop_lat = trop_lat,
                                    s_time   = s_time,              f_time  = f_time,
                                    s_year   = s_year,              f_year  = f_year,
                                    s_month  = s_month,             f_month = f_month)
            
        if mape:
            data  = self.mean_absolute_percent_error(data,          trop_lat = self.trop_lat,            
                                    model = model,                  source = source,
                                    s_time  = self.s_time,          f_time   = self.f_time,             s_year  = self.s_year,    
                                    f_year   = self.f_year,         s_month = self.s_month,             f_month  = self.f_month,
                                    time_isel = time_isel,          plev = plev,                        space_grid_factor = space_grid_factor,
                                    time_freq = time_freq,          time_length = time_length,          time_grid_factor = time_grid_factor)
        elif nfm:
            data  = self.normilized_forecast_metric(data,           trop_lat = self.trop_lat,         
                                    model = model,                  source = source,
                                    s_time  = self.s_time,          f_time   = self.f_time,             s_year  = self.s_year,  
                                    f_year   = self.f_year,         s_month = self.s_month,             f_month  = self.f_month,
                                    time_isel = time_isel,          plev = plev,                        space_grid_factor = space_grid_factor,
                                    time_freq = time_freq,          time_length = time_length,          time_grid_factor = time_grid_factor)         
        else:
            if preprocess           == True:
                data                = self.preprocessing(           data,                               preprocess = preprocess,
                                                                    trop_lat   = self.trop_lat,         model_variable = model_variable,       
                                                                    s_time  = self.s_time,              f_time     = self.f_time,
                                                                    s_year  = self.s_year,              f_year     = self.f_year,
                                                                    s_month = self.s_month,             f_month    = self.f_month,
                                                                    sort    = False,                    dask_array = False)
        
        if vmin                 != None:
            data                = data.where( data > vmin, drop = True)
        if time_isel is None:
            if data.time.size   != 1:
                snapshot        = data[0,:,:]
            else:
                snapshot        = data
        else:
            if isinstance(time_isel, int):
                snapshot        = data.isel(time = time_isel)
            else:
                raise Exception('time_isel must be an integer')
            
        # First set up the figure, the axis, and the plot element we want to animate
        fig = plt.figure( figsize = (8*figsize, 5*figsize) )
        
        ax                      = plt.axes(projection = ccrs.PlateCarree())
        
        if  contour:
            ax.coastlines(resolution = resol)
        
        ax.gridlines()

        if log:
            im                  = plt.imshow(snapshot, interpolation = 'nearest',  aspect = 'auto',  norm = LogNorm(vmin = vmin, vmax = vmax), alpha = 0.9,
                                             extent = (-180, 180, - self.trop_lat, self.trop_lat), origin = 'upper')
        else:
            im                  = plt.imshow(snapshot, interpolation = 'nearest',  aspect = 'auto',  vmin = vmin, vmax = vmax, alpha = 0.9,
                                             extent = (-180, 180, - self.trop_lat, self.trop_lat), origin = 'upper')

        cbar = fig.colorbar(im)
        plt.xlabel('Longitude',                         fontsize = 18)
        plt.ylabel('Latitude',                          fontsize = 18)
        plt.xticks([-180, -120, -60, 0, 60, 120, 180],  fontsize = 14)
        plt.yticks([-90, -60, -30, 0, 30, 60, 90],      fontsize = 14)

        plt.gca().xaxis.set_major_locator(plt.MaxNLocator(maxticknum))
        plt.gca().tick_params(axis = 'both',   which = 'major',             pad = 10)
        
        plt.grid(True)
        if plot_title is not None:
            plt.title(plot_title,                       fontsize = 17,      pad=15)
        if mape:
            cbar.set_label("MAPE, %", fontsize = 18)
        elif nfm:
            cbar.set_label("NFM", fontsize = 18)
        else:
            cbar.set_label(colorbarname, fontsize = 14)
        # set the spacing between subplots
        plt.tight_layout()
        if path_to_figure is not None and isinstance(path_to_figure, str):

            create_folder(folder    = extract_directory_path(path_to_figure), loglevel = 'WARNING')

            plt.savefig(path_to_figure,
                        bbox_inches  = "tight",
                        pad_inches   = 1,
                        transparent  = True,
                        facecolor    = "w",
                        edgecolor    = 'w',
                        orientation  = 'landscape')
        return {fig, ax}
    
    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ 
    def confidence_interval_along_coordinate(self, data,                    model_variable = 'tprate',     
                                    preprocess=True,                        glob=False,
                                    trop_lat = None,                        coord   = 'time',               
                                    s_time   = None,                        f_time  = None,
                                    s_year   = None,                        f_year  = None,
                                    s_month  = None,                        f_month = None):
        """ Function to calculate the mean value of variable in Dataset.

        Args:
            data (xarray):                      The Dataset
            model_variable (str, optional):     The variable of the Dataset.            Defaults to 'tprate'.
            trop_lat (float, optional):         The maximumal and minimal tropical latitude values in Dataset.  Defaults to None.
            coord (str, optional):              The coordinate of the Dataset.          Defaults to 'time'.
            s_time (str, optional):             The starting time of the Dataset.       Defaults to None.
            f_time (str, optional):             The ending time of the Dataset.         Defaults to None.
            s_year (str, optional):             The starting year of the Dataset.       Defaults to None.
            f_year (str, optional):             The ending year of the Dataset.         Defaults to None.
            s_month (str, optional):            The starting month of the Dataset.      Defaults to None.
            f_month (str, optional):            The ending month of the Dataset.        Defaults to None.

        Returns:
            xarray:         The mean value of variable.
        """
        self.class_attributes_update(trop_lat = trop_lat,
                                    s_time   = s_time,                      f_time  = f_time,
                                    s_year   = s_year,                      f_year  = f_year,
                                    s_month  = s_month,                     f_month = f_month)
        if preprocess == True:
            data = self.preprocessing(data,                                 preprocess = preprocess,
                                    model_variable   = model_variable,      trop_lat= self.trop_lat,
                                    s_time  = self.s_time,                  f_time  = self.f_time,
                                    s_year  = self.s_year,                  f_year  = self.f_year,   
                                    s_month = self.s_month,                 f_month = self.f_month,
                                    sort = False,                           dask_array = False)
        coord_lat, coord_lon = self.coordinate_names(data)
        
        z_score             = 1.96  # Z-score for 95% confidence interval
                                    ##2.58 # Z-score for 99% confidence interval
                                    ##1.645 # Z-score for 90% confidence interval    
                                    ##
        if glob:
            mean_y1         =  data.values.mean()
            std_y1          =  np.std(data.values)
            n_y1            =  data_size(data)
            margin_error_y1         = z_score * std_y1 / np.sqrt(n_y1)
            confidence_interval_y1  = (mean_y1 - margin_error_y1, mean_y1 + margin_error_y1)

        else:
            if coord        == 'time':
                y1          =  data.stack(total=[coord_lat, coord_lon]).values
                mean_y1     =  data.mean(coord_lat).mean(coord_lon).values
            elif coord  == coord_lat:
                y1          =  data.stack(total=['time', coord_lon]).values
                mean_y1     =  data.mean('time').mean(coord_lon).values
            elif coord  == coord_lon:
                y1          =  data.stack(total=['time', coord_lat]).values
                mean_y1     =  data.mean('time').mean(coord_lat).values
            
            n_y1                    =  len(y1[0])
            confidence_interval_y1  = []
            for i in range(0, len(mean_y1)):
                std_y1              = np.std(y1[i])
                margin_error_y1     = z_score * std_y1 / np.sqrt(n_y1)
                confidence_interval_y1.append((mean_y1[i] - margin_error_y1, mean_y1[i] + margin_error_y1))
        
        return confidence_interval_y1
    

    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """
    def check_if_belong_to_confidence_interval(self, 
                                    dataset_1,                              dataset_2 = None,               legend_1    = '_Hidden',
                                    model_variable = 'tprate',              preprocess=True,                figsize     = 1, 
                                    model = 'era5',                         source = 'monthly',             ls          = '-',
                                    plev = 0,                               glob = False,                   maxticknum  = 12,
                                    trop_lat = None,                        coord   = 'time',               ylogscale   = False,
                                    s_time   = None,                        f_time  = None,                 varname     = 'Precipitation',
                                    s_year   = None,                        f_year  = None,                 xlogscale   = False,
                                    s_month  = None,                        f_month = None,                 loc         = 'upper right',
                                    space_grid_factor = None,               time_freq = None,               plot_title  = None,
                                    time_length = None,                     time_grid_factor = None,        path_to_figure = None,
                                    plot = True,                            legend_2 = 'era5 monthly'):
        """ Function to check if second dataset belongs to the confidence intarval of the first dataset.
        Args:
            data (xarray):                      The Dataset
            model_variable (str, optional):     The variable of the Dataset.            Defaults to 'tprate'.
            trop_lat (float, optional):         The maximumal and minimal tropical latitude values in Dataset.  Defaults to None.
            coord (str, optional):              The coordinate of the Dataset.          Defaults to 'time'.
            s_time (str, optional):             The starting time of the Dataset.       Defaults to None.
            f_time (str, optional):             The ending time of the Dataset.         Defaults to None.
            s_year (str, optional):             The starting year of the Dataset.       Defaults to None.
            f_year (str, optional):             The ending year of the Dataset.         Defaults to None.
            s_month (str, optional):            The starting month of the Dataset.      Defaults to None.
            f_month (str, optional):            The ending month of the Dataset.        Defaults to None.
            model(str, optional):               The name of the odel in the catalogue.  Defaults to 'era5'.
            dataset_2(xarray, optional):        The second dataset.
            plev(int, optional):                The pressure level in era5 data.        Defaults to 0.
         
        Returns:
            Nonetype: None

        """
        self.class_attributes_update(trop_lat = trop_lat,
                                    s_time   = s_time,                      f_time  = f_time,
                                    s_year   = s_year,                      f_year  = f_year,
                                    s_month  = s_month,                     f_month = f_month)

        dataset_1, dataset_2 =  self.twin_data_and_observations(data = dataset_1,                model_variable = model_variable,  
                                    model = model,                          source = source,
                                    plev = plev,                            trop_lat = trop_lat,
                                    s_time   = s_time,                      f_time  = f_time,
                                    s_year   = s_year,                      f_year  = f_year,
                                    s_month  = s_month,                     f_month = f_month,
                                    time_length = time_length,              space_grid_factor = space_grid_factor,
                                    time_freq = time_freq,                  time_grid_factor = time_grid_factor)

        coord_lat, coord_lon = self.coordinate_names(dataset_1)
        interval_1 = self.confidence_interval_along_coordinate(dataset_1,                              model_variable = model_variable,     
                                    preprocess=preprocess,                  trop_lat= self.trop_lat,     
                                    coord     = coord,                      glob    = glob,
                                    s_time    = self.s_time,                f_time  = self.f_time,
                                    s_year    = self.s_year,                f_year  = self.f_year,
                                    s_month   = self.s_month,               f_month = self.f_month)
        interval_2 = self.confidence_interval_along_coordinate(dataset_2,                              model_variable = model_variable,    
                                    preprocess=preprocess,                  trop_lat= self.trop_lat,     
                                    coord     = coord,                      glob    = glob,
                                    s_time    = self.s_time,                f_time  = self.f_time,
                                    s_year    = self.s_year,                f_year  = self.f_year, 
                                    s_month   = self.s_month,               f_month = self.f_month)

        # Check if second dataset falls within the confidence interval of the first dataset
        if glob:
            mean_y2 =  dataset_2.values.mean()
            mean_y1 =  dataset_1.values.mean()
            is_within_confidence_interval_1   = interval_1[0] <= mean_y2 <= interval_1[1]
            is_within_confidence_interval_2   = interval_2[0] <= mean_y1 <= interval_2[1]
            if is_within_confidence_interval_1:
                print("The second dataset is within the 95% confidence interval of the first dataset.")
            else:
                print("The second dataset is not within the 95% confidence interval of the first dataset.")
        else:
            if coord        == 'time':
                mean_y2     =  dataset_2.mean(coord_lat).mean(coord_lon)
                mean_y1     =  dataset_1.mean(coord_lat).mean(coord_lon)
            elif coord  == coord_lat:
                mean_y2     =  dataset_2.mean('time').mean(coord_lon)
                mean_y1     =  dataset_1.mean('time').mean(coord_lon)
            elif coord  == coord_lon:
                mean_y2     =  dataset_2.mean('time').mean(coord_lat)
                mean_y1     =  dataset_1.mean('time').mean(coord_lat)
            is_within_confidence_interval_1 = []
            is_within_confidence_interval_2 = []
            for i in range(0, len(mean_y2)):
                is_within_confidence_interval_1.append(interval_1[i][0] <= mean_y2[i] <= interval_1[i][1])
                is_within_confidence_interval_2.append(interval_2[i][0] <= mean_y2[i] <= interval_2[i][1])
            if all(is_within_confidence_interval_1):
                print("The second dataset is within the 95% confidence interval of the first dataset.")
            else:
                print("The second dataset is not within the 95% confidence interval of the first dataset.")

        if plot:
            fig, ax = plt.subplots( figsize=(8*figsize, 5*figsize) )
            #make a plot with different y-axis using second axis object
            if coord            == 'time':
                if 'm' in time_interpreter(dataset_1):
                    labels      = [str(dataset_1['time.hour'][i].values) + ':'+str(dataset_1['time.minute'][i].values)
                                                                                        for i in range(0, dataset_1.time.size)]
                    labels_int  = [float(dataset_1['time.hour'][i].values)   for i in range(0, dataset_1.time.size)]
                elif 'H' in time_interpreter(dataset_1):
                    labels      = [convert_24hour_to_12hour_clock(dataset_1, i)
                                                                                        for i in range(0, dataset_1.time.size)]
                    labels_int  = [float(dataset_1['time.hour'][i].values)   for i in range(0, dataset_1.time.size)]
                elif time_interpreter(dataset_1) == 'D':
                    labels      = [str(dataset_1['time.day'][i].values + convert_monthnumber_to_str(dataset_1, i))
                                                                                        for i in range(0, dataset_1.time.size)]
                    labels_int  = [float(dataset_1['time.day'][i].values)    for i in range(0, dataset_1.time.size)]
                elif time_interpreter(dataset_1) == 'M':
                    labels      = [convert_monthnumber_to_str(dataset_1, i)
                                                                                        for i in range(0, dataset_1.time.size)]
                    labels_int  = [float(dataset_1['time.month'][i].values)  for i in range(0, dataset_1.time.size)]
                else:
                    labels      = [None for i in range(0, dataset_1.time.size)]
                    labels_int  = [None for i in range(0, dataset_1.time.size)]

            elif coord          == coord_lat:
                labels_int      = dataset_1[coord_lat]
            elif coord          == coord_lon:
                labels_int      = dataset_1[coord_lon]
            if glob:
                plt.axhline(y = mean_y2, label = legend_2, color = 'tab:orange')
                plt.axhline(y = mean_y1, label = legend_1, color = 'tab:blue')
                plt.fill_between(labels_int, interval_1[0],interval_1[1],
                                 alpha=0.9, color = 'tab:blue', label='95% Confidence Interval')
                plt.fill_between(labels_int, interval_2[0],interval_2[1],
                                 alpha=0.9, color = 'tab:orange', label='95% Confidence Interval')
            else:
                plt.plot(labels_int, mean_y2, label = legend_2, color = 'tab:orange')
                plt.plot(labels_int, mean_y1, label = legend_1, color = 'tab:blue')
                plt.fill_between(labels_int,
                                 [interval_1[i][0] for i in range(0, len(interval_1))],
                                 [interval_1[i][1] for i in range(0, len(interval_1))],
                                 alpha=0.9, color = 'tab:blue', label='95% Confidence Interval')
                plt.fill_between(labels_int,
                                 [interval_2[i][0] for i in range(0, len(interval_2))],
                                 [interval_2[i][1] for i in range(0, len(interval_2))],
                                 alpha=0.9, color = 'tab:orange', label='95% Confidence Interval')
            if coord   == 'time':
                plt.xlabel('Timestep index',                        fontsize=12)
                if dataset_1['time.year'][0].values  == dataset_1['time.year'][-1].values:
                    plt.xlabel(str(dataset_1['time.year'][0].values),
                                                                    fontsize=12)
                else:
                    plt.xlabel(str(dataset_1['time.year'][0].values)+' - '+str(dataset_1['time.year'][-1].values),
                                                                    fontsize=12)
            elif coord == coord_lat:
                plt.xlabel('Latitude',                              fontsize=12)
            elif coord == coord_lon:
                plt.xlabel('Longitude',                             fontsize=12)
            try:
                plt.ylabel(str(varname)+', '+str(dataset_1.units),
                                                                    fontsize=12)
            except KeyError:
                plt.ylabel(str(varname),                            fontsize=12)

            plt.gca().xaxis.set_major_locator(plt.MaxNLocator(maxticknum))
            plt.gca().tick_params(axis = 'both',   which = 'major',    pad = 10)
            plt.legend()
            plt.grid(True)
            plt.title(plot_title,                               fontsize=17,    pad=15)
            if legend_1!='_Hidden':
                plt.legend(loc=loc,                                 fontsize=12,    ncol=2)
            if ylogscale:
                plt.yscale('log')
            if xlogscale:
                plt.xscale('log')
            plt.tight_layout()
            if path_to_figure is not None and isinstance(path_to_figure, str):

                create_folder(folder    = extract_directory_path(path_to_figure), loglevel = 'WARNING')

                plt.savefig(path_to_figure,
                            bbox_inches  = "tight",
                            pad_inches   = 1,
                            transparent  = True,
                            facecolor    = "w",
                            edgecolor    = 'w',
                            orientation  = 'landscape')
            #return {fig, ax}