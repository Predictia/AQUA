import xarray as xr
from aqua import Reader
from aqua.logger import log_configure
from aqua.util import OutputSaver


class Diagnostic():

    def __init__(self, catalog: str = None, model: str = None,
                 exp: str = None, source: str = None, regrid: str = None,
                 startdate: str = None, enddate: str = None, loglevel: str = 'WARNING'):
        """
        Initialize the diagnostic class. This is a general purpose class that can be used
        by the diagnostic classes to retrieve data from a single model and to save the data
        to a netcdf file. It is not a working diagnostic class by itself.

        Args:
            catalog (str): The catalog to be used. If None, the catalog will be determined by the Reader.
            model (str): The model to be used.
            exp (str): The experiment to be used.
            source (str): The source to be used.
            regrid (str): The target grid to be used for regridding. If None, no regridding will be done.
            startdate (str): The start date of the data to be retrieved.
                             If None, all available data will be retrieved.
            enddate (str): The end date of the data to be retrieved.
                           If None, all available data will be retrieved.
            loglevel (str): The log level to be used. Default is 'WARNING'.
        """

        self.logger = log_configure(log_name='Diagnostic', log_level=loglevel)

        self.loglevel = loglevel
        self.catalog = catalog
        self.model = model
        self.exp = exp
        self.source = source

        if self.model is None or self.exp is None or self.source is None:
            raise ValueError('Model, experiment and source must be provided')

        self.regrid = regrid
        self.startdate = startdate
        self.enddate = enddate

        # Data to be retrieved
        self.data = None

    def retrieve(self, var: str = None):
        """
        Retrieve the data from the model.

        Args:
            var (str): The variable to be retrieved. If None, all variables will be retrieved.

        Attributes:
            self.data: The data retrieved from the model. If return_data is True, the data will be returned.
            self.catalog: The catalog used to retrieve the data if no catalog was provided.
        """
        self.data, self.reader, self.catalog = self._retrieve(model=self.model, exp=self.exp, source=self.source,
                                                              var=var, catalog=self.catalog, startdate=self.startdate,
                                                              enddate=self.enddate, regrid=self.regrid,
                                                              loglevel=self.logger.level)

        if self.startdate is None:
            self.startdate = self.data.time.values[0]
            self.logger.debug(f'Start date: {self.startdate}')
        if self.enddate is None:
            self.enddate = self.data.time.values[-1]
            self.logger.debug(f'End date: {self.enddate}')

    def save_netcdf(self, data, diagnostic: str, diagnostic_product: str = None,
                    default_path: str = '.', rebuild: bool = True, **kwargs):
        """
        Save the data to a netcdf file.

        Args:
            data (xarray Dataset or DataArray): The data to be saved.
            diagnostic (str): The diagnostic name.
            diagnostic_product (str): The diagnostic product.
            default_path (str): The default path to save the data. Default is '.'.
            rebuild (bool): If True, the netcdf file will be rebuilt. Default is True.

        Keyword Args:
            **kwargs: Additional keyword arguments to be passed to the OutputSaver.save_netcdf method.
        """
        if isinstance(data, xr.Dataset) is False and isinstance(data, xr.DataArray) is False:
            self.logger.error('Data to save as netcdf must be an xarray Dataset or DataArray')

        outputsaver = OutputSaver(diagnostic=diagnostic, diagnostic_product=diagnostic_product,
                                  default_path=default_path, rebuild=rebuild, catalog=self.catalog,
                                  model=self.model, exp=self.exp, loglevel=self.logger.level)

        outputsaver.save_netcdf(dataset=data, **kwargs)

    @staticmethod
    def _retrieve(model: str, exp: str, source: str, var: str = None, catalog: str = None,
                  startdate: str = None, enddate: str = None, regrid: str = None,
                  loglevel: str = 'WARNING'):
        """
        Static method to retrieve data and return everything instead of updating class
        attributes. Used internally by the retrieve method

        Args:
            model (str): model of the dataset to retrieve.
            exp (str): exp of the dataset to retrieve.
            source (str): source of the dataset to retrieve.
            var (str or list): variable to retrieve. If None all are retrieved.
            catalog (str): catalog of the dataset to retrieve.
            startdate (str): The start date of the data to be retrieved.
                             If None, all available data will be retrieved.
            enddate (str): The end date of the data to be retrieved.
                           If None, all available data will be retrieved.
            regrid (str): The target grid to be used for regridding. If None, no regridding will be done.
            loglevel (str): The log level to be used. Default is 'WARNING'.

        Returns:
            data (xarray Dataset or DataArray): The data retrieved from the model.
            reader (aqua.Reader): The reader object used to retrieve the data.
            catalog (str): The catalog used to retrieve the data.
        """
        reader = Reader(catalog=catalog, model=model, exp=exp, source=source,
                        regrid=regrid, startdate=startdate, enddate=enddate, loglevel=loglevel)

        data = reader.retrieve(var=var)

        if catalog is None:
            catalog = reader.catalog

        if regrid is not None:
            data = reader.regrid(data)

        return data, reader, catalog
