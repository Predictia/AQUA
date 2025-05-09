import os
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from aqua.logger import log_configure
from aqua.util import load_yaml
from aqua.reader import Reader
from aqua.graphics import plot_single_map

class ACC: 
    """ACC diagnostic"""

    def __init__(self, config, loglevel: str = 'WARNING'):
        """Initialize the ACC diagnostic class.

        Args:
            config: Configuration for the ACC diagnostic. Must contain 'data', 'data_ref',
                   'climatology_data', 'dates', and 'variables' sections.
                   Can be either a path to a YAML file or a dictionary.
            loglevel (str, optional): Logging level. Defaults to 'WARNING'.

        Raises:
            ValueError: If required configuration sections or keys are missing.
        """
        # Configure logger
        self.loglevel = loglevel
        self.logger = log_configure(self.loglevel, 'ACC')

        if isinstance(config, str):
            self.logger.debug("Reading configuration file %s", config)
            self.config = load_yaml(config)
        else:
            self.logger.debug("Configuration is a dictionary")
            self.config = config

        # Basic validation for required sections
        required_sections = ['data', 'data_ref', 'climatology_data', 'dates', 'variables']
        missing_sections = [s for s in required_sections if s not in self.config]
        if missing_sections:
            msg = f"Missing required configuration sections: {', '.join(missing_sections)}"
            self.logger.error(msg)
            raise ValueError(msg)

        # Evaluation dates
        self.startdate = self.config['dates'].get('startdate')
        self.enddate = self.config['dates'].get('enddate')
        if not self.startdate or not self.enddate:
            raise ValueError("Evaluation 'startdate' and 'enddate' must be provided in 'dates'.")

        # Climatology dates
        self.clim_startdate = self.config['climatology_data'].get('startdate')
        self.clim_enddate = self.config['climatology_data'].get('enddate')
        if not self.clim_startdate or not self.clim_enddate:
            raise ValueError("Climatology 'startdate' and 'enddate' must be provided in 'climatology_data'.")

        self._reader()

        # Initialize cache for climatology means
        self._climatology_means_cache = None

    def _reader(self):
        """
        The reader method. This method initializes the Reader class for both reference
        and main data.
        """

        # Get the data configs
        config_data_ref = self.config.get('data_ref', {})
        config_data = self.config.get('data', {})
        config_climatology = self.config.get('climatology_data', {})

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
        self.reader_climatology = Reader(
            catalog=config_climatology.get('catalog'),
            model=config_climatology.get('model'),
            exp=config_climatology.get('exp'),
            source=config_climatology.get('source'),
            regrid=config_climatology.get('regrid'),
            fix=config_climatology.get('fix'),
            startdate=self.clim_startdate,
            enddate=self.clim_enddate,
            loglevel=self.loglevel
        )

        self.logger.debug('Reader classes initialized for data_ref, data, and climatology')

    def retrieve(self):
        """
        Retrieves data for all variables specified in the configuration
        from both the reference and main data sources using the initialized readers.
        Stores retrieved data in self.retrieved_data_ref and self.retrieved_data dictionaries.
        Handles single levels, lists of levels, and surface variables.
        Invalidates the climatology mean cache.
        """
        # Invalidate cache when retrieving new data
        self.logger.debug("Resetting climatology means cache.")
        self._climatology_means_cache = None

        self.retrieved_data_ref = {}
        self.retrieved_data = {}
        self.retrieved_climatology_data = {}
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

                # Check the status
                ref_ok, data_ok, clim_ok = False, False, False

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
                    ref_ok = True
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
                    data_ok = True
                    self.logger.debug(f"Successfully retrieved main data for key: {data_key}")
                except Exception as e:
                    self.logger.error(f"An unexpected error occurred retrieving main {var_name}{log_msg_suffix}: {e}", exc_info=True)
                     # Clean up ref data if main data failed for this level
                    if data_key in self.retrieved_data_ref:
                        del self.retrieved_data_ref[data_key]
                    continue # Skip this level/variable on error

                # Retrieve Climatology
                try:
                    self.logger.debug(f"Retrieving climatology data for {var_name}{log_msg_suffix}")
                    data_clim = self.reader_climatology.retrieve(**retrieve_args)
                    if level is not None: data_clim = data_clim.sel(plev=level, drop=True)
                    self.retrieved_climatology_data[data_key] = data_clim
                    clim_ok = True
                    self.logger.debug(f"Successfully retrieved climatology data for key: {data_key}")
                except Exception as e:
                    # Critical failure if climatology is missing
                    self.logger.error(f"Failed retrieving MANDATORY climatology {data_key}: {e}", exc_info=False)
                    self.logger.error(f"Cannot compute ACC for {data_key} without climatology data.")
                    # Clean up potentially retrieved main/ref data for this key if clim failed
                    if data_key in self.retrieved_data: del self.retrieved_data[data_key]
                    if data_key in self.retrieved_data_ref: del self.retrieved_data_ref[data_key]
                    continue # Skip to next level/variable

                # Ensure all were retrieved successfully if climatology was needed
                if not (ref_ok and data_ok and clim_ok):
                     self.logger.warning(f"Skipping {data_key} due to incomplete data retrieval (ref: {ref_ok}, main: {data_ok}, clim: {clim_ok}).")
                     # Clean up partial retrievals for this key
                     if data_key in self.retrieved_data: del self.retrieved_data[data_key]
                     if data_key in self.retrieved_data_ref: del self.retrieved_data_ref[data_key]
                     if data_key in self.retrieved_climatology_data: del self.retrieved_climatology_data[data_key]

        valid_keys = list(self.retrieved_climatology_data.keys()) # Keys for which all data exists
        self.logger.info(f"Data retrieval finished. Valid keys for ACC: {valid_keys}")
        if not valid_keys:
             self.logger.warning("No variables/levels had data successfully retrieved from all three sources (ref, main, clim). ACC cannot be computed.")

    @staticmethod
    def _ensure_float32_coords(array):
        """
        Ensures the lat/lon coordinates of a DataArray are float32.

        Args:
            array (xr.DataArray): The DataArray to check and potentially convert.

        Returns:
            xr.DataArray: The DataArray with float32 lat/lon coordinates.
        """
        if not isinstance(array, xr.DataArray):
            self.logger.warning(f"Warning: Input to _ensure_float32_coords is not a DataArray (name: {getattr(array, 'name', 'N/A')}). Skipping.")
            return array

        # Identify potential latitude and longitude coordinate names dynamically
        lat_names = [dim for dim in array.coords if 'lat' in dim.lower()]
        lon_names = [dim for dim in array.coords if 'lon' in dim.lower()]

        if not lat_names or not lon_names:
            print(f"Debug: Could not find lat/lon coordinates in array {array.name}. Skipping conversion.")
            return array # Return unchanged if no lat/lon found

        lat_name = lat_names[0]
        lon_name = lon_names[0]

        # Check if conversion is needed
        needs_conversion = False
        if array[lat_name].dtype != np.float32:
            needs_conversion = True
        if array[lon_name].dtype != np.float32:
            needs_conversion = True

        if needs_conversion:
            print(f"Info: Converting lat/lon coordinate types to float32 for {array.name}")
            try:
                array = array.assign_coords({
                    lat_name: array[lat_name].astype('float32'),
                    lon_name: array[lon_name].astype('float32')
                })
            except Exception as e:
                print(f"Warning: Failed to convert coordinate types for {array.name}: {e}")

        return array

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
            suffix (str): Suffix describing the calculation (e.g., 'spatial_acc', 'temporal_acc').

        Returns:
            str: The full, unique path for the output file.
        """
        # Get config details with defaults and sanitize them
        data_cfg = self.config.get('data', {})
        ref_cfg = self.config.get('data_ref', {})
        dates_cfg = self.config.get('dates', {})
        clim_cfg = self.config.get('climatology_data', {})

        model = self._sanitize_filename_part(data_cfg.get('model', 'model'))
        exp = self._sanitize_filename_part(data_cfg.get('exp', 'exp'))
        source = self._sanitize_filename_part(data_cfg.get('source', 'src'))
        
        model_ref = self._sanitize_filename_part(ref_cfg.get('model', 'refmodel'))
        exp_ref = self._sanitize_filename_part(ref_cfg.get('exp', 'refexp'))
        source_ref = self._sanitize_filename_part(ref_cfg.get('source', 'refsrc'))

        startdate = self._sanitize_filename_part(dates_cfg.get('startdate', 'nodate'))
        enddate = self._sanitize_filename_part(dates_cfg.get('enddate', 'nodate'))
        
        clim_startdate = self._sanitize_filename_part(clim_cfg.get('startdate', 'nodate'))
        clim_enddate = self._sanitize_filename_part(clim_cfg.get('enddate', 'nodate'))

        # Construct the base filename from sanitized parts
        base_name_parts = [
            model, exp, source,
            'vs', model_ref, exp_ref, source_ref,
            clim_startdate, clim_enddate,
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

        # Ensure the output directory exists
        try:
            os.makedirs(output_dir, exist_ok=True)
        except OSError as e:
            self.logger.error(f"Could not create output directory {output_dir}: {e}")
            output_dir = '.'

        full_path = os.path.join(output_dir, f"{base_filename}{extension}")
        self.logger.debug(f"Generated path for {output_type} ({processed_key}, {suffix}): {full_path}")
        return full_path

    def _save_figure(self, fig, processed_key, plot_type):
        """
        Saves the generated figure with a unique name based on config.

        Args:
            fig (matplotlib.figure.Figure): The figure object to save.
            processed_key (str): The variable key (e.g., 'q_85000', '2t').
            plot_type (str): The type of plot ('spatial' or 'temporal').
        """
        filename = self._generate_filename(processed_key, 'figure', f'{plot_type}_acc')
        try:
            fig.savefig(filename)
            self.logger.info(f"Figure saved to {filename}")
        except Exception as e:
            self.logger.error(f"Failed to save figure {filename}: {e}", exc_info=True)

    def _save_netcdf(self, data, processed_key, data_type):
        """
        Saves the generated netcdf file with a unique name based on config.

        Args:
            data (xr.Dataset): The data to save.
            processed_key (str): The variable key (e.g., 'q_85000', '2t').
            data_type (str): The type of data ('spatial' or 'temporal').
        """
        filename = self._generate_filename(processed_key, 'netcdf', f'{data_type}_acc')
        try:
            data.to_netcdf(filename)
            self.logger.info(f"NetCDF data saved to {filename}")
        except Exception as e:
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

    def _calculate_anomalies(self, data_array, climatology_mean):
        """Calculates temporal anomalies by subtracting the provided climatology mean.

        Args:
            data_array (xr.DataArray): The data to calculate anomalies for.
            climatology_mean (xr.DataArray): The pre-calculated climatology mean
                                             (spatial map) from the external dataset.

        Returns:
            xr.DataArray: The calculated anomalies.

        Raises:
            ValueError: If climatology_mean is None or subtraction fails.
        """
        if climatology_mean is None:
            # This case should ideally be prevented by checks before calling
            msg = f"Internal Error: 'climatology_mean' was None for {data_array.name}."
            self.logger.error(msg)
            raise ValueError(msg)

        if not isinstance(data_array, xr.DataArray) or not isinstance(climatology_mean, xr.DataArray):
             msg = "Inputs 'data_array' and 'climatology_mean' must be xarray DataArrays."
             self.logger.error(msg)
             raise TypeError(msg)

        self.logger.debug(f"Calculating anomalies using provided climatology mean for {data_array.name}")
        try:
            anomalies = data_array - climatology_mean
            anomalies.attrs = data_array.attrs
            anomalies.name = f"{data_array.name}_anom"
            return anomalies
        except Exception as e:
            msg = f"Error subtracting climatology mean for {data_array.name}. Check dimensions/coords compatibility. Error: {e}"
            self.logger.error(msg, exc_info=True)
            raise ValueError(msg) from e # Raise error to stop processing this key

    def _prepare_climatology_means(self):
        """Calculates and returns a dictionary of climatology means, using a cache."""
        # Check cache first
        if self._climatology_means_cache is not None:
            self.logger.info("Using cached climatology means.")
            return self._climatology_means_cache

        # Proceed with calculation if not cached
        self.logger.info("Calculating climatology means (cache was empty)...")
        climatology_means = {}
        if not hasattr(self, 'retrieved_climatology_data') or not self.retrieved_climatology_data:
             self.logger.error("Climatology data dictionary is missing or empty. Cannot calculate means.")
             # Store empty dict in cache and return
             self._climatology_means_cache = {}
             return self._climatology_means_cache

        for key, data_clim_ds in self.retrieved_climatology_data.items():
             base_var_name, _ = self._parse_processed_key(key)
             if base_var_name in data_clim_ds:
                 da_clim = data_clim_ds[base_var_name]
                 try:
                     # Ensure 'time' dimension exists before taking mean
                     if 'time' in da_clim.dims:
                         climatology_means[key] = da_clim.mean(dim='time', skipna=True)
                         self.logger.debug(f"Calculated climatology mean for key: {key}")
                     else:
                         self.logger.warning(f"Climatology data for key '{key}' (variable '{base_var_name}') is missing 'time' dimension. Cannot calculate mean. Storing as is.")
                         # Store the non-time-varying climatology - anomaly calculation might still work if coords match
                         climatology_means[key] = da_clim
                 except Exception as e:
                     self.logger.error(f"Could not calculate climatology mean for key {key}: {e}. Skipping this key.", exc_info=True)
             else:
                 self.logger.error(f"Variable '{base_var_name}' not found in retrieved climatology data for key '{key}'. Skipping mean calculation for this key.")

        if not climatology_means:
            self.logger.error("Climatology mean calculation failed for all retrieved keys.")

        # Cache the results before returning
        self.logger.info("Caching calculated climatology means.")
        self._climatology_means_cache = climatology_means
        return climatology_means

    def spatial_acc(self, save_fig: bool = False, save_netcdf: bool = False):
        """
        Calculates and plots the spatial map of temporal Anomaly Correlation Coefficients (ACC)
        for all variables and levels retrieved.

        This method computes the correlation between the temporal anomaly time series
        of the main data and the reference data at each grid point.

        Args:
            save_fig (bool, optional): If True, saves the generated figures. Defaults to False.
            save_netcdf (bool, optional): If True, saves the ACC results as NetCDF files. Defaults to False.

        Returns:
            dict: A dictionary containing the ACC results (spatial maps) for each processed
                variable/level combination. Keys are processed variable names (e.g., 'q_85000', '2t')
                and values are the corresponding xarray DataArrays containing ACC values.
        """
        self.logger.info('Calculating and plotting spatial ACC maps.')
        if not hasattr(self, 'retrieved_data') or not hasattr(self, 'retrieved_data_ref'):
             self.logger.error("Data not retrieved. Call retrieve() first.")
             return {}
        climatology_means = self._prepare_climatology_means()
        if not climatology_means:
             self.logger.error("Cannot proceed without successfully calculated climatology means.")
             return {}
        common_keys = set(self.retrieved_data.keys()) & set(self.retrieved_data_ref.keys()) & set(climatology_means.keys())
        if not common_keys:
            self.logger.warning("No common data keys found with valid climatology means. Cannot calculate ACC.")
            return {}
        self.logger.info(f"Processing spatial ACC for keys: {list(common_keys)}")

        results = {}
        config_data = self.config.get('data', {})
        config_data_ref = self.config.get('data_ref', {})
        model = config_data.get('model', 'N/A'); exp = config_data.get('exp', 'N/A'); source = config_data.get('source', 'N/A')
        model_ref = config_data_ref.get('model', 'N/A'); exp_ref = config_data_ref.get('exp', 'N/A'); source_ref = config_data_ref.get('source', 'N/A')

        for processed_key in common_keys:
            base_var_name, level = self._parse_processed_key(processed_key)
            self.logger.info(f"Processing spatial ACC for key: {processed_key}")

            data_ds = self.retrieved_data[processed_key]
            data_ref_ds = self.retrieved_data_ref[processed_key]
            clim_mean_da = climatology_means[processed_key]

            if base_var_name not in data_ds or base_var_name not in data_ref_ds:
                self.logger.warning(f"Var '{base_var_name}' not in datasets for key '{processed_key}'. Skipping.")
                continue
            if not isinstance(clim_mean_da, xr.DataArray):
                 self.logger.warning(f"Climatology mean for key '{processed_key}' is not a DataArray. Skipping.")
                 continue

            try:
                # Get the DataArrays
                da = data_ds[base_var_name]
                da_ref = data_ref_ds[base_var_name]
                
                # Ensure all arrays have float32 coordinates
                da = self._ensure_float32_coords(da)
                da_ref = self._ensure_float32_coords(da_ref)
                clim_mean_da = self._ensure_float32_coords(clim_mean_da)
                self.logger.debug(f"Coordinates ensured float32 for {processed_key}")

                # Calculate Anomalies
                anom = self._calculate_anomalies(da, clim_mean_da)
                anom_ref = self._calculate_anomalies(da_ref, clim_mean_da)
                self.logger.debug(f"Anomalies calculated for {processed_key}")

                # Calculate spatial ACC map
                spatial_acc_map = xr.corr(anom, anom_ref, dim='time')
                spatial_acc_map.name = base_var_name
                self.logger.debug(f"Spatial ACC map calculated for {processed_key}")

                # Plotting
                vmin, vmax, cmap = -1, 1, 'RdBu_r'
                title_level_part = f" at {int(level / 100)} hPa" if level is not None else ""
                title = (f"Spatial ACC Map: {base_var_name}{title_level_part}\n"
                         f"{model} {exp} ({source}) vs {model_ref} {exp_ref} ({source_ref})\n"
                         f"{self.startdate} to {self.enddate} (Clim: {self.clim_startdate}-{self.clim_enddate})")
                fig, ax = plot_single_map(data=spatial_acc_map, return_fig=True, contour=True,
                                          title=title, sym=True, vmin=vmin, vmax=vmax, cmap=cmap)
                ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude")
                cbar_label = 'Anomaly Correlation Coefficient'
                if ax.collections: cbar = getattr(ax.collections[0], 'colorbar', None); cbar.set_label(cbar_label) if cbar else None
                elif ax.images: cbar = getattr(ax.images[0], 'colorbar', None); cbar.set_label(cbar_label) if cbar else None
                self.logger.info(f"Spatial ACC plot generated for {processed_key}")
                results[processed_key] = (fig, ax, xr.Dataset({base_var_name: spatial_acc_map}))

            except Exception as e:
                self.logger.error(f"Failed processing spatial ACC for key {processed_key}: {e}", exc_info=True)
                if processed_key in results: del results[processed_key]

        self.logger.info("Finished spatial ACC processing.")
        if save_fig:
             self.logger.info("Saving spatial ACC figures...")
             for key, res in results.items():
                 if res[0]: self._save_figure(res[0], key, 'spatial')
        if save_netcdf:
             self.logger.info("Saving spatial ACC netcdf files...")
             for key, res in results.items():
                 if res[2]: self._save_netcdf(res[2], key, 'spatial')

        return {key: res[2] for key, res in results.items() if res[2] is not None}

    def temporal_acc(self, save_fig: bool = False, save_netcdf: bool = False):
        """
        Calculates and plots the temporal evolution of the spatial pattern
        Anomaly Correlation Coefficient (ACC) for all variables and levels retrieved.

        This method computes the spatial correlation between the anomaly patterns
        of the main data and the reference data for each time step.

        Args:
            save_fig (bool, optional): If True, saves the generated figures. Defaults to False.
            save_netcdf (bool, optional): If True, saves the ACC results as NetCDF files. Defaults to False.

        Returns:
            dict: A dictionary containing the ACC time series results for each processed
                variable/level combination. Keys are processed variable names (e.g., 'q_85000', '2t')
                and values are the corresponding xarray DataArrays containing the ACC time series.
        """
        self.logger.info('Calculating and plotting temporal evolution of spatial ACC.')
        if not hasattr(self, 'retrieved_data') or not hasattr(self, 'retrieved_data_ref'):
             self.logger.error("Data not retrieved. Call retrieve() first.")
             return {}
        climatology_means = self._prepare_climatology_means()
        if not climatology_means:
             self.logger.error("Cannot proceed without successfully calculated climatology means.")
             return {}
        common_keys = set(self.retrieved_data.keys()) & set(self.retrieved_data_ref.keys()) & set(climatology_means.keys())
        if not common_keys:
            self.logger.warning("No common data keys found with valid climatology means. Cannot calculate ACC.")
            return {}
        self.logger.info(f"Processing temporal ACC for keys: {list(common_keys)}")
        results = {}
        config_data = self.config.get('data', {})
        config_data_ref = self.config.get('data_ref', {})
        model = config_data.get('model', 'N/A'); exp = config_data.get('exp', 'N/A'); source = config_data.get('source', 'N/A')
        model_ref = config_data_ref.get('model', 'N/A'); exp_ref = config_data_ref.get('exp', 'N/A'); source_ref = config_data_ref.get('source', 'N/A')

        for processed_key in common_keys:
            base_var_name, level = self._parse_processed_key(processed_key)
            self.logger.info(f"Processing temporal ACC for key: {processed_key}")

            data_ds = self.retrieved_data[processed_key]
            data_ref_ds = self.retrieved_data_ref[processed_key]
            clim_mean_da = climatology_means[processed_key]

            if base_var_name not in data_ds or base_var_name not in data_ref_ds:
                self.logger.warning(f"Var '{base_var_name}' not in datasets for key '{processed_key}'. Skipping.")
                continue
            if not isinstance(clim_mean_da, xr.DataArray):
                 self.logger.warning(f"Climatology mean for key '{processed_key}' is not a DataArray. Skipping.")
                 continue

            try:
                # Get the DataArrays
                da = data_ds[base_var_name]
                da_ref = data_ref_ds[base_var_name]

                # Ensure all arrays have float32 coordinates
                da = self._ensure_float32_coords(da)
                da_ref = self._ensure_float32_coords(da_ref)
                clim_mean_da = self._ensure_float32_coords(clim_mean_da)
                self.logger.debug(f"Coordinates ensured float32 for {processed_key}")

                # Calculate Anomalies
                anom = self._calculate_anomalies(da, clim_mean_da)
                anom_ref = self._calculate_anomalies(da_ref, clim_mean_da)
                self.logger.debug(f"Anomalies calculated for {processed_key}")

                # Determine spatial dimensions
                spatial_dims = [dim for dim in anom.dims if dim.lower() != 'time'] # Risky check
                if not spatial_dims:
                    self.logger.error(f"Could not determine spatial dims for {processed_key}. Skipping.")
                    continue
                self.logger.debug(f"Using spatial dimensions for correlation: {spatial_dims}")

                # Calculate temporal ACC time series
                temporal_acc_series = xr.corr(anom, anom_ref, dim=spatial_dims)
                temporal_acc_series.name = base_var_name
                self.logger.debug(f"Temporal ACC time series calculated for {processed_key}")

                # Plotting
                fig, ax = plt.subplots(figsize=(12, 6))
                temporal_acc_series.plot(ax=ax)
                time_coords = temporal_acc_series['time'].values
                if len(time_coords) > 1:
                    try:
                        inferred_freq = xr.infer_freq(temporal_acc_series.time)
                        date_format = mdates.DateFormatter('%Y-%m-%d %H:%M') if inferred_freq and any(f in inferred_freq for f in ['H','T','S']) else mdates.DateFormatter('%Y-%m-%d')
                    except:
                        if np.issubdtype(time_coords.dtype, np.datetime64):
                            time_diff_seconds = (time_coords[1] - time_coords[0]) / np.timedelta64(1, 's')
                            date_format = mdates.DateFormatter('%Y-%m-%d %H:%M') if time_diff_seconds < (24*3600) else mdates.DateFormatter('%Y-%m-%d')
                        else: date_format = mdates.DateFormatter('%Y-%m-%d')
                    ax.xaxis.set_major_formatter(date_format)
                    fig.autofmt_xdate()
                elif len(time_coords) == 1: self.logger.debug(f"Only one time point for {processed_key}.")
                ax.set_ylabel("Spatial Pattern ACC")
                ax.set_xlabel("Time")
                ax.set_ylim(-1, 1)
                ax.grid(True)
                title_level_part = f" at {int(level / 100)} hPa" if level is not None else ""
                title = (f"Temporal Evolution of Spatial ACC: {base_var_name}{title_level_part}\n"
                         f"{model} {exp} ({source}) vs {model_ref} {exp_ref} ({source_ref})\n"
                         f"{self.startdate} to {self.enddate} (Clim: {self.clim_startdate}-{self.clim_enddate})")
                ax.set_title(title)
                fig.tight_layout()
                self.logger.info(f"Temporal ACC plot generated for {processed_key}")
                results[processed_key] = (fig, ax, xr.Dataset({base_var_name: temporal_acc_series}))

            except Exception as e:
                self.logger.error(f"Failed processing temporal ACC for key {processed_key}: {e}", exc_info=True)
                if processed_key in results: del results[processed_key]

        self.logger.info("Finished temporal ACC processing.")
        if save_fig:
             self.logger.info("Saving temporal ACC figures...")
             for key, res in results.items():
                 if res[0]: self._save_figure(res[0], key, 'temporal')
        if save_netcdf:
             self.logger.info("Saving temporal ACC netcdf files...")
             for key, res in results.items():
                 if res[2]: self._save_netcdf(res[2], key, 'temporal')

        return {key: res[2] for key, res in results.items() if res[2] is not None}
