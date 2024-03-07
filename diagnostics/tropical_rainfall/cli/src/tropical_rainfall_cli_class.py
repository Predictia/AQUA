import os
import pandas as pd
from aqua.util import get_arg
from aqua import Reader
from aqua.logger import log_configure
from tropical_rainfall import Tropical_Rainfall
from .tropical_rainfall_utils import adjust_year_range_based_on_dataset


class Tropical_Rainfall_CLI:
    def __init__(self, config, args):
        self.s_year = config['data']['s_year']
        self.f_year = config['data']['f_year']
        self.s_month = config['data']['s_month']
        self.f_month = config['data']['f_month']

        self.trop_lat = config['class_attributes']['trop_lat']
        self.num_of_bins = config['class_attributes']['num_of_bins']
        self.first_edge = config['class_attributes']['first_edge']
        self.width_of_bin = config['class_attributes']['width_of_bin']
        self.model_variable = config['class_attributes']['model_variable']
        self.new_unit = config['class_attributes']['new_unit']

        self.color = config['plot']['color']
        self.figsize = config['plot']['figsize']
        self.xmax = config['plot']['xmax']
        self.loc = config['plot']['loc']
        self.pdf_format = config['plot']['pdf_format']

        self.model = get_arg(args, 'model', config['data']['model'])
        self.exp = get_arg(args, 'exp', config['data']['exp'])
        self.source = get_arg(args, 'source', config['data']['source'])
        self.freq = get_arg(args, 'freq', config['data']['freq'])
        self.regrid = get_arg(args, 'regrid', config['data']['regrid'])
        self.loglevel = get_arg(args, 'loglevel', config['logger']['diag_loglevel'])
        reader_loglevel = get_arg(args, 'loglevel', config['logger']['reader_loglevel'])

        nproc = get_arg(args, 'nproc', config['compute_resources']['nproc'])
        machine = config['machine']
        path_to_output = get_arg(args, 'outputdir', config['output'][machine])

        self.mswep = config['mswep'][machine]

        self.logger = log_configure(log_name="Trop. Rainfall CLI", log_level=self.loglevel)

        self.rebuild_output = config['rebuild_output']
        if path_to_output is not None:
            self.path_to_netcdf = os.path.join(path_to_output, f'netcdf/{self.model}_{self.exp}/')
            self.path_to_pdf = os.path.join(path_to_output, f'pdf/{self.model}_{self.exp}/')
        else:
            self.path_to_netcdf = self.path_to_pdf = None

        self.reader = Reader(model=self.model, exp=self.exp, source=self.source, loglevel=reader_loglevel, regrid=self.regrid,
                             nproc=nproc)
        self.diag = Tropical_Rainfall(trop_lat=self.trop_lat, num_of_bins=self.num_of_bins, first_edge=self.first_edge,
                                      width_of_bin=self.width_of_bin, loglevel=self.loglevel)

    def need_regrid_timmean(self, full_dataset):
        """Determines whether regridding or time averaging is needed for a dataset."""
        test_sample = full_dataset.isel(time=slice(1, 5))
        # Check for the need of regridding
        regrid_bool = False
        if isinstance(self.regrid, str):
            regrid_bool = self.diag.tools.check_need_for_regridding(test_sample, self.regrid)
        # Check for the need of time averaging
        freq_bool = False
        if isinstance(self.freq, str):
            freq_bool = self.diag.tools.check_need_for_time_averaging(test_sample, self.freq)
        return regrid_bool, freq_bool

    def calculate_histogram_by_months(self):
        """
        Calculates and saves histograms for each month within a specified year range. This function checks if histograms
        already exist in the specified output directory and decides whether to rebuild them based on the `rebuild_output` flag.
        It leverages the dataset to generate histograms by selecting data for each month, regridding and calculating the time mean
        if necessary, and then saves the histogram files in the designated path. This process is logged, and any years not present
        in the dataset are flagged with a warning.
        """
        full_dataset = self.reader.retrieve(var=self.model_variable)
        regrid_bool, freq_bool = self.need_regrid_timmean(full_dataset)

        self.s_year, self.f_year = adjust_year_range_based_on_dataset(full_dataset, start_year=self.s_year,
                                                                      final_year=self.f_year)
        s_month = 1 if self.s_month is None else self.s_month
        f_month = 12 if self.f_month is None else self.f_month

        for year in range(self.s_year, self.f_year+1):
            data_per_year = full_dataset.sel(time=str(year))
            if data_per_year.time.size != 0:
                for x in range(s_month, f_month+1):
                    path_to_output = self.path_to_netcdf+f"{self.regrid}/{self.freq}/histograms/"

                    bins_info = self.diag.get_bins_info()
                    keys = [f"{bins_info}_{year}-{x:02}", self.model, self.exp, self.regrid, self.freq]

                    # Check for file existence based on keys and decide on rebuilding
                    if self.rebuild_output and self.diag.tools.find_files_with_keys(folder_path=path_to_output, keys=keys):
                        self.logger.info("Rebuilding output...")
                        self.diag.tools.remove_file_if_exists_with_keys(folder_path=path_to_output, keys=keys)
                    elif not self.diag.tools.find_files_with_keys(folder_path=path_to_output, keys=keys):
                        self.logger.debug("No existing output. Proceeding with data processing...")
                        try:
                            data = data_per_year.sel(time=str(year)+'-'+str(x))
                            if freq_bool:
                                data = self.reader.timmean(data, freq=self.freq)
                            if regrid_bool:
                                data = self.reader.regrid(data)
                            self.diag.histogram(data, model_variable=self.model_variable,
                                                path_to_histogram=path_to_output,
                                                threshold = 30, name_of_file=f"{self.regrid}_{self.freq}")
                            self.logger.debug(f"The path to file is: {path_to_output}")
                        except KeyError:
                            pass
                        except Exception as e:
                                # Handle other exceptions
                                self.logger.error(f"An unexpected error occurred: {e}")
                    self.logger.debug(f"Current Status: {x}/{f_month} months processed in year {year}.")
            else:
                self.logger.warning("The specified year is not present in the dataset. " +
                            "Ensure the time range in your selection accurately reflects the available " +
                            "data. Check dataset time bounds and adjust your time selection parameters accordingly.")
        self.logger.info("The histograms are calculated and saved in storage.")
        return None

    def process_histograms(self, pdf_flag, plot_color='tab:red', linestyle='--'):
        """
        Processes histogram data by merging histograms from specified paths, plotting the merged histograms,
        and checking for the existence of a specific folder path for additional data comparison. Logs relevant
        information, errors, and successful completions
        """
        plot_title = f"Grid: {self.regrid}, frequency: {self.freq}"
        legend = f"{self.model} {self.exp}"
        name_of_pdf = f"{self.model}_{self.exp}"
        
        self.logger.debug(f"The path to file is: {self.path_to_netcdf}{self.regrid}/{self.freq}/histograms/.")

        hist_path = f"{self.path_to_netcdf}{self.regrid}/{self.freq}/histograms/"
        hist_merged = self.diag.merge_list_of_histograms(path_to_histograms=hist_path,
                                                        all=True, start_year=self.s_year, end_year=self.f_year,
                                                        start_month=self.s_month, end_month=self.f_month)

        add = self.diag.histogram_plot(hist_merged, figsize=self.figsize, new_unit=self.new_unit, pdf=pdf_flag,
                                    legend=legend, color=self.color, xmax=self.xmax, plot_title=plot_title, loc=self.loc,
                                    path_to_pdf=self.path_to_pdf, pdf_format=self.pdf_format, name_of_file=name_of_pdf)

        mswep_folder_path = os.path.join(self.mswep, self.regrid, self.freq)
        if not os.path.exists(mswep_folder_path):
            self.logger.error(f"Error: The folder for MSWEP data with resolution '{self.regrid}' "
                            f"and frequency '{self.freq}' does not exist. Histograms for the "
                            "desired resolution and frequency have not been computed yet.")
            return
        obs_interval = 1
        obs_merged = self.diag.merge_list_of_histograms(path_to_histograms=mswep_folder_path, all=True,
                                                        start_year=self.s_year-obs_interval, end_year=self.f_year+obs_interval,
                                                        start_month=self.s_month, end_month=self.f_month)
        self.logger.info(f"The MSWEP data with resolution '{self.regrid}' and frequency '{self.freq}' are prepared for comparison.")

        self.diag.histogram_plot(obs_merged, figsize=self.figsize, new_unit=self.new_unit, add=add, pdf=pdf_flag,
                                linewidth=2*self.diag.plots.linewidth, linestyle=linestyle, color=plot_color,
                                legend="MSWEP", xmax=self.xmax, loc=self.loc, plot_title=plot_title,
                                path_to_pdf=self.path_to_pdf, pdf_format=self.pdf_format, name_of_file=name_of_pdf)

        self.logger.info("The histograms are plotted and saved in storage.")
    
    def plot_histograms(self):
        """
        Generates and saves histogram plots for the specified model, experiment, and source data over a defined period.
        It constructs the plot titles and legends based on model, experiment, and source details, merges histograms
        from specified paths, and plots them. Additionally, it attempts to plot comparative histograms using MSWEP
        data if available. The function handles the absence of MSWEP data gracefully by logging an error. Plots are
        saved to the specified PDF format in the provided path.
        """
        pdf = True  # Set your PDF flag as needed
        self.process_histograms(pdf_flag=pdf)
        pdfP = True  # Set your PDF flag as needed
        self.process_histograms(pdf_flag=pdfP)
        
        self.logger.info("The Tropical Rainfall diagnostic is terminated.")
        
    def daily_variability(self):
        """
        Evaluates the daily variability of the dataset based on the specified model variable and frequency.
        This method specifically processes datasets with an hourly frequency ('h' or 'H') by slicing the first
        and last weeks of data within the defined start and final year and month range. It supports optional
        regridding of the data for these periods. The method adds localized time information to the sliced
        datasets and saves this information for further diagnostic analysis.
        """
        if 'h' in self.freq.lower():
            self.logger.debug("Contains 'h' or 'H'")
            full_dataset = self.reader.retrieve(var=self.model_variable)
            regrid_bool, freq_bool = self.need_regrid_timmean(full_dataset)
            self.s_year, self.f_year = adjust_year_range_based_on_dataset(full_dataset, start_year=self.s_year,
                                                                          final_year=self.f_year)

            # Ensure months are defined
            s_month = 1 if self.s_month is None else self.s_month
            f_month = 12 if self.f_month is None else self.f_month

            days=1

            # Define the start and end dates for selection
            start_date = pd.Timestamp(year=self.s_year, month=s_month, day=1)
            end_date = start_date + pd.Timedelta(days=days)
            # Slice the dataset for the first week
            first_week_data = full_dataset.sel(time=slice(start_date, end_date))
            
            last_date = pd.to_datetime(full_dataset['time'].max().values)
            f_month = min(last_date.month, f_month)
            end_date = pd.Timestamp(year=self.f_year, month=f_month, day=1) + pd.offsets.MonthEnd(1)
            # Calculate the start date for the last week by subtracting 6 days from the end_date
            start_date_last_week = end_date - pd.Timedelta(days=days)
            # Now select the last week of data
            last_week_data = full_dataset.sel(time=slice(start_date_last_week, end_date))
            
            if regrid_bool:
                first_week_data = self.reader.regrid(first_week_data)
                last_week_data = self.reader.regrid(last_week_data)
            self.diag.add_localtime(first_week_data, name_of_file="first_week", rebuild=self.rebuild_output)
            self.diag.add_localtime(last_week_data, name_of_file="last_week")
        else:
            self.logger.warning("Data appears to be not in hourly intervals. The CLI will not provide the netcdf of daily variability.")
            
    def plot_daily_variability(self):
        if 'h' in self.freq.lower():
            self.logger.debug("Contains 'h' or 'H'")
            legend = f"{self.model} {self.exp}"
            name_of_pdf =f"{self.model}_{self.exp}"
            path_to_output = f"{self.diag.path_to_netcdf}daily_variability/"
            
            keys=["daily_variability", "first_week"]
            filename = self.diag.tools.find_files_with_keys(folder_path=path_to_output, keys=keys, get_path=True)
            add = self.diag.daily_variability_plot(path_to_netcdf=filename, legend=legend+' first_week', color='tab:red',
                                                path_to_pdf=self.path_to_pdf, pdf_format=self.pdf_format, 
                                                name_of_file=name_of_pdf)
            
            keys=["daily_variability", "last_week"]
            filename = self.diag.tools.find_files_with_keys(folder_path=path_to_output, keys=keys, get_path=True)
            add = self.diag.daily_variability_plot(path_to_netcdf=filename, legend=legend+' last_week', color='tab:green', add=add,
                                                linestyle='--', path_to_pdf=self.path_to_pdf, pdf_format=self.pdf_format,
                                                name_of_file=name_of_pdf)
        else:
            self.logger.warning("Data appears to be not in hourly intervals. The CLI will not provide the plot of daily variability.")
