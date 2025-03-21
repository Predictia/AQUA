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
from aqua import Reader, plot_single_map
from aqua.logger import log_configure

class sshVariability():
    def __init__(self, variable=None, data_ref=None, data_model=None, name_ref=None, name_model=None, exp_ref=None, exp_model=None, startdate_model=None, enddate_model=None, startdate_ref=None, enddate_ref=None, outputdir=None, loglevel='WARNING', **kwargs):
        """
        Initialize the sshVariability.

        Args:
        """
        self.variable = variable
        self.data_ref = data_ref
        self.data_model = data_model
        self.ref_name = name_ref
        self.model_name = name_model
        self.ref_exp = exp_ref
        self.model_exp = exp_model
        self.startdate_model = startdate_model or pd.to_datetime(data_model.time[0].values).strftime('%Y-%m-%d')
        self.enddate_model = enddate_model or pd.to_datetime(data_model.time[-1].values).strftime('%Y-%m-%d')
        self.startdate_ref = startdate_ref or pd.to_datetime(data_ref.time[0].values).strftime('%Y-%m-%d')
        self.enddate_ref = enddate_ref or pd.to_datetime(data_ref.time[-1].values).strftime('%Y-%m-%d')
        self.outputdir = outputdir + "/ssh"
        self.logger = log_configure(log_level=loglevel, log_name='SSH Variability')
        # Plot options
        plot_options = kwargs.get('plot_options',{})
        self.scale_min = plot_options.get('scale_min',0.1)
        self.scale_max = plot_options.get('scale_max',0.4)
        self.cmap = plot_options.get('cmap','viridis')
        self.difference_plots = plot_options.get('difference_plots',False)
        self.region_selection = plot_options.get('region_selection',False)
        self.fig_format = plot_options.get('fig_format','png')
        self.contours = plot_options.get('contours',0)
        #self.regrid = plot_options.get('regrid',None)
        # Region selection
        region = kwargs.get('sub_region', {})
        self.region_name = region.get('name','Agulhas')
        self.region_lon_lim = region.get('lon_lim',[5,50])
        self.region_lat_lim = region.get('lat_lim',[-10,-50])
        # Retrieve the masking flags and boundary latitudes from the configuration, Specific to ICON
        mask_options = kwargs.get('mask_options',{})
        self.mask_northern_boundary = mask_options.get("mask_northern_boundary", True)
        self.mask_southern_boundary = mask_options.get("mask_southern_boundary", True)
        self.northern_boundary_latitude = mask_options.get("northern_boundary_latitude", 70)
        self.southern_boundary_latitude = mask_options.get("southern_boundary_latitude", -62)
        self.ref_std = None
        self.model_std = None

    def save_netcdf(self):
        """
        Save the standard deviation data to a NetCDF file.
        """
        # Create the file type folder within the output directory
        file_type_folder = os.path.join(self.outputdir,"netcdf")
        os.makedirs(file_type_folder, exist_ok=True)

        # Set the output file path
        if self.ref_std is not None:
            output_file = os.path.join(file_type_folder, f"{self.name_ref}_{self.exp_ref}_{self.startdate_ref}_to_{self.enddate_ref}_std.nc")
            self.ref_std.to_netcdf(output_file)
        if self.model_std is not None:
            output_file = os.path.join(file_type_folder, f"{self.name_model}_{self.exp_model}_{self.startdate_model}_to_{self.enddate_model}_std.nc")
            self.model_std.to_netcdf(output_file)

    def plot_std(self, data_std, model_name, exp_name, startdate, enddate, contours=21):
        """
        Visualize the SSH variability using Cartopy.
        """
        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})
        # Apply masking if the model is "ICON" and the flags are enabled with boundary latitudes provided
        if "ICON" in model_name and self.mask_northern_boundary and self.northern_boundary_latitude:
            data_std = data_std.where(data.lat < self.northern_boundary_latitude)
        if "ICON" in model_name and self.mask_southern_boundary and self.southern_boundary_latitude:
            data_std = data_std.where(data_std.lat > self.southern_boundary_latitude)
       
        lonname, latname = coord_names(data_std)

        if contours:
            lon, lat = np.meshgrid(data_std[lonname].values, data_std[latname].values)
            levels = np.linspace(self.scale_min,self.scale_max, contours)  # XXX num of levels hardcode, could be selected from config
            contf = ax.contourf(lon, lat, data_std, transform=ccrs.PlateCarree(), 
                                levels=levels, extend='both',cmap=self.cmap,
                                transform_first=True)  # It was failing with transform_first=False
        else:
            contf = ax.pcolormesh(data_std[lonname].values, data_std[latname].values, data_std,
                                  transform=ccrs.PlateCarree(), 
                                  vmin=self.scale_min, vmax=self.scale_max, cmap=self.cmap)
        ax.set_title(f"{model_name}")
        ax.coastlines()               
        
        # Add a colorbar for each subplot
        cbar = fig.colorbar(contf, ax=ax, orientation='vertical', shrink=0.9)
        cbar.set_label('SSH Variability (m)')
        #fig.tight_layout()
        filename = model_name + "_" + exp_name
        self.save_plot(filename, fig)

    def plot_std_diff(self, contours=21):
        """
        Visualize the difference in SSH variability data between each model and the AVISO model.

        Args:
            contours (int): Number of contours for plot (default: 21). If 0 or None the pcolormesh is used.
        """
        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})
        #to remove large fill values
        #ref_std = xr.where(self.ref_std < 100, self.ref_std, np.nan)
        if self.ref_std is not None and self.model_std is not None:
            #to remove large fill values
            ref_std = xr.where(self.ref_std < 100, self.ref_std, np.nan)
            diff_data = ref_std - self.model_std
        else:
            Print("ERROR!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        if "ICON" in self.model_name:
            if self.mask_northern_boundary and self.northern_boundary_latitude:
                diff_data = diff_data.where(data.lat < self.northern_boundary_latitude)
            if self.mask_southern_boundary and self.southern_boundary_latitude:
                diff_data = diff_data.where(data.lat > self.southern_boundary_latitude)

        lonname, latname = coord_names(self.model_std)

        if contours:
            lon, lat = np.meshgrid(self.model_std[lonname].values, self.model_std[latname].values)
            levels = np.linspace(-0.4, 0.4, contours)

            contf = ax.contourf(lon, lat, diff_data, transform=ccrs.PlateCarree(), 
                                levels=levels, extend='both',
                                cmap='RdBu', transform_first=True)
        else:
            contf = ax.pcolormesh(self.model_std[lonname], self.model_std[latname], diff_data,
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
        #fig.tight_layout()
        filename = "difference_plot_" + self.model_name + "-" + self.ref_name
        self.save_plot(filename, fig)

    def region_selection(self, data, model_name,exp_name):
    
        fig = plt.figure(figsize=(12, 8))
        
        # Apply masking if necessary
        if "ICON" in model_name and self.mask_northern_boundary and self.northern_boundary_latitude:
            data = data.where(data.lat < self.northern_boundary_latitude)
        if "ICON" in model_name and self.mask_southern_boundary and self.southern_boundary_latitude:
            data = data.where(data.lat > self.southern_boundary_latitude)
        
        ssh_sel = area_selection(data, lon=self.lon_lim, lat=self.lat_lim, drop=True)
            
        ax = fig.add_subplot(1, 1, 1)

        file_type_folder = os.path.join(self.outputdir,self.fig_format)
        os.makedirs(file_type_folder, exist_ok=True)
            
        plot_single_map(ssh_sel, ax=ax, title=f"{self.region_name} - {model_name}", 
                        vmin=self.scale_min, vmax=self.scale_max, 
                        cmap=self.cmap, save=True,
                        outputdir=save_path,
                        filename=f"ssh_{model_name}_{exp_name}_region_selection.plot.{self.fig_format}",
                        format=self.fig_format)


    def save_plot(self, filename, fig):
        """
        Saves the subplots as a PDF image file.
        """
        self.logger.info("Saving figure to %s",self.fig_format)
        file_type_folder = os.path.join(self.outputdir, self.fig_format)
        self.logger.debug(f"Saving figure to {file_type_folder}")
        file_type_folder = os.path.join(self.outputdir, self.fig_format)
        os.makedirs(file_type_folder, exist_ok=True)
        output_file = os.path.join(file_type_folder, filename)

        # Save the figure as a PDF file. fig.savefig() or plt.savefig() should accomplish the same task of saving the figure to a file. (DPI = dots per inch)
        fig.savefig(output_file, format=self.fig_format)

    def compute_std(self):
        """
        Compute std for the model and reference data 
        """
        if self.data_ref is not None and self.ref_std is None:
            self.logger.info("Computing std of %s ssh for the provided timespan", self.ref_name)
            self.ref_std = self.data_ref.std(axis=0)
        if self.data_model is not None and self.model_std is None:
            self.logger.info("Computing std of %s ssh for the provided timespan", self.model_name)
            self.model_std = self.data_model.std(axis=0)

    def run(self):
        self.compute_std()
        if self.ref_std is not None:
            self.plot_std(self.ref_std, self.ref_name, self.ref_exp, self.startdate_ref, self.enddate_ref, contours=21)
            #self.region_selection(self.ref_std, self.ref_name,self.ref_name)
        if self.model_std is not None:
            self.plot_std(self.model_std, self.model_name, self.model_name, self.startdate_model, self.enddate_model, contours=21)
            #self.region_selection(self.model_std, self.name_model,self.exp_model)
        # Plot the difference between the Reference std and Model std
        self.save_netcdf()
        print("###########################3")
        #self.plot_std_diff(contours=21)
        #print(self.ref_std)
