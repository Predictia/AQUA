from typing import Optional
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from aqua.logger import log_configure
from aqua.util import evaluate_colorbar_limits
from .styles import ConfigStyle

def plot_vertical_profile(data: xr.DataArray, var: str,
                         lev_min: Optional[float] = None, lev_max: Optional[float] = None, 
                         vmin: Optional[float] = None, vmax: Optional[float] = None, 
                         nlevels: Optional[int] = 18, lev_name: Optional[str] = 'plev',
                         title: Optional[str] = None, style: Optional[str] = None,
                         logscale: bool = False,
                         return_fig: bool = False, figsize: Optional[tuple] = (10, 8),
                         fig: Optional[plt.Figure] = None, ax: Optional[plt.Axes] = None,
                         ax_pos: tuple = (1, 1, 1),
                         loglevel='WARNING',  **kwargs):
    """
    Plots a zonal mean vertical profile 

    Args:
        data (xarray.DataArray): data to plot.
        var (str): Variable name to plot (for labeling purposes).
        vmin (float, optional): Minimum colorbar value.
        vmax (float, optional): Maximum colorbar value.
        lev_min (float, optional): Minimum vertical level to plot.
        lev_max (float, optional): Maximum vertical level to plot.
        nlevels (int, optional): Number of contour levels for the plot.
        lev_name (str, optional): Name of the vertical levels. Defaults to 'plev'.
        title (str, optional): Title of the plot.
        style (str, optional): Style to use. Defaults to None (aqua style)
        logscale (bool, optional): If True, use logarithmic scale for the y-axis. Defaults to False.
        return_fig (bool, optional): If True, returns the figure and axis objects. Defaults to False.
        figsize (tuple, optional): Figure size. Defaults to (10, 8).
        fig (plt.Figure, optional):  Figure to plot on. By default a new figure is created.
        ax (plt.Axes, optional):     Axes to plot on. By default a new axes is created.
        ax_pos (tuple, optional):    Axes position in the figure (nrows, ncols, index).
        loglevel (str, optional): Logging level. Defaults to 'WARNING'.
    """

    logger = log_configure(loglevel, 'plot_vertical_profile')
    ConfigStyle(style=style, loglevel=loglevel)

    if lev_min is None:
        lev_min = data[lev_name].min().item()
    if lev_max is None:
        lev_max = data[lev_name].max().item()
    # Slice vertical levels 
    mask = (data[lev_name] >= lev_min) & (data[lev_name] <= lev_max)
    data = data.sel({lev_name: data[lev_name].where(mask, drop=True)})
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
        data['lat'], data[lev_name], data,
        cmap='RdBu_r', levels=levels, extend='both'
    )
    if logscale:
        ax.set_yscale('log')
    ax.set_xlabel('Latitude')
    ax.set_ylabel("Pressure Level (Pa)" if lev_name == "plev" else lev_name)

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
                                lev_min: Optional[float] = None, lev_max: Optional[float] = None, 
                                vmin: Optional[float] = None, vmax: Optional[float] = None, 
                                vmin_contour: Optional[float] = None, vmax_contour: Optional[float] = None,
                                sym_contour: bool = False, add_contour: bool = False,
                                nlevels: Optional[int] = 18, lev_name: Optional[str] = 'plev',
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
        vmin_contour (float, optional): Minimum colorbar value for the contour plot.
        vmax_contour (float, optional): Maximum colorbar value for the contour plot.
        sym_contour (bool, optional): If True, the contour colorbar limits are symmetric
            around zero. Defaults to False.
        add_contour (bool, optional): Whether to add contour lines of the data.
        lev_min (float, optional): Minimum vertical level to plot.
        lev_max (float, optional): Maximum vertical level to plot.
        nlevels (int, optional): Number of contour levels for the plot.
        lev_name (str, optional): Name of the vertical levels. Defaults to 'plev'.
        title (str, optional): Title of the plot.
        return_fig (bool, optional): If True, returns the figure and axis objects. Defaults to False.
        fig: Optional[plt.Figure] = None, ax: Optional[plt.Axes] = None,
        style (str, optional): Style to use. Defaults to None (aqua style).
    """

    logger = log_configure(loglevel, 'plot_vertical_profile')

    # Evaluate the difference
    diff = data - data_ref

    fig, ax = plot_vertical_profile(
        diff, var=var, lev_min=lev_min, lev_max=lev_max,
        vmin=vmin, vmax=vmax, nlevels=nlevels, title=title,
        style=style, return_fig=True, fig=fig, ax=ax, ax_pos=ax_pos,
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

        # Use common levels for contour 
        data_common = data.sel({lev_name: diff[lev_name]})

        ds = ax.contour(
            data_common['lat'], data_common[lev_name], data_common,
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