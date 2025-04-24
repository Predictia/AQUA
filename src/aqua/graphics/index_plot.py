"""
This module contains simple function for index plotting.
"""
import xarray as xr
import matplotlib.pyplot as plt
from aqua.logger import log_configure
from .styles import ConfigStyle

def index_plot(index: xr.DataArray, thresh: float = 0,
               fig: plt.Figure = None, ax: plt.Axes = None,
               style=None, figsize: tuple = (11, 8.5),
               title: str = None, ylim: tuple = None,
               ylabel: str = None,
               loglevel='WARNING', **kwargs):
    """
    Index plot together with a black line at index=0.
    Values above thresh are filled in red, values below thresh are filled in blue.

    Args:
        index (DataArray):     Index DataArray
        thresh (float,opt):    Threshold for the index, default is 0
        fig (Figure,opt):      Figure object
        ax (Axes,opt):         Axes object
        style (str, optional): Style to use. Defaults to None (aqua style).
        figsize (tuple,opt):   Figure size, default is (11, 8.5)
        title (str,opt):       Title for the plot. Default is None
        ylim (tuple,opt):      y-axis limits. Default is None
        ylabel (str,opt):      y-axis label. Default is None
        loglevel (str,opt):    Loglevel for the logger. Default is 'WARNING'
        **kwargs:              Additional arguments

    Returns:
        fig, ax: Figure and Axes objects
    """
    logger = log_configure(loglevel, 'Index plot')
    ConfigStyle(style=style, loglevel=loglevel)

    logger.debug('Loading data in memory')
    index = index.load()

    if fig is None:
        fig = plt.figure(figsize=figsize)
    if ax is None:
        ax = fig.add_subplot(111)

    if ylim is not None:
        ax.set_ylim(ylim)

    # Plot the index
    ax.fill_between(index.time, index.values, where=index.values >= thresh,
                        alpha=0.6, color='red', interpolate=True)
    ax.fill_between(index.time, index.values, where=index.values < thresh,
                        alpha=0.6, color='blue', interpolate=True)
    index.plot(ax=ax, color='black', alpha=0.8)

    ax.hlines(y=0, xmin=min(index['time']), xmax=max(index['time']),
              color='black')

    if title is not None:
        ax.set_title(title)
        logger.debug("Title set to %s", title)

    # Set the ylabel
    if ylabel is not None:
        ax.set_ylabel(ylabel)
    else:
        ax.set_ylabel('Index')

    return fig, ax


def indexes_plot(index1: xr.DataArray, index2: xr.DataArray, thresh: float = 0,
                 style=None, figsize: tuple = (11, 8.5),
                 titles: list = None, suptitle: str = None,
                 ylabel: str = None, loglevel='WARNING'):
    """
    Use the plot_index function to plot two indexes in two
    subplots.

    Args:
        index1 (DataArray):    First index DataArray
        index2 (DataArray):    Second index DataArray
        thresh (float,opt):     Threshold for the index, default is 0
        style (str, optional):  Style to use. Defaults to None (aqua style).
        figsize (tuple,opt):    Figure size, default is (11, 8.5)
        titles (list,opt):      List of two strings for the titles of the plots.
                                Default is None
        suptitle (str,opt):     Title for the figure. Default is None
        ylabel (str,opt):       y-axis label. Default is None
        loglevel (str,opt):     Loglevel for the logger. Default is 'WARNING'

    Returns:
        fig: Figure object
    """
    logger = log_configure(loglevel, 'Indexes plot')

    fig, axs = plt.subplots(2, 1, figsize=figsize)

    # Evaluating a common ylim:
    ymin = min(index1.min().values, index2.min().values)
    ymax = max(index1.max().values, index2.max().values)
    ylim = [ymin, ymax]

    logger.debug('Plotting the first index')
    fig, axs[0] = index_plot(index1, loglevel=loglevel,
                             fig=fig, ax=axs[0],
                             title=titles[0], ylim=ylim)
    logger.debug('Plotting the second index')
    fig, axs[1] = index_plot(index2, loglevel=loglevel,
                             fig=fig, ax=axs[1],
                             title=titles[1], ylim=ylim)

    if suptitle is not None:
        fig.suptitle(suptitle)

    fig.tight_layout()

    return fig
