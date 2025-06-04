"""
Module to plot multiple hovemoller data

"""

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

from aqua import plot_hovmoller
from aqua.graphics import ConfigStyle
from aqua.logger import log_configure
from aqua.util import cbar_get_label, evaluate_colorbar_limits, plot_box


def plot_multi_hovmoller(
    maps: list,
    contour: bool = True,
    save=False,
    sym: bool = False,
    figsize: tuple = None,
    variables: list = None,
    dim="lon",
    invert_axis: bool = False,
    invert_time: bool = False,
    fig: plt.Figure = None,
    ax: plt.Axes = None,
    ax_pos: tuple = (1, 1, 1),
    style=None,
    vmin: float = None,
    vmax: float = None,
    nlevels: int = 11,
    title: str = None,
    titles: list = None,
    cmap="PuOr_r",
    cbar_label=None,
    outputdir=".",
    filename="hovmoller.pdf",
    transform_first=False,
    cyclic_lon=True,
    display=True,
    return_fig=False,
    loglevel="WARNING",
    **kwargs,
):
    logger = log_configure(loglevel, "plot_multi_hovmoller")
    ConfigStyle(style=style, loglevel=loglevel)

    if maps is None or any(not isinstance(data_map, xr.DataArray)
                           for data_map in maps):
        raise ValueError("Maps should be a list of xarray.DataArray")
    else:
        logger.debug("Loading maps")
        maps = [data_map.load(keep_attrs=True) for data_map in maps]

    # Generate the figure
    nrows, ncols = plot_box(len(maps))
    figsize = figsize if figsize is not None else (ncols * 6, nrows * 5 + 1)
    logger.debug("Creating a %d x %d grid with figsize %s", nrows, ncols,
                 figsize)

    fig = plt.figure(figsize=figsize)

    # Evaluate min and max values for the common colorbar
    if vmin is None or vmax is None or sym:
        vmin, vmax = evaluate_colorbar_limits(maps=maps, sym=sym)

    for i in range(len(maps)):
        logger.debug("Plotting map %d", i)
        # if variables is not None:
        #     maps[i] = maps[i][variables]
        fig, ax = plot_hovmoller(data=maps[i],
                                 invert_axis=False,
                                 invert_time=False,
                                 sym=sym,
                                 contour=contour,
                                 save=save,
                                 dim="lon",
                                 vmin=vmin,
                                 vmax=vmax,
                                 cmap=cmap,
                                 nlevels=nlevels,
                                 cbar_label=cbar_label,
                                 return_fig=True,
                                 ax_pos=(nrows, ncols, i + 1),
                                 fig=fig)

    # Adjust the location of the subplots on the page to make room for the colorbar
    fig.subplots_adjust(bottom=0.25,
                        top=0.9,
                        left=0.05,
                        right=0.95,
                        wspace=0.1,
                        hspace=0.5)

    # Add a colorbar axis at the bottom of the graph
    cbar_ax = fig.add_axes([0.2, 0.15, 0.6, 0.03])

    cbar_label = cbar_get_label(data=maps[0],
                                cbar_label=cbar_label,
                                loglevel=loglevel)
    logger.debug("Setting colorbar label to %s", cbar_label)

    mappable = ax.collections[0]

    # Add the colorbar
    cbar = fig.colorbar(mappable,
                        cax=cbar_ax,
                        orientation="horizontal",
                        label=cbar_label)

    # Make the colorbar ticks symmetrical if sym=True
    if sym:
        logger.debug("Setting colorbar ticks to be symmetrical")
        cbar.set_ticks(np.linspace(-vmax, vmax, nlevels + 1))
    else:
        cbar.set_ticks(np.linspace(vmin, vmax, nlevels + 1))

    # Add a super title
    if title:
        logger.debug("Setting super title to %s", title)
        fig.suptitle(title, fontsize=16)

    if return_fig:
        return fig
