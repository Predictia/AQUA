import sys
import os
import argparse
from aqua.util import load_yaml, get_arg
from aqua import Reader
from aqua.logger import log_configure

aqua_path = os.getenv('AQUA')  # This will return None if 'AQUA' is not set
sys.path.insert(0, os.path.join(aqua_path, 'diagnostics'))
from tropical_rainfall import Tropical_Rainfall

def parse_arguments(args):
    """Parse command line arguments"""

    parser = argparse.ArgumentParser(description='Trop. Rainfall CLI')
    parser.add_argument('-c', '--config', type=str,
                        help='yaml configuration file')
    parser.add_argument('-l', '--loglevel', type=str,
                        help='log level [default: WARNING]')

    # This arguments will override the configuration file if provided
    parser.add_argument('--model', type=str, help='model name',
                        required=False)
    parser.add_argument('--exp', type=str, help='experiment name',
                        required=False)
    parser.add_argument('--source', type=str, help='source name',
                        required=False)
    parser.add_argument('--outputdir', type=str, help='output directory',
                        required=False)
    parser.add_argument('--nproc', type=int, required=False,
                        help='the number of processes to run in parallel',
                        default=4)
    return parser.parse_args(args)


def validate_arguments(args):
    """
    Validate the types of command line arguments.

    Args:
        args: Parsed arguments from argparse.

    Raises:
        TypeError: If any argument is not of the expected type.
    """
    if args.config and not isinstance(args.config, str):
        raise TypeError("Config file path must be a string.")
    if args.loglevel and not isinstance(args.loglevel, str):
        raise TypeError("Log level must be a string.")
    if args.model and not isinstance(args.model, str):
        raise TypeError("Model name must be a string.")
    if args.exp and not isinstance(args.exp, str):
        raise TypeError("Experiment name must be a string.")
    if args.source and not isinstance(args.source, str):
        raise TypeError("Source name must be a string.")
    if args.outputdir and not isinstance(args.outputdir, str):
        raise TypeError("Output directory must be a string.")
    if args.nproc and not isinstance(args.nproc, int):
        raise TypeError("The number of processes (nproc) must be an integer.")


def load_configuration(file_path):
    """Load and return the YAML configuration."""
    print('Reading configuration YAML file..')
    config = load_yaml(file_path)
    return config


def adjust_year_range_based_on_dataset(full_dataset, start_year=None, final_year=None):
    """
    Adjusts the start and end years for processing based on the dataset's time range and optional user inputs.
    """
    # Extract the first and last year from the dataset's time dimension
    try:
        first_year_in_dataset = full_dataset['time'].dt.year.values[0]
        last_year_in_dataset = full_dataset['time'].dt.year.values[-1]
    except AttributeError:
        raise ValueError("The dataset must have a 'time' dimension with datetime64 data.")

    # Adjust start_year based on the dataset's range or user input
    start_year = first_year_in_dataset if start_year is None else max(start_year, first_year_in_dataset)

    # Adjust final_year based on the dataset's range or user input
    final_year = last_year_in_dataset if final_year is None else min(final_year, last_year_in_dataset)

    return start_year, final_year

class Tropical_Rainfall_CLI:
    def __init__(self, config, args):
        self.freq = config['data']['freq']
        self.regrid = config['data']['regrid']
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

        self.color  = config['plot']['color']
        self.figsize = config['plot']['figsize']
        self.xmax = config['plot']['xmax']
        self.loc = config['plot']['loc']
        self.pdf_format = config['plot']['pdf_format']

        self.model = get_arg(args, 'model', config['data']['model'])
        self.exp = get_arg(args, 'exp', config['data']['exp'])
        self.source = get_arg(args, 'source', config['data']['source'])
        self.loglevel = get_arg(args, 'loglevel', config['logger']['loglevel'])

        nproc = get_arg(args, 'nproc', config['compute_resources']['nproc'])
        machine = config['machine']
        path_to_output = get_arg(args, 'outputdir', config['output'][machine])

        self.mswep = config['mswep'][machine]

        self.logger = log_configure(log_name="Trop. Rainfall CLI", log_level=self.loglevel)

        self.rebuild_output = config['rebuild_output']
        if path_to_output is not None:
            self.path_to_netcdf = os.path.join(path_to_output, f'netcdf/{self.model}_{self.exp}_{self.source}/')
            self.path_to_pdf = os.path.join(path_to_output, f'pdf/{self.model}_{self.exp}_{self.source}/')
        else:
            self.path_to_netcdf = self.path_to_pdf = None

        self.reader = Reader(model=self.model, exp=self.exp, source=self.source, loglevel=self.loglevel, regrid=self.regrid, nproc=nproc)
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

        s_year, f_year = adjust_year_range_based_on_dataset(full_dataset, start_year=self.s_year, final_year=self.f_year)
        s_month = 1 if self.s_month is None else self.s_month
        f_month = 12 if self.f_month is None else self.f_month

        for year in range(s_year, f_year+1):
            data_per_year = full_dataset.sel(time=str(year))
            if data_per_year.time.size != 0:
                for x in range(s_month, f_month+1):
                    path_to_output = self.path_to_netcdf+f"{self.regrid}/{self.freq}/histograms/"

                    bins_info = self.diag.get_bins_info()
                    keys = [f"{bins_info}_{year}-{x:02}", self.model, self.exp, self.source, self.regrid, self.freq]
                    self.logger.debug(f"The keys are: {keys}")

                    # Check for file existence based on keys and decide on rebuilding
                    if self.rebuild_output and self.diag.tools.find_files_with_keys(folder_path=path_to_output, keys=keys):
                        self.logger.info("Rebuilding output...")
                        self.diag.tools.remove_file_if_exists_with_keys(folder_path=path_to_output, keys=keys)
                    elif not self.diag.tools.find_files_with_keys(folder_path=path_to_output, keys=keys):
                        self.logger.info("No existing output. Proceeding with data processing...")
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

    def plot_histograms(self):
        """
        Generates and saves histogram plots for the specified model, experiment, and source data over a defined period.
        It constructs the plot titles and legends based on model, experiment, and source details, merges histograms
        from specified paths, and plots them. Additionally, it attempts to plot comparative histograms using MSWEP
        data if available. The function handles the absence of MSWEP data gracefully by logging an error. Plots are
        saved to the specified PDF format in the provided path.
        """
        plot_title = f"{self.model} {self.exp} {self.source} {self.regrid} {self.freq}"
        legend = f"{self.model} {self.exp} {self.source}"
        name_of_pdf =f"{self.model}_{self.exp}_{self.source}"

        self.logger.debug(f"The path to file is: {self.path_to_netcdf}{self.regrid}/{self.freq}/histograms/.")
        hist_merged = self.diag.merge_list_of_histograms(path_to_histograms=self.path_to_netcdf+f"{self.regrid}/{self.freq}/histograms/",
                                                    all=True, start_year=self.s_year, end_year=self.f_year,
                                                    start_month=self.s_month, end_month=self.f_month)

        add = self.diag.histogram_plot(hist_merged, figsize=self.figsize, new_unit=self.new_unit,
                            legend=legend, color=self.color, xmax=self.xmax, plot_title=plot_title, loc=self.loc,
                            path_to_pdf=self.path_to_pdf, pdf_format=self.pdf_format, name_of_file=name_of_pdf)

        mswep_folder_path = f'{self.mswep}{self.regrid}/{self.freq}'
        # Check if the folder exists
        if not os.path.exists(mswep_folder_path):
            self.logger.error(f"Error: The folder for MSWEP data with resolution '{self.regrid}' "
                            f"and frequency '{self.freq}' does not exist. Histograms for the "
                            "desired resolution and frequency have not been computed yet.")
        else:
            obs_merged = self.diag.merge_list_of_histograms(path_to_histograms=mswep_folder_path, all=True,
                                                            start_year=self.s_year, end_year=self.f_year,
                                                        start_month=self.s_month, end_month=self.f_month)
            self.logger.info(f"The MSWEP data with resolution '{self.regrid}' and frequency '{self.freq}' are prepared for comparison.")

            self.diag.histogram_plot(hist_merged, figsize=self.figsize, new_unit=self.new_unit, add=add,
                                linewidth=2*self.diag.plots.linewidth, linestyle='--', color='tab:red',
                                legend=f"MSWEP", xmax=self.xmax,  loc=self.loc, plot_title=plot_title,
                                path_to_pdf=self.path_to_pdf, pdf_format=self.pdf_format, name_of_file=name_of_pdf)
        self.logger.info("The histograms are plotted and saved in storage.")

def main():
    """Main function to orchestrate the tropical rainfall CLI operations."""
    args = parse_arguments(sys.argv[1:])
    validate_arguments(args)

    config = load_configuration(get_arg(args, 'config',
                                        f'{aqua_path}/diagnostics/tropical_rainfall/cli/cli_config_trop_rainfall.yml'))

    trop_rainfall_cli = Tropical_Rainfall_CLI(config, args)
    trop_rainfall_cli.calculate_histogram_by_months()
    trop_rainfall_cli.plot_histograms()

if __name__ == '__main__':
    main()