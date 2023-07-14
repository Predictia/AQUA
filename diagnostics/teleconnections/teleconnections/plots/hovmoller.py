'''
This module contains simple functions for hovmoller plots.
Their main purpose is to provide a simple interface for plotting
hovmoller diagrams with xarray DataArrays.
'''
import os

import xarray as xr
import matplotlib.pyplot as plt

from aqua.logger import log_configure


def hovmoller_plot(data: xr.DataArray, invert_axis=False,
                   contour=True, save=False, **kwargs):
    """"
    Args:
        data (DataArray):       DataArray to be plot
        invert_axis (bool,opt): enable or disable axis inversion,
                                default is False
        contour (bool,opt):     True for contour plot, False for pcolormesh,
                                default is True
        save (bool,opt):        save the figure, default is False
        **kwargs:               additional arguments

    Kwargs:
        loglevel (str,opt):     log level for the logger,
                                default is 'WARNING'
        dim (str,opt):          dimension to be averaged over,
                                default is 'lon'
        figsize (tuple,opt):    figure size, default is (11, 8.5)
        levels (int,opt):       number of contour levels, default is 8
        cbar_label (str,opt):   colorbar label, default is None
        outputdir (str,opt):    output directory, default is '.'
        filename (str,opt):     output filename, default is 'hovmoller.png'
    """
    loglevel = kwargs.pop('loglevel', 'WARNING')
    logger = log_configure(log_level=loglevel, log_name='Hovmoller')

    logger.debug('Plotting Hovmoller diagram')

    # Check if data is a DataArray
    if not isinstance(data, xr.DataArray):
        logger.error('Data is not a DataArray')
        raise TypeError('Data is not a DataArray')

    # Evalueate the mean over the dimension to be averaged over
    dim = kwargs.get('dim', 'lon')
    data_mean = data.mean(dim=dim, keep_attrs=True)

    # Create figure and axes
    figsize = kwargs.get('figsize', (11, 8.5))
    fig, ax = plt.subplots(figsize=figsize)

    # Plot the data
    if invert_axis:
        x = data_mean.coords[data_mean.dims[-1]]
        y = data_mean.coords['time']
    else:
        x = data_mean.coords['time']
        y = data_mean.coords[data_mean.dims[-1]]

    if contour:
        levels = kwargs.get('levels', 8)
        if invert_axis:
            im = ax.contourf(x, y, data_mean, levels=levels)
        else:
            im = ax.contourf(x, y, data_mean.T, levels=levels)
    else:  # pcolormesh
        if invert_axis:
            im = ax.pcolormesh(x, y, data_mean)
        else:
            im = ax.pcolormesh(x, y, data_mean.T)

    cbar_label = kwargs.get('cbar_label')
    cbar = fig.colorbar(im, ax=ax)
    if cbar_label:
        cbar.set_label(cbar_label)

    # Save the figure
    if save is True:
        outputdir = kwargs.get('outputdir', '.')

        # check the outputdir exists and create it if necessary
        if not os.path.exists(outputdir):
            logger.info('Creating output directory {}'.format(outputdir))
            os.makedirs(outputdir)
        try:
            filename = kwargs.get('filename')
        except ValueError:
            try:
                model = kwargs.get('model')
                exp = kwargs.get('exp')
                filename = model + '_' + exp + '.pdf'
            except ValueError:
                filename = 'hovmoller.pdf'

        logger.info('Saving figure to {}/{}'.format(outputdir, filename))
        fig.savefig('{}/{}'.format(outputdir, filename), format='pdf',
                    dpi=300, bbox_inches='tight')
