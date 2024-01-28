import sys
sys.path.append('../')
from src.tropical_rainfall_tools import ToolsClass
import os
import argparse
from aqua.util import load_yaml, get_arg
from aqua import Reader
from aqua.logger import log_configure


def parse_arguments(args):
    """Parse command line arguments"""

    parser = argparse.ArgumentParser(description='Tropical Rainfall CLI')
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

    return parser.parse_args(args)


if __name__ == '__main__':
    args = parse_arguments(sys.argv[1:])

    # change the current directory to the one of the CLI so that relative path works
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    if os.getcwd() != dname:
        os.chdir(dname)
        print(f'Moving from current directory to {dname} to run!')

    try:
        sys.path.insert(0, '../../')
        from tropical_rainfall import Tropical_Rainfall
    except ImportError as import_error:
        print(f"ImportError occurred: {import_error}")
        sys.exit(0)
    except Exception as custom_error:
        print(f"CustomError occurred: {custom_error}")
        sys.exit(0)
    else:
        print("Modules imported successfully.")

    file = get_arg(args, 'config', 'config/trop_rainfall_config.yml')
    print('Reading configuration yaml file..')
    config = load_yaml(file)

    loglevel = get_arg(
        args, 'loglevel', config['class_attributes']['loglevel'])
    logger = log_configure(log_name="Tropical Rainfall CLI",
                           log_level=loglevel)

    model = get_arg(args, 'model', config['data']['model'])
    exp = get_arg(args, 'exp', config['data']['exp'])
    source = get_arg(args, 'source', config['data']['source'])
    logger.debug(f"Accessing {model} {exp} {source} data")

    freq = config['data']['freq']
    regrid = config['data']['regrid']
    s_year = config['data']['s_year']
    f_year = config['data']['f_year']

    machine = config['machine']
    logger.info(f"The machine is {machine}")

    path_to_output = get_arg(
        args, 'outputdir', config['path'][machine])

    if path_to_output is not None:
        path_to_netcdf = os.path.join(
            path_to_output, 'netcdf/'+model+'_'+exp+'_'+source+'/')
        path_to_pdf = os.path.join(
            path_to_output, 'pdf/'+model+'_'+exp+'_'+source+'/')
    name_of_netcdf = model+'_'+exp+'_'+source
    name_of_pdf = model+'_'+exp+'_'+source

    logger.debug(f"NetCDF folder: {path_to_netcdf}")
    logger.debug(f"PDF folder: {path_to_pdf}")

    trop_lat = config['class_attributes']['trop_lat']
    num_of_bins = config['class_attributes']['num_of_bins']
    first_edge = config['class_attributes']['first_edge']
    width_of_bin = config['class_attributes']['width_of_bin']

    model_variable = config['class_attributes']['model_variable']
    new_unit = config['class_attributes']['new_unit']

    color = config['plot']['color']
    figsize = config['plot']['figsize']
    legend = config['plot']['legend']
    xmax = config['plot']['xmax']
    plot_title = model+'_'+exp+'_'+source
    loc = config['plot']['loc']
    pdf_format = config['plot']['pdf_format']

    diag = Tropical_Rainfall(trop_lat=trop_lat, num_of_bins=num_of_bins,
                             first_edge=first_edge, width_of_bin=width_of_bin, loglevel=loglevel)
    reader = Reader(model=model, exp=exp, source=source, loglevel=loglevel, regrid=regrid)
    full_dataset = reader.retrieve(var=model_variable)

    test_sample = full_dataset.isel(time=slice(1, 11))
    regrid_bool = ToolsClass().check_need_for_regridding(test_sample, regrid)
    freq_bool = ToolsClass().check_need_for_time_averaging(test_sample, freq)

    first_year_in_dataset = full_dataset['time.year'][0].values
    last_year_in_dataset = full_dataset['time.year'][-1].values

    s_year = first_year_in_dataset if s_year is None else max(s_year, first_year_in_dataset)
    f_year = last_year_in_dataset if f_year is None else min(f_year, last_year_in_dataset)

    for year in range(s_year, f_year):
        data_per_year = full_dataset.sel(time=slice(str(year), str(year)))
        if data_per_year.time.size != 0:
            for x in range(1, 12):
                data = data_per_year.sel(time=slice(str(year)+'-'+str(x), str(year)+'-'+str(x+1)))
                if freq_bool:
                    data = reader.timmean(data, freq=freq)
                if regrid_bool:
                    data = reader.regrid(data)
                try:
                    diag.histogram(data, model_variable=model_variable,
                                   path_to_histogram=path_to_netcdf+"/"+regrid+'_'+freq+'/histograms/',
                                   threshold = 30, name_of_file=regrid+'_'+freq)
                except Exception as e:
                    # Handle other exceptions
                    logger.error(f"An unexpected error occurred: {e}")
                logger.debug(f"Current Status: {x}/12 months processed in year {year}.")
        else:
            logger.warning("The specified year is not present in the dataset. " +
                           "Ensure the time range in your selection accurately reflects the available " +
                           "data. Check dataset time bounds and adjust your time selection parameters accordingly.")

    logger.info("The histograms are calculated and saved in storage.")
    try:
        hist_merged = diag.merge_list_of_histograms(
            path_to_histograms=path_to_netcdf+"/"+regrid+'_'+freq+'/histograms/', all=True)

        diag.histogram_plot(hist_merged, figsize=figsize, new_unit=new_unit,
                            legend=legend, color=color, xmax=xmax, plot_title=plot_title, loc=loc,
                            path_to_pdf=path_to_pdf, pdf_format=pdf_format, name_of_file=name_of_pdf)
        logger.info("The histograms are plotted and saved in storage.")
    except FileNotFoundError as file_error:
        # Handle FileNotFoundError
        logger.error(f"FileNotFoundError occurred: {file_error}")
    except Exception as e:
        # Handle other exceptions
        logger.error(f"An unexpected error occurred: {e}")
    logger.info("Tropical Rainfall Diagnostic is terminated.")
