'''
RMSE diagnostic

This diagnostic calculates the Root Mean Square Error (RMSE) between two datasets.
It has been built taken as reference the code of the GlobalBiases diagnostic.
'''

import xarray as xr
import pandas as pd
from aqua.logger import log_configure
from aqua.exceptions import NoDataError
from aqua.graphics import plot_single_map, plot_timeseries

# Set default options for xarray
xr.set_options(keep_attrs=True)

class RMSE:
    def __init__(self, data_ref=None, data=None, var_name=None, plev=None, loglevel='WARNING', 
                 model_ref=None, exp_ref=None, source_ref=None,
                 model=None, exp=None, source=None, 
                 startdate=None, enddate=None):
        
        self.data = data
        self.data_ref = data_ref
        self.var_name = var_name
        self.plev = plev
        self.logger = log_configure(log_level=loglevel, log_name='RMSE')
        self.model_ref = model_ref
        self.exp_ref = exp_ref  
        self.source_ref = source_ref
        self.model = model
        self.exp = exp
        self.source = source
        self.startdate = startdate
        self.enddate = enddate

        # Check if data or data_ref is None
        if data is None or data_ref is None:
            self.logger.error("Both data and reference data must be provided")
            raise ValueError("Both data and reference data must be provided")
        else:
            self.data = self._process_data(self.data)
            self.data_ref = self._process_data(self.data_ref)

        # Check if startdate and enddate are provided
        if self.startdate is None or self.enddate is None:
            self.logger.error("Both startdate and enddate must be provided")
            raise ValueError("Both startdate and enddate must be provided")
        else:
            # Subset the data to the specified start and end dates
            self.data = self.data.sel(time=slice(self.startdate, self.enddate))
            self.data_ref = self.data_ref.sel(time=slice(self.startdate, self.enddate))

        # Check and convert coordinates
        self.data, self.data_ref = self.check_and_convert_coords(self.data, self.data_ref, self.var_name)

    def _process_data(self, data):
        """
        Processes the dataset, electing the specified pressure level.

        Args:
            data (xr.Dataset): The dataset to process.
        """
        if self.plev is not None:
            self.logger.info(f'Selecting pressure level {self.plev} for variable {self.var_name}.')
            data = self.select_pressure_level(data, self.plev, self.var_name)
        elif 'plev' in data[self.var_name].dims:
            self.logger.warning(f"Variable {self.var_name} has multiple pressure levels but none selected. Skipping 2D plotting for RMSE maps.")

        return data

    @staticmethod
    def select_pressure_level(data, plev, var_name):
        """
        Selects a specified pressure level from the dataset.

        Args:
            data (xr.Dataset): Dataset to select from.
            plev (float): Desired pressure level.
            var_name (str): Variable name to filter by.

        Returns:
            xr.Dataset: Filtered dataset at specified pressure level.

        Raises:
            NoDataError: If specified pressure level is not available.
        """
        if 'plev' in data[var_name].dims:
            try:
                return data.sel(plev=plev)
            except KeyError:
                raise NoDataError("The specified pressure level is not in the dataset.")
        else:
            raise NoDataError(f"{var_name} does not have a 'plev' coordinate.")

    @staticmethod
    def check_and_convert_coords(data, data_ref, var_name):
        """
        Checks if latitude and longitude coordinates are of the same type between datasets.
        Converts them to float32 if they differ.

        Args:
            data (xr.Dataset): First dataset to check
            data_ref (xr.Dataset): Reference dataset to check
            var_name (str): Variable name to check coordinates for

        Returns:
            tuple: Processed datasets with matching coordinate types
        """
        # Get coordinate names for lat/lon
        lat_name = [dim for dim in data[var_name].dims if 'lat' in dim.lower()][0]
        lon_name = [dim for dim in data[var_name].dims if 'lon' in dim.lower()][0]

        # Check if types match
        if data[lat_name].dtype != data_ref[lat_name].dtype or data[lon_name].dtype != data_ref[lon_name].dtype:
            # Convert both to float32
            data = data.assign_coords({
                lat_name: data[lat_name].astype('float32'),
                lon_name: data[lon_name].astype('float32')
            })
            data_ref = data_ref.assign_coords({
                lat_name: data_ref[lat_name].astype('float32'),
                lon_name: data_ref[lon_name].astype('float32')
            })

        return data, data_ref

    def plot_spatial_rmse(self, vmin=None, vmax=None):
        """
        Plots temporal averaged RMSE.

        Args:
            vmin (float, optional): Minimum colorbar value.
            vmax (float, optional): Maximum colorbar value.

        Returns:
            tuple: Matplotlib figure, axis objects, and xarray Dataset of the calculated RMSE.
        """
        self.logger.info('Plotting spatial RMSE.')

        # Check if pressure levels exist but are not specified
        if 'plev' in self.data[self.var_name].dims and self.plev is None:
            self.logger.warning(f"Variable {self.var_name} has multiple pressure levels, but no specific level was selected. Skipping 2D bias plotting.")
            return None  # Return None for both fig and ax  

        # Calculate the RMSE between two datasets
        rmse = ((self.data[self.var_name] - self.data_ref[self.var_name])**2).mean(dim='time')**0.5

        # Plot the RMSE map between the two datasets
        self.logger.info('Plotting spatial RMSE map between the two datasets.')

        # For RMSE, always use asymmetric colorbar starting at 0
        if vmin is not None:
            self.logger.warning("vmin will be set to 0 for RMSE plot")
        vmin = 0
        
        # If vmax is not provided, let it be determined by the data
        if vmax is None:
            vmax = float(rmse.quantile(0.98))

        title = (f"{self.var_name} RMSE of {self.model} {self.exp} ({self.source}) \n"
                f"relative to {self.model_ref} {self.exp_ref} ({self.source_ref})\n"
                f"from {self.startdate} to {self.enddate}"
                + (f" at {int(self.plev / 100)} hPa" if self.plev else ""))

        fig, ax = plot_single_map(data=rmse,
                                  return_fig=True, 
                                  contour=True,
                                  title=title,
                                  sym=False,
                                  vmin=vmin,
                                  vmax=vmax,
                                  cmap='Reds')
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        
        return fig, ax, rmse
    
    def plot_temporal_rmse(self):
        """
        Calculates and plots the spatially averaged RMSE as a time series.

        Returns:
            tuple: Matplotlib figure, axis object, and xarray DataArray of the RMSE time series.
        """
        self.logger.info('Calculating and plotting temporal RMSE.')

        # Check if pressure levels exist but are not specified
        if 'plev' in self.data[self.var_name].dims and self.plev is None:
            self.logger.warning(f"Variable {self.var_name} has multiple pressure levels, but no specific level was selected. Skipping temporal RMSE plotting.")
            return None  # Return None for both fig and ax  

        # Calculate temporal RMSE
        squared_diff = (self.data[self.var_name] - self.data_ref[self.var_name])**2
        mse_time_series = squared_diff.mean(dim=['lat', 'lon'], skipna=True)
        rmse_time_series = mse_time_series**0.5

        # Plot the RMSE time series
        title=f"{self.var_name} RMSE of {self.model} {self.exp} ({self.source}) \n" \
              f"relative to {self.model_ref} {self.exp_ref} ({self.source_ref}) " \
              + (f" at {int(self.plev / 100)} hPa" if self.plev else "")  

        fig, ax = plot_timeseries(monthly_data=rmse_time_series,
                                  return_fig=True,
                                  data_labels=['RMSE'],
                                  title=title)

        return fig, ax, rmse_time_series