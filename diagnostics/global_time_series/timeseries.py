import os

import matplotlib.pyplot as plt
import xarray as xr
from aqua import Reader
from aqua.logger import log_configure
from aqua.exceptions import NoObservationError, NoDataError
from aqua.util import eval_formula, create_folder, add_pdf_metadata
from aqua.graphics import plot_timeseries

from .reference_data import get_reference_timeseries

xr.set_options(keep_attrs=True)


class Timeseries():
    """
    Plot a time series of the global mean value of a given variable.
    By default monthly and annual time series are plotted,
    the annual mean is plotted as dashed line and reference data is included,
    ERA5 by default, with the option to plot the standard deviation as uncertainty quantification.
    A model, exp, source string or list of strings can be passed.
    If a list is passed, the time series will be plotted for each combination
    of model, exp and source.
    """
    def __init__(self, var=None, formula=False,
                 models=None, exps=None, sources=None,
                 monthly=True, annual=True,
                 regrid=None, plot_ref=True,
                 plot_ref_kw={'model': 'ERA5',
                              'exp': 'era5',
                              'source': 'monthly'},
                 startdate=None, enddate=None,
                 monthly_std=True, annual_std=True,
                 std_startdate=None, std_enddate=None,
                 plot_kw={'ylim': {}},
                 outdir='./',
                 outfile=None,
                 loglevel='WARNING'):
        """
        Args:
            var (str): Variable name.
            formula (bool): (Optional) If True, try to derive the variable from other variables.
                            Default is False.
            models (list or str): Model IDs.
            exps (list or str): Experiment IDs.
            sources (list or str): Source IDs.
            regrid (str): Optional regrid resolution. Default is None.
            plot_ref (bool): Include reference data. Default is True.
            annual (bool): Plot annual mean. Default is True.
            startdate (str): Start date. Default is None.
            enddate (str): End date. Default is None.
            std_startdate (str): Start date for standard deviation. Default is "1991-01-01".
            std_enddate (str): End date for standard deviation. Default is "2020-12-31".
            monthly_std (bool): Plot monthly standard deviation. Default is True.
            annual_std (bool): Plot annual standard deviation. Default is True.
            ylim (dict): Keyword arguments passed to `set_ylim()`.
            reader_kw (dict): Additional keyword arguments passed to the `aqua.Reader`.
            plot_kw (dict): Additional keyword arguments passed to the plotting function.
            ax (matplotlib.Axes): (Optional) axes to plot in.
        """
        self.loglevel = loglevel

        self.logger = log_configure(log_level=self.loglevel, log_name='Timeseries')

        self.var = var
        self.formula = formula

        self.models = models
        self.exps = exps
        self.sources = sources

        if isinstance(self.models, str):
            self.models = [self.models]
        if isinstance(self.exps, str):
            self.exps = [self.exps]
        if isinstance(self.sources, str):
            self.sources = [self.sources]

        self.monthly = monthly
        self.annual = annual
        self.regrid = regrid

        self.plot_ref = plot_ref
        if self.plot_ref:
            self.ref_mon = None
            self.ref_mon_std = None
            self.ref_ann = None
            self.ref_ann_std = None
            self.plot_ref_kw = plot_ref_kw
            self.monthly_std = monthly_std
            self.annual_std = annual_std
            self.std_startdate = std_startdate
            self.std_enddate = std_enddate

        self.startdate = startdate
        self.enddate = enddate

        self.plot_kw = plot_kw

        self.outdir = outdir
        self.outfile = outfile

    def run(self):
        """
        Retrieve ref, retrieve data and plot
        """
        self.retrieve_data()
        self.retrieve_ref()
        self.plot()
        self.save_netcdf()

    def retrieve_ref(self):
        """
        Retrieve reference data
        """
        if self.plot_ref:
            self.logger.debug('Retrieving reference data')
            try:
                self.ref_mon, self.ref_mon_std, self.ref_ann, self.ref_ann_std =\
                    get_reference_timeseries(var=self.var,
                                             formula=self.formula,
                                             **self.plot_ref_kw,  # model,exp,source
                                             startdate=self.startdate,
                                             enddate=self.enddate,
                                             std_startdate=self.std_startdate,
                                             std_enddate=self.std_enddate,
                                             regrid=self.regrid,
                                             monthly=self.monthly,
                                             annual=self.annual,
                                             monthly_std=self.monthly_std,
                                             annual_std=self.annual_std,
                                             loglevel=self.loglevel)
            except NoObservationError:
                self.plot_ref = False
                self.logger.warning('Reference data not found, skipping reference data')
        else:
            self.logger.debug('Reference data not requested')

    def retrieve_data(self):
        """
        Retrieve data from the list and store them in a list
        of xarray.DataArray
        """
        self.logger.debug('Retrieving data')
        if self.monthly:
            self.data_mon = []
        if self.annual:
            self.data_annual = []

        if self.startdate is None:
            startdate = None
        if self.enddate is None:
            enddate = None

        for model in self.models:
            for exp in self.exps:
                for source in self.sources:
                    self.logger.info(f'Retrieving data for {model} {exp} {source}')
                    try:
                        reader = Reader(model=model, exp=exp, source=source,
                                        startdate=self.startdate, enddate=self.enddate,
                                        regrid=self.regrid, loglevel=self.loglevel)
                        if self.formula:
                            data = reader.retrieve()
                            self.logger.debug(f"Evaluating formula for {self.var}")
                            data = eval_formula(self.var, data)
                        else:
                            data = reader.retrieve(var=self.var)
                    except Exception as e:
                        self.logger.debug(f"Error while retrieving: {e}")
                        raise NoDataError(f'No data found for {model} {exp} {source}') from e

                    if self.startdate is None:
                        if startdate is None:
                            startdate = data[self.var].time[0].values
                        else:
                            startdate = min(startdate, data[self.var].time[0].values)
                    if self.enddate is None:
                        if enddate is None:
                            enddate = data[self.var].time[-1].values
                        else:
                            enddate = max(enddate, data[self.var].time[-1].values)

                    if self.monthly:
                        if 'monthly' in source or 'mon' in source:
                            self.logger.debug(f"No monthly resample needed for {model} {exp} {source}")
                            data_mon = data
                        else:
                            data_mon = reader.timmean(data, freq='MS', exclude_incomplete=True)
                        data_mon = reader.fldmean(data_mon)
                        self.logger.info("Monthly data retrieved")
                        self.data_mon.append(data_mon[self.var])

                    if self.annual:
                        data_ann = reader.timmean(data, freq='YS',
                                                  exclude_incomplete=True,
                                                  center_time=True)
                        data_ann = reader.fldmean(data_ann)
                        self.logger.info("Annual data retrieved")
                        self.data_annual.append(data_ann[self.var])

        if self.startdate is None:
            self.logger.debug(f"Start date: {startdate}")
            self.startdate = startdate
        if self.enddate is None:
            self.enddate = enddate
            self.logger.debug(f"End date: {enddate}")

    def plot(self):
        """
        Call an external function using the data to plot
        """
        self.logger.info("Plotting the timeseries")

        data_labels = []
        for model in self.models:
            for exp in self.exps:
                for source in self.sources:
                    data_labels.append(f'{model} {exp}')

        if self.plot_ref:
            try:
                ref_label = self.plot_ref_kw['model']
            except KeyError:
                ref_label = 'Reference'

        title = f'{self.var} timeseries'

        fig, ax = plot_timeseries(monthly_data=self.data_mon,
                                  annual_data=self.data_annual,
                                  ref_monthly_data=self.ref_mon,
                                  ref_annual_data=self.ref_ann,
                                  std_monthly_data=self.ref_mon_std,
                                  std_annual_data=self.ref_ann_std,
                                  ref_label=ref_label,
                                  data_labels=data_labels,
                                  title=title)

        # Save to outdir/pdf/filename
        outfig = os.path.join(self.outdir, 'pdf')
        self.logger.debug(f"Saving figure to {outfig}")
        create_folder(outfig, self.loglevel)
        if self.outfile is None:
            self.outfile = f'timeseries_{self.var}'
            for model in self.models:
                for exp in self.exps:
                    for source in self.sources:
                        self.outfile += f'_{model}_{exp}_{source}'
            if self.plot_ref:
                self.outfile += f'_{ref_label}'
            self.outfile += '.pdf'
        self.logger.debug(f"Outfile: {self.outfile}")
        fig.savefig(os.path.join(outfig, self.outfile))

        description = f"Time series of the global mean of {self.var}"
        description += f" from {self.startdate} to {self.enddate}"
        for model in self.models:
            for exp in self.exps:
                for source in self.sources:
                    description += f" for {model} {exp} {source},"
        if self.plot_ref:
            description += f" with {ref_label} as reference,"
            description += f" std evaluated from {self.std_startdate} to {self.std_enddate}"
        add_pdf_metadata(filename=os.path.join(outfig, self.outfile),
                         metadata_value=description)

    def save_netcdf(self):
        """
        Save the data to a netcdf file.
        Every model-exp-source combination is saved in a separate file.
        Reference data is saved in a separate file.
        Std data is saved in a separate file.
        """
        outdir = os.path.join(self.outdir, 'netcdf')
        create_folder(outdir, self.loglevel)

        for model in self.models:
            for exp in self.exps:
                for i, source in enumerate(self.sources):
                    outfile = f'timeseries_{self.var}_{model}_{exp}_{source}.nc'
                    self.logger.debug(f"Saving data to {outdir}/{outfile}")
                    if self.monthly:
                        self.data_mon[i].to_netcdf(os.path.join(outdir, outfile))
                    if self.annual:
                        self.data_annual[i].to_netcdf(os.path.join(outdir, outfile))

        if self.plot_ref:
            outfile = f'timeseries_{self.var}_ref.nc'
            self.logger.debug(f"Saving reference data to {outdir}/{outfile}")
            if self.monthly:
                self.ref_mon.to_netcdf(os.path.join(outdir, outfile))
            if self.annual:
                self.ref_ann.to_netcdf(os.path.join(outdir, outfile))

            outfile = f'timeseries_{self.var}_std.nc'
            self.logger.debug(f"Saving std data to {outdir}/{outfile}")
            if self.monthly:
                self.ref_mon_std.to_netcdf(os.path.join(outdir, outfile))
            if self.annual:
                self.ref_ann_std.to_netcdf(os.path.join(outdir, outfile))
