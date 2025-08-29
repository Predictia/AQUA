from typing import Optional
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from aqua.logger import log_configure
from aqua.util import evaluate_colorbar_limits
from .styles import ConfigStyle

def plot_vertical_profile(data: xr.DataArray, var: str,
                         plev_min: Optional[float] = None, plev_max: Optional[float] = None, 
                         vmin: Optional[float] = None, vmax: Optional[float] = None, 
                         nlevels: Optional[int] = 18,  
                         title: Optional[str] = None, style: Optional[str] = None,
                         return_fig: bool = False, figsize: Optional[tuple] = (10, 8),
                         fig: Optional[plt.Figure] = None, ax: Optional[plt.Axes] = None,
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
        figsize (tuple, optional): Figure size. Defaults to (10, 8).
        fig (plt.Figure, optional):  Figure to plot on. By default a new figure is created.
        ax (plt.Axes, optional):     Axes to plot on. By default a new axes is created.
        style (str, optional): Style to use. Defaults to None (aqua style).
    """

    logger = log_configure(loglevel, 'plot_vertical_profile')
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
    
    # Determine colorbar limits if not provided
    if vmin is None or vmax is None:
        vmin, vmax = float(data.min()), float(data.max())
        if vmin * vmax < 0:
            vmax = max(abs(vmin), abs(vmax))
            vmin = -vmax

    levels = np.linspace(vmin, vmax, nlevels)

    if fig is None:
        fig = plt.figure(figsize=figsize)
    if ax is None:
        ax = fig.add_subplot(ax_pos[0], ax_pos[1], ax_pos[2])

    cax = ax.contourf(
        data['lat'], data['plev'], data,
        cmap='RdBu_r', levels=levels, extend='both'
    )
    ax.set_yscale('log')
    ax.set_ylabel('Pressure Level (Pa)')
    ax.set_xlabel('Latitude')
    ax.invert_yaxis()
    fig.colorbar(cax, ax=ax, label=f'{var} [{data.attrs.get("units", "")}]')
    ax.grid(True)

    if title:
        logger.debug("Setting title to %s", title)
        ax.set_title(title)

    if return_fig:
        logger.debug("Returning figure and axes")
        return fig, ax


def plot_vertical_profile_diff(data: xr.DataArray, data_ref: xr.DataArray,
                                var: str,
                                plev_min: Optional[float] = None, plev_max: Optional[float] = None, 
                                vmin: Optional[float] = None, vmax: Optional[float] = None, 
                                vmin_contour: Optional[float] = None, vmax_contour: Optional[float] = None,
                                sym_contour: bool = False, add_contour: bool = False,
                                nlevels: Optional[int] = 18,  
                                title: Optional[str] = None, style: Optional[str] = None,
                                return_fig: bool = False,
                                fig: Optional[plt.Figure] = None, ax: Optional[plt.Axes] = None,
                                ax_pos: tuple = (1, 1, 1),
                                loglevel='WARNING',  **kwargs):
    """
    Plot the difference of data-data_ref as vertical profile and add the data 
    as a contour plot.

    Args:
        data (xarray.DataArray): data to plot.
        data_ref (xr.DataArray): Reference data to plot the difference.
        var (str): Variable name to plot (for labeling purposes).
        vmin (float, optional): Minimum colorbar value.
        vmax (float, optional): Maximum colorbar value.
        plev_min (float, optional): Minimum pressure level to plot.
        plev_max (float, optional): Maximum pressure level to plot.
        nlevels (int, optional): Number of contour levels for the plot.
        title (str, optional): Title of the plot.
        return_fig (bool, optional): If True, returns the figure and axis objects. Defaults to False.
        fig: Optional[plt.Figure] = None, ax: Optional[plt.Axes] = None,
        style (str, optional): Style to use. Defaults to None (aqua style).
    """

    logger = log_configure(loglevel, 'plot_vertical_profile')

    # Evaluate the difference
    diff = data - data_ref

    fig, ax = plot_vertical_profile(
        diff, var=var, plev_min=plev_min, plev_max=plev_max,
        vmin=vmin, vmax=vmax, nlevels=nlevels, title=title,
        style=style, return_fig=True, fig=fig, ax=ax,
        loglevel=loglevel, **kwargs
    )

    # Evaluate vmin and vmax of the contour
    if vmin_contour is None or vmax_contour is None:
        vmin_contour, vmax_contour = evaluate_colorbar_limits(maps=[data], sym=sym_contour)
    else:
        if sym_contour:
            logger.warning("sym_contour=True, vmin_map and vmax_map given will be ignored")
            vmin_contour, vmax_contour = evaluate_colorbar_limits(maps=[data], sym=sym_contour)

    logger.debug("Setting contour vmin to %s, vmax to %s", vmin_contour, vmax_contour)

    if add_contour:

        if vmin is None or vmax is None:
            vmin, vmax = float(diff.min()), float(diff.max())
        if vmin * vmax < 0:
            vmax = max(abs(vmin), abs(vmax))
            vmin = -vmax
        
        nlevels = max(2, int(nlevels))
        levels = np.linspace(vmin, vmax, nlevels)

        # Use common plevs for contour 
        data_common = data.sel(plev=diff['plev'])

        ds = ax.contour(
            data_common['lat'], data_common['plev'], data_common,
            levels=levels, colors='k', linewidths=0.5
        )
        fmt = {level: f"{level:.1e}" if (abs(level) < 0.1 or abs(level) > 1000)
            else f"{level:.1f}" for level in ds.levels}
        ax.clabel(ds, fmt=fmt, fontsize=6, inline=True)
    
    if title:
        logger.debug("Setting title to %s", title)
        ax.set_title(title)

    if return_fig:
        logger.debug("Returning figure and axes")
        return fig, ax