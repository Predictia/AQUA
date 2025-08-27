from typing import Optional
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from aqua.logger import log_configure
from .styles import ConfigStyle

def plot_vertical_profile(data: xr.DataArray, var: str,
                         plev_min: Optional[float] = None, plev_max: Optional[float] = None, 
                         vmin: Optional[float] = None, vmax: Optional[float] = None, 
                         nlevels: Optional[int] = 18,  
                         title: Optional[str] = None, style: Optional[str] = None,
                         return_fig: bool = False, 
                         loglevel='WARNING',  **kwargs):
    """
    Plots a zonal mean vertical profile 

    Args:
        data (xarray.DataArray): data to plot.
        var (str): Variable name to plot (for labeling purposes).
        vmin (float, optional): Minimum colorbar value.
        vmax (float, optional): Maximum colorbar value.
        plev_min (float, optional): Minimum pressure level to plot.
        plev_max (float, optional): Maximum pressure level to plot.
        nlevels (int, optional): Number of contour levels for the plot.
        title (str, optional): Title of the plot.
        return_fig (bool, optional): If True, returns the figure and axis objects. Defaults to False.
        style (str, optional): Style to use. Defaults to None (aqua style).
    """

    logger = log_configure(loglevel, 'plot_single_map')
    ConfigStyle(style=style, loglevel=loglevel)

    if plev_min is None:
        plev_min = data['plev'].min().item()
    if plev_max is None:
        plev_max = data['plev'].max().item()
    # Slice pressure levels 
    mask = (data['plev'] >= plev_min) & (data['plev'] <= plev_max)
    data = data.sel(plev=data['plev'].where(mask, drop=True))
    # Ensure reasonable number of levels
    nlevels = max(2, int(nlevels))
    zonal_mean = data.mean(dim='lon')
    
    # Determine colorbar limits if not provided
    if vmin is None or vmax is None:
        vmin, vmax = float(zonal_mean.min()), float(zonal_mean.max())
        if vmin * vmax < 0:
            vmax = max(abs(vmin), abs(vmax))
            vmin = -vmax

    levels = np.linspace(vmin, vmax, nlevels)

    fig, ax = plt.subplots(figsize=(10, 8))
    cax = ax.contourf(
        zonal_mean['lat'], zonal_mean['plev'], zonal_mean,
        cmap='RdBu_r', levels=levels, extend='both'
    )
    ax.set_yscale('log')
    ax.set_ylabel('Pressure Level (Pa)')
    ax.set_xlabel('Latitude')
    ax.invert_yaxis()
    fig.colorbar(cax, ax=ax, label=f'{var} [{zonal_mean.attrs.get("units", "")}]')
    ax.grid(True)

    if title:
        logger.debug("Setting title to %s", title)
        ax.set_title(title)

    if return_fig:
        logger.debug("Returning figure and axes")
        return fig, ax