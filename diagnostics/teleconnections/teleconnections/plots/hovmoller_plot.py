'''
This module contains simple functions for hovmoller plots.
Their main purpose is to provide a simple interface for plotting
hovmoller diagrams with xarray DataArrays.
'''
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

from aqua.util import create_folder
from aqua.logger import log_configure

# set default options for xarray
xr.set_options(keep_attrs=True)


def hovmoller_plot(data: xr.DataArray,
                   invert_axis=False, center=False,
                   contour=True, save=False,
                   dim='lon', figsize=(11, 8.5),
                   vmin=None, vmax=None, cmap='RdBu_r',
                   nlevels=8, cbar_label=None,
                   outputdir='.', filename='hovmoller.png',
                   loglevel: str = "WARNING"):
    """"
    Args:
        data (DataArray):       DataArray to be plot
        invert_axis (bool,opt): enable or disable axis inversion,
                                default is False
        center (bool,opt):      center the cbar around zero,
                                default is False
        contour (bool,opt):     True for contour plot, False for pcolormesh,
                                default is True
        save (bool,opt):        save the figure, default is False
        dim (str,opt):          dimension to be averaged over,
                                default is 'lon'
        figsize (tuple,opt):    figure size, default is (11, 8.5)
        vmin (float,opt):       minimum value for the colorbar
        vmax (float,opt):       maximum value for the colorbar
        cmap (str,opt):         colormap, default is 'RdBu_r'
        nlevels (int,opt):      number of contour levels, default is 8
        cbar_label (str,opt):   colorbar label, default is None
        outputdir (str,opt):    output directory, default is '.'
        filename (str,opt):     output filename, default is 'hovmoller.png'
        loglevel (str,opt):     log level for the logger,
                                default is 'WARNING'
    """
    logger = log_configure(log_level=loglevel, log_name='Hovmoller')

    # Check if data is a DataArray
    if not isinstance(data, xr.DataArray):
        raise TypeError('Data is not a DataArray')

    # Evaluate the mean over the dimension to be averaged over
    logger.info('Averaging over dimension: {}'.format(dim))
    data_mean = data.mean(dim=dim)

    # Create figure and axes
    fig, ax = plt.subplots(figsize=figsize)

    # Plot the data
    if invert_axis:
        x = data_mean.coords[data_mean.dims[-1]]
        y = data_mean.coords['time']
    else:
        x = data_mean.coords['time']
        y = data_mean.coords[data_mean.dims[-1]]

    if vmin is not None and vmax is not None:
        logger.debug('Cbar limits set by user')
    if center:
        logger.debug('Centering colorbar around zero')
        if vmin is None or vmax is None:
            logger.warning('Exploring data to find absmax, may take a while')
            absmax = max(abs(data_mean.min().values),
                         abs(data_mean.max().values))
        else:
            logger.info('Cbar limits set by user, centering around zero')
            absmax = max(abs(vmin), abs(vmax))
        vmin = -absmax
        vmax = absmax
    else:
        logger.debug('Not centering colorbar around zero')
        if vmin is None:
            vmin = data_mean.min().values
        if vmax is None:
            vmax = data_mean.max().values
    logger.debug('vmin: {}, vmax: {}'.format(vmin, vmax))

    if contour:
        try:
            levels = np.linspace(vmin, vmax, nlevels)
            if invert_axis:
                im = ax.contourf(x, y, data_mean, levels=levels, cmap=cmap,
                                 vmin=vmin, vmax=vmax)
            else:
                im = ax.contourf(x, y, data_mean.T, levels=levels, cmap=cmap,
                                 vmin=vmin, vmax=vmax)
        except TypeError as e:
            logger.warning('Could not evaluate levels: {}'.format(e))
            if invert_axis:
                im = ax.contourf(x, y, data_mean, cmap=cmap,
                                 vmin=vmin, vmax=vmax)
            else:
                im = ax.contourf(x, y, data_mean.T, cmap=cmap,
                                 vmin=vmin, vmax=vmax)
    else:  # pcolormesh
        if invert_axis:
            im = ax.pcolormesh(x, y, data_mean, cmap=cmap,
                               vmin=vmin, vmax=vmax)
        else:
            im = ax.pcolormesh(x, y, data_mean.T, cmap=cmap,
                               vmin=vmin, vmax=vmax)

    # Adjust the location of the subplots on the page to make room for the colorbar
    fig.subplots_adjust(bottom=0.25, top=0.9, left=0.05, right=0.95,
                        wspace=0.1, hspace=0.5)

    # Add a colorbar axis at the bottom of the graph
    cbar_ax = fig.add_axes([0.2, 0.15, 0.6, 0.02])

    if cbar_label is not None:
        fig.colorbar(im, cax=cbar_ax, orientation='horizontal',
                     label=cbar_label)
    else:
        try:
            fig.colorbar(im, cax=cbar_ax, orientation='horizontal',
                         label=data_mean.short_name)
        except AttributeError:
            fig.colorbar(im, cax=cbar_ax, orientation='horizontal')

    # Save the figure
    if save is True:
        create_folder(outputdir, loglevel=loglevel)

        logger.info('Saving figure to {}/{}'.format(outputdir, filename))
        fig.savefig('{}/{}'.format(outputdir, filename), format='pdf',
                    dpi=300, bbox_inches='tight')
