import os
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from aqua.logger import log_configure
from aqua.util import load_yaml
from aqua.reader import Reader
from aqua.graphics import plot_single_map

class RMSE:
    """RMSE diagnostic"""

    def __init__(self, config, loglevel: str = 'WARNING'):
        """Initialize the RMSE diagnostic class.

        Args:
            config: Configuration for the RMSE diagnostic. Can be either a path to a YAML file
                   or a dictionary containing the configuration.
            loglevel (str, optional): Logging level. Defaults to 'WARNING'.

        Raises:
            ValueError: If startdate or enddate are not provided in the configuration.
        """
        # Configure logger
        self.loglevel = loglevel
        self.logger = log_configure(self.loglevel, 'RMSE')

        if isinstance(config, str):
            self.logger.debug("Reading configuration file %s", config)
            self.config = load_yaml(config)
        else:
            self.logger.debug("Configuration is a dictionary")
            self.config = config 

        # Check if startdate and enddate are provided
        self.startdate = self.config.get('dates', {}).get('startdate')
        self.enddate = self.config.get('dates', {}).get('enddate')

        if self.startdate is None or self.enddate is None:
            self.logger.error("Both startdate and enddate must be provided")
            raise ValueError("Both startdate and enddate must be provided")

        # Initialize the Reader class
        self._reader() 

    def _reader(self):
        """
        The reader method. This method initializes the Reader class for both reference
        and main data.
        """

        # Get the data configs
        config_data_ref = self.config.get('data_ref', {})
        config_data = self.config.get('data', {})

        # Check if necessary keys exist within the data configs
        if not all(k in config_data_ref for k in ['catalog', 'model', 'exp', 'source', 'regrid', 'fix']):
             self.logger.warning("Reference data configuration ('data_ref') might be incomplete.")
        if not all(k in config_data for k in ['catalog', 'model', 'exp', 'source', 'regrid', 'fix']):
             self.logger.warning("Main data configuration ('data') might be incomplete.")

        # Pass only existing keys
        self.reader_data_ref = Reader(
            catalog=config_data_ref.get('catalog'),
            model=config_data_ref.get('model'),
            exp=config_data_ref.get('exp'),
            source=config_data_ref.get('source'),
            regrid=config_data_ref.get('regrid'),
            fix=config_data_ref.get('fix'),
            startdate=self.startdate,
            enddate=self.enddate,
            loglevel=self.loglevel
        )
        self.reader_data = Reader(
            catalog=config_data.get('catalog'),
            model=config_data.get('model'),
            exp=config_data.get('exp'),
            source=config_data.get('source'),
            regrid=config_data.get('regrid'),
            fix=config_data.get('fix'),
            startdate=self.startdate,
            enddate=self.enddate,
            loglevel=self.loglevel
        )
        self.logger.debug('Reader classes initialized for data_ref and data')

    def retrieve(self):
        """
        Retrieves data for all variables specified in the configuration
        from both the reference and main data sources using the initialized readers.
        Stores retrieved data in self.retrieved_data_ref and self.retrieved_data dictionaries.
        Handles single levels, lists of levels, and surface variables.
        """

        self.retrieved_data_ref = {}
        self.retrieved_data = {}
        variables_to_process = self.config.get('variables', [])

        if not variables_to_process:
            self.logger.warning("No 'variables' section found in the configuration. Nothing to retrieve.")
            return # Exit if no variables are defined

        self.logger.info("Starting data retrieval...")

        for var_info in variables_to_process:
            var_name = var_info.get('name')
            if not var_name:
                self.logger.warning("Skipping variable entry with no name: %s", var_info)
                continue

            levels = var_info.get('level') # Can be None, int, or list

            # Ensure levels is a list to simplify iteration, handle None case
            if levels is None:
                levels_to_iterate = [None] # Treat surface variables as a list with one None element
            elif isinstance(levels, (int, float)):
                levels_to_iterate = [int(levels)] # Single level
            elif isinstance(levels, list):
                levels_to_iterate = [int(lvl) for lvl in levels] # List of levels
            else:
                self.logger.warning(f"Invalid level format for variable {var_name}: {levels}. Skipping.")
                continue

            for level in levels_to_iterate:
                # Determine the key for storing data (e.g., 'q_85000' or '2t')
                data_key = f"{var_name}_{level}" if level is not None else var_name
                log_msg_suffix = f" at level {level}" if level is not None else " (surface)"

                # Arguments for reader.retrieve
                retrieve_args = {'var': var_name}
                if level is not None:
                    retrieve_args['level'] = level

                # Retrieve Reference Data
                try:
                    self.logger.debug(f"Retrieving reference data for {var_name}{log_msg_suffix}")
                    data_ref = self.reader_data_ref.retrieve(**retrieve_args)

                    if level is not None and 'plev' in data_ref.coords:
                         if level in data_ref['plev']:
                             data_ref = data_ref.sel(plev=level, drop=True) # drop=True removes plev coord
                         else:
                             self.logger.warning(f"Level {level} not found in reference data for {var_name}. Skipping this level.")
                             continue # Skip to next level or variable

                    self.retrieved_data_ref[data_key] = data_ref
                    self.logger.debug(f"Successfully retrieved reference data for key: {data_key}")
                except Exception as e:
                    self.logger.error(f"An unexpected error occurred retrieving reference {var_name}{log_msg_suffix}: {e}", exc_info=True)
                    continue # Skip this level/variable on error

                # Retrieve Main Data
                try:
                    self.logger.debug(f"Retrieving main data for {var_name}{log_msg_suffix}")
                    data = self.reader_data.retrieve(**retrieve_args)
                    
                    if level is not None and 'plev' in data.coords:
                         if level in data['plev']:
                            data = data.sel(plev=level, drop=True)
                         else:
                             self.logger.warning(f"Level {level} not found in main data for {var_name}. Skipping this level.")
                             # Clean up ref data if main data failed for this level
                             if data_key in self.retrieved_data_ref:
                                 del self.retrieved_data_ref[data_key]
                             continue # Skip to next level or variable

                    self.retrieved_data[data_key] = data
                    self.logger.debug(f"Successfully retrieved main data for key: {data_key}")
                except Exception as e:
                    self.logger.error(f"An unexpected error occurred retrieving main {var_name}{log_msg_suffix}: {e}", exc_info=True)
                     # Clean up ref data if main data failed for this level
                    if data_key in self.retrieved_data_ref:
                        del self.retrieved_data_ref[data_key]
                    continue # Skip this level/variable on error

        self.logger.info("Data retrieval finished.")
        if not self.retrieved_data_ref and not self.retrieved_data:
             self.logger.warning("No data was successfully retrieved for any variable.")
        else:
             # Log the keys which now include levels
             self.logger.info(f"Retrieved reference data for keys: {list(self.retrieved_data_ref.keys())}")
             self.logger.info(f"Retrieved main data for keys: {list(self.retrieved_data.keys())}")

    @staticmethod
    def check_and_convert_coords(data, data_ref, base_var_name): # Renamed arg for clarity
        """
        Checks if latitude and longitude coordinates are of the same type between datasets.
        Converts them to float32 if they differ.

        Args:
            data (xr.Dataset): First dataset to check
            data_ref (xr.Dataset): Reference dataset to check
            base_var_name (str): The actual variable name within the datasets (e.g., 'q', '2t')

        Returns:
            tuple: Processed datasets with matching coordinate types
        """
        # Check if the base variable exists in both datasets before proceeding
        if base_var_name not in data or base_var_name not in data_ref:
             # Log or raise an error, depending on desired behavior
             print(f"Warning: Base variable '{base_var_name}' not found in one or both datasets during coordinate check.")
             return data, data_ref # Return original data if var not found

        # Get coordinate names for lat/lon using the base variable name
        try:
            lat_name = [dim for dim in data[base_var_name].dims if 'lat' in dim.lower()][0]
            lon_name = [dim for dim in data[base_var_name].dims if 'lon' in dim.lower()][0]
        except IndexError:
             print(f"Warning: Could not determine lat/lon dimension names for variable '{base_var_name}'.")
             return data, data_ref


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

    def _sanitize_filename_part(self, part):
        """Sanitizes a string part for use in a filename."""
        if not isinstance(part, str):
            part = str(part) # Ensure it's a string
        # Replace potentially problematic characters with underscores
        invalid_chars = [' ', '/', '\\', ':', '*', '?', '"', '<', '>', '|', '.'] 
        for char in invalid_chars:
            part = part.replace(char, '_')
        return part

    def _generate_filename(self, processed_key, output_type, suffix):
        """
        Generates a unique filename based on config and context.

        Args:
            processed_key (str): The variable key (e.g., 'q_85000', '2t').
            output_type (str): Type of output ('figure' or 'netcdf').
            suffix (str): Suffix describing the calculation (e.g., 'spatial_rmse', 'temporal_rmse').

        Returns:
            str: The full, unique path for the output file.
        """
        # Get config details with defaults and sanitize them
        data_cfg = self.config.get('data', {})
        ref_cfg = self.config.get('data_ref', {})
        dates_cfg = self.config.get('dates', {})

        model = self._sanitize_filename_part(data_cfg.get('model', 'model'))
        exp = self._sanitize_filename_part(data_cfg.get('exp', 'exp'))
        source = self._sanitize_filename_part(data_cfg.get('source', 'src')) # Shorten 'source' label if needed
        model_ref = self._sanitize_filename_part(ref_cfg.get('model', 'refmodel'))
        
        exp_ref = self._sanitize_filename_part(ref_cfg.get('exp', 'refexp'))
        startdate = self._sanitize_filename_part(dates_cfg.get('startdate', 'nodate'))
        enddate = self._sanitize_filename_part(dates_cfg.get('enddate', 'nodate'))

        # Construct the base filename from sanitized parts
        base_name_parts = [
            model, exp, source,
            'vs', model_ref,
            startdate, enddate,
            processed_key,
            suffix
        ]
        # Filter out any empty strings that might result from missing config values
        base_filename = '_'.join(filter(None, base_name_parts))

        # Determine directory and extension based on output_type
        if output_type == 'figure':
            output_dir = self.config.get('outputdir_fig', './figs')
            extension = '.pdf'
        elif output_type == 'netcdf':
            output_dir = self.config.get('outputdir_data', './output')
            extension = '.nc'
        else:
            self.logger.error(f"Unknown output_type requested for filename generation: {output_type}")
            # Return a fallback path or raise an error
            return os.path.join('.', f"{processed_key}_{suffix}_unknown_type") # Basic fallback

        # Ensure the output directory exists
        try:
            os.makedirs(output_dir, exist_ok=True)
        except OSError as e:
            self.logger.error(f"Could not create output directory {output_dir}: {e}")
            # Fallback to current directory? Or re-raise? For now, log and continue path creation
            output_dir = '.'

        full_path = os.path.join(output_dir, f"{base_filename}{extension}")
        self.logger.debug(f"Generated path for {output_type} ({processed_key}, {suffix}): {full_path}")
        return full_path

    def _save_figure(self, fig, processed_key, plot_type): # plot_type: 'spatial' or 'temporal'
        """
        Saves the generated figure with a unique name based on config.

        Args:
            fig (matplotlib.figure.Figure): The figure object to save.
            processed_key (str): The variable key (e.g., 'q_85000', '2t').
            plot_type (str): The type of plot ('spatial' or 'temporal').
        """
        # Generate the unique filename using the helper method
        filename = self._generate_filename(processed_key, 'figure', f'{plot_type}_rmse')
        try:
            fig.savefig(filename)
            self.logger.info(f"Figure saved to {filename}")
        except Exception as e:
            # Log the error with the specific filename that failed
            self.logger.error(f"Failed to save figure {filename}: {e}", exc_info=True)

    def _save_netcdf(self, data, processed_key, data_type): # data_type: 'spatial' or 'temporal'
        """
        Saves the generated netcdf file with a unique name based on config.

        Args:
            data (xr.Dataset): The data to save.
            processed_key (str): The variable key (e.g., 'q_85000', '2t').
            data_type (str): The type of data ('spatial' or 'temporal').
        """
        # Generate the unique filename using the helper method
        filename = self._generate_filename(processed_key, 'netcdf', f'{data_type}_rmse')
        try:
            data.to_netcdf(filename)
            self.logger.info(f"NetCDF data saved to {filename}")
        except Exception as e:
            # Log the error with the specific filename that failed
            self.logger.error(f"Failed to save NetCDF {filename}: {e}", exc_info=True)

    # Helper function to parse the processed key
    def _parse_processed_key(self, processed_key):
        parts = processed_key.split('_')
        level = None
        base_var_name = processed_key
        # Check if the last part is likely a level (numeric)
        if len(parts) > 1 and parts[-1].isdigit():
            try:
                level = int(parts[-1])
                base_var_name = '_'.join(parts[:-1]) # Rejoin in case var name had underscores
            except ValueError:
                 # Not a simple integer level, treat whole key as base name
                 pass # Keep defaults: level=None, base_var_name=processed_key
                 
        return base_var_name, level

    def spatial_rmse(self, save_fig: bool = False, save_netcdf: bool = False):
        """
        Calculates and plots the temporal averaged spatial RMSE for all variables
        and levels retrieved.

        This method processes all common variables between the main and reference datasets,
        calculating the Root Mean Square Error (RMSE) spatially for each timestep and then
        averaging over time.

        Args:
            save_fig (bool, optional): If True, saves the generated figures to the configured
                output directory. Defaults to False.
            save_netcdf (bool, optional): If True, saves the RMSE results as NetCDF files
                to the configured output directory. Defaults to False.

        Returns:
            dict: A dictionary containing the RMSE results for each processed variable/level
                combination. Keys are the processed variable names (e.g., 'q_85000', '2t')
                and values are the corresponding xarray DataArrays containing RMSE values.

        Note:
            - The retrieve() method must be called before this method.
            - Only variables/levels present in both datasets will be processed.
        """
        self.logger.info('Calculating and plotting spatial RMSE for retrieved variables/levels.')

        # Ensure data has been retrieved
        if not hasattr(self, 'retrieved_data') or not hasattr(self, 'retrieved_data_ref'):
             self.logger.error("Data has not been retrieved yet. Call the retrieve() method first.")
             return {}

        # Find common keys (e.g., 'q_85000', '2t') retrieved in both datasets
        common_keys = set(self.retrieved_data.keys()) & set(self.retrieved_data_ref.keys())

        if not common_keys:
            self.logger.warning("No common data keys found between reference and main retrieved data. Cannot calculate RMSE.")
            return {}

        results = {} # Dictionary to store results for each key

        # Get metadata for title from config
        config_data = self.config.get('data', {})
        config_data_ref = self.config.get('data_ref', {})
        model = config_data.get('model', 'N/A')
        exp = config_data.get('exp', 'N/A')
        source = config_data.get('source', 'N/A')
        model_ref = config_data_ref.get('model', 'N/A')
        exp_ref = config_data_ref.get('exp', 'N/A')
        source_ref = config_data_ref.get('source', 'N/A')

        for processed_key in common_keys:
            base_var_name, level = self._parse_processed_key(processed_key)
            self.logger.info(f"Processing spatial RMSE for key: {processed_key} (Variable: {base_var_name}, Level: {level})")

            data = self.retrieved_data[processed_key]
            data_ref = self.retrieved_data_ref[processed_key]

            # Check if base_var_name actually exists in the datasets after retrieval
            if base_var_name not in data or base_var_name not in data_ref:
                self.logger.warning(f"Variable '{base_var_name}' not found in data for key '{processed_key}'. Skipping.")
                continue

            try:
                # Coordinate Check/Conversion - Pass base_var_name
                data, data_ref = self.check_and_convert_coords(data, data_ref, base_var_name=base_var_name)
                self.logger.debug(f"Coordinates checked/converted for {processed_key}")

                # Calculate RMSE using the base variable name
                rmse = ((data[base_var_name] - data_ref[base_var_name])**2).mean(dim='time', skipna=True)**0.5
                self.logger.debug(f"RMSE calculated for {processed_key}")

                # Plotting
                vmin = 0 # RMSE is always non-negative
                # Ensure the rmse DataArray is not empty before quantile calculation
                if rmse.size > 0:
                    vmax = float(rmse.quantile(0.98, skipna=True))
                    if np.isnan(vmax): vmax = float(rmse.max(skipna=True)) # Fallback if quantile is NaN
                    if np.isnan(vmax) or vmax <= vmin : vmax = vmin + 1.0 # Further fallback if max is also NaN or not > vmin
                else:
                     vmax = 1.0 # Default vmax if rmse is empty
                     self.logger.warning(f"RMSE data for {processed_key} is empty or all NaN. Using default vmax=1.0.")

                self.logger.debug(f"Plotting parameters for {processed_key}: vmin={vmin}, vmax={vmax}")

                title_level_part = f" at {int(level / 100)} hPa" if level is not None else ""
                title = (f"{base_var_name}{title_level_part} RMSE of {model} {exp} ({source})\n" # Use base_var_name
                         f"relative to {model_ref} {exp_ref} ({source_ref})\n"
                         f"{self.startdate} to {self.enddate}")

                fig, ax = plot_single_map(data=rmse, # Pass the calculated rmse DataArray
                                          return_fig=True,
                                          contour=True,
                                          title=title,
                                          sym=False,
                                          vmin=vmin,
                                          vmax=vmax,
                                          cmap='Reds')
                ax.set_xlabel("Longitude")
                ax.set_ylabel("Latitude")
                self.logger.info(f"Spatial RMSE plot generated for {processed_key}")

                # Store results using the processed key
                results[processed_key] = (fig, ax, xr.Dataset({base_var_name: rmse})) # Store dataset with base_var_name

            except Exception as e:
                self.logger.error(f"Failed to calculate or plot spatial RMSE for key {processed_key}: {e}", exc_info=True)
                # Clear potentially incomplete results for this key
                if processed_key in results: del results[processed_key]

        self.logger.info("Finished spatial RMSE processing.")

        if save_fig:
            self.logger.info("Saving spatial RMSE figures...")
            for key, result_tuple in results.items():
                if len(result_tuple) >= 1 and result_tuple[0] is not None: # Check if fig exists
                     fig_to_save = result_tuple[0]
                     self._save_figure(fig_to_save, key, 'spatial') # Pass 'spatial' type
                else:
                     self.logger.warning(f"Skipping saving figure for key {key} as no figure object was found in results.")

        if save_netcdf:
            self.logger.info("Saving spatial RMSE netcdf files...")
            for key, result_tuple in results.items():
                if len(result_tuple) >= 3 and result_tuple[2] is not None: # Check if dataset exists
                    rmse_ds_to_save = result_tuple[2]
                    self._save_netcdf(data=rmse_ds_to_save, processed_key=key, data_type='spatial') # Pass 'spatial' type
                else:
                    self.logger.warning(f"Skipping saving NetCDF for key {key} as no dataset object was found in results.")

        # Return only the datasets for consistency, or modify based on actual needs
        return {key: res[2] for key, res in results.items() if len(res) >= 3 and res[2] is not None}

    def temporal_rmse(self, save_fig: bool = False, save_netcdf: bool = False):
        """
        Calculates and plots the temporal RMSE (spatially averaged) for all variables and levels retrieved.

        The temporal RMSE is calculated by:
        1. Taking the difference between the main and reference datasets
        2. Squaring the differences
        3. Averaging spatially over latitude and longitude
        4. Taking the square root
        
        This gives a time series of RMSE values showing how the error varies temporally.

        Parameters
        ----------
        save_fig : bool, optional
            Whether to save the generated figures to disk (default is False)
        save_netcdf : bool, optional 
            Whether to save the RMSE data as NetCDF files (default is False)

        Returns
        -------
        dict
            Dictionary containing the results for each variable/level combination.
            Keys are the processed variable names (e.g. 'q_85000' for specific humidity at 850hPa)
            Values are tuples of (figure, axis, dataset) containing the plot and data
        """
        self.logger.info('Calculating and plotting temporal RMSE for retrieved variables/levels.')

        # Ensure data has been retrieved
        if not hasattr(self, 'retrieved_data') or not hasattr(self, 'retrieved_data_ref'):
             self.logger.error("Data has not been retrieved yet. Call the retrieve() method first.")
             return {}

        # Find common keys (e.g., 'q_85000', '2t')
        common_keys = set(self.retrieved_data.keys()) & set(self.retrieved_data_ref.keys())

        if not common_keys:
            self.logger.warning("No common data keys found between reference and main retrieved data. Cannot calculate RMSE.")
            return {}

        results = {} # Dictionary to store results for each key

        # Get metadata for title from config
        config_data = self.config.get('data', {})
        config_data_ref = self.config.get('data_ref', {})
        model = config_data.get('model', 'N/A')
        exp = config_data.get('exp', 'N/A')
        source = config_data.get('source', 'N/A')
        model_ref = config_data_ref.get('model', 'N/A')
        exp_ref = config_data_ref.get('exp', 'N/A')
        source_ref = config_data_ref.get('source', 'N/A')

        for processed_key in common_keys:
            base_var_name, level = self._parse_processed_key(processed_key)
            self.logger.info(f"Processing temporal RMSE for key: {processed_key} (Variable: {base_var_name}, Level: {level})")

            data = self.retrieved_data[processed_key]
            data_ref = self.retrieved_data_ref[processed_key]

            # Check if base_var_name actually exists
            if base_var_name not in data or base_var_name not in data_ref:
                self.logger.warning(f"Variable '{base_var_name}' not found in data for key '{processed_key}'. Skipping.")
                continue

            try:
                # Coordinate Check/Conversion - Pass base_var_name
                data, data_ref = self.check_and_convert_coords(data, data_ref, base_var_name=base_var_name)
                self.logger.debug(f"Coordinates checked/converted for {processed_key}")

                # Calculate RMSE (averaged spatially) using base_var_name
                rmse = ((data[base_var_name] - data_ref[base_var_name])**2).mean(dim=['lat', 'lon'], skipna=True)**0.5
                self.logger.debug(f"Temporal RMSE calculated for {processed_key}")

                # Plotting
                fig, ax = plt.subplots(figsize=(12, 6))

                # Plot the rmse DataArray directly
                rmse.plot(ax=ax)

                # Format Time Axis
                time_coords = rmse['time'].values
                if len(time_coords) > 1:
                    time_diff = np.diff(time_coords)[0]
                    if time_diff < np.timedelta64(1, 'D'):
                         date_format = mdates.DateFormatter('%Y-%m-%d %H:%M')
                         self.logger.debug(f"Using hourly time format for x-axis for {processed_key}")
                    else:
                         date_format = mdates.DateFormatter('%Y-%m-%d')
                         self.logger.debug(f"Using daily time format for x-axis for {processed_key}")
                    ax.xaxis.set_major_formatter(date_format)
                    fig.autofmt_xdate()
                elif len(time_coords) == 1:
                     self.logger.debug(f"Only one time point for {processed_key}, standard x-axis formatting.")

                # Extract units for y-label if available from original data
                units = data[base_var_name].attrs.get('units', '')
                ylabel = f"RMSE ({units})" if units else "RMSE"
                ax.set_ylabel(ylabel)
                ax.set_xlabel("Time")
                ax.grid(True)

                # Construct title using base_var_name and level
                title_level_part = f" at {int(level / 100)} hPa" if level is not None else ""
                title = (f"Temporal RMSE: {base_var_name}{title_level_part}\n" # Use base_var_name
                         f"{model} {exp} ({source}) vs {model_ref} {exp_ref} ({source_ref})\n"
                         f"{self.startdate} to {self.enddate}")
                ax.set_title(title)

                fig.tight_layout()

                self.logger.info(f"Temporal RMSE plot generated for {processed_key}")

                # Store results using processed key, dataset contains base_var_name
                results[processed_key] = (fig, ax, xr.Dataset({base_var_name: rmse}))

            except Exception as e:
                self.logger.error(f"Failed to calculate or plot temporal RMSE for key {processed_key}: {e}", exc_info=True)
                # Clear potentially incomplete results for this key
                if processed_key in results: del results[processed_key]

        self.logger.info("Finished temporal RMSE processing.")

        # Save Figure if requested
        if save_fig:
            self.logger.info("Saving temporal RMSE figures...")
            for key, result_tuple in results.items():
                if len(result_tuple) >= 1 and result_tuple[0] is not None:
                    fig_to_save = result_tuple[0]
                    # Note: No longer adding suffix manually here
                    self._save_figure(fig_to_save, key, 'temporal') # Pass 'temporal' type
                else:
                     self.logger.warning(f"Skipping saving figure for key {key} as no figure object was found in results.")

        # Save NetCDF if requested
        if save_netcdf:
            self.logger.info("Saving temporal RMSE netcdf files...")
            for key, result_tuple in results.items():
                 if len(result_tuple) >= 3 and result_tuple[2] is not None:
                    rmse_ds_to_save = result_tuple[2]
                    # Note: No longer adding suffix manually here
                    self._save_netcdf(data=rmse_ds_to_save, processed_key=key, data_type='temporal') # Pass 'temporal' type
                 else:
                    self.logger.warning(f"Skipping saving NetCDF for key {key} as no dataset object was found in results.")

        # Return only the datasets
        return {key: res[2] for key, res in results.items() if len(res) >= 3 and res[2] is not None}