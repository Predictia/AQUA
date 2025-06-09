import os
from collections import Counter
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import xarray as xr
# from dask import compute
from aqua.graphics import plot_timeseries, plot_single_map
from aqua.logger import log_configure
from aqua.util import create_folder

xr.set_options(keep_attrs=True)

class EnsembleTimeseries:
    """
    This class computes mean and standard deviation of the ensemble.mulit-model ensemble.
    This also plots ensemble mean and standard deviation.
    """

    def __init__(
        self,
        var=None,
        mon_model_dataset=None,
        ann_model_dataset=None,
        mon_ref_data=None,
        ann_ref_data=None,
        ensemble_dimension_name="ensemble",
        outputdir="./",
        loglevel="WARNING",
        **kwargs,
    ):
        """
        Args:
            var (str): Variable name.
            mon_model_dataset: xarray Dataset of ensemble members of monthly timeseries.
                     The ensemble memebers are concatenated along a new dimension "ensemble".
                     This can be editted with the function edit_attributes.
            ann_model_dataset: xarray Dataset of ensemble members of annual timeseries.
                     Similarly, the members are concatenated along the dimension "ensemble"
            ensemble_dimension_name="ensemble" (str): a default name given to the
                     dimensions along with the individual Datasets were concatenated.
            mon_ref_data: xarray Dataset of monthly reference data.
            ann_ref_data: xarray Dataset of annual reference data.
            outputdir (str): String input for output path.
            loglevel (str): Log level. Default is "WARNING".
            **kwargs (dict): dictonary contains options for plots. Defaults values have been set already.
        """
        self.loglevel = loglevel
        self.logger = log_configure(log_level=self.loglevel, log_name="Ensemble Timeseries")
        self.var = var
        self.dim = ensemble_dimension_name
        self.mon_model_dataset = mon_model_dataset
        self.ann_model_dataset = ann_model_dataset
        self.mon_ref_data = mon_ref_data
        self.ann_ref_data = ann_ref_data
        self.mon_dataset_mean = None
        self.mon_dataset_std = None
        self.ann_dataset_mean = None
        self.ann_dataset_std = None
        self.outputdir = outputdir + "Ensemble_Timeseries"
        self.outfile = f"ensemble_time_series_timeseries_{self.var}"

        self.figure = None
        plot_options = kwargs.get("plot_options", {})
        self.plot_label = plot_options.get("plot_label", True)
        self.plot_std = plot_options.get("plot_std", True)
        self.plot_ensemble_members = plot_options.get("plot_ensemble_members", True)
        self.plot_ref = plot_options.get("plot_ref", True)
        self.figure_size = plot_options.get("figure_size", [10, 5])
        #self.label_size = plot_options.get("label_size", 7.5)
        self.ensemble_label = plot_options.get("ensemble_label", "Ensemble")
        self.ref_label = plot_options.get("ref_label", "ERA5")
        self.plot_title = plot_options.get("plot_title", "Ensemble statistics for " + self.var)
        #self.label_ncol = plot_options.get("label_ncol", 3)
        #self.units = plot_options.get("units", None)  # TODO

    def compute_statistics(self):
        """
        A function to compute the mean and standard devivation of the input dataset
        It is import to make sure that the dim along which the mean is compute is correct.
        The default dim="ensemble". The DASK's .compute() function is also used here.
        """
       
        if self.model_list is not None and self.mon_model_dataset is not None:
            pass # <---- HERE
        else:
            if self.mon_model_dataset is not None:
                self.mon_dataset_mean = self.mon_model_dataset[self.var].mean(dim=self.dim)
                self.mon_dataset_std = self.mon_model_dataset[self.var].std(dim=self.dim)

            if self.ann_model_dataset is not None:
                self.ann_dataset_mean = self.ann_model_dataset[self.var].mean(dim=self.dim)
                self.ann_dataset_std = self.ann_model_dataset[self.var].std(dim=self.dim)

        # TODO: Does it make sence to apply DASK's .compute() here?
        # if self.mon_model_dataset != None:
        #    self.mon_dataset_mean = self.mon_model_dataset[self.var].mean(dim=self.dim).compute()
        # if self.ann_model_dataset != None:
        #    self.ann_dataset_mean = self.ann_model_dataset[self.var].mean(dim=self.dim).compute()

        # if self.mon_model_dataset != None:
        #    self.mon_dataset_std = self.mon_model_dataset[self.var].std(dim=self.dim).compute()
        # if self.ann_model_dataset != None:
        #    self.ann_dataset_std = self.ann_model_dataset[self.var].std(dim=self.dim).compute()

    def plot(self):
        """
        This plots the ensemble mean and +/- 2 x standard deviation of the ensemble statistics
        around the ensemble mean.
        In this method, it is also possible to plot the individual ensemble members.
        It does not plots +/- 2 x STD for the referene. 
        
        Returns:
            fig, ax
        """
        self.logger.info("Plotting the ensemble timeseries")

        fig, ax = plot_timeseries( 
            ref_monthly_data=self.mon_ref_data, 
            ref_annual_data=self.ann_ref_data, 
            ens_monthly_data=self.mon_dataset_mean, 
            ens_annual_data=self.ann_dataset_mean, 
            std_ens_monthly_data=self.mon_dataset_std, 
            std_ens_annual_data=self.ann_dataset_std,
            ref_label=self.ref_label,
            ens_label=self.ensemble_label,
            figsize=self.figure_size,
            title=self.plot_title,
            loglevel=self.loglevel,
        )
        # Loop over if need to plot the ensemble members
        if self.plot_ensemble_members:
            for i in range(0, len(self.mon_model_dataset[self.var][:, 0])):
                fig1, ax1 = plot_timeseries(
                    fig=fig, ax=ax,
                    ens_monthly_data=self.mon_dataset_mean,
                    ens_annual_data=self.ann_dataset_mean,
                    monthly_data=self.mon_model_dataset[self.var][i, :], 
                    annual_data=self.ann_model_dataset[self.var][i, :],
                    figsize=self.figure_size,
                    title=self.plot_title,
                    loglevel=self.loglevel,
                )

        # Saving plots
        self.logger.info("Saving plots as png and pdf the output folder {self.outputdir}/plots")
        plots_path = os.path.join(self.outputdir, "plots")
        create_folder(plots_path, self.loglevel)
        # pdf plots
        fig.savefig(
            os.path.join(plots_path, self.outfile) + ".pdf", bbox_inches="tight", pad_inches=0.1
        )
        # pdf plots
        fig.savefig(
            os.path.join(plots_path, self.outfile) + ".png", bbox_inches="tight", pad_inches=0.1
        )
        return fig, ax

class EnsembleLatLon:
    """
    A class to compute ensemble mean and standard deviation of a 2D (lon-lat) Dataset.
    Make sure that the dataset has correct lon-lat dimensions.
    """

    def __init__(
        self,
        var=None,
        dataset=None,
        ensemble_dimension_name="ensemble",
        outputdir="./",
        loglevel="WARNING",
        **kwargs,
    ):
        """
        Args:
            var (str): Variable name.
            dataset: xarray Dataset composed of ensembles 2D lon-lat data, i.e.,
                     the individual Dataset (lon-lat) are concatenated along.
                     a new dimension "ensemble". This ensemble name can be changed.
            ensemble_dimension_name="ensemble" (str): a default name given to the
                     dimensions along with the individual Datasets were concatenated.
            outputdir (str): String input for output path.
            loglevel (str): Log level. Default is "WARNING".
            **kwargs (dict): dictonary contains options for plots. Defaults values have been set already.
        """
        self.loglevel = loglevel
        self.logger = log_configure(log_level=self.loglevel, log_name="Ensemble LatLon")

        self.var = var
        self.dataset = dataset
        self.dataset_mean = None
        self.dataset_std = None
        self.dim = ensemble_dimension_name
        self.outputdir = outputdir + "Ensemble_LatLon"
        self.outputfile = f"global_2D_map_{self.var}"

        self.figure = None
        plot_options = kwargs.get("plot_options", {})
        self.plot_label = plot_options.get("plot_label", True)
        self.plot_std = plot_options.get("plot_std", True)
        self.figure_size = plot_options.get("figure_size", [15, 15])
        self.dpi = plot_options.get("dpi", 600)
        self.draw_labels = plot_options.get("draw_labels", True)

        # TODO: mention is the config file
        # Specific for colorbars is mean and std plots
        self.vmin_mean = plot_options.get("vmin_mean", None)
        self.vmax_mean = plot_options.get("vmax_mean", None)
        self.vmin_std = plot_options.get("vmin_std", None)
        self.vmax_std = plot_options.get("vmax_std", None)

        self.proj = plot_options.get("projection", ccrs.PlateCarree())
        self.transform_first = plot_options.get("transform_first", False)
        self.cyclic_lon = plot_options.get("cyclic_lon", False)
        self.contour = plot_options.get("contour", True)
        self.coastlines = plot_options.get("coastlines", True)

        self.units = plot_options.get("units", None)
        if self.units is None:
            self.units = self.dataset[self.var].units
        self.cbar_label = plot_options.get("cbar_label", None)
        if self.cbar_label is None:
            self.cbar_label = self.var + " in " + self.units
        self.mean_plot_title = plot_options.get(
            "mean_plot_title", f"Map of {self.var} for Ensemble mean"
        )
        self.std_plot_title = plot_options.get(
            "std_plot_title", f"Map of {self.var} for Ensemble standard deviation"
        )

        # TODO: save the ensemble mean and the std values as netcdf files
        # self.netcdf_save = True

    def compute_statistics(self):
        """
        A function to compute the mean and standard devivation of the input dataset
        It is import to make sure that the dim along which the mean is compute is correct.
        The default dim="ensemble". This can be reassianged with the method "edit_attributes".
        """
        if self.dataset is not None:
            self.dataset_mean = self.dataset.mean(dim=self.dim)
            self.dataset_std = self.dataset.std(dim=self.dim)
        else:
            raise NoDataError("No data is given to the compute method")

    def plot(self):
        """
        This plots the ensemble mean and standard deviation of the ensemble statistics.
        
        Returns:
            a dict of fig and ax for mean and STD
            return {'mean_plot': [fig1, ax1], 'std_plot': [fig2, ax2]}
        """

        self.logger.info("Plotting the ensemble computation")
        if (self.dataset_mean is None) or (self.dataset_std is None):
            raise NoDataError("No data given to the plotting function")
        create_folder(self.outputdir, self.loglevel)
        outfig = os.path.join(self.outputdir, "plots")
        self.logger.debug(f"Path to output diectory for plots: {outfig}")
        create_folder(outfig, self.loglevel)

        if isinstance(self.dataset_mean, xr.Dataset):
            self.dataset_mean = self.dataset_mean[self.var]
        else:
            self.dataset_mean = self.dataset_mean
        if self.vmin_mean is None:
            self.vmin_mean = self.dataset_mean.values.min()
        if self.vmax_mean is None:
            self.vmax_mean = self.dataset_mean.values.max()
        fig1, ax1 = plot_single_map(
            self.dataset_mean,
            proj=self.proj,
            contour=self.contour,
            cyclic_lon=self.cyclic_lon,
            coastlines=self.coastlines,
            transform_first=self.transform_first,
            return_fig=True,
            title=self.mean_plot_title,
            vmin=self.vmin_mean,
            vmax=self.vmax_mean,
        )
        ax1.set_xlabel("Longitude")
        ax1.set_ylabel("Latitude")
        self.logger.debug(f"Saving 2D map of mean to {outfig}")
        # 2D mean plot in pdf
        fig1.savefig(
            os.path.join(outfig, self.var + "_LatLon_mean.pdf"),
            bbox_inches="tight",
            pad_inches=0.1,
            dpi=self.dpi,
        )
        # 2D mean plots in png
        fig1.savefig(
            os.path.join(outfig, self.var + "_LatLon_mean.png"),
            bbox_inches="tight",
            pad_inches=0.1,
            dpi=self.dpi,
        )

        if isinstance(self.dataset_std, xr.Dataset):
            self.dataset_std = self.dataset_std[self.var]
        else:
            self.dataset_std = self.dataset_std
        if self.vmin_std is None:
            self.vmin_std = self.dataset_std.values.min()
        if self.vmax_std is None:
            self.vmax_std = self.dataset_std.values.max()
        if self.vmin_std == self.vmax_std:
            self.logger.info("STD is Zero everywhere")
            return {'mean_plot': [fig1, ax1]}
        fig2, ax2 = plot_single_map(
            self.dataset_std,
            proj=self.proj,
            contour=self.contour,
            cyclic_lon=self.cyclic_lon,
            coastlines=self.coastlines,
            transform_first=self.transform_first,
            return_fig=True,
            title=self.std_plot_title,
            vmin=self.vmin_std,
            vmax=self.vmax_std,
        )
        ax2.set_xlabel("Longitude")
        ax2.set_ylabel("Latitude")
        self.logger.debug(f"Saving 2D map of STD to {outfig}")
        # 2D STD plot in pdf
        fig2.savefig(
            os.path.join(outfig, self.var + "_LatLon_STD.pdf"),
            bbox_inches="tight",
            pad_inches=0.1,
            dpi=self.dpi,
        )
        # 2D STD plots in png
        fig2.savefig(
            os.path.join(outfig, self.var + "_LatLon_STD.png"),
            bbox_inches="tight",
            pad_inches=0.1,
            dpi=self.dpi,
        )
        return {'mean_plot': [fig1, ax1], 'std_plot': [fig2, ax2]}

class EnsembleZonal:
    """
    A class to compute ensemble mean and standard deviation of the Zonal averages
    Make sure that the dataset has correct lev-lat dimensions.
    """

    def __init__(
        self,
        var=None,
        dataset=None,
        ensemble_dimension_name="ensemble",
        outputdir="./",
        loglevel="WARNING",
        **kwargs,
    ):
        """
        Args:
            var (str): Variable name.
            dataset: xarray Dataset composed of ensembles 2D Zonal data, i.e.,
                     the individual Dataset (lev-lat) are concatenated along.
                     a new dimension "ensemble". This ensemble name can be changed.
            ensemble_dimension_name="ensemble" (str): a default name given to the
                     dimensions along with the individual Datasets were concatenated.
            loglevel (str): Log level. Default is "WARNING".
            **kwargs (dict): dictonary contains options for plots. Defaults values have been set already.
        """
        self.loglevel = loglevel
        self.logger = log_configure(log_level=self.loglevel, log_name="Ensemble Zonal Averages")

        self.var = var
        self.dataset = dataset
        self.dim = ensemble_dimension_name
        self.dataset_mean = None
        self.dataset_std = None

        self.outputdir = outputdir + "Ensemble_Zonal"
        self.outputfile = f"global_Zonal_plot_{var}"

        self.figure = None
        plot_options = kwargs.get("plot_options", {})
        self.plot_label = plot_options.get("plot_label", True)
        self.plot_std = plot_options.get("plot_std", True)
        self.figure_size = plot_options.get("figure_size", [15, 15])
        self.units = plot_options.get("units", None)
        self.dpi = plot_options.get("dpi", 300)
        if self.units is None:
            self.units = self.dataset[self.var].units
        self.cbar_label = plot_options.get("cbar_label", None)
        if self.cbar_label is None:
            self.cbar_label = self.var + " in " + self.units
        self.mean_plot_title = plot_options.get(
            "mean_plot_title", f"Ensemble mean zonal average of {self.var}"
        )
        self.std_plot_title = plot_options.get(
            "std_plot_title", f"Ensemble standard deviation of zonal average of {self.var}"
        )

    def compute_statistics(self):
        """
        A function to compute the mean and standard devivation of the input dataset
        It is import to make sure that the dim along which the mean is compute is correct.
        The default dim="ensemble". This can be reassianged with the method "edit_attributes".
        """
        if self.dataset is not None:
            self.dataset_mean = self.dataset.mean(dim=self.dim)
            self.dataset_std = self.dataset.std(dim=self.dim)
        else:
            raise NoDataError("No data is given to the compute method")

    def plot(self):
        """
        This plots the ensemble mean and standard deviation of the ensemble statistics.
        To edit the default settings please call the method "edit_attributes"
        
        Returns:
            a dict of fig and ax for mean and STD
            return {'mean_plot': [fig1, ax1], 'std_plot': [fig2, ax2]}
        """

        self.logger.info(
            "Plotting the ensemble computation of Zonal-averages as mean and STD in Lev-Lon of var {self.var}"
        )

        if (self.dataset_mean is None) or (self.dataset_std is None):
            raise NoDataError("No data given to the plotting function")

        create_folder(self.outputdir, self.loglevel)
        outfig = os.path.join(self.outputdir, "plots")
        self.logger.debug(f"Path to output diectory for plots: {outfig}")
        create_folder(outfig, self.loglevel)

        if isinstance(self.dataset_mean, xr.Dataset):
            self.dataset_mean = self.dataset_mean[self.var]
        else:
            self.dataset_mean = self.dataset_mean
        self.logger.info("Plotting ensemble-mean Zonal-average")
        fig1 = plt.figure(figsize=(self.figure_size[0], self.figure_size[1]))
        ax1 = fig1.add_subplot(1, 1, 1)
        im = ax1.contourf(
            self.dataset_mean.lat,
            self.dataset_mean.lev,
            self.dataset_mean,
            cmap="RdBu_r",
            levels=20,
            extend="both",
        )
        ax1.set_ylim((5500, 0))
        ax1.set_ylabel("Depth (in m)", fontsize=9)
        ax1.set_xlabel("Latitude (in deg North)", fontsize=9)
        ax1.set_facecolor("grey")
        ax1.set_title(self.mean_plot_title)
        cbar = fig1.colorbar(im, ax=ax1, shrink=0.9, extend="both")
        cbar.set_label(self.cbar_label)
        self.logger.debug(
            f"Saving Lev-Lon Zonal-average ensemble-mean as pdf and png to {outfig}"
        )
        # Lev-Lon Zonal mean plot in pdf
        fig1.savefig(
            os.path.join(outfig, self.var + "_LevLon_mean.pdf"),
            bbox_inches="tight",
            pad_inches=0.1,
            dpi=self.dpi,
        )
        # Lev-Lon Zonal mean plot in png
        fig1.savefig(
            os.path.join(outfig, self.var + "_LevLon_mean.png"),
            bbox_inches="tight",
            pad_inches=0.1,
            dpi=self.dpi,
        )

        if isinstance(self.dataset_std, xr.Dataset):
            self.dataset_std = self.dataset_std[self.var]
        else:
            self.dataset_std = self.dataset_std
        self.logger.info("Plotting ensemble-STD Zonal-average")
        fig2 = plt.figure(figsize=(self.figure_size[0], self.figure_size[1]))
        ax2 = fig2.add_subplot(1, 1, 1)
        im = ax2.contourf(
            self.dataset_std.lat,
            self.dataset_std.lev,
            self.dataset_std,
            cmap="OrRd",
            levels=20,
            extend="both",
        )
        ax2.set_ylim((5500, 0))
        ax2.set_ylabel("Depth (in m)", fontsize=9)
        ax2.set_xlabel("Latitude (in deg North)", fontsize=9)
        ax2.set_facecolor("grey")
        ax2.set_title(self.std_plot_title)
        cbar = fig2.colorbar(im, ax=ax2, shrink=0.9, extend="both")
        cbar.set_label(self.cbar_label)
        self.logger.debug(
            f"Saving Lev-Lon Zonal-average ensemble-STD as pdf and png to {outfig}"
        )
        # Lev-Lon Zonal STD plot in pdf
        fig2.savefig(
            os.path.join(outfig, self.var + "_LevLon_STD.pdf"),
            bbox_inches="tight",
            pad_inches=0.1,
            dpi=self.dpi,
        )
        # Lev-Lon Zonal STD plot in png
        fig2.savefig(
            os.path.join(outfig, self.var + "_LevLon_STD.png"),
            bbox_inches="tight",
            pad_inches=0.1,
            dpi=self.dpi,
        )

        return {'mean_plot': [fig1, ax1], 'std_plot': [fig2, ax2]}

