from typing import Optional, Tuple
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

from aqua.logger import log_configure
from aqua.util import evaluate_colorbar_limits
from .styles import ConfigStyle


def plot_vertical_profile(data: xr.DataArray, var: str,
                          lev_name: str = "plev", x_coord: str = "lat",
                          lev_min: Optional[float] = None,lev_max: Optional[float] = None,
                          vmin: Optional[float] = None, vmax: Optional[float] = None,
                          nlevels: int = 18, 
                          title: Optional[str] = None, style: Optional[str] = None,
                          logscale: bool = False,
                          return_fig: bool = False, figsize: Tuple[int, int] = (10, 8),
                          fig: Optional[plt.Figure] = None, ax: Optional[plt.Axes] = None,
                          ax_pos: Tuple[int, int, int] = (1, 1, 1),
                          loglevel: str = "WARNING",
                          **kwargs):
    """
    Plots a zonal mean vertical profile.

    Args:
        data: DataArray to plot.
        lev_name: Name of the vertical levels (default 'plev').
        x_coord: Name of the horizontal coordinate (default 'lat').
        var: Variable name for labeling purposes.
        lev_min, lev_max: Range of vertical levels to plot.
        vmin, vmax: Colorbar limits.
        nlevels: Number of contour levels.
        lev_name: Name of the vertical levels (default 'plev').
        title: Plot title.
        style: Plot style (default aqua style).
        logscale: Use log scale for y-axis if True.
        return_fig: If True, return (fig, ax).
        figsize: Figure size.
        fig, ax: Optional figure/axes to plot on.
        ax_pos: Position of subplot.
        loglevel: Logging level.
    """

    logger = log_configure(loglevel, "plot_vertical_profile")

    # Select vertical levels
    lev_min = lev_min or data[lev_name].min().item()
    lev_max = lev_max or data[lev_name].max().item()
    mask = (data[lev_name] >= lev_min) & (data[lev_name] <= lev_max)
    data = data.sel({lev_name: data[lev_name].where(mask, drop=True)})

    # Ensure reasonable number of levels
    nlevels = max(2, int(nlevels))

    # Auto colorbar limits if not provided
    if vmin is None or vmax is None:
        vmin, vmax = float(data.min()), float(data.max())
        if vmin * vmax < 0:  # symmetric around 0
            vmax = max(abs(vmin), abs(vmax))
            vmin = -vmax

    levels = np.linspace(vmin, vmax, nlevels)

    # Prepare figure and axis
    fig = fig or plt.figure(figsize=figsize)
    ax = ax or fig.add_subplot(*ax_pos)

    # Plot
    cax = ax.contourf(data[x_coord], data[lev_name], data,
                      cmap="RdBu_r", levels=levels, extend="both")
    if logscale:
        ax.set_yscale("log")
    ax.set_xlabel("Latitude") if x_coord == "lat" else x_coord
    ax.set_ylabel("Pressure Level (Pa)" if lev_name == "plev" else lev_name)
    ax.invert_yaxis()
    fig.colorbar(cax, ax=ax, label=f"{var} [{data.attrs.get('units', '')}]")
    ax.grid(True)

    if title:
        logger.debug("Setting title to %s", title)
        ax.set_title(title)

    if return_fig:
        logger.debug("Returning figure and axes")
        return fig, ax


def plot_vertical_profile_diff(data: xr.DataArray, data_ref: xr.DataArray,
                               var: str, 
                               lev_name: str = "plev", x_coord: str = "lat",
                               lev_min: Optional[float] = None, lev_max: Optional[float] = None,
                               vmin: Optional[float] = None, vmax: Optional[float] = None,
                               vmin_contour: Optional[float] = None, vmax_contour: Optional[float] = None,
                               sym_contour: bool = False, add_contour: bool = False,
                               nlevels: int = 18,
                               title: Optional[str] = None, style: Optional[str] = None,
                               return_fig: bool = False, fig: Optional[plt.Figure] = None,
                               ax: Optional[plt.Axes] = None, ax_pos: Tuple[int, int, int] = (1, 1, 1),
                               loglevel: str = "WARNING",
                                **kwargs):
    """
    Plot the difference (data - data_ref) as vertical profile.
    Optionally add contour lines of the reference data.

    Args:
        data, data_ref: DataArrays to compare.
        var: Variable name for labeling purposes.
        lev_name: Name of the vertical levels.
        x_coord: Name of the horizontal coordinate.
        vmin, vmax: Limits for the difference plot.
        vmin_contour, vmax_contour: Limits for contour plot.
        sym_contour: If True, contour limits symmetric around zero.
        add_contour: If True, overlay contour lines from reference data.
        lev_min, lev_max: Range of vertical levels to plot.
        nlevels: Number of contour levels.
        title: Plot title.
        return_fig: If True, return (fig, ax).
    """

    logger = log_configure(loglevel, "plot_vertical_profile_diff")

    # Difference
    diff = data - data_ref

    fig, ax = plot_vertical_profile(
        diff, var=var, lev_min=lev_min, lev_max=lev_max,
        vmin=vmin, vmax=vmax, nlevels=nlevels, title=title,
        style=style, return_fig=True, fig=fig, ax=ax, ax_pos=ax_pos,
        loglevel=loglevel, **kwargs)

    # Add contours of reference data
    if add_contour:
        # Contour limits
        if vmin_contour is None or vmax_contour is None:
            vmin_contour, vmax_contour = evaluate_colorbar_limits([data], sym=sym_contour)

        levels = np.linspace(vmin_contour, vmax_contour, max(2, int(nlevels)))
        data_common = data.sel({lev_name: diff[lev_name]})

        cs = ax.contour(data_common[x_coord], data_common[lev_name], data_common,
                        levels=levels, colors="k", linewidths=0.5)
        fmt = {lvl: f"{lvl:.1e}" if (abs(lvl) < 0.1 or abs(lvl) > 1000)
               else f"{lvl:.1f}" for lvl in cs.levels}
        ax.clabel(cs, fmt=fmt, fontsize=6, inline=True)

    if title:
        logger.debug("Setting title to %s", title)
        ax.set_title(title)

    if return_fig:
        logger.debug("Returning figure and axes")
        return fig, ax
