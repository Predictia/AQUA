import xarray as xr
from aqua.logger import log_configure
from aqua.util import pandas_freq_to_string
from aqua.diagnostics.core import Diagnostic, OutputSaver, start_end_dates

xr.set_options(keep_attrs=True)

class BaseMixin(Diagnostic):
    """The BaseMixin class is used to save the outputs from the ssh module."""

    def __init__(
        self,
        diagnostic_name: str = "sshVariability",
        catalog: str = None,
        model: str = None,
        exp: str = None,
        source: str = None,
        startdate: str = None,
        enddate: str = None,
        region: str = None,
        regrid: str = None,
        lon_limits: list[float] = None,
        lat_limits: list[float] = None,
        zoom: float = None,
        outputdir: str = "./",
        reader_kwargs: dict = {},
        var: str = None,
        long_name: str = None,
        short_name: str = None,
        units: str = None,
        rebuild: bool = True,
        loglevel: str = "WARNING",
    ):
        
        """
        Initialize the Base class.

        Args:
            diagnostic_name (str): The name of the diagnostic ,i.e., 'sshVariability'.
                                   This will be used to configure the logger and the output files.
            catalog (str): The catalog to be used. If None, the catalog will be determined by the Reader.
            model (str): The model to be used.
            exp (str): The experiment to be used.
            source (str): The source to be used.
            regrid (str): The target grid to be used for regridding. If None, no regridding will be done.
            startdate (str): The start date of the data to be retrieved.
                             If None, all available data will be retrieved.
            enddate (str): The end date of the data to be retrieved.
                           If None, all available data will be retrieved.
            region (str): The region to select. This will define the lon and lat limits.
            lon_limits (list): The longitude limits to be used. Overriden by region.
            lat_limits (list): The latitude limits to be used. Overriden by region.
            rebuild (bool): If True, rebuild the data from the original files.
            outputdir (str): The directory to save the data.
            reader_kwargs (dict): Additional keyword arguments for the Reader. Default is an empty dictionary.
            loglevel (str): The log level to be used. Default is 'WARNING'.

        Keyword Args: 
            zoom (int, optional): HEALPix grid zoom level (e.g. zoom=10 is h1024). Allows for multiple gridname definitions.
            realization (int, optional): The ensemble realization number, included in the output filename.
            **kwargs: Additional arbitrary keyword arguments to be passed as additional parameters to the intake catalog entry.
        """
        super().__init__(catalog=catalog, model=model, exp=exp, source=source, regrid=regrid, startdate=startdate, enddate=enddate, loglevel=loglevel)
        
        # Log name is the diagnostic name with the first letter capitalized
        self.logger = log_configure(log_level=loglevel, log_name=diagnostic_name.capitalize())
        self.diagnostic_name = diagnostic_name

        # We want to make sure we retrieve the required amount of data with a single Reader instance
        self.startdate, self.enddate = start_end_dates(startdate=startdate, enddate=enddate)
        self.logger.debug(f"Retrieve start date: {self.startdate}, End date: {self.enddate}")
        
        if region is not None and lon_limits is not None and lat_limits is not None:
            # Set the region based on the region name or the lon and lat limits
            self.region, self.lon_limits, self.lat_limits = self._set_region(region=region, diagnostic='sshVariability',
                                                                         lon_limits=lon_limits, lat_limits=lat_limits)
        self.logger.debug(f"Region: {self.region}, Lon limits: {self.lon_limits}, Lat limits: {self.lat_limits}")
        
        self.outputdir = outputdir
        logger.info(f"Outputs will be saved at {self.outputdir}.")

        self.var = var
        self.zoom = zoom
        self.rebuild = rebuild
        if zoom:
            reader_kwargs["zoom"] = zoom
        self.reader_kwargs = reader_kwargs

    def _check_data(self, var: str, units: str):
        """
        Make sure that the data is in the correct units.

        Args:
            var (str): The variable to be checked.
            units (str): The units to be checked.
        """
        self.data[self.var] = super()._check_data(data=self.data[self.var], var=var, units=units)

    def retrieve(self):
        """
        Retrieve the data for the given variable.
        """  
        
        super().retrieve(var=self.var, reader_kwargs=self.reader_kwargs)
        if self.data is None:
            raise ValueError(f'Variable {var} not found in the data. '
                             'Check the variable name and the data source.')
        # Get the xr.DataArray to be aligned with the formula code
        self.data = self.data[self.var]

        # Customization of the data, expecially needed for formula
        if self.units is not None:
            self._check_data(self.var, self.units)
        else:
            self.units = self.data.attrs.get("units")
        if self.long_name is not None:
            self.data.attrs['long_name'] = self.long_name
        # We want to be sure that a long_name is always defined for description setup
        elif self.data.attrs.get('long_name') is None:
            self.data.attrs['long_name'] = self.var
        # We use the short_name as the name of the variable
        # to be always used in plots
        if self.short_name is not None:
            self.data.attrs['short_name'] = self.short_name
            self.data.name = self.short_name
        else:
            self.data.attrs['short_name'] = self.var


    def netcdf_save(self, data, diagnostic_product: str='sshVariability', freq: str=None,
                    create_catalog_entry: bool = False,
                    dict_catalog_entry: dict = {'jinjalist': ['freq', 'realization', 'region'],
                                                'wildcardlist': ['var']}):
        """
        Save the data to a netcdf file.

        Args:
            data (xarray.DataArray): Input data array
            diagnostic_product (str): The product name to be used in the filename 'sshVariability'.
            freq (str): The frequency of the data. It is set to 'None' for this release of code.
            outputdir (str): The directory to save the data.
            rebuild (bool): If True, rebuild the data from the original files.
            create_catalog_entry (bool): If True, create a catalog entry for the data. Default is False.
            dict_catalog_entry (dict): A dictionary with catalog entry information. Default is {'jinjalist': ['freq', 'region', 'realization'], 'wildcardlist': ['var']}.
        """
        #TODO:
        # the 'freq' variable will be updated in depends on the frequency of the data. 
        # the idea is to implement the formula of 'variance of variances'. In this case, this variable will be used. 
        
        #str_freq = pandas_freq_to_string(freq)

        #if str_freq == 'hourly':
        #    data = self.hourly if self.hourly is not None else self.logger.error('No hourly data available')
        #    data_std = self.std_hourly if self.std_hourly is not None else None
        #elif str_freq == 'daily':
        #    data = self.daily if self.daily is not None else self.logger.error('No daily data available')
        #    data_std = self.std_daily if self.std_daily is not None else None
        #elif str_freq == 'monthly':
        #    data = self.monthly if self.monthly is not None else self.logger.error('No monthly data available')
        #    data_std = self.std_monthly if self.std_monthly is not None else None
        #elif str_freq == 'annual':
        #    data = self.annual if self.annual is not None else self.logger.error('No annual data available')
        #    data_std = self.std_annual if self.std_annual is not None else None

        var = getattr(data, 'short_name', None)
        #extra_keys = {'var': var, 'freq': str_freq}
        extra_keys = {'var': var}

        if data.name is None:
            data.name = var

        # In order to have a catalog entry we want to have a key region even in the global case
        region = self.region.replace(' ', '').lower() if self.region is not None else 'global'
        extra_keys.update({'region': region})

        #self.logger.info('Saving %s data for %s to netcdf in %s', str_freq, diagnostic_product, outputdir)
        self.logger.info('Saving output data for %s to netcdf in %s', diagnostic_product, outputdir)

        super().save_netcdf(data=data, diagnostic=self.diagnostic_name, diagnostic_product=diagnostic_product,
                            outputdir=self.outputdir, rebuild=self.rebuild, extra_keys=extra_keys,
                            create_catalog_entry=create_catalog_entry, dict_catalog_entry=dict_catalog_entry)

    
class PlotBaseMixin():
    """PlotBaseMixin class is used for the PlotSSHVariability."""
    def __init__(
        self, 
        diagnostic_name: str = 'sshVariability', 
        loglevel: str = 'WARNING',    
    ):
        """
        Initialize the PlotBaseMixin class.

        Args:
            diagnostic_name (str): The name of the diagnostic 'ssh'.
                                   This will be used to configure the logger and the output files.
            loglevel (str): The log level to be used. Default is 'WARNING'.
        """
        # Data info initalized as empty
        self.loglevel = loglevel
        self.diagnostic_name = diagnostic_name
        log_name = 'Plot' + diagnostic_name.capitalize()
        self.logger = log_configure(log_level=loglevel, log_name=log_name)
 
    def save_plot(
        self,
        fig,
        var: str = None, 
        description: str = None, 
        rebuild: bool = True,
        outputdir: str = './', 
        dpi: int = 300, 
        format: str = 'png', 
        diagnostic_product: str = 'sshVariability',
        catalog: str = None,
        model: str = None,
        exp: str = None,
        region: str = None,
        startdate: str = None,
        enddate: str = None,
        #long_name: str = None,
        #units: str = None,
    ):
        """
        Save the plot to a file.

        Args:
            fig (matplotlib.figure.Figure): Figure object.
            description (str): Description of the plot.
            rebuild (bool): If True, rebuild the plot even if it already exists.
            outputdir (str): Output directory to save the plot.
            dpi (int): Dots per inch for the plot.
            format (str): Format of the plot ('png' or 'pdf'). Default is 'png'.
            diagnostic_product (str): Diagnostic product name i.e., 'sshVariability'.
            catalog (str): The catalog to be used in the 'OutputSaver' class. (Mandatory)
            model (str): The model to be used in the 'OutputSaver' class. (Mandatory)
            exp (str): The experiment to be used in the 'OutputSaver' class. (Mandatory)
            startdate (str): The start date of the data to be used in description and title.
                             If None, all available data will be retrieved.
            enddate (str): The end date of the data to be retrieved.
                           If None, all available data will be retrieved.
            region (str): The region to select. This will define the lon and lat limits.
            rebuild (bool): If True, rebuild the data from the original files.
            outputdir (str): The directory to save the data.
            reader_kwargs (dict): Additional keyword arguments for the Reader. Default is an empty dictionary.
            loglevel (str): The log level to be used. Default is 'WARNING'.

        """
        outputsaver = OutputSaver(diagnostic=self.diagnostic_name,
                                  catalog=catalog,
                                  model=model,
                                  exp=exp,
                                  outputdir=outputdir,
                                  loglevel=self.loglevel)
        if description is None: description = "sshVariability diagnostic" 
        description = description + f" ({startdate}-{enddate}) "
        metadata = {"Description": description, "dpi": dpi }
        extra_keys = {'diagnostic_product': diagnostic_product}

        if self.short_name is not None:
            extra_keys.update({'var': self.short_name})
        if self.region is not None:
            region = self.region.replace(' ', '').lower()
            extra_keys.update({'region': region})

        if format == 'png':
            outputsaver.save_png(fig, diagnostic_product=diagnostic_product, rebuild=rebuild, extra_keys=extra_keys, metadata=metadata)
        elif format == 'pdf':
            outputsaver.save_pdf(fig, diagnostic_product=diagnostic_product, rebuild=rebuild, extra_keys=extra_keys, metadata=metadata)
        else:
            raise ValueError(f'Format {format} not supported. Use png or pdf.')

    def save_diff_plot(
        self,
        fig,
        var: str = None, 
        description: str = None, 
        rebuild: bool = True,
        outputdir: str = './', 
        dpi: int = 600, 
        format: str = 'png', 
        diagnostic_product: str = 'sshVariability_Difference',
        catalog: str = None,
        model: str = None,
        exp: str = None,
        startdate: str = None,
        enddate: str = None,
        catalog_ref: str = None,
        model_ref: str = None,
        exp_ref: str = None,
        startdate_ref: str = None,
        enddate_ref: str = None,
        region: str = None,
        #long_name: str = None,
        #units: str = None,
    ):
        """
        Save the plot of the difference of SSH variabilities b/w reference and model to a file.

        Args:

            fig (matplotlib.figure.Figure): Figure object.
            description (str): Description of the plot.
            rebuild (bool): If True, rebuild the plot even if it already exists.
            outputdir (str): Output directory to save the plot.
            dpi (int): Dots per inch for the plot.
            format (str): Format of the plot ('png' or 'pdf'). Default is 'png'.
            catalog (str): The catalog to be used in the 'OutputSaver' class. (Mandatory)
            model (str): The model to be used in the 'OutputSaver' class. (Mandatory)
            exp (str): The experiment to be used in the 'OutputSaver' class. (Mandatory)
            startdate (str): The start date of the data to be used in description and title.
                             If None, all available data will be retrieved.
            enddate (str): The end date of the data to be retrieved.
                           If None, all available data will be retrieved.
            region (str): The region to select. This will define the lon and lat limits.
            rebuild (bool): If True, rebuild the data from the original files.
            outputdir (str): The directory to save the data.
            reader_kwargs (dict): Additional keyword arguments for the Reader. Default is an empty dictionary.
            loglevel (str): The log level to be used. Default is 'WARNING'.

            diagnostic_product (str): Diagnostic product to be used in the filename as diagnostic_product.
                                      In this diagnostic this variable can be: 'sshVariability' or 'Diff_sshVariability'
        """
        outputsaver = OutputSaver(diagnostic=self.diagnostic_name,
                                  catalog=catalog,
                                  model=model,
                                  exp=exp,
                                  catalog_ref=catalog_ref,
                                  model_ref=model_ref,
                                  exp_ref=exp_ref,
                                  outputdir=outputdir,
                                  loglevel=self.loglevel)
        if description is None: description = "sshVariability diagnostic" 
        description = description + f" model time: ({startdate}-{enddate}) and reference time: ({startdate}-{enddate})" 
        metadata = {"Description": description, "dpi": dpi }
        extra_keys = {'diagnostic_product': diagnostic_product}

        if self.short_name is not None:
            extra_keys.update({'var': self.short_name})
        if self.region is not None:
            region = self.region.replace(' ', '').lower()
            extra_keys.update({'region': region})

        if format == 'png':
            outputsaver.save_png(fig, diagnostic_product=diagnostic_product, rebuild=rebuild, extra_keys=extra_keys, metadata=metadata)
        elif format == 'pdf':
            outputsaver.save_pdf(fig, diagnostic_product=diagnostic_product, rebuild=rebuild, extra_keys=extra_keys, metadata=metadata)
        else:
            raise ValueError(f'Format {format} not supported. Use png or pdf.')


