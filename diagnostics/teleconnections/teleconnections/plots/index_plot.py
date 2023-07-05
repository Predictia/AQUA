"""
This module contains simple function for index plotting.
"""

import os

import matplotlib.pyplot as plt

from aqua.logger import log_configure
from teleconnections.plots import set_layout


def index_plot(indx, save=False, outputdir='./', filename='index.png',
               step=False, loglevel='WARNING', **kwargs):
    """
    Index plot together with a black line at indx=0

    Args:
        indx (DataArray): Index DataArray
        save (bool,opt):        enable or disable saving the plot,
                                default is False
        outputdir (str,opt):    directory to save the plot,
                                default is './'
        filename (str,opt):     filename for the plot
                                default is 'index.png'
        step (bool,opt):        enable or disable step plot,
                                default is False
        loglevel (str,opt):     log level for the logger,
                                default is 'WARNING'
        **kwargs:               additional arguments for set_layout

    Returns:
        fig (Figure):           Figure object
        ax (Axes):              Axes object
    """
    # 0. -- Configure the logger --
    logger = log_configure(loglevel, 'index_plot')

    # 1. -- Generate the figure --
    fig, ax = plt.subplots(figsize=(12, 8))

    # 2. -- Plot the index --
    if step:
        logger.warning('Step plot has some issues with fill_between')
        logger.warning('Steps are not filled if a change in sign occurs')

        plt.fill_between(indx.time, indx.values, where=indx.values >= 0,
                         step="pre", alpha=0.6, color='red')
        plt.fill_between(indx.time, indx.values, where=indx.values < 0,
                         step="pre", alpha=0.6, color='blue')
        indx.plot.step(ax=ax, color='black', alpha=0.8)
    else:
        plt.fill_between(indx.time, indx.values, where=indx.values >= 0,
                         alpha=0.6, color='red', interpolate=True)
        plt.fill_between(indx.time, indx.values, where=indx.values < 0,
                         alpha=0.6, color='blue', interpolate=True)
        indx.plot(ax=ax, color='black', alpha=0.8)

    ax.hlines(y=0, xmin=min(indx['time']), xmax=max(indx['time']),
              color='black')

    # 3. -- Set the layout --
    set_layout(fig, ax, **kwargs)

    # 4. -- Save the figure --
    if save:
        filepath = os.path.join(outputdir, filename)
        fig.savefig(filepath)
        logger.info('Figure saved in ' + filepath)

    return fig, ax
