import os
import pandas as pd
from aqua.util import get_arg
from aqua import Reader
from aqua.logger import log_configure
from aqua.util import add_pdf_metadata
from dask.distributed import Client, LocalCluster
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
        self.loc = config['plot']['loc']
        self.pdf_format = config['plot']['pdf_format']
        self.factor = config['plot']['factor']

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
        path_to_buffer = get_arg(args, 'bufferdir', config['buffer'][machine])

        self.xmax = get_arg(args, 'xmax', config['plot']['xmax'])

        self.mswep = config['mswep'][machine]
        self.mswep_s_year = config['mswep']['s_year']
        self.mswep_f_year = config['mswep']['f_year']
        self.mswep_auto = config['mswep']['auto']
        
        self.era5 = config['era5'][machine]
        self.era5_s_year = config['era5']['s_year']
        self.era5_f_year = config['era5']['f_year']
        self.era5_auto = config['era5']['auto']
        
        self.imerg = config['imerg'][machine]
        self.imerg_s_year = config['imerg']['s_year']
        self.imerg_f_year = config['imerg']['f_year']
        self.imerg_auto = config['imerg']['auto']
  
        self.logger = log_configure(log_name="Trop. Rainfall CLI", log_level=self.loglevel)

        # Dask distributed cluster
        nworkers = get_arg(args, 'nworkers', None)
        if nworkers:
            cluster = LocalCluster(n_workers=nworkers, threads_per_worker=1)
            client = Client(cluster)
            self.logger.info(f"Running with {nworkers} dask distributed workers.")


        self.rebuild_output = config['rebuild_output']
        if path_to_output is not None:
            self.path_to_netcdf = os.path.join(path_to_output, f'netcdf/{self.model}_{self.exp}/')
            self.path_to_pdf = os.path.join(path_to_output, f'pdf/{self.model}_{self.exp}/')
            self.path_to_buffer = os.path.join(path_to_buffer, f'netcdf/{self.model}_{self.exp}/')
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
                    path_to_output = self.path_to_buffer+f"{self.regrid}/{self.freq}/histograms/"

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

    def get_merged_histogram_for_source(self, source_info, default_interval=10):
        """
        Merges histogram data for a given source based on specified parameters or defaults.
        """
        folder_name = 'yearly_grouped' if self.s_month is None and self.f_month is None else 'monthly_grouped'
        folder_path = os.path.join(source_info['path'], self.regrid, self.freq, folder_name)
        self.logger.info(f"The path to {source_info['name']} data is {folder_path}")

        if not os.path.exists(folder_path):
            self.logger.error(f"Error: The folder for {source_info['name']} data with resolution '{self.regrid}' "
                              f"and frequency '{self.freq}' does not exist.")
            return None

        start_year = self.s_year - default_interval if source_info.get('auto', False) else source_info.get('s_year', self.s_year)
        end_year = self.f_year + default_interval if source_info.get('auto', False) else source_info.get('f_year', self.f_year)

        return self.diag.merge_list_of_histograms(
            path_to_histograms=folder_path,
            start_year=start_year, end_year=end_year,
            start_month=self.s_month, end_month=self.f_month
        )

    def plot_histograms(self):
        """
        Optimized method to handle the merging and plotting of histograms from multiple sources.
        """
        hist_path = f"{self.path_to_netcdf}histograms/"
        hist_buffer_path = f"{self.path_to_buffer}{self.regrid}/{self.freq}/histograms/"
        bins_info = self.diag.get_bins_info()
        model_merged = self.diag.merge_list_of_histograms(
            path_to_histograms=hist_buffer_path,
            start_year=self.s_year, end_year=self.f_year,
            start_month=self.s_month, end_month=self.f_month,
            flag=bins_info
        )
        self.diag.dataset_to_netcdf(model_merged, path_to_netcdf=hist_path, name_of_file=f'histogram_{self.model}_{self.exp}_{self.regrid}_{self.freq}')
        
        # Define source information for MSWEP, IMERG, ERA5
        sources = [
            {'name': 'MSWEP', 'path': self.mswep, 's_year': self.mswep_s_year, 'f_year': self.mswep_f_year, 'auto': self.mswep_auto},
            {'name': 'IMERG', 'path': self.imerg, 's_year': self.imerg_s_year, 'f_year': self.imerg_f_year, 'auto': self.imerg_auto},
            {'name': 'ERA5', 'path': self.era5, 's_year': self.era5_s_year, 'f_year': self.era5_f_year, 'auto': self.era5_auto}
        ]

        # Loop through each source and process
        for source in sources:
            merged_data = self.get_merged_histogram_for_source(source)
            if merged_data is not None:
                self.diag.dataset_to_netcdf(
                    merged_data, path_to_netcdf=hist_path,
                    name_of_file=f"histogram_{source['name']}_{self.regrid}_{self.freq}"
                )

        # Example call to process_histograms, set flags as necessary
        pdf, pdfP = True, False
        self.process_histograms(pdf_flag=pdf, pdfP_flag=pdfP, model_merged=model_merged,
                                mswep_merged=self.get_merged_histogram_for_source(sources[0]),
                                imerg_merged=self.get_merged_histogram_for_source(sources[1]),
                                era5_merged=self.get_merged_histogram_for_source(sources[2]))

        self.logger.info("The Tropical Rainfall diagnostic is terminated.")
        
    def process_histograms(self, pdf_flag, pdfP_flag, model_merged=None, mswep_merged=None, 
                       imerg_merged=None, era5_merged=None, linestyle='--'):
        """
        Generates and saves histograms for model and observational data, with options for PDF and PDF*P plots.
        Allows for some datasets to be None, in which case those plots are skipped.
        """
        plot_title = f"Grid: {self.regrid}, frequency: {self.freq}"
        legend_model = f"{self.model} {self.exp}"
        name_of_pdf = f"{self.model}_{self.exp}_{self.regrid}_{self.freq}"
        if pdf_flag:
            description = f"Comparison of the probability distribution function (PDF) for precipitation data from {self.model} {self.exp}, \
                measured in {self.new_unit}, over the time range {model_merged.time_band}, against observations."
        else:
            description = f"Comparison of the probability distribution function (PDF) multiplied by probability (PDF*P) \
                for precipitation data from {self.model} {self.exp}, measured in {self.new_unit}, \
                    across the time range {model_merged.time_band}, with observations."

        self.logger.debug('Description: %s', description)
                    
        # Initial plot with model data if it exists
        if model_merged is not None:
            add, _path_to_pdf = self.diag.histogram_plot(model_merged, figsize=self.figsize, new_unit=self.new_unit, pdf=pdf_flag,
                                        pdfP=pdfP_flag, legend=legend_model, color=self.color, xmax=self.xmax,
                                        plot_title=plot_title, loc=self.loc, path_to_pdf=self.path_to_pdf,
                                        pdf_format=self.pdf_format, name_of_file=name_of_pdf, factor=self.factor)
            
            add_pdf_metadata(filename=_path_to_pdf, metadata_value=description,
                             old_metadata = True, loglevel = self.loglevel)
        else:
            add = False  # Ensures that additional plots can be added to an existing plot if the model data is unavailable

        # Subsequent plots for each dataset
        if mswep_merged is not None:
            add, _path_to_pdf = self.diag.histogram_plot(mswep_merged, figsize=self.figsize, new_unit=self.new_unit, add=add, pdf=pdf_flag,
                                    pdfP=pdfP_flag, linewidth=1, linestyle=linestyle, color='tab:red',
                                    legend="MSWEP", xmax=self.xmax, loc=self.loc, plot_title=plot_title,
                                    path_to_pdf=self.path_to_pdf, pdf_format=self.pdf_format, name_of_file=name_of_pdf,
                                    factor=self.factor)
            description = f"The time range of MSWEP is {mswep_merged.time_band}."
            add_pdf_metadata(filename=_path_to_pdf, metadata_value=description,
                             old_metadata = True, loglevel = self.loglevel)
            self.logger.info("Plotting MSWEP data for comparison.")
        else:
            self.logger.warning("MSWEP data with a proper resolution is NOT found for comparison.")

        if imerg_merged is not None:
            add, _path_to_pdf = self.diag.histogram_plot(imerg_merged, figsize=self.figsize, new_unit=self.new_unit, add=add, pdf=pdf_flag,
                                    pdfP=pdfP_flag, linewidth=1, linestyle=linestyle, color='tab:blue',
                                    legend="IMERG", xmax=self.xmax, loc=self.loc, plot_title=plot_title,
                                    path_to_pdf=self.path_to_pdf, pdf_format=self.pdf_format, name_of_file=name_of_pdf,
                                    factor=self.factor)
            description = f"The time range of IMERG is {imerg_merged.time_band}."
            add_pdf_metadata(filename=_path_to_pdf, metadata_value=description, loglevel = self.loglevel)
            self.logger.info("Plotting IMERG data for comparison.")
        else:
            self.logger.warning("IMERG data with a proper resolution is NOT found for comparison.")

        if era5_merged is not None:
            add, _path_to_pdf = self.diag.histogram_plot(era5_merged, figsize=self.figsize, new_unit=self.new_unit, add=add, pdf=pdf_flag,
                                    pdfP=pdfP_flag, linewidth=1, linestyle=linestyle, color='tab:orange',
                                    legend="ERA5", xmax=self.xmax, loc=self.loc, plot_title=plot_title,
                                    path_to_pdf=self.path_to_pdf, pdf_format=self.pdf_format, name_of_file=name_of_pdf,
                                    factor=self.factor)
            description = f"The time range of ERA5 is {era5_merged.time_band}."
            add_pdf_metadata(filename=_path_to_pdf, metadata_value=description,
                             old_metadata = True, loglevel = self.loglevel)
            self.logger.info("Plotting ERA5 data for comparison.")
        else:
            self.logger.warning("ERA5 data with a proper resolution is NOT found for comparison.")
        self.logger.info("Histogram plots (as available) have been generated and saved.")
    
    