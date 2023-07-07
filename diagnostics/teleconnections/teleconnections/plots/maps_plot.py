import os

import cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import matplotlib.pyplot as plt
import numpy as np

from aqua.logger import log_configure

from .plot_utils import minmax_maps, plot_box


def maps_plot(maps=None, models=None, exps=None, save=False, **kwargs):
    """
    Plot maps (regression, correlation, etc.)
    A list of xarray.DataArray objects is expected
    and a map is plotted for each of them

    Args:
        maps (list):        list of xarray.DataArray objects
        models (list):      list of models
        exps (list):        list of experiments
        save (bool, opt):   save the figure
        **kwargs:           additional arguments

    Raises:
        ValueError:         if maps is None
        ValueError:         if models or exps is None
    """
    loglevel = kwargs.get('loglevel', 'WARNING')
    logger = log_configure(loglevel, 'maps_plot')

    if maps is None:
        raise ValueError('Nothing to plot')

    if models is None:
        raise ValueError('No models provided')
    if exps is None:
        raise ValueError('No experiments provided')

    # Generate the figure
    nrows, ncols = plot_box(len(maps))
    figsize = kwargs.get('figsize', (11, 8.5))

    fig, axs = plt.subplots(nrows=nrows, ncols=ncols,
                            subplot_kw={'projection': ccrs.PlateCarree()},
                            figsize=figsize)
    axs = axs.flatten()

    # Evaluate min and max values for the common colorbar
    vmin, vmax = minmax_maps(maps)
    logger.debug('Min value for the colorbar: {}'.format(vmin))
    logger.debug('Max value for the colorbar: {}'.format(vmax))

    # Drop unused axes
    for i in range(len(axs)):
        if i >= len(maps):
            axs[i].axis('off')
            logger.debug('Dropping unused axes {}'.format(i))

    # Set the number of levels for the colorbar
    nlevels = kwargs.get('nlevels', 11)

    # Plot the maps
    for i in range(len(maps)):
        try:
            logger.info('Plotting model {} experiment {}'.format(models[i],
                                                                 exps[i]))
        except IndexError:
            logger.info('Plotting map {}'.format(i))

        # Contour plot
        cs = maps[i].plot.contourf(ax=axs[i], transform=ccrs.PlateCarree(),
                                   cmap='RdBu_r', levels=nlevels,
                                   add_colorbar=False, add_labels=False,
                                   extend='both', vmin=vmin, vmax=vmax)

        # Title
        try:
            axs[i].set_title('{} {}'.format(models[i], exps[i]))
        except IndexError:
            logger.warning('No title for map {}'.format(i))

        # Coastlines
        axs[i].coastlines()

        # Longitude labels
        axs[i].set_xticks(np.arange(-180, 181, 60), crs=ccrs.PlateCarree())
        lon_formatter = cticker.LongitudeFormatter()
        axs[i].xaxis.set_major_formatter(lon_formatter)

        # Latitude labels
        axs[i].set_yticks(np.arange(-90, 91, 30), crs=ccrs.PlateCarree())
        lat_formatter = cticker.LatitudeFormatter()
        axs[i].yaxis.set_major_formatter(lat_formatter)

    # Adjust the location of the subplots on the page to make room for the colorbar
    fig.subplots_adjust(bottom=0.25, top=0.9, left=0.05, right=0.95,
                        wspace=0.1, hspace=0.5)

    # Add a colorbar axis at the bottom of the graph
    cbar_ax = fig.add_axes([0.2, 0.15, 0.6, 0.02])

    # Add the colorbar
    fig.colorbar(cs, cax=cbar_ax, orientation='horizontal')

    # Add a super title
    fig.suptitle(kwargs.get('title', 'Maps'), fontsize=16)

    # Save the figure
    if save is True:
        outputdir = kwargs.get('outputdir', '.')
        filename = kwargs.get('filename', 'maps.png')
        logger.info('Saving figure to {}/{}'.format(outputdir, filename))
        fig.savefig('{}/{}'.format(outputdir, filename), format='pdf',
                    dpi=300, bbox_inches='tight')


def single_map_plot(map=None, save=False, **kwargs):
    """
    Plot a single map (regression, correlation, etc.)
    An xarray.DataArray objects is expected
    and a map is plotted

    Args:
        map (xarray.DataArray): xarray.DataArray object
        save (bool, opt):       save the figure
        **kwargs:               additional arguments

    Raises:
        ValueError: if no map is provided
    """
    loglevel = kwargs.get('loglevel', 'WARNING')
    logger = log_configure(loglevel, 'single_map_plot')

    if map is None:
        raise ValueError('Nothing to plot')

    model = kwargs.get('model', 'model')
    exp = kwargs.get('exp', 'exp')

    # Generate the figure
    figsize = kwargs.get('figsize', (11, 8.5))

    fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()},
                           figsize=figsize)

    # Set the number of levels for the colorbar
    nlevels = kwargs.get('nlevels', 11)

    # Plot the map
    try:
        logger.info('Plotting model {} experiment {}'.format(model, exp))
    except ValueError:
        logger.info('Plotting map')

    # Contour plot
    cs = map.plot.contourf(ax=ax, transform=ccrs.PlateCarree(),
                           cmap='RdBu_r', levels=nlevels,
                           add_colorbar=False, add_labels=False,
                           extend='both')

    # Title
    try:
        ax.set_title('{} {}'.format(model, exp))
    except ValueError:
        logger.warning('No title for map')

    # Coastlines
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

    # Add the colorbar
    fig.colorbar(cs, cax=cbar_ax, orientation='horizontal')

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
                filename = model + '_' + exp + '.pdf'
            except ValueError:
                filename = 'map.pdf'

        logger.info('Saving figure to {}/{}'.format(outputdir, filename))
        fig.savefig('{}/{}'.format(outputdir, filename), format='pdf',
                    dpi=300, bbox_inches='tight')
