"""Gregory module."""
import xarray as xr
from aqua.util import eval_formula
from aqua.diagnostics.core import Diagnostic, convert_data_units

xr.set_options(keep_attrs=True)


class Gregory(Diagnostic):

    def __init__(self, catalog: str = None, model: str = None,
                 exp: str = None, source: str = None, regrid: str = None,
                 startdate: str = None, enddate: str = None, loglevel: str = 'WARNING'):
        """
        Initialize the Gregory Plot class. This evaluates values necessary for the Gregory Plot
        from a single model and to save the data to a netcdf file.

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
        super().__init__(catalog=catalog, model=model, exp=exp, source=source, regrid=regrid,
                         startdate=startdate, enddate=enddate, loglevel=loglevel)
        # Initialize the variables
        self.t2m = None
        self.net_toa = None

        # Initialize the possible results
        self.t2m_monthly = None
        self.t2m_annual = None
        self.t2m_std = None
        self.net_toa_monthly = None
        self.net_toa_annual = None
        self.net_toa_std = None

    def run(self, freq: list = ['monthly', 'annual'],
            t2m: bool = True, net_toa: bool = True, std: bool = False,
            t2m_name: str = '2t', net_toa_name: str = 'tnlwrf+tnswrf',
            t2m_units: str = 'degC',
            exclude_incomplete: bool = True, outputdir: str = './',
            rebuild: bool = True):
        """Run the Gregory Plot."""
        self.retrieve(t2m=t2m, net_toa=net_toa, t2m_name=t2m_name, net_toa_name=net_toa_name)

        self.logger.info(f'Computing the Gregory Plot for the {freq} frequency.')
        if t2m:
            self.compute_t2m(freq=freq, std=std, units=t2m_units, var=t2m_name,
                             exclude_incomplete=exclude_incomplete)
        if net_toa:
            # TODO: If needed add the units conversion for net_toa
            self.compute_net_toa(freq=freq, std=std,
                                 exclude_incomplete=exclude_incomplete)

        self.save_netcdf(freq=freq, std=std, t2m=t2m, net_toa=net_toa,
                         outputdir=outputdir, rebuild=rebuild)

    def retrieve(self, t2m: bool = True, net_toa: bool = True,
                 t2m_name: str = '2t', net_toa_name: str = 'tnlwrf+tnswrf'):
        """
        Retrieve the necessary data for the Gregory Plot.

        Args:
            t2m (bool): Whether to retrieve the 2m temperature data. Default is True.
            net_toa (bool): Whether to retrieve the net TOA radiation data. Default is True.
            t2m_name (str): The name of the 2m temperature data.
            net_toa_name (str): The name of the net TOA radiation data.
        """
        data, self.reader, self.catalog = super()._retrieve(catalog=self.catalog, model=self.model,
                                                            exp=self.exp, source=self.source,
                                                            regrid=self.regrid, startdate=self.startdate,
                                                            enddate=self.enddate)

        if t2m:
            self.t2m = data[t2m_name]
        if net_toa:
            self.net_toa = eval_formula(mystring=net_toa_name, xdataset=data)

    def compute_t2m(self, freq: list = ['monthly', 'annual'], std: bool = False,
                    var: str = '2t', units: str = 'degC', exclude_incomplete=True):
        """
        Compute the 2m temperature data.

        Args:
            freq (list): The frequency of the data to be computed. Default is ['monthly', 'annual'].
            std (bool): Whether to compute the standard deviation. Default is False.
            units (str): The units of the data. Default is 'degC'.
            exclude_incomplete (bool): Whether to exclude incomplete timespans. Default is True.
        """
        t2m = self.reader.fldmean(self.t2m)
        if units:
            t2m = convert_data_units(data=t2m, var=var, units=units, loglevel=self.loglevel)

        if 'monthly' in freq:
            self.t2m_monthly = self.reader.timmean(t2m, freq='MS', exclude_incomplete=exclude_incomplete)
        if 'annual' in freq:
            self.t2m_annual = self.reader.timmean(t2m, freq='YS', exclude_incomplete=exclude_incomplete)
            if std:
                self.t2m_std = self.t2m_annual.std()

    def compute_net_toa(self, freq: list = ['monthly', 'annual'], std: bool = False,
                        exclude_incomplete=True):
        """
        Compute the net TOA radiation data.

        Args:
            freq (list): The frequency of the data to be computed. Default is ['monthly', 'annual'].
            std (bool): Whether to compute the standard deviation. Default is False.
            exclude_incomplete (bool): Whether to exclude incomplete timespans. Default is True.
        """
        net_toa = self.reader.fldmean(self.net_toa)

        if 'monthly' in freq:
            self.net_toa_monthly = self.reader.timmean(net_toa, freq='MS', exclude_incomplete=exclude_incomplete)
        if 'annual' in freq:
            self.net_toa_annual = self.reader.timmean(net_toa, freq='YS', exclude_incomplete=exclude_incomplete)
            if std:
                self.net_toa_std = self.net_toa_annual.std()

    def save_netcdf(self, freq: list = ['monthly', 'annual'], std: bool = False,
                    t2m: bool = True, net_toa: bool = True,
                    outputdir: str = './', rebuild: bool = True):
        """
        Save the computed data to a netcdf file.

        Args:
            freq (list): The frequency of the data to be saved. Default is ['monthly', 'annual'].
            std (bool): Whether to save the standard deviation. Default is False.
            t2m (bool): Whether to save the 2m temperature data. Default is True.
            net_toa (bool): Whether to save the net TOA radiation data. Default is True.
            outputdir (str): The output directory to save the netcdf file. Default is './'.
            rebuild (bool): Whether to rebuild the netcdf file. Default is True.
        """
        diagnostic = 'gregory'

        if t2m:
            if std:
                diagnostic_product = '2t.annual.std'
                super().save_netcdf(data=self.t2m_std, diagnostic=diagnostic,
                                    diagnostic_product=diagnostic_product,
                                    default_path=outputdir, rebuild=rebuild)
            if 'monthly' in freq:
                diagnostic_product = '2t.monthly'
                super().save_netcdf(data=self.t2m_monthly, diagnostic=diagnostic,
                                    diagnostic_product=diagnostic_product,
                                    default_path=outputdir, rebuild=rebuild)
            if 'annual' in freq:
                diagnostic_product = '2t.annual'
                super().save_netcdf(data=self.t2m_annual, diagnostic=diagnostic,
                                    diagnostic_product=diagnostic_product,
                                    default_path=outputdir, rebuild=rebuild)
        if net_toa:
            if std:
                diagnostic_product = 'net_toa.annual.std'
                super().save_netcdf(data=self.net_toa_std, diagnostic=diagnostic,
                                    diagnostic_product=diagnostic_product,
                                    default_path=outputdir, rebuild=rebuild)
            if 'monthly' in freq:
                diagnostic_product = 'net_toa.monthly'
                super().save_netcdf(data=self.net_toa_monthly, diagnostic=diagnostic,
                                    diagnostic_product=diagnostic_product,
                                    default_path=outputdir, rebuild=rebuild)
            if 'annual' in freq:
                diagnostic_product = 'net_toa.annual'
                super().save_netcdf(data=self.net_toa_annual, diagnostic=diagnostic,
                                    diagnostic_product=diagnostic_product,
                                    default_path=outputdir, rebuild=rebuild)
