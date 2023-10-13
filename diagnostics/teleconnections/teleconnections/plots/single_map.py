import os

import cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

from aqua.logger import log_configure
from .plot_utils import add_cyclic_lon, evaluate_colorbar_limits


def plot_single_map(data : xr.DataArray, save=False,
                    contour=True, sym=True,
                    figsize=(11, 8.5),
                    nlevels=11, outputdir=".",
                    loglevel='WARNING',
                    **kwargs):
    logger = log_configure(loglevel, 'plot_single_map')

    # We load in memory the data, to avoid problems with dask
    logger.debug("Loading data in memory")
    data = data.load()
    data = add_cyclic_lon(data)

    proj = ccrs.PlateCarree()

    logger.debug("Setting figsize to %s", figsize)
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection=proj)

    vmin, vmax = evaluate_colorbar_limits(maps=[data], sym=sym)
    logger.debug("Setting vmin to %s", vmin)
    logger.debug("Setting vmax to %s", vmax)
    if contour:
        levels = np.linspace(vmin, vmax, nlevels+1)
    
    # Plot the data
    if contour:
        cs = ax.contourf(data['lon'], data['lat'], data, cmap='RdBu_r',
                         transform=proj, levels=levels)
    else:   
        cs = ax.pcolormesh(data['lon'], data['lat'], data, cmap='RdBu_r',
                           transform=proj, vmin=vmin, vmax=vmax)

    ax.coastlines()

    # Longitude labels
    ax.set_xticks(np.arange(-180, 181, 60), crs=ccrs.PlateCarree())
    lon_formatter = cticker.LongitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)

    # Latitude labels
    ax.set_yticks(np.arange(-90, 91, 30), crs=ccrs.PlateCarree())
    lat_formatter = cticker.LatitudeFormatter()
    ax.yaxis.set_major_formatter(lat_formatter)

    # Adjust the location of the subplots on the page to make room for the colorbar
    fig.subplots_adjust(bottom=0.25, top=0.9, left=0.05, right=0.95,
                        wspace=0.1, hspace=0.5)

    # Add a colorbar axis at the bottom of the graph
    cbar_ax = fig.add_axes([0.2, 0.15, 0.6, 0.02])
