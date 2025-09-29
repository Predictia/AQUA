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
from .base import BaseMixin

xr.set_options(keep_attrs=True)

class sshVariabilityPlot(PlotBaseMixin):
    """
    Plot sshVariability and the difference of sshVariability
    """
    def __init__(
        self, 
        diagnostic_name=None,
        outputdir='./', 
        loglevel='WARNING', 
    ):
        """
        Initialize the sshVariability.

        Args:
            diagnostic_name (str): sshVariability
            outputdir (str): output directory
            loglevel (str): Default WARNING
        """

        self.loglevel = loglevel
        self.outputdir = outputdir

        super().__init__(
            diagnostic_name=self.diagnostic_name
            loglevel=self.loglevel
        )

    def plot(
        self,
        var=None,
        dataset_std=None,
        catalog=None, 
        model=None, 
        exp=None, 
        startdate=None, 
        enddate=None, 
        regrid=None,
        contours=21,
        plot_options={},
        vmin=None,
        vmax=None,
        proj='robinson', 
        proj_params={}
        save_png=True,
        save_pdf=True,
        dpi=600,
        region=None,
        lon_lim=None,
        lat_lim=None,
        # Retrieve the masking flags and boundary latitudes from the configuration, Specific to ICON
        mask_options={},
        mask_northern_boundary=True,
        mask_southern_boundary=True,
        northern_boundary_latitude=70,
        southern_boundary_latitude=-62,
        diagnostic_product='sshVariabililty',
        rebuild: bool = True,
        description=None,
    ):
        """
        Visualize the SSH variability.

        Args:
            data_std: xarray.Dataset as input to be plotted.
            var (str): variable name.
            The following Args are used for the title in the plot.
            catalog (str): catalog name. (Mandatory)
            model (str): Name of the Dataset. (Mandatory)
            exp (str): Name of the experiment. (Mandatory)
            startdate (str): start date to be used in the plot title
            enddate (str): end date to be used in the plot title
            contours (int): Number of contours for plot (default: 21). If 0 or None the pcolormesh is used.
            dpi (int): Default is 300.
            vmin (float): If this is 'None', choose by the function.
            vmax (float): If this is 'None', choose by the function.
            save_pdf (bool): Default is True.
            save_png (bool): Default is True.
            proj (str): Projection type. Default is 'robinson'. 
            proj_params (dict): dictionary for plot kwargs.
            region (str): The region to select. This will define the lon and lat limits.
            lon_lim (List[float]): limits of lon for plotting.
            lat_lim (List[float]): limits of lat for plotting.
            rebuild (bool): If True, rebuild the data from the original files.
        """
        
        if dataset_std is None: self.logger.error("Please provide the data to the plot function")

        if isinstance(dataset_std, xr.Dataset):
            dataset_std = dataset_std[var]
        else:
            dataset_std = dataset_std
        
        if regrid:
            dataset_std = dataset_std[var].aqua.regrid()
        if startdate is None or enddate is None: self.logger.error("Please specify the time period of the data") 

        self.logger.info(f'Plotting SSH Variability for {model} and {exp}, from {startdate} to {enddate}.')
        long_name = dataset_std[var].attrs.get('long_name', var)
        title = (f"SSH Variability of {long_name} for {model} {exp} ({startdate}-{enddate}) ")
        
        #TODO: discuss what should be in the description
        description = (f"SSH Variability of {long_name} for {model} {exp} ({startdate}-{enddate}) ")
        
        if vmin is None:
            vmin = dataset_std.values.min()
        if vmax is None:
            vmax = dataset_std.values.max()

        if region is not None:
            title = title + "{region} "
            if lon_lim is None or lat_lim is None: self.logger.error(f"For the {region}, please specify the lon_lim and lat_lim.")
            description = description + "for {region} "
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
   
        proj = get_projection(proj, **proj_params)
        
        if vmin == vmax:
            # TODO: discuss what should do here in this case.
            self.logger.info("STD is Zero everywhere") 
            fig, ax = plot_single_map(
                dataset[var],
                return_fig=True,
                title=title,
                proj=proj,
                loglevel=self.loglevel,
                cbar_label=cbar_label
            )
        else:
            fig, ax = plot_single_map(
                dataset[var],
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
            self.save_plot(
                var=var, 
                fig=fig, 
                description=description, 
                rebuild=rebuild, 
                outputdir=outputdir, 
                format='png',
                catalog=catalog,
                model=model,
                exp=exp,
                startdate=startdate,
                enddate=enddate,
                #long_name=long_name,
                #units=units,
                dpi=dpi)
        if save_pdf:
            self.save_plot(
                var=var, 
                fig=fig, 
                description=description, 
                rebuild=rebuild, 
                outputdir=outputdir, 
                format='pdf',
                catalog=catalog,
                model=model,
                exp=exp,
                startdate=startdate,
                enddate=enddate,
                #long_name=long_name,
                #units=units,
                dpi=dpi)

        return fig, ax

    def plot_diff(
        self,
        var=None 
        dataset_std=None,
        catalog=None, 
        model=None, 
        exp=None,
        startdate=None, 
        enddate=None, 
        dataset_std_ref=None,
        catalog_ref=None,
        model_ref=None,
        exp_ref=None,
        startdate_ref=None, 
        enddate_ref=None, 
        regrid=None,
        contours=21,
        plot_options={},
        vmin_diff=None,
        vmax_diff=None,
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
        
        diagnostic_product='sshVariabililty'
        description=None,
    ):
        """
        Visualize the SSH variability using Cartopy.

        Args:
            data_std: xarray.Dataset as input to be plotted.
            The following Args are used for the title in the plot
            model_name (str): Name of the Dataset.
            exp_name (str): Name of the experiment.
            startdate (str): start date
            enddate (str): end date
            contours (int): Number of contours for plot (default: 21). If 0 or None the pcolormesh is used.
        """
        
        if dataset_std is None and dataset_std_ref is None: self.logger.error("Please provide the data to the plot function")

        if isinstance(dataset_std, xr.Dataset):
            dataset_std = dataset_std[var]
        else:
            dataset_std = dataset_std

        if isinstance(dataset_std_ref, xr.Dataset):
            dataset_std_ref = dataset_std_ref[var]
        else:
            dataset_std_ref = dataset_std_ref

        if regrid:
            dataset_std = dataset_std.aqua.regrid()
            dataset_std_ref = dataset_std_ref.aqua.regrid() 

        if startdate is None or enddate is None: self.logger.error("Please specify the time period of the data") 
        if startdate_ref is None or enddate_ref is None: self.logger.error("Please specify the time period of the reference data") 
        
        title = (f"The difference of the SSH Variability of {dataset_std[var].attrs.get('long_name', var)} for {model} {exp} ({startdate}-{enddate}) and, reference {catalog_ref} {model_ref} and {exp_ref} ({startdate_ref}-{enddate_ref}) ")
        
        #TODO: discuss what should be in the description
        description = (f"The difference of the SSH Variability of {dataset_std[var].attrs.get('long_name', var)} for {model} {exp} ({startdate}-{enddate}) and, reference {catalog_ref} {model_ref} and {exp_ref} ({startdate_ref}-{enddate_ref}) ")
        
            title = title + "{region} "
            if lon_lim is None or lat_lim is None: self.logger.error(f"For the {region}, please specify the lon_lim and lat_lim.")
            description = description + "for {region} "
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
            dataset_std_ref = self.subregion_selection(
                data=dataset_std_ref, 
                model=model_ref, 
                exp=exp_ref, 
                lon_lim=lon_lim,
                lat_lim=lat_lim,
                region=region)
       
        #if regrid:
        #    dataset_std = dataset_std.aqua.regrid()
        #    dataset_std_ref = dataset_std_ref.aqua.regrid() 

        dataset_diff = dataset_std - dataset_std_ref
 
        proj = get_projection(proj, **proj_params)

        if vmin_diff is None:
            vmin_diff = dataset_diff.values.min()
        if vmax_diff is None:
            vmax_diff = dataset_diff.values.max()
        
        if vmin_diff == vmax_diff:
            # TODO: discuss what should do here in this case.
            self.logger.info("STD is Zero everywhere") 
            fig, ax = plot_single_map(
                dataset[var],
                return_fig=True,
                title=title,
                proj=proj,
                loglevel=self.loglevel,
                cbar_label=cbar_label
            )
        else:
            fig, ax = plot_single_map(
                dataset[var],
                return_fig=True,
                title=title,
                vmin=vmin_diff,
                vmax=vmax_diff,
                proj=proj,
                loglevel=self.loglevel,
                cbar_label=cbar_label
            )
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")

        # Saving plots
        if save_png:
            self.save_plot_diff(
                var=var, 
                fig=fig, 
                description=description, 
                rebuild=rebuild, 
                outputdir=outputdir, 
                format='png',
                catalog=catalog,
                model=model,
                exp=exp,
                startdate=startdate,
                enddate=enddate,
                catalog_ref=catalog_ref,
                model_ref=model_ref,
                exp_ref=exp_ref,
                startdate_ref=startdate_ref,
                enddate_ref=enddate_ref,
                #long_name=long_name,
                #units=units,
                dpi=dpi)
        if save_pdf:
            self.save_plot_diff(
                var=var, 
                fig=fig, 
                description=description, 
                rebuild=rebuild, 
                outputdir=outputdir, 
                format='pdf',
                catalog=catalog,
                model=model,
                exp=exp,
                startdate=startdate,
                enddate=enddate,
                #long_name=long_name,
                #units=units,
                dpi=dpi)

        return fig, ax

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
        Selecting sub-region based on lon-lat 
        """
        self.logger.info(f'Selecting the sub-region plots: {region_name}.')
        # Apply masking if necessary
        if "ICON" in model and mask_northern_boundary and northern_boundary_latitude:
            data = data.where(data.lat < northern_boundary_latitude)
        if "ICON" in model and mask_southern_boundary and southern_boundary_latitude:
            data = data.where(data.lat > southern_boundary_latitude)
        
        return area_selection(data, lon=lon_lim, lat=lat_lim, drop=True)

