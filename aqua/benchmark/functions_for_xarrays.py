
"""The module contains functions useful for xarrays:
     - xarray_attribute_update,
     - data_size

.. moduleauthor:: AQUA team <natalia.nazarova@polito.it>

"""

def xarray_attribute_update(xr1, xr2):
    """Combining the attributes of two xarrays

    Args:
        xr1 (xarray): xarray, to which we would like to add attributes
        xr2 (xarray): xarray, which attributes we want to pass to another xarray

    Returns:
        xarray: xarray with combained attributes
    """
    combined_attrs = {**xr1.attrs, **xr2.attrs}
    history_attr  = xr1.attrs['history'] +  xr2.attrs['history']
    xr1.attrs = combined_attrs
    xr1.attrs['history'] = history_attr
    return xr1


def data_size(data):
    """Returning the size of the Dataset or DataArray

    Args:
        data (xarray): Dataset or dataArray, the size of which we would like to return
    Returns:
        int: size of data
    """ 
    if 'DataArray' in str(type(data)):
            size = data.size
    elif 'Dataset' in str(type(data)): 
        names = list(data.dims) #_coord_names)
        size = 1
        for i in names:
            size *= data[i].size
    return size


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
        

""" """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ 
def ds_per_time_range(data,  s_time = None, f_time = None, s_year = None, f_year = None,
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
        Exception: "Please, insert only s_time or only s_year.  Do not combine them!"
        Exception: "Please, insert only s_time or only s_month. Do not combine them!"
        Exception: "Please, insert only f_time or only f_year.  Do not combine them!"
        Exception: "Please, insert only f_time or only f_month. Do not combine them!"
        Exception: "s_year must be an integer"
        Exception: "s_year and f_year must be an integer"
        Exception: "s_month and f_month must be an integer"
        Exception: "Unknown format of time. Try one more time"
        Exception: "Unknown format of time. Try one more time"

    Returns:
        xarray: The Dataset only for selected time range. 
    """         

    if s_time != None and s_year != None:
        raise Exception("Please, insert only s_time or only s_year. Do not combine them!")  
    if s_time != None and s_month != None:
        raise Exception("Please, insert only s_time or only s_month. Do not combine them!")
    if f_time != None and f_year != None:
        raise Exception("Please, insert only f_time or only f_year. Do not combine them!") 
    if f_time != None and f_month != None:
        raise Exception("Please, insert only f_time or only f_month. Do not combine them!")

    if isinstance( s_time, int) and f_time==None:
        return data.time[s_time]
    elif isinstance(f_time, int) and s_time==None:
        return data.time[f_time]
    elif isinstance( s_time, int) and isinstance( f_time, int): 
        return data.isel(time=slice( s_time,  f_time))
    
    if  s_year != None and  f_year == None:
        if isinstance(s_year, int):
            data= data.where(data['time.year'] ==  s_year, drop=True)
        else:
            raise Exception("s_year must be an integer")
    elif  s_year != None and  f_year != None:
        if isinstance(s_year, int) and isinstance(f_year, int): 
            data = data.where(data['time.year'] >=  s_year, drop=True)
            data = data.where(data['time.year'] <=  f_year, drop=True)
        else:
            raise Exception("s_year and f_year must be an integer") 
    
    if  s_month != None and  f_month != None:
        if isinstance(s_month, int) and isinstance(f_month, int): 
            data = data.where(data['time.month'] >=  s_month, drop=True)
            data = data.where(data['time.month'] <=  f_month, drop=True)  
        else:
            raise Exception("s_month and f_month must be an integer") 
    
    if isinstance( s_time, str) and isinstance( f_time, str):
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
            raise Exception("Unknown format of time. Try one more time")  
        data=data.sel(time=slice(s_time, f_time))    
    elif  isinstance(s_year, str) and   f_time == None:
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
            raise Exception("Unknown format of time. Try one more time")    
        data=data.sel(time=slice(time))
    return data