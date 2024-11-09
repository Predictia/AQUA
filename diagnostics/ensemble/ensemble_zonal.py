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


class EnsembleZonal():
    """
    A class to compute ensemble mean and standard deviation of the Zonal averages
    Make sure that the dataset has correct lev-lat dimensions.
    """
    def __init__(self, var=None, dataset=None, ensemble_dimension_name="Ensembles", loglevel='WARNING'):
        """
        Args:
            var (str): Variable name.
            dataset: xarray Dataset composed of ensembles 2D Zonal data, i.e., 
                     the individual Dataset (lev-lat) are concatenated along.
                     a new dimension "Ensemble". This Ensemble name can be changed.
            ensemble_dimension_name="Ensembles" (str): a default name given to the 
                     dimensions along with the individual Datasets were concatenated.
            loglevel (str): Log level. Default is "WARNING".
        """
        self.loglevel = loglevel
        self.logger = log_configure(log_level=self.loglevel, log_name='Multi-model Ensemble')

        self.var = var
        self.dataset = dataset
        # if self.dataset != None: self.units = self.dataset[self.var].units
        self.dim = ensemble_dimension_name
        self.plot_std = True
        self.figure_size = [15, 15]
        self.plot_label = True
        self.outdir = './'
        self.outfile = None
        self.pdf_save = True
        self.mean_plot_title = 'Ensemble mean of zonal average of '+self.var
        self.std_plot_title = 'Ensemble standard deviation of zonal average of '+self.var
        self.cbar_label = self.var

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
        # projection = ccrs.PlateCarree()
        cmap = 'RdBu_r'
        var = self.var
        if self.dataset_mean.sizes != 0:
            if isinstance(self.dataset_mean,xr.Dataset):
                dataset_mean = self.dataset_mean[var]
            else:
                dataset_mean = self.dataset_mean
 
            fig0 = plt.figure(figsize=(self.figure_size[0], self.figure_size[1]))
            if self.outfile is None:
                self.outfile = f'multimodel_zonal_average_{var}'
            ax0 = fig0.add_subplot(111)
            im = ax0.contourf(dataset_mean.lat,dataset_mean.lev,dataset_mean,cmap=cmap, levels=20, extend='both')
            ax0.set_ylim((5500, 0))
            ax0.set_ylabel("Depth (in m)", fontsize=9)
            ax0.set_xlabel("Latitude (in deg North)", fontsize=9)
            ax0.set_facecolor('grey')
            ax0.set_title(self.mean_plot_title)
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
            if isinstance(self.dataset_std,xr.Dataset):
                dataset_std = self.dataset_std[var]
            else:
                dataset_std = self.dataset_std
 
            fig1 = plt.figure(figsize=(self.figure_size[0], self.figure_size[1]))
            if self.outfile is None:
                self.outfile = f'multimodel_zonal_average_{var}'
            ax1 = fig1.add_subplot(111)
            #im = self.dataset_std[var].contourf(ax=ax1, cmap=cmap, levels=20, extend='both')
            im = ax1.contourf(dataset_std.lat,dataset_std.lev,dataset_std,cmap=cmap,levels=20,extend='both')
            ax1.set_ylim((5500, 0))
            ax1.set_ylabel("Depth (in m)", fontsize=9)
            ax1.set_xlabel("Latitude (in deg North)", fontsize=9)
            ax1.set_facecolor('grey')
            ax1.set_title(self.std_plot_title)
            cbar = fig1.colorbar(im, ax=ax1, shrink=0.4, extend='both')
            cbar.set_label(self.cbar_label)
            self.logger.info("Saving ensemble std map to pdf")
            outfig = os.path.join(self.outdir, 'std_pdf')
            self.logger.debug(f"Saving figure to {outfig}")
            create_folder(outfig, self.loglevel)
            outfile = self.outfile + '_std.pdf'
            self.logger.debug(f"Outfile: {outfile}")
            fig1.savefig(os.path.join(outfig, outfile))

    def run(self):
        self.compute()
        self.edit_attributes()
        self.plot()
