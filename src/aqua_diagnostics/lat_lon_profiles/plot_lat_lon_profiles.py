import xarray as xr
from aqua.graphics import plot_seasonal_and_annual_data
from aqua.logger import log_configure
from aqua.util import to_list
from aqua.graphics import plot_lat_lon_profiles
from aqua.diagnostics.core import OutputSaver

class PlotLatLonProfiles():
    """
    Class for plotting Lat-Lon Profiles diagnostics.
    This class provides methods to set data labels, description, title,
    and to plot the data. It also handles the initialization of the class
    with various data arrays for different frequencies (hourly, daily,
    monthly, annual, seasonal annual) and their standard deviations.
    """
    def __init__(self, hourly_data=None, daily_data=None,
             monthly_data=None, annual_data=None,
             seasonal_annual_data=None,
             seasonal_annual_ref_data=None,
             ref_hourly_data=None, ref_daily_data=None,
             ref_monthly_data=None, ref_annual_data=None,
             std_hourly_data=None, std_daily_data=None,
             std_monthly_data=None, std_annual_data=None,
             loglevel: str = 'WARNING'):
        """
        Initialise the PlotLatLonProfiles class.
        This class is used to plot lat lon profiles data previously processed
        by the LatLonProfiles class.

        Any subset of frequency can be provided, however the order and length
        of the list of data arrays must be the same for each frequency.

        Note: Currently, only monthly and annual data are supported.
        Additionally, only one reference data array is supported for each frequency.

        Args:
            hourly_data (list): List of hourly data arrays.
            daily_data (list): List of daily data arrays.
            monthly_data (list): List of monthly data arrays.
            annual_data (list): List of annual data arrays.
            seasonal_annual_data (list): List of seasonal and annual means [DJF, MAM, JJA, SON, Annual].
            ref_hourly_data (xr.DataArray): Reference hourly data array.
            ref_daily_data (xr.DataArray): Reference daily data array.
            ref_monthly_data (xr.DataArray): Reference monthly data array.
            ref_annual_data (xr.DataArray): Reference annual data array.
            std_hourly_data (xr.DataArray): Standard deviation hourly data array.
            std_daily_data (xr.DataArray): Standard deviation daily data array.
            std_monthly_data (xr.DataArray): Standard deviation monthly data array.
            std_annual_data (xr.DataArray): Standard deviation annual data array.
            loglevel (str): Logging level. Default is 'WARNING'.
        """
        self.loglevel = loglevel
        self.logger = log_configure(loglevel, 'PlotLatLonProfiles')

        # TODO: support hourly and daily data
        for data in [hourly_data, daily_data, ref_hourly_data, ref_daily_data,
                    std_hourly_data, std_daily_data]:
            if data is not None:
                raise NotImplementedError("Hourly and daily data are not supported yet.")

        self.monthly_data = to_list(monthly_data) if monthly_data is not None else []
        self.annual_data = to_list(annual_data) if annual_data is not None else []
        self.seasonal_annual_data = seasonal_annual_data  
        self.seasonal_annual_ref_data = seasonal_annual_ref_data 

        # TODO: support ref list
        self.ref_monthly_data = ref_monthly_data if isinstance(ref_monthly_data, xr.DataArray) else (ref_monthly_data[0] if ref_monthly_data is not None else None)
        self.ref_annual_data = ref_annual_data if isinstance(ref_annual_data, xr.DataArray) else (ref_annual_data[0] if ref_annual_data is not None else None)

        self.std_monthly_data = (
            std_monthly_data if (std_monthly_data is not None and isinstance(std_monthly_data, xr.DataArray))
            else (std_monthly_data[0] if std_monthly_data is not None else None)
        )

        self.std_annual_data = (
            std_annual_data if (std_annual_data is not None and isinstance(std_annual_data, xr.DataArray))
            else (std_annual_data[0] if std_annual_data is not None else None)
        )

        self.len_data, self.len_ref = self._check_data_length()
        self.get_data_info()

    # [Copia qui tutti i metodi da PlotBaseMixin:]
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
        
        # Check for reference data in order of priority: monthly, annual
        ref_data = self.ref_monthly_data if self.ref_monthly_data is not None else self.ref_annual_data
        
        if ref_data is not None:
            model = ref_data.attrs.get('AQUA_model', 'Unknown')
            exp = ref_data.attrs.get('AQUA_exp', 'Unknown')
            ref_label = f'{model} {exp}'
        
        self.logger.debug('Reference label: %s', ref_label)
        return ref_label
    
    def set_seasonal_data_labels(self):
        """
        Set the data labels for seasonal plots that may include reference data.
        This method handles the case where seasonal_annual_data contains both model and reference data.

        Returns:
            data_labels (list): List of data labels for the seasonal plot.
        """
        data_labels = []
        
        if self.seasonal_annual_data and len(self.seasonal_annual_data) > 0:
            # Check the first season to understand the data structure
            first_season = self.seasonal_annual_data[0]
            
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
                
                # If there are more than 2 DataArrays, add labels for them
                for i in range(2, len(first_season)):
                    extra_data = first_season[i]
                    if hasattr(extra_data, 'AQUA_model') and hasattr(extra_data, 'AQUA_exp'):
                        extra_label = f'{extra_data.AQUA_model} {extra_data.AQUA_exp}'
                        data_labels.append(extra_label)
                    else:
                        data_labels.append(f'Data {i+1}')
            else:
                # Fallback
                data_labels = ['Unknown Data']
        else:
            # No seasonal data, fall back to regular method
            data_labels = self.set_data_labels()
        
        self.logger.debug('Seasonal data labels: %s', data_labels)
        return data_labels
    
    def get_data_info(self):
        """
        We extract the data needed for labels, description etc
        from the data arrays attributes.

        The attributes are:
        - AQUA_catalog
        - AQUA_model
        - AQUA_exp
        - std_startdate
        - std_enddate
        """
        # Check monthly and annual data first
        for data in [self.monthly_data, self.annual_data]:
            if data is not None and len(data) > 0:
                if len(data) == 1:
                    if hasattr(data[0], 'AQUA_catalog'):
                        self.catalogs = [data[0].AQUA_catalog]
                        self.models = [data[0].AQUA_model]
                        self.exps = [data[0].AQUA_exp]
                    else:
                        self.catalogs = []
                        self.models = []
                        self.exps = []
                else:
                    self.catalogs = [d.AQUA_catalog for d in data]
                    self.models = [d.AQUA_model for d in data]
                    self.exps = [d.AQUA_exp for d in data]
                break
        else:
            # If no monthly or annual data, check seasonal_annual_data
            if self.seasonal_annual_data is not None and len(self.seasonal_annual_data) > 0:
                # Check if seasonal_annual_data is a simple list of DataArrays
                # or a nested list (multi-variable case)
                first_item = self.seasonal_annual_data[0]
                
                if isinstance(first_item, list):
                    # Multi-variable case: [[DJF_data1, DJF_data2, ...], [MAM_data1, ...], ...]
                    # Take metadata from the first DataArray of the first season
                    if len(first_item) > 0 and hasattr(first_item[0], 'AQUA_catalog'):
                        self.catalogs = [first_item[0].AQUA_catalog]
                        self.models = [first_item[0].AQUA_model]
                        self.exps = [first_item[0].AQUA_exp]
                    else:
                        self.catalogs = []
                        self.models = []
                        self.exps = []
                else:
                    # Simple case: [DJF_data, MAM_data, JJA_data, SON_data, Annual_data]
                    if hasattr(first_item, 'AQUA_catalog'):
                        self.catalogs = [first_item.AQUA_catalog]
                        self.models = [first_item.AQUA_model]
                        self.exps = [first_item.AQUA_exp]
                    else:
                        self.catalogs = []
                        self.models = []
                        self.exps = []
            else:
                # Fallback if no data is available
                self.logger.warning('No data available for metadata extraction, using empty lists')
                self.catalogs = []
                self.models = []
                self.exps = []
        
        self.logger.debug(f'Catalogs: {self.catalogs}')
        self.logger.debug(f'Models: {self.models}')
        self.logger.debug(f'Experiments: {self.exps}')
        
        self.std_startdate = None
        self.std_enddate = None

        for std in [self.std_monthly_data, self.std_annual_data]:
            if std is not None:
                self.std_startdate = std.std_startdate if std.std_startdate is not None else None
                self.std_enddate = std.std_enddate if std.std_enddate is not None else None
                break
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
        # Get the appropriate data (monthly has priority over annual)
        if self.monthly_data:
            data_to_plot = self.monthly_data
            ref_data_to_plot = self.ref_monthly_data
        elif self.annual_data:
            data_to_plot = self.annual_data
            ref_data_to_plot = self.ref_annual_data
        else:
            raise ValueError("No data available for plotting")
        
        # Validate data before plotting
        if not data_to_plot or len(data_to_plot) == 0:
            raise ValueError("No valid data arrays found for plotting")
        
        # Log data information for debugging
        self.logger.debug(f"Data to plot: {len(data_to_plot)} arrays")
        for i, d in enumerate(data_to_plot):
            if d is not None:
                self.logger.debug(f"  Data {i}: shape={d.shape}, dims={d.dims}")
            else:
                self.logger.debug(f"  Data {i}: None")
        
        if ref_data_to_plot is not None:
            self.logger.debug(f"Ref data: shape={ref_data_to_plot.shape}, dims={ref_data_to_plot.dims}")
        else:
            self.logger.debug("Ref data: None")
        
        # Call the graphics function with reference data
        return plot_lat_lon_profiles(
            data=data_to_plot,
            ref_data=ref_data_to_plot,
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
        # Get the appropriate data (monthly has priority over annual)
        if self.monthly_data:
            data_to_plot = self.monthly_data
            ref_data_to_plot = self.ref_monthly_data
        elif self.annual_data:
            data_to_plot = self.annual_data
            ref_data_to_plot = self.ref_annual_data
        else:
            raise ValueError("No data available for plotting")
        
        # Call the graphics function with reference data
        return plot_lat_lon_profiles(
            data=data_to_plot,
            ref_data=ref_data_to_plot,
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
                                rebuild=rebuild,
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
        Check the length of the data arrays and reference data.
        Returns:
            tuple: (length of data arrays, length of reference data)
        """
        len_data = 0
        len_ref = 0
        
        # Check main data
        for data_list in [self.monthly_data, self.annual_data]:
            if data_list:
                len_data = max(len_data, len(data_list))
        
        # Check reference data
        if self.ref_monthly_data is not None or self.ref_annual_data is not None:
            len_ref = 1
        
        self.logger.debug(f'Data length: {len_data}, Reference length: {len_ref}')
        return len_data, len_ref

    def set_title(self, region: str = None, var: str = None, units: str = None):
        """
        Set the title for the plot.
        Specialized for Lat-Lon Profiles diagnostic.
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

        for i in range(self.len_data):
            description += f'for {self.catalogs[i]} {self.models[i]} {self.exps[i]} '

        if self.std_startdate is not None and self.std_enddate is not None:
            description += f'with standard deviation from {self.std_startdate} to {self.std_enddate} '

        self.logger.debug('Description: %s', description)
        return description

    def run(self, var: str, units: str = None, region: str = None, outputdir: str = './',
        rebuild: bool = True, dpi: int = 300, format: str = 'png', plot_type: str = 'standard'):
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
            # Use specialized method for seasonal data labels
            data_labels = self.set_seasonal_data_labels()
            description = self.set_description(region=region)
            title = self.set_title(region=region, var=var, units=units)
            
            fig, axs = plot_seasonal_and_annual_data(
                maps=self.seasonal_annual_data,
                ref_maps=self.seasonal_annual_ref_data,
                plot_type='seasonal',
                data_labels=data_labels,
                title=title,
                loglevel=self.loglevel
            )
            
            # Add title to the figure
            if title:
                fig.suptitle(title, fontsize=14, fontweight='bold', y=0.98)
        else:
            # Standard single profile plotting
            data_label = self.set_data_labels()
            ref_label = self.set_ref_label()
            description = self.set_description(region=region)
            title = self.set_title(region=region, var=var, units=units)
            
            fig, _ = self.plot_lat_lon_profiles(data_labels=data_label, ref_label=ref_label, title=title)
        
        region_short = region.replace(' ', '').lower() if region is not None else None
        diagnostic_suffix = '_seasonal' if plot_type == 'seasonal' else ''
        
        # Specialized save_plot for Lat-Lon Profiles
        self.save_plot(fig, var=var, description=description, region=region_short, rebuild=rebuild,
                    outputdir=outputdir, dpi=dpi, format=format, 
                    diagnostic=f'lat_lon_profiles{diagnostic_suffix}')
        
        self.logger.info('PlotLatLonProfiles completed successfully')

    def plot_seasonal_annual_lines(self, data_labels=None, title=None, style=None):
        """
        Plot seasonal and annual means using multiple_lines.py.
        Creates a 5-panel plot with DJF, MAM, JJA, SON and Annual mean.

        Args:
            data_labels (list): List of data labels.
            title (str): Title of the plot.
            style (str): Plotting style.

        Returns:
            fig (matplotlib.figure.Figure): Figure object.
            axs (list): List of axes objects.
        """
        
        if self.seasonal_annual_data is None:
            self.logger.error('No seasonal and annual data available. Compute them first.')
            return None, None
        
        self.logger.info('Plotting seasonal and annual means using multiple_lines')
        
        # Prepare data in the format expected by plot_seasonal_and_annual_data
        # Structure: [[DJF], [MAM], [JJA], [SON], [Annual]]
        maps = [[self.seasonal_annual_data[i]] for i in range(5)]
        
        # Use plot_seasonal_and_annual_data to create the 5-panel seasonal plot
        fig, axs = plot_seasonal_and_annual_data(maps=maps,
                             plot_type='seasonal',
                             style=style,
                             loglevel=self.loglevel,
                             data_labels=data_labels)
        
        if title:
            fig.suptitle(title, fontsize=16, y=0.98)
        
        return fig, axs

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
        if self.seasonal_annual_data is None:
            raise ValueError("No seasonal data available. Run compute_seasonal_and_annual_means first.")
        
        # Create combined labels
        data_labels = []
        for i, var_name in enumerate(var_names):
            unit = units_list[i] if units_list and i < len(units_list) else ""
            label = f"{var_name} ({unit})" if unit else var_name
            data_labels.append(label)
        
        # Use the enhanced plot_seasonal_and_annual_data for seasonal multi-variable plotting
        fig, axs = plot_seasonal_and_annual_data(
            maps=self.seasonal_annual_data,
            ref_maps=self.seasonal_annual_ref_data,
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
