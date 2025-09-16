import os
import gc
import sys
import numpy as np
import pandas as pd
import xarray as xr
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from aqua import Reader
from aqua.exceptions import NotEnoughDataError, NoDataError, NoObservationError
from aqua.util import create_folder, coord_names, area_selection
from aqua.util import get_projection
from aqua import Reader, plot_single_map
from aqua.logger import log_configure


class sshVariabilityPlot(PlotBaseMixin):
    def __init__(
        self, 
        var=None,
        catalog=None, 
        model=None,
        exp=None,
        source=None,
        ref_catalog=None, 
        ref_model=None, 
        ref_exp=None, 
        ref_source=None,
        short_name=None,
        long_name=None,
        region=None,
        outputdir='./', 
        loglevel='WARNING', 
        **kwargs,
    ):
        """
        Initialize the sshVariability.

        Args:
            var (str): Variable name
            data_ref: xarray.Dataset of the obeservational data
            data_model: xarray.Dataset of the model data
            name_ref (str): Name of the observational data
            name_model (str): Name of the model data
            exp_ref (str): Name of the obervational experiment
            exp_model (str): Name of the model experiment
            region (str): Name of the region
            outputdir (str): output directory
            loglevel (str): Default WARNING
        """
        self.var = var
        self.outputdir = outputdir
        
        super().__init__(
            log_level=self.log_level
            catalog = catalog
            model = model
            exp = exp
            ref_catalog = ref_catalog
            ref_model = ref_model
            ref_exp = ref_exp
            region = region
            short_name = short_name
            long_name = long_name
            units = units
        )

    def plot_std(
        self, 
        data_std=None, 
        model=None, 
        exp=None, 
        source=None, 
        startdate=None, 
        enddate=None, 
        contours=21,
        plot_options={},
        vmin=None,
        vmax=None,
        proj='robinson', 
        proj_params={}
        save_png=True,
        save_pdf=True,
        dpi=300,
        region=None,
        lon_lim=None,
        lat_lim=None,
        # Retrieve the masking flags and boundary latitudes from the configuration, Specific to ICON
        mask_options={},
        mask_northern_boundary=True
        mask_southern_boundary=True
        northern_boundary_latitude=70
        southern_boundary_latitude=-62
    ):
        """
        Visualize the SSH variability using Cartopy.

        Args:
            data_std: xarray.Dataset as input to be plotted.
            The following Args are used for the title in the plot
            model_name (str): Name of the Dataset.
            exp_name (str): Name of the experiment.
            source (str): source defined in the catalog file
            startdate (str): start date
            enddate (str): end date
            contours (int): Number of contours for plot (default: 21). If 0 or None the pcolormesh is used.
        """
        # STD plot
        if isinstance(dataset_std, xr.Dataset):
            dataset_std = dataset_std[self.var]
        else:
            dataset_std = dataset_std

        self.logger.info(f'Plotting SSH Variability for {model} and {exp}, from {startdate} to {enddate}.')
        
        title = (f"SSH Variability of {dataset_std[self.var].attrs.get('long_name', self.var)} for {model} {exp} from {startdate} to {enddate} ")
        
        #TODO: discuss what should be in the description
        description = (f"SSH Variability of {dataset_std[self.var].attrs.get('long_name', self.var)} for {model} {exp} from {startdate} to {enddate} ")
        
        if vmin is None:
            vmin = dataset_std.values.min()
        if vmax_std is None:
            vmax_std = dataset_std.values.max()

        if region is not None:
            title = title + "{region} "
            description = description + "{description} "
            dataset_std = self.subregion_selection(
                data=dataset_std, 
                model=model, 
                exp=exp, 
                mask_northern_boundary=mask_northern_boundary,
                northern_boundary_latitude=northern_boundary_latitude,
                mask_southern_boundary=mask_southern_boundary,
                southern_boundary_latitude=southern_boundary_latitude,
                lon_lim=lon_lim,
                lat_lim=lat_lim,
                region=region)
   
        startdate = startdate or pd.to_datetime(data_std.time[0].values).strftime('%Y-%m-%d')
        enddate = enddate or pd.to_datetime(data_std.time[-1].values).strftime('%Y-%m-%d')
        proj = get_projection(proj, **proj_params)
        
        if vmin_std == vmax_std:
            # TODO: discuss what should do here in this case.
            self.logger.info("STD is Zero everywhere") 
            fig, ax = plot_single_map(
                data[self.var],
                return_fig=True,
                title=title,
                proj=proj,
                loglevel=self.loglevel,
                cbar_label=cbar_label
            )
        else:
            fig, ax = plot_single_map(
                data[self.var],
                return_fig=True,
                title=title,
                vmin=vmin,
                vmax=vmax,
                proj=proj,
                loglevel=self.loglevel,
                cbar_label=cbar_label
            )
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")

        # Saving plots
        if save_png:
            self.save_plot(var=self.var, fig=fig, region=region, description=description, rebuild=rebuild, outputdir=outputdir, format='png', dpi=dpi)
        if save_pdf:
            self.save_plot(var=self.var, fig=fig, region=region, description=description, rebuild=rebuild, outputdir=outputdir, format='pdf', dpi=dpi)

        return fig1, ax1

    def plot_std_diff(self, contours=21):
        """
        Visualize the difference in SSH variability data between each model and the AVISO model.

        Args:
            contours (int): Number of contours for plot (default: 21). If 0 or None the pcolormesh is used.
        """
        self.logger.info(f'Plotting the difference in std between: {self.name_model} and {self.name_ref}.')
        fig, ax = plt.subplots(figsize=(12, 6), subplot_kw={'projection': ccrs.PlateCarree()})
        #to remove large fill values
        data_ref = xr.where(self.data_ref < 100, self.data_ref, np.nan)
        if self.data_ref is not None and self.data_model is not None:
            #to remove large fill values
            data_ref = xr.where(self.data_ref < 100, self.data_ref, np.nan)
            diff_data = data_ref - self.data_model
        else:
            raise ValueError("Data is missing for for plotting the difference std plot")

        if "ICON" in self.name_model:
            if self.mask_northern_boundary and self.northern_boundary_latitude:
                diff_data = diff_data.where(data.lat < self.northern_boundary_latitude)
            if self.mask_southern_boundary and self.southern_boundary_latitude:
                diff_data = diff_data.where(data.lat > self.southern_boundary_latitude)

        lonname, latname = coord_names(self.data_model)

        if contours:
            lon, lat = np.meshgrid(self.data_model[lonname].values, self.data_model[latname].values)
            levels = np.linspace(-0.4, 0.4, contours)

            contf = ax.contourf(lon, lat, diff_data, transform=ccrs.PlateCarree(), 
                                levels=levels, extend='both',
                                cmap='RdBu', transform_first=True)
        else:
            contf = ax.pcolormesh(self.data_model[lonname], self.data_model[latname], diff_data,
                                transform=ccrs.PlateCarree(),
                                vmin=-0.4,
                                vmax=0.4,
                                cmap="RdBu")

        # ax.set_title(f"{model_name} - Difference from {ref_model_name}")
        ax.coastlines()
        ax.set_title(f"{self.name_model} - Difference from {self.name_ref}")
        # Add a colorbar for each subplot
        cbar = fig.colorbar(contf, ax=ax, orientation='vertical', shrink=0.9)
        cbar.set_label('SSH Variability Difference (m)')
        fig.tight_layout()
        filename = "difference_plot_" + self.name_model + "-" + self.name_ref
        self.save_plot(filename, fig)

    def subregion_selection(
        self,
        data=None, 
        model=None, 
        exp=None,
        mask_northern_boundary=None,
        northern_boundary_latitude=None,
        mask_southern_boundary=None,
        southern_boundary_latitude=None,
        lon_lim=None,
        lat_lim=None,
        region_name=None
    ):
        """
        Plotting the subregion and saving as pdf and png
        """
        self.logger.info(f'Plotting the sub-region plots: {region_name}.')
        # Apply masking if necessary
        if "ICON" in model and mask_northern_boundary and northern_boundary_latitude:
            data = data.where(data.lat < northern_boundary_latitude)
        if "ICON" in model and mask_southern_boundary and southern_boundary_latitude:
            data = data.where(data.lat > southern_boundary_latitude)
        
        return area_selection(data, lon=lon_lim, lat=lat_lim, drop=True)

