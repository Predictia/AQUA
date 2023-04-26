import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.ticker import PercentFormatter
import time
import fast_histogram 

import boost_histogram as bh #pip
import dask.array as da
import dask_histogram as dh # pip

import dask_histogram.boost as dhb
import dask

import math 
import re
import cartopy
import cartopy.feature as cfeature
import cartopy.crs as ccrs

import matplotlib.animation as animation
import numpy as np

from aqua.benchmark.time_functions import time_interpreter, month_convert_num_to_str, hour_convert_num_to_str

"""The module contains Tropical Precipitation Diagnostic:

.. moduleauthor:: AQUA team <natalia.nazarova@polito.it>

"""

class TR_PR_Diagnostic:
    """Tropical precipitation diagnostic
    """ 
    #attributes = inspect.getmembers(diag, lambda a:not(inspect.isroutine(a)))

    def class_attributes_update(self,   trop_lat = None,  s_time = None, f_time = None,  
                          s_year = None, f_year = None, s_month = None, f_month = None, 
                          num_of_bins = None, first_edge = None, width_of_bin = None, bins = None):
        
        if trop_lat:    self.trop_lat = trop_lat
        """ 
        self.s_time = s_time
        self.f_time = f_time 
        self.s_year = s_year    
        self.f_year = f_year  
        self.s_month = s_month
        self.f_month = f_month 
        """
        if s_time:          self.s_time = s_time
        if f_time:          self.f_time = f_time
        if s_year:          self.s_year = s_year
        if f_year:          self.f_year = f_year
        if s_month:         self.s_month = s_month
        if f_month:         self.f_month = f_month

        if num_of_bins:     self.num_of_bins = num_of_bins
        if first_edge:      self.first_edge = first_edge
        if width_of_bin:    self.width_of_bin = width_of_bin 
        if bins:            self.bins = bins

        # check if its possible to generilize 


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
        
        """The Tropical Precipitaion constructor.
        Arguments:
            trop_lat        (int/float, optional):    The maximumal and minimal tropical latitude values in Dataset.  Defaults to 10.
            s_time          (str/int, optional):      The starting time value/index in Dataset. Defaults to None.
            f_time          (str/int, optional):      The final time value/index in Dataset. Defaults to None.
            s_year          (int, optional):          The starting/first year of the desired Dataset. 
            f_year          (int, optional):          The final/last year of the desired Dataset.
            s_month         (int, optional):          The starting/first month of the desired Dataset.
            f_month         (int, optional):          The final/last month of the desired Dataset.
            num_of_bins     (int, optional):          The number of bins in the histogram.
            first_edge      (int, optional):          The first edge of the first bin of the histogram.
            width_of_bin    (int/float, optional):    Histogram bin width.
            bins            (array, optional):        The array of bins in the histogram. Defaults to 0.
        """
        # Attributes are assigned to all objects of the class
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
        """Returning the names of coordinates

        Args:
            data (xarray): The Dataset.

        Returns:
            str: name of latitude coordinate
            str: name of longitude coordinate
        """
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
    def ds_per_lat_range(self, data, trop_lat=None):
        """Selecting the Dataset for specified latitude range

        Args:
            data (xarray):                  The Dataset
            trop_lat (float, optional):     The maximumal and minimal tropical latitude values in Dataset.  Defaults to None.

        Returns:
            xarray: The Dataset for selected latitude range.
        """        
        #If the user has specified a function argument ***trop_lat***, then the argument becomes a new class attribute. 
        coord_lat, coord_lon = self.coordinate_names(data)
        self.class_attributes_update( trop_lat=trop_lat )

        data_trop = data.where(abs(data[coord_lat]) <= self.trop_lat, drop=True)  
        return data_trop
    


    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ 
    def ds_per_time_range(self, data,  s_time = None, f_time = None, s_year = None, f_year = None,
        s_month = None, f_month = None):
        """Selecting the Dataset for specified time range

        Args:
            data (xarray):              The Dataset
            s_time (str/int, optional): The starting time value/index in Dataset. Defaults to None.
            f_time (str/int, optional): The final time value/index in Dataset. Defaults to None.
            s_year (int, optional):     The starting year in Dataset. Defaults to None.
            f_year (int, optional):     The final year in Dataset. Defaults to None.
            s_month (int, optional):    The starting month in Dataset. Defaults to None.
            f_month (int, optional):    The final month in Dataset. Defaults to None.


        Raises:
            Exception: "s_year must to be integer"
            Exception: "s_year and f_year must to be integer"
            Exception: "s_month and f_month must to be integer"
            Exception: "Sorry, unknown format of time. Try one more time"
            Exception: "Sorry, unknown format of time. Try one more time"

        Returns:
            xarray: The Dataset only for selected time range. 
        """              
        #If the user has specified a function argument ***s_year,  f_year, s_month, f_month***, then the argument becomes a new class attributes.
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
    def ds_into_array(self, data, variable_1 = 'tprate', sort = False):
        """Generatig DataArray from Dataset of specific variable

        Args:
            data (xarray):              The Dataset
            variable_1 (str, optional): The variable of the Dataset. Defaults to 'tprate'.
            sort (bool, optional):      If sort is True, the DataArray is sorted. Defaults to False.

        Returns:
            xarray: DataArray
        """        
        coord_lat, coord_lon = self.coordinate_names(data)

        if 'Dataset' in str(type(data)):
            data  = data[variable_1]

        data_1d  = data.stack(total=['time', coord_lat, coord_lon])
        if sort == True:
            data_1d  = data_1d.sortby(data_1d)
        return data_1d

    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ 
    def mean_per_timestep(self, data, variable_1 = 'tprate', trop_lat = None, s_time = None, f_time = None, 
        s_year = None, f_year = None, s_month = None, f_month = None):
        """Calculating the mean value of varibale in Dataset 

        Args:
            data (xarray):                  The Dataset
            variable_1 (str, optional):     The variable of the Dataset. Defaults to 'tprate'.
            trop_lat (float, optional):     The maximumal and minimal tropical latitude values in Dataset.  Defaults to None.
            s_time (str/int, optional):     The starting time value/index in Dataset. Defaults to None.
            f_time (str/int, optional):     The final time value/index in Dataset. Defaults to None.
            s_year (int, optional):         The starting year in Dataset. Defaults to None.
            f_year (int, optional):         The final year in Dataset. Defaults to None.
            s_month (int, optional):        The starting month in Dataset. Defaults to None.
            f_month (int, optional):        The final month in Dataset. Defaults to None.

        Returns:
            float/xarray: The mean value of the argument variable for each time step. 
        """ 
        if 'lat' in data.dims:
            #If the user has specified a function argument **trop_lat, s_year, f_year, s_month, f_month***, then the argument becomes a new class attributes.
            self.class_attributes_update( s_time = s_time, f_time = f_time, trop_lat = trop_lat, 
                                   s_year = s_year, f_year = f_year, s_month = s_month, f_month = f_month)
        
        
            coord_lat, coord_lon = self.coordinate_names(data)

            ds = self.ds_per_lat_range(data, trop_lat=self.trop_lat)
            ds = self.ds_per_time_range(ds, s_time = self.s_time, f_time = self.f_time,
                                        s_year=self.s_year, f_year=self.f_year, s_month=self.s_month, f_month=self.f_month)
            if 'Dataset' in str(type(data)):
                ds = ds[variable_1]

            return ds.mean(coord_lat).mean(coord_lon)
        else:
            for i in data.dims:
                coord = i
            return data.median(coord)



    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """
    def median_per_timestep(self, data, variable_1 = 'tprate', trop_lat = None,  s_time = None, f_time = None, 
                            s_year = None, f_year = None, s_month = None, f_month = None):
        """Calculating the median value of varibale in Dataset 

        Args:
            data (xarray):                  The Dataset
            variable_1 (str, optional):     The variable of the Dataset. Defaults to 'tprate'.
            trop_lat (float, optional):     The maximumal and minimal tropical latitude values in Dataset.  Defaults to None.
            s_time (str/int, optional):     The starting time value/index in Dataset. Defaults to None.
            f_time (str/int, optional):     The final time value/index in Dataset. Defaults to None.
            s_year (int, optional):         The starting year in Dataset. Defaults to None.
            f_year (int, optional):         The final year in Dataset. Defaults to None.
            s_month (int, optional):        The starting month in Dataset. Defaults to None.
            f_month (int, optional):        The final month in Dataset. Defaults to None.

        Returns:
            float/xarray: The median value of the argument variable for each time step. 
        """        

        if 'lat' in data.dims:
            #If the user has specified a function argument **trop_lat, s_year, f_year, s_month, f_month***, then the argument becomes a new class attributes.
            self.class_attributes_update(s_time = s_time, f_time = f_time, trop_lat = trop_lat, 
                                   s_year = s_year, f_year = f_year, s_month = s_month, f_month = f_month)
        
            coord_lat, coord_lon = self.coordinate_names(data)

            ds = self.ds_per_lat_range(data, trop_lat=self.trop_lat)
            ds = self.ds_per_time_range(ds, s_time = self.s_time, f_time = self.f_time, 
                                        s_year=self.s_year, f_year=self.f_year, s_month=self.s_month, f_month=self.f_month)
            if 'Dataset' in str(type(data)):
                ds = ds[variable_1]

            return ds.median(coord_lat).median(coord_lon)
        
        else:
            for i in data.dims:
                coord = i
            return data.median(coord)
    
    def mean_and_median_plot(self, data,  variable_1 = 'tprate', trop_lat = None, s_time = None, f_time = None, 
                            s_year = None, f_year = None, s_month = None, f_month = None, savelabel = '', maxticknum = 8):
        """Plotting the mean and median values of variable

        Args:
            data (xarray):                  The Dataset
            variable_1 (str, optional):     The variable of the Dataset. Defaults to 'tprate'.
            trop_lat (float, optional):     The maximumal and minimal tropical latitude values in Dataset.  Defaults to None.
            s_time (str/int, optional):     The starting time value/index in Dataset. Defaults to None.
            f_time (str/int, optional):     The final time value/index in Dataset. Defaults to None.
            s_year (int, optional):         The starting year in Dataset. Defaults to None.
            f_year (int, optional):         The final year in Dataset. Defaults to None.
            s_month (int, optional):        The starting month in Dataset. Defaults to None.
            f_month (int, optional):        The final month in Dataset. Defaults to None.
            savelabel (str, optional):      The unique label of the figure in the filesystem. Defaults to ''.
            maxticknum (int, optional):     The maximal number of ticks on x-axe. Defaults to 8.
        """              
        fig, ax =  plt.subplots( ) #figsize=(8,5) )
        data_mean = self.mean_per_timestep(data, variable_1 = variable_1, trop_lat = trop_lat, s_time = s_time, f_time = f_time, 
                            s_year = s_year, f_year = f_year, s_month = s_month, f_month = f_month)
        data_median = self.median_per_timestep(data, variable_1 = variable_1, trop_lat = trop_lat, s_time = s_time, f_time = f_time, 
                            s_year = s_year, f_year = f_year, s_month = s_month, f_month = f_month)
        ax2=ax.twiny()
        # make a plot with different y-axis using second axis object
        if 'm' in time_interpreter(data):
            time_labels = [str(data['time.hour'][i].values)+':'+str(data['time.minute'][i].values) for i in range(0, len(data)) ] 
        elif 'H' in time_interpreter(data):
            time_labels = [hour_convert_num_to_str(data, i)  for i in range(0, len(data)) ]
            #time_labels = [str(data['time.hour'][i].values)+':00' for i in range(0, len(data)) ]
        elif time_interpreter(data) == 'D':
            time_labels = [str(data['time.day'][i].values+month_convert_num_to_str(data, i)) for i in range(0, len(data)) ]
        elif time_interpreter(data) == 'M':   
            time_labels = [month_convert_num_to_str(data, i) for i in range(0, len(data)) ] 
            #time_labels = [str(data['time.year'][i].values)+':'+str(data['time.month'][i].values)+':'+str(data['time.day'][i].values) for i in range(0, len(data)) ]
        else:
            time_labels = [None for i in range(0, len(data))]

        if data_mean.size == 1 and data_median.size == 1:
            ax.axhline(data_mean, label= 'mean', color = 'tab:blue')
            ax.axhline(data_median, label= 'median',color = 'tab:orange')

            ax2.plot(time_labels, data_median.values, ls = ' ')
        else:
            ax.plot(data_mean, label= 'mean', color = 'tab:blue')
            ax.plot(data_median, label='median', color = 'tab:orange')
            ax2.plot(time_labels, data_median.values, ls = ' ')

        #ax.set_yscale('log')
        ax2.xaxis.set_major_locator(plt.MaxNLocator(maxticknum))
        ax.tick_params(axis='both', which='major', pad=10)
        ax2.tick_params(axis='both', which='major', pad=10)
        #ax.xaxis.set_label_position('top') 
        #ax2.locator_params(axis='x', nbins=5)
        ax.grid(True)
        ax.set_xlabel('Timestep index', fontsize=12)
        ax2.set_xlabel('Time', fontsize=12)
        ax.set_ylabel('Precipitation per timestep, '+str(data.attrs['units']), fontsize=12)
        ax.set_title('Mean/median values of precipitation', fontsize =17, pad=15)
        ax.legend(fontsize=12)
        
        

        #plt.yscale('log')
        #print('gmean ....')
        if savelabel == None:
            savelabel = str(data.attrs['title'])
            savelabel = re.split(r'[ ]', savelabel)[0]

        # set the spacing between subplots
        fig.tight_layout()
        fig.savefig("./figures/"+str(savelabel)+"_mean_and_median.png",
                    bbox_inches ="tight",
                    pad_inches = 1,
                    transparent = True,
                    facecolor ="w",
                    edgecolor ='w',
                    orientation ='landscape')
            
  
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
            ds_per_time = self.ds_per_time_range(data, s_time=self.s_time, f_time=self.f_time, 
                                        s_year=self.s_year, f_year=self.f_year, s_month=self.s_month, f_month=self.f_month) 
            ds_var = ds_per_time[variable_1]
            ds_per_lat = self.ds_per_lat_range(ds_var, trop_lat=self.trop_lat)
            #ds_array = self.ds_into_array(ds_per_lat, variable_1=variable_1, sort=sort)
            if dask_array == True:
                ds = da.from_array(ds_per_lat)
                return ds
            else:
                return ds_per_lat
        else:
            print("Nothong to preprocess")


    """ """ """ """ """ """ """ """ """ """
    def hist1d_fast(self, data, preprocess = True,   trop_lat = 10, variable_1 = 'tprate',  
                    s_time = None, f_time = None,
                    s_year = None, f_year = None, s_month = None, f_month = None, 
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
        #If the user has specified a function argument **trop_lat, s_year, f_year, s_month, f_month***, 
        # then the argument becomes a new class attributes.
        self.class_attributes_update(s_time = s_time, f_time = f_time, trop_lat = trop_lat, 
                               s_year = s_year, f_year = f_year, s_month = s_month, f_month = f_month, first_edge = first_edge, 
                               num_of_bins = num_of_bins, width_of_bin = width_of_bin)


        if preprocess == True:
            data = self.preprocessing(data, preprocess=preprocess,  variable_1=variable_1, trop_lat=trop_lat, 
                                      s_time = self.s_time, f_time = self.f_time,
                                      s_year=s_year, f_year=f_year, s_month=s_month, f_month=f_month,  sort = False, dask_array = False)

        if isinstance(bins, int):
            bin_table = [self.first_edge + self.width_of_bin*j for j in range(0, self.num_of_bins)]     
            hist_fast = fast_histogram.histogram1d(data, 
                                                   range=[self.first_edge, self.first_edge + (self.num_of_bins)*self.width_of_bin], bins = (self.num_of_bins))  
        else: 
            bin_table = bins
            hist_fast = fast_histogram.histogram1d(data, 
                                                   range=[min(bins),max(bins)], bins = len(bins))   
        
        
        
        frequency_bin =  xr.DataArray(hist_fast, coords=[bin_table], dims=["bin"])
        frequency_bin.attrs = data.attrs
        return  frequency_bin 
    
    
    
    """ """ """ """ """ """ """ """ """ """
    def hist1d_np(self, data, preprocess = True,   trop_lat = 10, variable_1 = 'tprate',  
                  s_time = None, f_time = None,   
                  s_year = None, f_year = None, s_month = None, f_month = None, 
                  num_of_bins = None, first_edge = None,  width_of_bin  = None,  bins = 0):
        """Calculating the histogram with the use of numpy.histogram (***numpy*** package)
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
        #If the user has specified a function argument **trop_lat, s_year, f_year, s_month, f_month***, 
        # then the argument becomes a new class attributes.
        self.class_attributes_update(s_time = s_time, f_time = f_time,  trop_lat = trop_lat, 
                               s_year = s_year, f_year = f_year, s_month = s_month, f_month = f_month, first_edge = first_edge, 
                               num_of_bins = num_of_bins, width_of_bin = width_of_bin, bins = bins)
        
        #last_edge = self.first_edge  + self.num_of_bins*self.width_of_bin
        

        if preprocess == True:
            data = self.preprocessing(data, preprocess=preprocess, variable_1=variable_1, trop_lat=self.trop_lat, 
                                      s_time = self.s_time, f_time = self.f_time, 
                                      s_year=self.s_year, f_year=self.f_year, s_month=self.s_month, f_month=self.f_month,  
                                      sort = False, dask_array = False)


        if isinstance(self.bins, int):
            hist_np = np.histogram(data, range=[self.first_edge, self.first_edge + (self.num_of_bins )*self.width_of_bin], bins = (self.num_of_bins))
        else:
            #bins = bins
            hist_np = np.histogram(data,  bins = self.bins) 
        frequency_bin =  xr.DataArray(hist_np[0], coords=[hist_np[1][0:-1]], dims=["bin"])
        frequency_bin.attrs = data.attrs
        return  frequency_bin
        
    """ """ """ """ """ """ """ """ """ """
    def hist1d_pyplot(self, data, preprocess = True,  trop_lat = 10,  variable_1 = 'tprate',  
                      s_time = None, f_time = None,  
                      s_year = None, f_year = None, s_month = None, f_month = None, 
                      num_of_bins = None, first_edge = None,  width_of_bin  = None,  bins = 0):
        """Calculating the histogram with the use of plt.hist (***matplotlib.pyplot*** package)
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
        #If the user has specified a function argument **trop_lat, s_year, f_year, s_month, f_month***, 
        # then the argument becomes a new class attributes.
        self.class_attributes_update(s_time = s_time, f_time = f_time,  trop_lat = trop_lat, 
                               s_year = s_year, f_year = f_year, s_month = s_month, f_month = f_month, first_edge = first_edge, 
                               num_of_bins = num_of_bins, width_of_bin = width_of_bin)  

        last_edge = self.first_edge  + self.num_of_bins*self.width_of_bin

        if preprocess == True:
            data = self.preprocessing(data, preprocess=preprocess, variable_1=variable_1, trop_lat=trop_lat, 
                                      s_time = self.s_time, f_time = self.f_time, 
                                      s_year=s_year, f_year=f_year, s_month=s_month, f_month=f_month,  sort = False, dask_array = False)

        bins = [self.first_edge  + i*self.width_of_bin for i in range(0, self.num_of_bins+1)]
        hist_pyplt = plt.hist(x = data, bins = bins)

        plt.close()

        frequency_bin =  xr.DataArray(hist_pyplt[0], coords=[hist_pyplt[1][0:-1]], dims=["bin"])
        frequency_bin.attrs = data.attrs
        return  frequency_bin

        
         
    """ """ """ """ """ """ """ """ """ """
    def dask_factory(self, data, preprocess = True,   trop_lat = 10,  variable_1 = 'tprate',  
                     s_time = None, f_time = None, 
                     s_year = None, f_year = None, s_month = None, f_month = None, 
                     num_of_bins = None, first_edge = None,  width_of_bin  = None,   bins = 0, 
                     delay = False):
        """Calculating the histogram 
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
            delay (bool, optional):         
        Returns:
            xarray: The frequency histogram of the specified variable in the Dataset
        """ 

        #If the user has specified a function argument **trop_lat, s_year, f_year, s_month, f_month***, 
        # then the argument becomes a new class attributes.
        self.class_attributes_update(s_time = s_time, f_time = f_time, trop_lat = trop_lat, 
                               s_year = s_year, f_year = f_year, s_month = s_month, f_month = f_month, first_edge = first_edge, 
                               num_of_bins = num_of_bins, width_of_bin = width_of_bin)

        last_edge = self.first_edge  + self.num_of_bins*self.width_of_bin
        

        if preprocess == True:
            data = self.preprocessing(data, preprocess=preprocess, variable_1=variable_1, trop_lat=trop_lat, 
                                      s_time = self.s_time, f_time = self.f_time, 
                                      s_year=s_year, f_year=f_year, s_month=s_month, f_month=f_month,  sort = False, dask_array = False)


        h = dh.factory(data, 
                axes=(bh.axis.Regular(self.num_of_bins, self.first_edge, last_edge),))     
        counts, edges = h.to_dask_array()
        if delay == False:
            counts = counts.compute()
            edges = edges.compute()
        frequency_bin =  xr.DataArray(counts, coords=[edges[0:-1]], dims=["bin"])
        frequency_bin.attrs = data.attrs  
        return  frequency_bin


    """ """ """ """ """ """ """ """ """ """
    def dask_factory_weights(self, data, preprocess = True,  trop_lat = 10,  variable_1 = 'tprate',  
                             s_time = None, f_time = None,
                             s_year = None, f_year = None, s_month = None, f_month = None, 
                             num_of_bins = None, first_edge = None,  width_of_bin  = None,  bins = 0,   
                             delay = False):
        """Calculating the histogram 
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
            delay (bool, optional):         
        Returns:
            xarray: The frequency histogram of the specified variable in the Dataset
        """ 

        #If the user has specified a function argument **trop_lat, s_year, f_year, s_month, f_month***, 
        # then the argument becomes a new class attributes.
        self.class_attributes_update(s_time = s_time, f_time = f_time, trop_lat = trop_lat, 
                               s_year = s_year, f_year = f_year, s_month = s_month, f_month = f_month, first_edge = first_edge, 
                               num_of_bins = num_of_bins, width_of_bin = width_of_bin)    

        last_edge = self.first_edge  + self.num_of_bins*self.width_of_bin

        if preprocess == True:
            data = self.preprocessing(data, preprocess=preprocess, variable_1=variable_1, trop_lat=trop_lat, 
                                      s_time = self.s_time, f_time = self.f_time,
                                      s_year=s_year, f_year=f_year, s_month=s_month, f_month=f_month,  sort = False, dask_array = False)

        ref = bh.Histogram(bh.axis.Regular(self.num_of_bins, self.first_edge, last_edge), storage=bh.storage.Weight())
        h = dh.factory(data, weights=data, histref=ref)
        counts, edges = h.to_dask_array()
        if delay == False:
            counts = counts.compute()
            edges = edges.compute()
        
        frequency_bin =  xr.DataArray(counts, coords=[edges[0:-1]], dims=["bin"])
        frequency_bin.attrs = data.attrs        
        return  frequency_bin


    """ """ """ """ """ """ """ """ """ """
    def dask_boost(self, data, preprocess = True, trop_lat = 10,  variable_1 = 'tprate',  
                   s_time = None, f_time = None, 
                   s_year = None, f_year = None, s_month = None, f_month = None, 
                   num_of_bins = None, first_edge = None,  width_of_bin  = None,  bins = 0):
        """Calculating the histogram 
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
        #If the user has specified a function argument **trop_lat, s_year, f_year, s_month, f_month***, 
        # then the argument becomes a new class attributes.
        self.class_attributes_update(s_time = s_time, f_time = f_time,  trop_lat = trop_lat, 
                               s_year = s_year, f_year = f_year, s_month = s_month, f_month = f_month, first_edge = first_edge, 
                               num_of_bins = num_of_bins, width_of_bin = width_of_bin) 

        last_edge = self.first_edge  + self.num_of_bins*self.width_of_bin

        if preprocess == True:
            data = self.preprocessing(data, preprocess=preprocess, variable_1=variable_1, trop_lat=trop_lat, 
                                      s_time = self.s_time, f_time = self.f_time, 
                                      s_year=s_year, f_year=f_year, s_month=s_month, f_month=f_month,  sort = False, dask_array = False)


        h = dhb.Histogram(dh.axis.Regular(self.num_of_bins, self.first_edge, last_edge),  storage=dh.storage.Double(), )
        h.fill(data)
        
        counts, edges = h.to_dask_array()
        print(counts, edges)
        counts =  dask.compute(counts)
        edges = dask.compute(edges[0]) 
        frequency_bin =  xr.DataArray(counts[0], coords=[edges[0][0:-1]], dims=["bin"])
        #frequency_bin.attrs = data.attrs
        #else: 
        #    counts =  dask.compute(counts.to_delayed())
        #    edges = dask.compute(edges[0].to_delayed())
           

        return  frequency_bin



    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """
    def hist_plot(self, data, pdf = True, smooth = True,  ls = '-', xlogscale = False, color = 'tab:blue', varname = 'Precipitation', plot_title = None,  label = None):
        """Ploting the histogram 

        Args:
            data (xarray):              The histogarm 
            pdf (bool, optional):       If pdf is True, the function returns the pdf histogram. Defaults to True.
            smooth (bool, optional):    If smooth is True, the function returns the smooth 2D-line instead of bars. Defaults to True.
            ls (str, optional):         The style of the line. Defaults to '-'.
            xlogscale (bool, optional): If xlogscale is True, the scale of x-axe is logaritmical. Defaults to False.
            color (str, optional):      The color of the line. Defaults to 'tab:blue'.
            varname (str, optional):    The name of the variable and x-axe. Defaults to 'Precipitation'.
            plot_title (str, optional): The title of the plot. Defaults to None.
            label (str, optional):      The unique label of the figure in the file system. Defaults to None.
        """        
   
        #pdf             (bool)      :   If ***_pdf=True***, then function returns the pdf histogram.
        #                                    If ***_pdf=False***, then function returns the frequency histogram.
        #Return:
        #    plot                        :   Frequency or pdf histogram. 
            

        fig = plt.figure( figsize=(8,5) )
        if pdf:
            data_density = data[0:]/sum(data[:])
            if smooth:
                plt.plot(data.bin[0:], data_density, 
                    linewidth=3.0, ls = ls, color = color, label = label )
                plt.grid(True)
            else:
                N, bins, patches = plt.hist(x= data.bin[0:], bins = data.bin[0:], weights= data_density,  label = label)

                fracs = ((N**(1 / 5)) / N.max())
                norm = colors.Normalize(fracs.min(), fracs.max())

                for thisfrac, thispatch in zip(fracs, patches):
                    color = plt.cm.viridis(norm(thisfrac))
                    thispatch.set_facecolor(color)
            
            plt.ylabel('PDF', fontsize=14)
            plt.xlabel(varname+", "+str(data.attrs['units']), fontsize=14)
            plt.yscale('log') 
        else:
            if smooth:
                plt.plot(data.bin[0:],  data[0:], 
                    linewidth=3.0, ls = ls, color = color, label = label )
                plt.grid(True)
            else:
                N, bins, patches = plt.hist(x= data.bin[0:], bins = data.bin[0:], weights=data[0:],  label = label)
                fracs = ((N**(1 / 5)) / N.max())
                norm = colors.Normalize(fracs.min(), fracs.max())

                for thisfrac, thispatch in zip(fracs, patches):
                    color = plt.cm.viridis(norm(thisfrac))
                    thispatch.set_facecolor(color)
                
            
            plt.ylabel('Frequency', fontsize=14)
            plt.xlabel(varname+", "+str(data.attrs['units']), fontsize=14)
            plt.yscale('log')
        if xlogscale == True:
            plt.xscale('log') 
        
        

        if plot_title == None:
            plot_title = str(data.attrs['title'])
            plot_title = re.split(r'[ ]', plot_title)[0]
        plt.title(plot_title, fontsize=16)

        if label == None:
            label = str(data.attrs['title'])
            label = re.split(r'[ ]', label)[0]

        # set the spacing between subplots
        fig.tight_layout()
        if smooth:
            if pdf: 
                plt.savefig('../notebooks/figures/'+str(label)+'_pdf_histogram_smooth.png')
            else:
                plt.savefig('../notebooks/figures/'+str(label)+'_histogram_smooth.png')
        else:
            if pdf:
                plt.savefig('../notebooks/figures/'+str(label)+'_pdf_histogram_viridis.png')
            else: 
                plt.savefig('../notebooks/figures/'+str(label)+'_histogram_viridis.png') 
    # You also can check this normalization
    #cmap = plt.get_cmap('viridis')
    #norm = plt.Normalize(min(_x), max(_x))
    #colors = cmap(norm(_x))


    """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """
    def hist_figure(self, data, pdf = True, smooth = True,  ls = '-', xlogscale = False, color = 'tab:blue', 
                   varname = 'Precipitation', plot_title = None,  add = None, save = True, label = None):
        """Ploting the histogram 

        Args:
            data (xarray):              The histogarm 
            pdf (bool, optional):       If pdf is True, the function returns the pdf histogram. Defaults to True.
            smooth (bool, optional):    If smooth is True, the function returns the smooth 2D-line instead of bars. Defaults to True.
            ls (str, optional):         The style of the line. Defaults to '-'.
            xlogscale (bool, optional): If xlogscale is True, the scale of x-axe is logaritmical. Defaults to False.
            color (str, optional):      The color of the line. Defaults to 'tab:blue'.
            varname (str, optional):    The name of the variable and x-axe. Defaults to 'Precipitation'.
            plot_title (str, optional): The title of the plot. Defaults to None.
            save (bool, optional):      The function saves the figure in the file system if the save is True.
            label (str, optional):      The unique label of the figure in the file system. Defaults to None.
        """        
   
        #pdf             (bool)      :   If ***_pdf=True***, then function returns the pdf histogram.
        #                                    If ***_pdf=False***, then function returns the frequency histogram.
        #Return:
        #    plot                        :   Frequency or pdf histogram. 
            

        if add==None:
            fig, ax = plt.subplots() #figsize=(8,5) 
        else: 
            fig, ax = add
        
        line_label = re.split(r'/', label)[-1]
        if pdf:
            data_density = data[0:]/sum(data[:])
            if smooth:
                ax.plot(data.bin[0:], data_density, linewidth=3.0, ls = ls, color = color, label = line_label )
                ax.grid(True)
            else:
                N, bins, patches = ax.hist(x= data.bin[0:], bins = data.bin[0:], weights= data_density,  label = line_label)

                fracs = ((N**(1 / 5)) / N.max())
                norm = colors.Normalize(fracs.min(), fracs.max())

                for thisfrac, thispatch in zip(fracs, patches):
                    color = ax.cm.viridis(norm(thisfrac))
                    thispatch.set_facecolor(color)
            
            plt.ylabel('PDF', fontsize=14)
            plt.xlabel(varname+", "+str(data.attrs['units']), fontsize=14)
            plt.yscale('log') 
        else:
            if smooth:
                plt.plot(data.bin[0:],  data[0:], 
                    linewidth=3.0, ls = ls, color = color, label = line_label )
                plt.grid(True)
            else:
                N, bins, patches = plt.hist(x= data.bin[0:], bins = data.bin[0:], weights=data[0:],  label = line_label)
                fracs = ((N**(1 / 5)) / N.max())
                norm = colors.Normalize(fracs.min(), fracs.max())

                for thisfrac, thispatch in zip(fracs, patches):
                    color = plt.cm.viridis(norm(thisfrac))
                    thispatch.set_facecolor(color)
                
            
            plt.ylabel('Frequency', fontsize=14)
            plt.xlabel(varname+", "+str(data.attrs['units']), fontsize=14)
            plt.yscale('log')
        if xlogscale == True:
            plt.xscale('log') 
        
        

        if plot_title == None:
            plot_title = str(data.attrs['title'])
            plot_title = re.split(r'[ ]', plot_title)[0]
        plt.title(plot_title, fontsize=16)

        if label == None:
            label = str(data.attrs['title'])
            label = re.split(r'[ ]', label)[0]

        plt.legend(loc='upper right', fontsize=12)
        # set the spacing between subplots
        fig.tight_layout()
        
        if save:
            if smooth:
                if pdf: 
                    plt.savefig('../notebooks/figures/'+str(label)+'_pdf_histogram_smooth.png')
                else:
                    plt.savefig('../notebooks/figures/'+str(label)+'_histogram_smooth.png')
            else:
                if pdf:
                    plt.savefig('../notebooks/figures/'+str(label)+'_pdf_histogram_viridis.png')
                else: 
                    plt.savefig('../notebooks/figures/'+str(label)+'_histogram_viridis.png') 
        return {fig, ax}
    # You also can check this normalization
    #cmap = plt.get_cmap('viridis')
    #norm = plt.Normalize(min(_x), max(_x))
    #colors = cmap(norm(_x))




    """ 

    def hist_figure(self, data, _plt = plt, pdf = None, ls = '-', color = 'tab:blue', label = None):

        pdf =  True if None else pdf 
           
        if pdf == True:
            print('pdf')
            _data_density = data[0:]/sum(data[:]) #*(data.bin[1]-data.bin[0]))
            _plt.step(data.bin[0:], _data_density, #data.bin[1]-data.bin[0],
                linewidth=3.0, ls = ls, color = color, label = label )
            _plt.set_ylabel('Probability', fontsize=14)
            _plt.set_xlabel('Total Precipitation', fontsize=14)
            _plt.set_yscale('log') 
        else:
            _plt.step(data.bin[0:], data[0:],  #data.bin[1]-data.bin[0], 
                linewidth=3.0,  ls = ls, color = color, label = label )
            _plt.set_yscale('log')
            _plt.set_ylabel('Frequency', fontsize=14)
            _plt.set_xlabel('Total Precipitation', fontsize=14)
        # FIG SAVE 
        """
        # For i amount of step
        # Function which compute the histogramn before ploting! 
        # Save the data
        # Probability to reset the hist values (bool parameters) 
        # Only after plot





