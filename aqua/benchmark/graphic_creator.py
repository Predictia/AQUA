import numpy as np
import xarray

import matplotlib.pyplot as plt
import matplotlib.animation as animation

import cartopy
import cartopy.feature as cfeature
import cartopy.crs as ccrs

from .time_functions import time_into_plot_title, time_interpreter, month_convert_num_to_str, hour_convert_num_to_str, time_units_converter 

"""The module contains functions to create animations and images:
     - animation_creator,
     - image_creator,
     - lon_lat_regrider
     
.. moduleauthor:: AQUA team <natalia.nazarova@polito.it>

"""

def data_size(data):
    """Returning the size of the Dataset or DataArray

    Args:
        data (xarray): Dataset or dataArray, the size of which we would like to return
    Returns:
        int: size of data
    """   
    if 'DataArray' in str(type(data)):
            _size = data.size
    elif 'Dataset' in str(type(data)): 
        names = list(data.dims) #_coord_names)
        size = 1
        for i in _names:
            size *= data[i].size
    return size

""" """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """
def animation_creator(ds, vmin = None, vmax = None, trop_lat = 10,  time_ind_max = None,  nSeconds = 10,  contour  = True, 
                      label = 'test', title = 'Tropical precipitation', resol = '110m'):
    """Creating the animation of the dataset

    Args:
        ds (xarray):                    The Dataset.
        vmin (float, optional):         The minimal data value of the colormap. Defaults to None.
        vmax (float, optional):         The maximal data value of the colormap. Defaults to None.
        trop_lat (int/float, optional): Tropical latitudes borders. Defaults to 10.
        time_ind_max (int, optional):   The maximal time index of Dataset for animation. Defaults to None.
        nSeconds (int, optional):       The duration of the animation in seconds. Defaults to 10.
        contour (bool, optional):       The contour of continents. Defaults to True.
        label (str, optional):          The name of created animation in the filesystem. Defaults to 'test'.
        title (str, optional):          The title of the animation. Defaults to 'Tropical precipitation'.
        resol (str, optional):          The resolution of contour of continents. Defaults to '110m'.

    Returns:
        mp4: amination
    """    
    if vmin != None:
        ds = ds.where( ds > vmin, drop=True) 

    if time_ind_max != None:
        fps = int(time_ind_max/nSeconds)
    else:
        fps = int(ds.time.size/nSeconds)

    snapshots = [ds[number,:,:] for number in range(0, fps*nSeconds )]

    # First set up the figure, the axis, and the plot element we want to animate
    fig = plt.figure( figsize=(20,8) )

    ax = plt.axes(projection=ccrs.PlateCarree())

    if  contour:
        ax.coastlines(resolution=resol)
    # branch, animation for different variables 
    
    ax.gridlines()

    a = snapshots[0]
    
    #ax.axhspan(-trop_lat, trop_lat, facecolor='grey', alpha=0.3)
    im = plt.imshow(a, interpolation='none',  aspect='auto', vmin=vmin, vmax=vmax, #alpha = 1., 
                    extent = (-180, 180, - trop_lat, trop_lat), origin = 'upper')


    fig.colorbar(im).set_label(ds.units, fontsize = 14)
    
    def animate_func(i):
        if i % fps == 0:
            print( '.', end ='' )
        im.set_array(snapshots[i])
        time = time_into_plot_title(ds, i)
        plt.title(title+',     '+time, fontsize = 16)
        return [im]

    

    dpi = 100
    fig.set_size_inches(12, 8, True)
    writer = animation.writers['ffmpeg'](fps=30, extra_args=['-vcodec', 'libx264'])
    
    anim = animation.FuncAnimation(fig, 
                            animate_func, 
                            frames = nSeconds * fps,
                            interval = 1000 / fps, # in ms
                            )

    #plt.title(title,     fontsize =18)
    plt.xlabel('longitude',                 fontsize =18)
    plt.ylabel('latitude',                  fontsize =18)
    plt.xticks([-180, -120, -60, 0, 60, 120, 180],  fontsize=14)   #, 240, 300, 360
    plt.yticks([-90, -60, -30, 0, 30, 60, 90],      fontsize=14) 
   
    
    anim.save('../notebooks/figures/animation/'+str(label)+'_anim.mp4', writer=writer,  dpi=dpi) #

    print('Done!')
    return  True

""" """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """ """
def image_creator(ds, vmin = None, vmax = None, trop_lat = 10, figsize =1, contour  = True,   label = 'test',  
                  title = 'Tropical precipitation', resol = '110m'):
    """Creating the image of the Dataset.

    Args:
        ds (xarray):                    The Dataset.
        vmin (float, optional):         The minimal data value of the colormap. Defaults to None.
        vmax (float, optional):         The maximal data value of the colormap. Defaults to None.
        trop_lat (int/float, optional): Tropical latitudes borders. Defaults to 10.
        figsize (int, optional):        The scale factor of the size of the created image. Defaults to 1.
        contour (bool, optional):       The contour of continents. Defaults to True.
        label (str, optional):          The name of created animation in the filesystem. Defaults to 'test'.
        title (str, optional):          The title of the animation. Defaults to 'Tropical precipitation'.
        resol (str, optional):          The resolution of contour of continents. Defaults to '110m'.
    """    
    if vmin != None:
        ds = ds.where( ds > vmin, drop=True) 

    if ds.time.size!=1:
        snapshot = ds[0,:,:] 
    else:
        snapshot = ds
    # First set up the figure, the axis, and the plot element we want to animate
    fig = plt.figure( figsize=(8*figsize,5*figsize) )
    
    ax = plt.axes(projection=ccrs.PlateCarree())
    
    if  contour:
        ax.coastlines(resolution=resol)
    
    ax.gridlines() 
    
    ax.axhspan(-trop_lat, trop_lat, facecolor='grey', alpha=0.3)
    im = plt.imshow(snapshot, interpolation='none',  aspect='auto', vmin=vmin, vmax=vmax, #alpha = 1., 
                    extent = (-180, 180, - trop_lat, trop_lat), origin = 'upper')

    fig.colorbar(im)

    plt.title( title,     fontsize =18)
    plt.xlabel('longitude',                 fontsize =18)
    plt.ylabel('latitude',                  fontsize =18)
    plt.xticks([-180, -120, -60, 0, 60, 120, 180],  fontsize=14)   #, 240, 300, 360
    plt.yticks([-90, -60, -30, 0, 30, 60, 90],      fontsize=14) 
    plt.savefig('../notebooks/figures/'+str(label)+'.png')
    print('Done!')


def lon_lat_regrider(data, space_grid_factor = None, coord_name = 'lat'):
    """The space regrider of the Dataset

    Args:
        data (xarray):                      The Dataset to be space regrided.
        space_grid_factor (int, optional):  The resolution of the new space grid. If the input value is negative, the space grid will be less dense 
                                            in space_grid_factor time. If the input value is positive, the space grid will be dense 
                                            in space_grid_factor times. Defaults to None.
        coord_name (str, optional):         The name of space coordinate. Defaults to 'lat'.

    Returns:
        xarray: The space regrided Dataset.
    """    
    # work only for lat and lon only for now. Check the line with interpolation command and modify it in the future
    if isinstance(space_grid_factor, int):
        if space_grid_factor>1:
            del_c = float((float(data[coord_name][1])- float(data[coord_name][0]))/2)
            ds = []
            new_dataset = data.copy(deep=True)
            new_dataset[coord_name] = data[coord_name][:] 
            for i in range(1, space_grid_factor):
                if coord_name == 'lat':  
                    new_dataset = new_dataset.interp(lat=new_dataset['lat'][:]+del_c, method="linear", kwargs={"fill_value": "extrapolate"})
                elif coord_name == 'lon':
                    new_dataset = new_dataset.interp(lon=new_dataset['lon'][:]+del_c, method="linear", kwargs={"fill_value": "extrapolate"}) 
                ds.append(new_dataset)
                del_c = del_c/2
            combined = xarray.concat(ds, dim=coord_name)
            combined = combined.sortby(combined[coord_name])
            return combined
        elif space_grid_factor<1:
            space_grid_factor = abs(space_grid_factor)
            if coord_name == 'lat': 
                new_dataset = data.isel(lat=[i for i in range(0, data.lat.size, space_grid_factor)])
            elif coord_name == 'lon':
                new_dataset = data.isel(lon=[i for i in range(0, data.lon.size, space_grid_factor)])
            return new_dataset












