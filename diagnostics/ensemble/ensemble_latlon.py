import os
import gc

import xarray as xr
import numpy as np
from aqua import Reader
from aqua.logger import log_configure
from aqua.exceptions import NoObservationError, NoDataError
from aqua.util import create_folder
from aqua.util import add_pdf_metadata, time_to_string
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.gridspec as gridspec
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
xr.set_options(keep_attrs=True)


class EnsembleLatLon():
    """
    A class to compute ensemble mean and standard deviation of a 2D (lon-lat) Dataset.
    Make sure that the dataset has correct lon-lat dimensions.
    """
    def __init__(self, var=None, dataset=None, ensemble_dimension_name="Ensembles", loglevel='WARNING'):
        """
        Args:
            var (str): Variable name.
            dataset: xarray Dataset composed of ensembles 2D lon-lat data, i.e., 
                     the individual Dataset (lon-lat) are concatenated along.
                     a new dimension "Ensemble". This Ensemble name can be changed.
            ensemble_dimension_name="Ensembles" (str): a default name given to the 
                     dimensions along with the individual Datasets were concatenated.
            loglevel (str): Log level. Default is "WARNING".
        """
        self.loglevel = loglevel
        self.logger = log_configure(log_level=self.loglevel, log_name='Multi-model Ensemble')

        self.var = var
        self.dataset = dataset
        if self.dataset != None:
            self.units = self.dataset[self.var].units
        self.dim = ensemble_dimension_name
        self.plot_std = True
        self.figure_size = [15, 15]
        self.plot_label = True
        self.outdir = './'
        self.outfile = None
        self.pdf_save = True
        self.mean_plot_title = 'Map of '+self.var[0]+' for Ensemble mean'
        self.std_plot_title = 'Map of '+self.var[0]+' for Ensemble standard deviation'
        self.cbar_label = self.var[0]+' in '+self.units

        if self.pdf_save is False:
            self.logger.info("Figure will not be saved")
        self.dataset_mean = None
        self.dataset_std = None

    def compute(self):
        """
        A function to compute the mean and standard devivation of the input dataset
        It is import to make sure that the dim along which the mean is compute is correct.
        The default dim="Ensembles". This can be reassianged with the method "edit_attributes".
        """
        if self.dataset != None:
            self.dataset_mean = self.dataset.mean(dim=self.dim)
            self.dataset_std = self.dataset.std(dim=self.dim)

    def edit_attributes(self, **kwargs):
        """
        This method helps edit the default attributes. 
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                print(f"Attribute '{key}' does not exist.")

    def plot(self):
        """
        This plots the ensemble mean and standard deviation of the ensemble statistics.
        To edit the default settings please call the method "edit_attributes"
        """
        self.logger.info('Plotting the ensemble computation')
        projection = ccrs.PlateCarree()
        cmap = 'RdBu_r'
        var = self.var[0]
        if self.dataset_mean.sizes != 0:
            fig0 = plt.figure(figsize=(self.figure_size[0], self.figure_size[1]))
            levels = np.linspace(self.dataset_mean[var].values.min(), self.dataset_mean[var].values.max(), num=21)
            if self.outfile is None:
                self.outfile = f'multimodel_global_2D_map_{var}'
            gs = gridspec.GridSpec(1, 1, figure=fig0)
            ax0 = fig0.add_subplot(gs[0, :], projection=projection)
            ax0.coastlines()
            ax0.add_feature(cfeature.LAND, facecolor='lightgray')
            ax0.add_feature(cfeature.OCEAN, facecolor='lightblue')
            ax0.xaxis.set_major_formatter(LongitudeFormatter())
            ax0.yaxis.set_major_formatter(LatitudeFormatter())
            ax0.gridlines(draw_labels=True)
            im = ax0.contourf(self.dataset_mean.lon, self.dataset_mean.lat,
                              self.dataset_mean[var], cmap=cmap, levels=levels, extend='both')
            ax0.set_title(self.mean_plot_title)
            ax0.set_xlabel('Longitude')
            ax0.set_ylabel('Latitude')
            cbar = fig0.colorbar(im, ax=ax0, shrink=0.4, extend='both')
            cbar.set_label(self.cbar_label)
            self.logger.info("Saving ensemble mean map to pdf")
            outfig = os.path.join(self.outdir, 'mean_pdf')
            self.logger.debug(f"Saving figure to {outfig}")
            create_folder(outfig, self.loglevel)
            outfile = self.outfile + '_mean.pdf'
            self.logger.debug(f"Outfile: {outfile}")
            fig0.savefig(os.path.join(outfig, outfile))

        if self.dataset_std.sizes != 0:
            fig1 = plt.figure(figsize=(self.figure_size[0], self.figure_size[1]))
            levels = np.linspace(self.dataset_std[var].values.min(), self.dataset_std[var].values.max(), num=21)
            gs = gridspec.GridSpec(1, 1, figure=fig1)
            ax1 = fig1.add_subplot(gs[0, :], projection=projection)
            ax1.coastlines()
            ax1.add_feature(cfeature.LAND, facecolor='lightgray')
            ax1.add_feature(cfeature.OCEAN, facecolor='lightblue')
            ax1.xaxis.set_major_formatter(LongitudeFormatter())
            ax1.yaxis.set_major_formatter(LatitudeFormatter())
            ax1.gridlines(draw_labels=True)
            im = ax1.contourf(self.dataset_std.lon, self.dataset_std.lat,
                              self.dataset_std[var], cmap=cmap, levels=levels, extend='both')
            ax1.set_title(self.std_plot_title)
            ax1.set_xlabel('Longitude')
            ax1.set_ylabel('Latitude')
            cbar = fig1.colorbar(im, ax=ax1, shrink=0.4, extend='both')
            cbar.set_label(self.cbar_label)
            self.logger.info("Saving ensemble std map to pdf")
            outfig = os.path.join(self.outdir, 'std_pdf')
            self.logger.debug(f"Saving figure to {outfig}")
            create_folder(outfig, self.loglevel)
            outfile = self.outfile + '_std.pdf'
            self.logger.debug(f"Outfile: {outfile}")
            fig1.savefig(os.path.join(outfig, outfile))
            self.logger.debug(f"Outfile: {outfile}")
            fig1.savefig(os.path.join(outfig, outfile))

    def run(self):
        self.compute()
        self.edit_attributes()
        self.plot()
