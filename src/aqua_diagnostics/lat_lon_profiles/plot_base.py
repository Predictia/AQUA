import xarray as xr

from aqua.logger import log_configure
from aqua.util import to_list
from aqua.graphics import plot_lat_lon_profiles
from aqua.diagnostics.core import OutputSaver

class PlotBaseMixin():
    """
    Base class for plotting lat lon profiles data.
    This class provides methods to set data labels, description, title,
    and to plot the data. It also handles the initialization of the class
    with various data arrays for different frequencies (hourly, daily,
    monthly, annual, seasonal annual) and their standard deviations.
    """
    def __init__(self, hourly_data=None, daily_data=None,
                 monthly_data=None, annual_data=None,
                 seasonal_annual_data=None,
                 std_hourly_data=None, std_daily_data=None,
                 std_monthly_data=None, std_annual_data=None,
                 loglevel: str = 'WARNING'):
        """
        Initialize the PlotBaseMixin class.
        This class is used to plot lat lon profiles data previously processed
        by the LatLonProfiles class.

        Any subset of frequency can be provided, however the order and length
        of the list of data arrays must be the same for each frequency.

        Note: Currently, only monthly and annual data are supported.

        Args:
            hourly_data (list): List of hourly data arrays.
            daily_data (list): List of daily data arrays.
            monthly_data (list): List of monthly data arrays.
            annual_data (list): List of annual data arrays.
            seasonal_annual_data (list): List of seasonal and annual means [DJF, MAM, JJA, SON, Annual].
            std_hourly_data (xr.DataArray): Standard deviation hourly data array.
            std_daily_data (xr.DataArray): Standard deviation daily data array.
            std_monthly_data (xr.DataArray): Standard deviation monthly data array.
            std_annual_data (xr.DataArray): Standard deviation annual data array.
            loglevel (str): Logging level. Default is 'WARNING'.
        """
        self.loglevel = loglevel
        self.logger = log_configure(log_level=loglevel, log_name='PlotLatLonProfiles')

        # TODO: support hourly and daily data
        for data in [hourly_data, daily_data,
                     std_hourly_data, std_daily_data]:
            if data is not None:
                self.logger.warning('Hourly and daily data are not yet supported, they will be ignored')

        self.monthly_data = to_list(monthly_data) if monthly_data is not None else []
        self.annual_data = to_list(annual_data) if annual_data is not None else []
        # seasonal_annual_data should be a list of lists: 
        # [[DJF_data1, DJF_data2], [MAM_data1, MAM_data2], ...]
        self.seasonal_annual_data = seasonal_annual_data  

        # self.std_hourly_data = to_list(std_hourly_data)
        # self.std_daily_data = to_list(std_daily_data)
        self.std_monthly_data = (
            std_monthly_data if (std_monthly_data is not None and isinstance(std_monthly_data, xr.DataArray))
            else (std_monthly_data[0] if std_monthly_data is not None else None)
        )

        self.std_annual_data = (
            std_annual_data if (std_annual_data is not None and isinstance(std_annual_data, xr.DataArray))
            else (std_annual_data[0] if std_annual_data is not None else None)
        )

        self.len_data = self._check_data_length()

        # Filling them
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
        
    def set_description(self, region: str = None, diagnostic: str = None):
        """
        Set the caption for the plot.
        The caption is extracted from the data arrays attributes.
        The caption is stored as 'Description' in the metadata dictionary.

        Args:
            region (str): Region to be used in the caption.
            diagnostic (str): Diagnostic name to be used in the caption.

        Returns:
            description (str): Caption for the plot.
        """

        description = f'{diagnostic} '
        if region is not None:
            description += f'for region {region} '

        for i in range(self.len_data):
            description += f'for {self.catalogs[i]} {self.models[i]} {self.exps[i]} '

        if self.std_startdate is not None and self.std_enddate is not None:
            description += f'with standard deviation from {self.std_startdate} to {self.std_enddate} '

        self.logger.debug('Description: %s', description)
        return description
    
    def set_title(self, region: str = None, var: str = None, units: str = None, diagnostic: str = None):
        """
        Set the title for the plot.

        Args:
            region (str): Region to be used in the title.
            var (str): Variable name to be used in the title.
            units (str): Units of the variable to be used in the title.
            diagnostic (str): Diagnostic name to be used in the title.

        Returns:
            title (str): Title for the plot.
        """
        title = f'{diagnostic} '
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

    def plot_lat_lon_profiles(self, data_labels=None, title=None):
        """
        Plot the lat lon profiles data.

        Args:
            data_labels (list): List of data labels.
            title (str): Title of the plot.

        Returns:
            fig (matplotlib.figure.Figure): Figure object.
            ax (matplotlib.axes.Axes): Axes object.
        """
        fig, ax = plot_lat_lon_profiles(mean_type='zonal',
                                        monthly_data=self.monthly_data, 
                                        annual_data=self.annual_data,
                                        #fig=fig, ax=ax,
                                        data_labels= data_labels,
                                        )

        return fig, ax
    
    def plot_multi_line_profiles(self, data_labels=None, title=None):
        """
        Plot multiple lat lon profiles on the same plot.
        
        Returns:
            fig, ax: matplotlib figure and axes
        """
        from aqua.graphics.multiple_lines import plot_multi_lines
        
        # Choose the data to plot (monthly or annual)
        if self.monthly_data:
            data_to_plot = self.monthly_data
        elif self.annual_data:
            data_to_plot = self.annual_data
        else:
            raise ValueError("No data available for plotting")
        
        fig, ax = plot_multi_lines(
            data_arrays_list=data_to_plot,
            data_labels=data_labels,
            title=title
        )
        
        return fig, ax
    
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
        """Check the length of the data arrays."""
        lengths = []
        
        for data in [self.monthly_data, self.annual_data]:
            if data is not None and len(data) > 0:  # Aggiungi controllo che la lista non sia vuota
                lengths.append(len(data))
        
        # For seasonal_annual_data, we assume it represents one dataset with seasonal/annual means
        if self.seasonal_annual_data is not None and len(self.seasonal_annual_data) > 0:
            lengths.append(1)  # Un dataset con dati stagionali
        
        if len(lengths) == 0:
            return 0
        elif len(set(lengths)) == 1:
            return lengths[0]
        else:
            # Se abbiamo solo seasonal_annual_data, dovrebbe essere 1
            if len(self.monthly_data) == 0 and len(self.annual_data) == 0 and self.seasonal_annual_data is not None:
                return 1
            else:
                self.logger.warning('Data arrays have different lengths')
                return max(lengths)