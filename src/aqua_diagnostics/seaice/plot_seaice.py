""" PlotSeaIce doc """
import os
import xarray as xr
from matplotlib import pyplot as plt

from aqua.exceptions import NoDataError, NotEnoughDataError
from aqua.logger import log_configure, log_history
from aqua.util import ConfigPath, OutputSaver
from aqua.graphics import plot_timeseries

xr.set_options(keep_attrs=True)

class PlotSeaIce:
    """ PlotSeaIce class """
    
    def __init__(self, 
                 monthly_models=None, annual_models =None,
                 monthly_ref=None, annual_ref=None,
                 plot_std=None, # 'ref', 'all', ('model', int) [the int give the list index for the model to use]
                 plot_anom=None, # 'ref', ('model', int) [the int give the list index for the model to use]                
                 harmonise_time=None, # 'common', 'to_ref' (only if ref is given), tuple: ('to_model', int) [the int give the list index for the time to use]
                 fillna=None, # 'zero', 'nan', 'interpolate', 'value'
                 plot_kw={'ylimits': {}, 'xlimits': {}, 
                          'title': None, 'xlabel': None, 'ylabel': None, 'grid': None, 'figsize': None},
                 twinx=None, # {'ts_left': int, 'ts_right': int} NB: the int is the index of the model to use in the list monthly or annual_models
                 longname=None, # longname (str): Long name of the variable. Default is None and logname attribute is used.
                 unit=None, # This might involve some function to get the unit of the variable or to convert the unit [from timeseries.py 
                            # Units of the variable. Default is None and units attribute is used.]
                 save=True,
                 outdir='./',
                 loglevel='WARNING',
                 rebuild=None, 
                 filename_keys=None,  # List of keys to keep in the filename. Default is None, which includes all keys.
                 save_pdf=True, save_png=True, dpi=300):
        
        self.loglevel = loglevel
        self.logger = log_configure(log_level=self.loglevel, log_name='PlotSeaIce')

        # self.logger = log_history()

        self.monthly_models = monthly_models
        self.annual_models = annual_models
        self.monthly_ref = monthly_ref
        self.annual_ref = annual_ref
        self.plot_std = plot_std
        self.plot_anom = plot_anom
        self.harmonise_time = harmonise_time
        self.fillna = fillna
        self.plot_kw = plot_kw
        self.twinx = twinx
        self.longname = longname
        self.unit = unit
        self.save = save
        self.outdir = outdir

    def plot_seaice(self, #data: xr.Dataset,
                    monthly_data=None,
                    annual_data=None,
                    ref_monthly_data=None,
                    ref_annual_data=None,
                    std_monthly_data=None,
                    std_annual_data=None,
                    data_labels: list = None,
                    ref_label: str = None,
                    loglevel: str = 'WARNING',
                    **kwargs):

        """ Plot data """
        '''
        if data is None:
            raise NoDataError("No data to plot")

        if len(data.time) < 2:
            raise NotEnoughDataError("Not enough data to plot")
        '''

        fig, ax = plt.subplots()
        data.seaice_extent.plot(ax=ax)
        fig.savefig(os.path.join(self.output.path, "seaice_extent.png"))
        plt.close(fig)
        self.logger.info("Seaice extent plot saved")

        if unit is None:
            unit = index.units
        '''
        def plot_timeseries(monthly_data=None,
                annual_data=None,
                ref_monthly_data=None,
                ref_annual_data=None,
                std_monthly_data=None,
                std_annual_data=None,
                data_labels: list = None,
                ref_label: str = None,
                loglevel: str = 'WARNING',
                **kwargs):
        '''
    def plot_diff():
        """ Plot difference """
        pass

    def time_harmonisation(self, monthly_array_list, annual_array_list, monthly_ref, annual_ref, harmonise_time):
        """ Harmonise time """
        if harmonise_time is not None:
            if harmonise_time == "common":
                # Harmonise time to common period
                common_time = xr.concat([monthly_ref.time, annual_ref.time], dim="time").time
                monthly_array_list = [array.sel(time=common_time) for array in monthly_array_list]
                annual_array_list = [array.sel(time=common_time) for array in annual_array_list]
            elif harmonise_time == "to_ref":
                # Harmonise time to reference
                monthly_array_list = [array.sel(time=monthly_ref.time) for array in monthly_array_list]
                annual_array_list = [array.sel(time=annual_ref.time) for array in annual_array_list]
            elif isinstance(harmonise_time, tuple):
                # Harmonise time to specific time

                if harmonise_time[0] == "to_model":
                    targ_time_index = int(harmonise_time[1])
                    monthly_array_list = [array.sel(time=monthly_ref.time[targ_time_index]) for array in monthly_array_list]
                    annual_array_list = [array.sel(time=annual_ref.time[targ_time_index]) for array in annual_array_list]
                # elif if the tuple entries are time strings such as ['2020-01-01', '2020-12-31']
                elif harmonise_time[0] == 'TODO':
                    pass

                    time_index = int(harmonise_time[1])
                    monthly_array_list = [array.sel(time=monthly_ref.time[time_index]) for array in monthly_array_list]
                    annual_array_list = [array.sel(time=annual_ref.time[time_index]) for array in annual_array_list]
            else:
                self.logger.error(' ADDD LOGGER.')
                raise ValueError("Invalid harmonise_time value")

        if isinstance(var, str):
            print(f"String detected: {var.upper()}")
        elif isinstance(var, (int, float)):  # Handles numbers
            print(f"Number detected: {var * 2}")
        else:
            print("Unsupported type!") 
    
        """ Other thing to include might be the twinx() method to plot two different y-axis on the same plot
        the user must choose between the two model (if multiples given) to plot on the first and the second y-axis 
        """

        """ ANOMLAY
        If comparing two datasets with different reliability (e.g., observations vs. model), you can weight based on uncertainty:

        ~~~ Weight by Confidence/Uncertainty
        # Assume lower standard deviation means more reliable data
        uncertainty = ds["uncertainty"]  # Standard deviation or confidence metric
        weights = 1 / uncertainty  # Higher weight for lower uncertainty
        weights /= weights.max()  # Normalize

        # Compute weighted anomaly
        anomaly = (time_series1 - time_series2) * weights
        
        ~~~ Weighted Anomaly Using External Weights
        If you have predefined weights (e.g., from external datasets or expert judgment):
        external_weights = xr.open_dataarray("weights.nc")  # Precomputed weights
        anomaly = (time_series1 - time_series2) * external_weights
        """

        """_notes_summary_
        * Imagine I put data with different time limits, one thing I might want is to huniform the data I gave
        *
        *
        """