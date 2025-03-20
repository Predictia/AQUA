from aqua.graphics import plot_timeseries
from aqua.logger import log_configure
from aqua.util import to_list


class PlotTimeseries:
    def __init__(self,hourly_data=None, daily_data=None,
                 monthly_data=None, annual_data=None,
                 ref_hourly_data=None, ref_daily_data=None,
                 ref_monthly_data=None, ref_annual_data=None,
                 std_hourly_data=None, std_daily_data=None,
                 std_monthly_data=None, std_annual_data=None,
                 loglevel: str = 'WARNING'):
        
        self.loglevel = loglevel
        self.logger = log_configure(self.loglevel, 'PlotTimeseries')

        for data in [hourly_data, daily_data, ref_hourly_data, ref_daily_data,
                     std_hourly_data, std_daily_data]:
            if data is not None:
                self.logger.error('Hourly and daily data are not yet supported')
        
        self.monthly_data = to_list(monthly_data)
        self.annual_data = to_list(annual_data)
        self.ref_monthly_data = to_list(ref_monthly_data)
        self.ref_annual_data = to_list(ref_annual_data)
        self.std_monthly_data = to_list(std_monthly_data)
        self.std_annual_data = to_list(std_annual_data)

        self.data_dict = {'monthly': self.monthly_data, 'annual': self.annual_data}
        self.ref_dict = {'monthly': self.ref_monthly_data, 'annual': self.ref_annual_data}
        self.std_dict = {'monthly': self.std_monthly_data, 'annual': self.std_annual_data}

    def run(self):

        self.logger.info('Running PlotTimeseries')
        self.set_data_labels()
        self.set_ref_label()
        self.set_description()
        self.plot_timeseries()
        self.logger.info('PlotTimeseries completed successfully')

    def set_data_labels(self):
        return

    def set_ref_label(self):
        return

    def set_description(self):
        return

    def plot_timeseries(self):
        
        fig, ax = plot_timeseries(monthly_data=self.monthly_data,
                            ref_monthly_data=self.ref_monthly_data,
                            std_monthly_data=self.std_monthly_data,
                            annual_data=self.annual_data,
                            ref_annual_data=self.ref_annual_data,
                            std_annual_data=self.std_annual_data,
                            data_labels=self.data_labels,
                            return_fig=True,
                            ref_label=self.ref_label, loglevel=self.loglevel)