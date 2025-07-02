from aqua.graphics import plot_seasonal_and_annual_data
from aqua.logger import log_configure
from .plot_base import PlotBaseMixin

class PlotLatLonProfiles(PlotBaseMixin):
    """
    Class for plotting Lat-Lon Profiles diagnostics.
    Inherits from PlotBaseMixin for basic plotting functionality.
    This class is specialized for handling lat-lon profile plots,
    including seasonal and annual means.
    """
    def __init__(self, hourly_data=None, daily_data=None,
             monthly_data=None, annual_data=None,
             seasonal_annual_data=None,
             ref_hourly_data=None, ref_daily_data=None,
             ref_monthly_data=None, ref_annual_data=None,
             std_hourly_data=None, std_daily_data=None,
             std_monthly_data=None, std_annual_data=None,
             loglevel: str = 'WARNING'):
        """
        Initialize the PlotLatLonProfiles class.
        Inherits from PlotBaseMixin for basic plotting functionality.
        """
        # Call the parent constructor
        super().__init__(
            hourly_data=hourly_data,
            daily_data=daily_data,
            monthly_data=monthly_data,
            annual_data=annual_data,
            seasonal_annual_data=seasonal_annual_data,
            ref_hourly_data=ref_hourly_data,
            ref_daily_data=ref_daily_data,
            ref_monthly_data=ref_monthly_data,
            ref_annual_data=ref_annual_data,
            std_hourly_data=std_hourly_data,
            std_daily_data=std_daily_data,
            std_monthly_data=std_monthly_data,
            std_annual_data=std_annual_data,
            loglevel=loglevel
        )
        self.logger = log_configure(self.loglevel, 'PlotLatLonProfiles')
    
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
        title = super().set_title(region=region, var=var, units=units, diagnostic='Lat-Lon Profiles')
        return title

    def set_description(self, region: str = None):
        """
        Set the caption for the plot.
        Specialized for Lat-Lon Profiles diagnostic.

        Args:
            region (str): Region to be used in the caption.

        Returns:
            description (str): Caption for the plot.
        """
        description = super().set_description(region=region, diagnostic='lat_lon_profiles')
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
        data_label = self.set_data_labels()
        ref_label = self.set_ref_label()
        description = self.set_description(region=region)
        title = self.set_title(region=region, var=var, units=units)
        
        if plot_type == 'seasonal':
            fig, axs = plot_seasonal_and_annual_data(
                maps=self.seasonal_annual_data,
                plot_type='seasonal',
                data_labels=data_label,
                title=title
            )
        else:
            fig, _ = self.plot_lat_lon_profiles(data_labels=data_label, ref_label=ref_label, title=title)
        
        region_short = region.replace(' ', '').lower() if region is not None else None
        diagnostic_suffix = '_seasonal' if plot_type == 'seasonal' else ''
        
        # Specialized save_plot for Lat-Lon Profiles
        self.save_plot(fig, var=var, description=description, region=region_short, rebuild=rebuild,
                    outputdir=outputdir, dpi=dpi, format=format, 
                    diagnostic=f'lat_lon_profiles{diagnostic_suffix}')
        
        self.logger.info('PlotLatLonProfiles completed successfully')

    def save_plot(self, fig, var: str = None, description: str = None, region: str = None, rebuild: bool = True,
              outputdir: str = './', dpi: int = 300, format: str = 'png', diagnostic: str = None):
        """
        Save the plot to a file.
        Specialized for Lat-Lon Profiles diagnostic.

        Args:
            fig (matplotlib.figure.Figure): Figure object.
            var (str): Variable name to be used in the title and description.
            description (str): Description of the plot.
            region (str): Region to be used in the title and description.
            rebuild (bool): If True, rebuild the plot even if it already exists.
            outputdir (str): Output directory to save the plot.
            dpi (int): Dots per inch for the plot.
            format (str): Format of the plot ('png' or 'pdf'). Default is 'png'.
            diagnostic (str): Diagnostic name. If None, defaults to 'lat_lon_profiles'.
        """
        # Default diagnostic for lat_lon_profiles if not specified
        if diagnostic is None:
            diagnostic = 'lat_lon_profiles'
        
        super().save_plot(fig=fig, var=var, description=description,
                        region=region, rebuild=rebuild,
                        outputdir=outputdir, dpi=dpi, format=format, 
                        diagnostic=diagnostic)

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
        fig, axs = plot_seasonal_and_annual_data(maps=self.seasonal_annual_data,
                            plot_type='seasonal',
                            data_labels=data_labels,
                            loglevel=self.loglevel)
        
        title = f"Multi-variable Seasonal Comparison: {', '.join(var_names)}"
        fig.suptitle(title, fontsize=14, fontweight='bold')
        
        # Specialized save_plot for multi-variable seasonal comparison
        self.save_plot(fig, var='_'.join(var_names), 
                    description=f"Multi-variable seasonal comparison: {', '.join(var_names)}",
                    diagnostic='lat_lon_profiles_seasonal_multi')
        
        return fig, axs
