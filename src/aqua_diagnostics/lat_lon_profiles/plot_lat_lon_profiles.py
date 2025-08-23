import xarray as xr
from aqua.graphics import plot_seasonal_lat_lon_profiles
from aqua.logger import log_configure
from aqua.util import to_list
from aqua.graphics import plot_lat_lon_profiles
from aqua.diagnostics.core import OutputSaver

class PlotLatLonProfiles():
    """
    Class for plotting Lat-Lon Profiles diagnostics.
    This class provides methods to set data labels, description, title,
    and to plot the data. It handles data arrays regardless of their original
    temporal frequency, as temporal averaging is handled upstream.
    """
    def __init__(self, data=None, ref_data=None,
                 data_type='standard',
                 std_data=None,
                 ref_std_data=None,
                 loglevel: str = 'WARNING'):
        """
        Initialise the PlotLatLonProfiles class.
        This class is used to plot lat lon profiles data previously processed
        by the LatLonProfiles class.

        Args:
            data: Can be either:
                - List of temporally-averaged data arrays for standard plots
                - List of seasonal data [DJF, MAM, JJA, SON] for seasonal plots
            ref_data: Reference data (structure matches data based on data_type)
            data_type (str): 'standard' for single/multi-line plots, 'seasonal' for 4-panel seasonal plots
            std_data: Standard deviation data (structure matches data based on data_type)
            ref_std_data: Reference standard deviation data
            loglevel (str): Logging level. Default is 'WARNING'.
            
        Note:
            data_type determines how 'data' is interpreted:
            - 'standard': data should be list of DataArrays for single plot
            - 'seasonal': data should be [DJF, MAM, JJA, SON] for 4-panel seasonal plots
        """
        self.loglevel = loglevel
        self.logger = log_configure(loglevel, 'PlotLatLonProfiles')

        self.data_type = data_type

        # Store data based on type
        if data_type == 'standard':
            self.data = to_list(data) if data is not None else []
            self.ref_data = ref_data

        elif data_type == 'seasonal':
            self.data = data if data is not None else []  # Store seasonal data directly in unified interface
            self.ref_data = ref_data  # Store seasonal ref data directly
        else:
            raise ValueError(f"data_type must be 'standard' or 'seasonal', got '{data_type}'")
        
        self.std_data = std_data
        self.ref_std_data = ref_std_data
        
        self.len_data, self.len_ref = self._check_data_length()
        self.get_data_info()

    def set_data_labels(self):
        """
        Set the data labels for the plot.
        The labels are extracted from the data arrays attributes.

        Returns:
            data_labels (list): List of data labels for the plot.
        """
        data_labels = []
        # Handle case where len_data might be 0 or lists might be empty
        if self.len_data > 0 and len(self.models) > 0 and len(self.exps) > 0:
            for i in range(min(self.len_data, len(self.models), len(self.exps))):
                label = f'{self.models[i]} {self.exps[i]}'
                data_labels.append(label)
        else:
            # Fallback label
            data_labels = ['Unknown Model/Experiment']

        self.logger.debug('Data labels: %s', data_labels)
        return data_labels
    
    def set_ref_label(self):
        """
        Set the reference label for the plot.
        The label is extracted from the reference data array attributes.

        Returns:
            ref_label (str): Reference label for the plot.
        """
        ref_label = None
        
        if self.ref_data is not None:
            model = self.ref_data.attrs.get('AQUA_model', 'Unknown')
            exp = self.ref_data.attrs.get('AQUA_exp', 'Unknown')
            ref_label = f'{model} {exp}'
        
        self.logger.debug('Reference label: %s', ref_label)
        return ref_label
    
    def set_seasonal_data_labels(self):
        """
        Set the data labels for seasonal plots.
        This method works with the unified data interface.

        Returns:
            data_labels (list): List of data labels for the seasonal plot.
        """
        data_labels = []
        
        if self.data_type == 'seasonal' and self.data and len(self.data) > 0:
            # Check the first season to understand the data structure
            first_season = self.data[0]
            
            if isinstance(first_season, list) and len(first_season) >= 1:
                # Extract labels from the first DataArray of the first season
                first_data = first_season[0]
                if hasattr(first_data, 'AQUA_model') and hasattr(first_data, 'AQUA_exp'):
                    model_label = f'{first_data.AQUA_model} {first_data.AQUA_exp}'
                    data_labels.append(model_label)
                else:
                    data_labels.append('Model Data')
                
                # If there's a second DataArray, it's reference data
                if len(first_season) >= 2:
                    ref_data = first_season[1]
                    if hasattr(ref_data, 'AQUA_model') and hasattr(ref_data, 'AQUA_exp'):
                        ref_label = f'{ref_data.AQUA_model} {ref_data.AQUA_exp}'
                        data_labels.append(ref_label)
                    else:
                        data_labels.append('Reference Data')
            else:
                # Simple case: single DataArray per season
                if hasattr(first_season, 'AQUA_model') and hasattr(first_season, 'AQUA_exp'):
                    data_labels.append(f'{first_season.AQUA_model} {first_season.AQUA_exp}')
                else:
                    data_labels.append('Unknown Data')
        else:
            # Fallback to standard data labels
            data_labels = self.set_data_labels()
        
        self.logger.debug('Seasonal data labels: %s', data_labels)
        return data_labels
    
    def get_data_info(self):
        """
        Extract metadata from data arrays based on data_type.
        """
        if self.data and len(self.data) > 0:
            if self.data_type == 'standard':
                # Standard mode: extract from self.data
                if len(self.data) == 1:
                    if hasattr(self.data[0], 'AQUA_catalog'):
                        self.catalogs = [self.data[0].AQUA_catalog]
                        self.models = [self.data[0].AQUA_model] 
                        self.exps = [self.data[0].AQUA_exp]
                        self.logger.debug(f'Data item metadata extracted: {self.models[0]} {self.exps[0]}')
                    else:
                        self.catalogs = []
                        self.models = []
                        self.exps = []
                        self.logger.warning('Data item has no metadata attributes')
                else:
                    self.catalogs = [d.AQUA_catalog for d in self.data]
                    self.models = [d.AQUA_model for d in self.data]
                    self.exps = [d.AQUA_exp for d in self.data]
                    self.logger.debug(f'Multiple data items metadata extracted: {len(self.data)} items')
                    
            elif self.data_type == 'seasonal':
                # Seasonal mode: extract from first season in self.data
                if len(self.data) > 0:
                    first_season = self.data[0]
                    
                    if isinstance(first_season, list) and len(first_season) > 0:
                        # Multi-variable case: each season contains a list of DataArrays
                        first_data = first_season[0]
                        if hasattr(first_data, 'AQUA_catalog'):
                            self.catalogs = [first_data.AQUA_catalog]
                            self.models = [first_data.AQUA_model]
                            self.exps = [first_data.AQUA_exp]
                            self.logger.debug(f'Seasonal data metadata extracted from first season: {self.models[0]} {self.exps[0]}')
                        else:
                            self.catalogs = []
                            self.models = []
                            self.exps = []
                            self.logger.warning('Seasonal data (first season, first item) has no metadata attributes')
                    else:
                        # Simple case: each season is a single DataArray (most common)
                        if hasattr(first_season, 'AQUA_catalog'):
                            self.catalogs = [first_season.AQUA_catalog]
                            self.models = [first_season.AQUA_model]
                            self.exps = [first_season.AQUA_exp]
                            self.logger.debug(f'Seasonal data metadata extracted: {self.models[0]} {self.exps[0]}')
                        else:
                            self.catalogs = []
                            self.models = []
                            self.exps = []
                            self.logger.warning('Seasonal data (first season) has no metadata attributes')
                else:
                    self.catalogs = []
                    self.models = []
                    self.exps = []
                    self.logger.warning('No seasonal data available')
        else:
            # Fallback
            self.logger.warning('No data available for metadata extraction')
            self.catalogs = []
            self.models = []
            self.exps = []
        
        self.logger.debug(f'Catalogs: {self.catalogs}')
        self.logger.debug(f'Models: {self.models}')
        self.logger.debug(f'Experiments: {self.exps}')
        
        self.std_startdate = None
        self.std_enddate = None

        if self.std_data is not None:
            self.std_startdate = self.std_data.std_startdate if hasattr(self.std_data, 'std_startdate') else None
            self.std_enddate = self.std_data.std_enddate if hasattr(self.std_data, 'std_enddate') else None
        
        self.logger.debug(f'Standard deviation dates: {self.std_startdate} - {self.std_enddate}')

    def plot_lat_lon_profiles(self, data_labels=None, ref_label=None, title=None):
        """
        Plot latitude or longitude profiles of data.
        
        Args:
            data_labels (list, optional): Labels for the data.
            ref_label (str, optional): Label for the reference data.
            title (str, optional): Title for the plot.
            
        Returns:
            tuple: Matplotlib figure and axes objects.
        """
        # Use the main data
        if not self.data or len(self.data) == 0:
            raise ValueError("No data available for plotting")
        
        # Clean data by removing any remaining time dimension if it has only one timestep
        cleaned_data = []
        for i, d in enumerate(self.data):
            if d is not None:
                # If data has a time dimension with only one timestep, remove it
                if 'time' in d.dims and d.sizes.get('time', 0) == 1:
                    d_cleaned = d.isel(time=0, drop=True)
                    self.logger.debug(f"Removed single time dimension from data {i}")
                else:
                    d_cleaned = d
                cleaned_data.append(d_cleaned)
                self.logger.debug(f"Data {i}: shape={d_cleaned.shape}, dims={d_cleaned.dims}")
            else:
                cleaned_data.append(None)
                self.logger.debug(f"Data {i}: None")
        
        # Clean reference data in the same way
        cleaned_ref_data = self.ref_data
        if self.ref_data is not None:
            if 'time' in self.ref_data.dims and self.ref_data.sizes.get('time', 0) == 1:
                cleaned_ref_data = self.ref_data.isel(time=0, drop=True)
                self.logger.debug("Removed single time dimension from reference data")
            self.logger.debug(f"Ref data: shape={cleaned_ref_data.shape}, dims={cleaned_ref_data.dims}")
        else:
            self.logger.debug("Ref data: None")
        
        # Call the graphics function with cleaned data
        return plot_lat_lon_profiles(
            data=cleaned_data,
            ref_data=cleaned_ref_data,
            std_data=self.std_data,
            ref_std_data=self.ref_std_data,
            data_labels=data_labels,
            ref_label=ref_label,
            title=title,
            loglevel=self.loglevel
        )
    
    def plot_multi_line_profiles(self, data_labels=None, ref_label=None, title=None):
        """
        Plot multiple latitude or longitude profiles of data.
        
        Args:
            data_labels (list, optional): Labels for the data.
            ref_label (str, optional): Label for the reference data.
            title (str, optional): Title for the plot.
            
        Returns:
            tuple: Matplotlib figure and axes objects.
        """
        # Use the main data
        if not self.data or len(self.data) == 0:
            raise ValueError("No data available for plotting")
        
        # Call the graphics function with reference data
        return plot_lat_lon_profiles(
            data=self.data,
            ref_data=self.ref_data,
            std_data=self.std_data,
            ref_std_data=self.ref_std_data,
            data_labels=data_labels,
            ref_label=ref_label,
            title=title,
            loglevel=self.loglevel
        )
    
    def save_plot(self, fig, var: str = None, description: str = None, region: str = None, rebuild: bool = True,
                  outputdir: str = './', dpi: int = 300, format: str = 'png', diagnostic: str = None):
        """
        Save the plot to a file.

        Args:
            fig (matplotlib.figure.Figure): Figure object.
            var (str): Variable name to be used in the title and description.
            description (str): Description of the plot.
            region (str): Region to be used in the title and description.
            rebuild (bool): If True, rebuild the plot even if it already exists.
            outputdir (str): Output directory to save the plot.
            dpi (int): Dots per inch for the plot.
            format (str): Format of the plot ('png' or 'pdf'). Default is 'png'.
            diagnostic (str): Diagnostic name to be used in the filename as diagnostic_product.
        """
        # Check if we have valid metadata, otherwise use defaults
        if hasattr(self, 'catalogs') and len(self.catalogs) > 0 and len(self.models) > 0 and len(self.exps) > 0:
            catalog = self.catalogs[0]
            model = self.models[0] 
            exp = self.exps[0]
        else:
            # Fallback values when metadata is not available
            catalog = 'unknown_catalog'
            model = 'unknown_model'
            exp = 'unknown_exp'
            self.logger.warning('Metadata not available, using default values for saving')

        # Default diagnostic for lat_lon_profiles if not specified
        if diagnostic is None:
            diagnostic = 'lat_lon_profiles'

        outputsaver = OutputSaver(diagnostic='lat_lon_profiles',
                                  catalog=catalog,
                                  model=model,
                                  exp=exp,
                                  outdir=outputdir,
                                  loglevel=self.loglevel)

        metadata = {"Description": description, "dpi": dpi }
        extra_keys = {'diagnostic_product': diagnostic}

        if var is not None:
            extra_keys.update({'var': var})
        if region is not None:
            region = region.replace(' ', '').lower() if region is not None else None
            extra_keys.update({'region': region})

        if format == 'png':
            outputsaver.save_png(fig, diagnostic_product=diagnostic, extra_keys=extra_keys, metadata=metadata)
        elif format == 'pdf':
            outputsaver.save_pdf(fig, diagnostic_product=diagnostic, extra_keys=extra_keys, metadata=metadata)
        else:
            raise ValueError(f'Format {format} not supported. Use png or pdf.')

    def _check_data_length(self):
        """
        Check the length of the data arrays and reference data based on data_type.
        Returns:
            tuple: (length of data arrays, length of reference data)
        """
        len_data = len(self.data) if self.data else 0
        
        if self.data_type == 'standard':
            len_ref = 1 if self.ref_data is not None else 0
        elif self.data_type == 'seasonal':
            len_ref = len(self.ref_data) if self.ref_data else 0
        else:
            len_ref = 0
        
        self.logger.debug(f'Data type: {self.data_type}, Data length: {len_data}, Reference length: {len_ref}')
        return len_data, len_ref

    def set_title(self, region: str = None, var: str = None, units: str = None):
        """
        Set the title for the plot.
        Specialized for Lat-Lon Profiles diagnostic.

        Args:
            region (str): Region to be used in the title.
            var (str): Variable name to be used in the title.
            units (str): Units of the variable to be used in the title.
            
        Returns:
            title (str): Title for the plot.
        """
        title = 'Lat-Lon Profiles '
        if var is not None:
            title += f'for {var} '

        if units is not None:
            title += f'[{units}] '

        if region is not None:
            title += f'[{region}] '

        if self.len_data == 1:
            title += f'for {self.catalogs[0]} {self.models[0]} {self.exps[0]} '

        self.logger.debug('Title: %s', title)
        return title

    def set_description(self, region: str = None):
        """
        Set the caption for the plot.
        Specialized for Lat-Lon Profiles diagnostic.
        """
        description = 'lat_lon_profiles '
        if region is not None:
            description += f'for region {region} '

        # Check if we have enough metadata for all data items
        num_items = min(len(self.catalogs), len(self.models), len(self.exps)) if hasattr(self, 'catalogs') else 0
        
        for i in range(min(self.len_data, num_items)):
            description += f'for {self.catalogs[i]} {self.models[i]} {self.exps[i]} '
        
        # If we don't have enough metadata, add a generic description
        if num_items < self.len_data:
            remaining = self.len_data - num_items
            description += f'and {remaining} additional dataset(s) '

        if hasattr(self, 'std_startdate') and self.std_startdate is not None and hasattr(self, 'std_enddate') and self.std_enddate is not None:
            description += f'with standard deviation from {self.std_startdate} to {self.std_enddate} '

        self.logger.debug('Description: %s', description)
        return description

    def run(self, 
            var: str, 
            units: str = None, 
            region: str = None, 
            outputdir: str = './',
            rebuild: bool = True, 
            dpi: int = 300, 
            format: str = 'png', 
            plot_type: str = 'standard',
            plot_std: bool = False,
            std_maps: list = None,
            ref_std_maps: list = None):
        """
        Run the PlotLatLonProfiles class.

        Args:
            var (str): Variable name to be used in the title and description.
            units (str): Units of the variable to be used in the title.
            region (str): Region to be used in the title and description.
            outputdir (str): Output directory to save the plot.
            rebuild (bool): If True, rebuild the plot even if it already exists.
            dpi (int): Dots per inch for the plot.
            format (str): Format of the plot ('png' or 'pdf'). Default is 'png'.
            plot_type (str): Type of plot ('standard' or 'seasonal'). Default is 'standard'.
        """
        self.logger.info('Running PlotLatLonProfiles')
        
        if plot_type == 'seasonal':
            # Only plot the 4 seasonal subplots (no annual)
            data_labels = self.set_seasonal_data_labels()
            description = self.set_description(region=region)
            title = self.set_title(region=region, var=var, units=units)
            
            # Call the updated seasonal plot function with only 4 seasons
            fig, axs = self.plot_seasonal_lines(data_labels=data_labels, 
                                                title=title, 
                                                std_maps=std_maps, 
                                                ref_std_maps=ref_std_maps)
            
            # Save the plot
            region_short = region.replace(' ', '').lower() if region is not None else None
            self.save_plot(fig, var=var, description=description, region=region_short, 
                        rebuild=rebuild, outputdir=outputdir, dpi=dpi, format=format, 
                        diagnostic='lat_lon_profiles_seasonal')
        else:
            # Standard single profile plotting
            data_label = self.set_data_labels()
            ref_label = self.set_ref_label()
            description = self.set_description(region=region)
            title = self.set_title(region=region, var=var, units=units)
            
            # Include std information in title/description if available
            if plot_std and (self.std_data is not None or self.ref_std_data is not None):
                title += " (±2σ)"
                description += " with standard deviation bands"

            fig, _ = self.plot_lat_lon_profiles(data_labels=data_label, ref_label=ref_label, title=title)
            
            region_short = region.replace(' ', '').lower() if region is not None else None
            self.save_plot(fig, var=var, description=description, region=region_short, rebuild=rebuild,
                        outputdir=outputdir, dpi=dpi, format=format, diagnostic='lat_lon_profiles')
        
        self.logger.info('PlotLatLonProfiles completed successfully')

    def plot_seasonal_lines(self, 
                            data_labels=None, 
                            title=None, 
                            style=None,
                            std_maps=None, 
                            ref_std_maps=None):
        """
        Plot seasonal means using plot_seasonal_lat_lon_profiles.
        Creates a 4-panel plot with DJF, MAM, JJA, SON only (no annual).

        Args:
            data_labels (list): List of data labels.
            title (str): Title of the plot.
            style (str): Plotting style.
            std_maps (list): Standard deviation data for each season.
            ref_std_maps (list): Reference standard deviation data for each season.

        Returns:
            fig (matplotlib.figure.Figure): Figure object.
            axs (list): List of axes objects.
        """
        if self.data_type != 'seasonal':
            raise ValueError("plot_seasonal_lines() can only be used with data_type='seasonal'")
        
        if not self.data or len(self.data) < 4:
            raise ValueError("Seasonal data must contain at least 4 elements: [DJF, MAM, JJA, SON]")
        
        # Use first 4 seasons only (DJF, MAM, JJA, SON)
        seasonal_data_only = self.data[:4]
        seasonal_ref_only = self.ref_data[:4] if self.ref_data and len(self.ref_data) >= 4 else None
        
        # Handle std data - use first 4 seasons if available
        seasonal_std_only = None
        if std_maps:
            seasonal_std_only = std_maps[:4] if len(std_maps) >= 4 else std_maps
        elif hasattr(self, 'std_seasonal_annual_data') and self.std_seasonal_annual_data:
            seasonal_std_only = self.std_seasonal_annual_data[:4]
        
        seasonal_ref_std_only = None
        if ref_std_maps:
            seasonal_ref_std_only = ref_std_maps[:4] if len(ref_std_maps) >= 4 else ref_std_maps
        
        self.logger.debug(f'Plotting {len(seasonal_data_only)} seasons')
        
        return plot_seasonal_lat_lon_profiles(
            maps=seasonal_data_only,
            ref_maps=seasonal_ref_only,
            std_maps=seasonal_std_only,
            ref_std_maps=seasonal_ref_std_only,
            data_labels=data_labels,
            title=title,
            style=style,
            loglevel=self.loglevel
        )
    
    def plot_annual_mean(self, data_labels=None, ref_label=None, title=None):
        """
        Plot only the annual mean as a separate single plot.
        
        Args:
            data_labels (list, optional): Labels for the data.
            ref_label (str, optional): Label for the reference data.
            title (str, optional): Title for the plot.
            
        Returns:
            tuple: Matplotlib figure and axes objects.
        """
        if self.data_type != 'seasonal':
            raise ValueError("plot_annual_mean() can only be used with seasonal data containing annual means")
        
        if not self.data or len(self.data) < 5:
            raise ValueError("Seasonal data must contain at least 5 elements to access annual data (index 4)")
        
        # Get annual data (index 4: [DJF, MAM, JJA, SON, Annual])
        annual_data = self.data[4]
        annual_ref = self.ref_data[4] if self.ref_data and len(self.ref_data) > 4 else None
        
        # Call the basic lat_lon_profiles plotting function
        return plot_lat_lon_profiles(
            data=annual_data,
            ref_data=annual_ref,
            data_labels=data_labels,
            ref_label=ref_label,
            title=title,
            loglevel=self.loglevel
        )

    def run_multi_seasonal(self, var_names: list, units_list: list = None, 
                        plot_type: str = 'seasonal_multi'):
        """
        Run multi-variable seasonal plotting.

        Args:
            var_names (list): List of variable names to be plotted.
            units_list (list): List of units corresponding to each variable.
            plot_type (str): Type of plot ('seasonal_multi' for multi-variable seasonal comparison).

        Returns:
            fig (matplotlib.figure.Figure): Figure object containing the multi-variable seasonal plot.
            axs (list): List of axes objects for the multi-variable seasonal plot.
        """
        if self.data_type != 'seasonal':
            raise ValueError("run_multi_seasonal() can only be used with data_type='seasonal'")
        
        if not self.data:
            raise ValueError("No seasonal data available.")
        
        # Create combined labels
        data_labels = []
        for i, var_name in enumerate(var_names):
            unit = units_list[i] if units_list and i < len(units_list) else ""
            label = f"{var_name} ({unit})" if unit else var_name
            data_labels.append(label)
        
        # Use the unified data interface
        fig, axs = plot_seasonal_and_annual_data(
            maps=self.data,  # Use unified self.data
            ref_maps=self.ref_data,  # Use unified self.ref_data
            plot_type='seasonal',
            data_labels=data_labels,
            loglevel=self.loglevel
        )
        
        title = f"Multi-variable Seasonal Comparison: {', '.join(var_names)}"
        fig.suptitle(title, fontsize=14, fontweight='bold')
        
        # Specialized save_plot for multi-variable seasonal comparison
        self.save_plot(fig, var='_'.join(var_names), 
                    description=f"Multi-variable seasonal comparison: {', '.join(var_names)}",
                    diagnostic='lat_lon_profiles_seasonal_multi')
        
        return fig, axs
