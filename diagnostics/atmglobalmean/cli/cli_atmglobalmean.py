# All necessary import for a cli diagnostic
import sys
import os
import argparse

from aqua.util import load_yaml, get_arg
from aqua import Reader
from aqua.logger import log_configure


def parse_arguments(args):
    """Parse command line arguments"""

    parser = argparse.ArgumentParser(description='Atmospheric global mean biases CLI')
    parser.add_argument('-c', '--config', type=str,
                        help='yaml configuration file')
    # This arguments will override the configuration file if provided
    parser.add_argument('--model', type=str, help='model name',
                        required=False)
    parser.add_argument('--exp', type=str, help='experiment name',
                        required=False)
    parser.add_argument('--source', type=str, help='source name',
                        required=False)
    parser.add_argument('--outputdir', type=str, help='output directory',
                        required=False)
    parser.add_argument('--loglevel', '-l', type=str, help='loglevel',
                        required=False)
    parser.add_argument('--start_date1', type=str, help='start date for dataset1',
                        required=False)
    parser.add_argument('--end_date1', type=str, help='end date for dataset1',
                        required=False)
    parser.add_argument('--start_date2', type=str, help='start date for dataset2',
                        required=False)
    parser.add_argument('--end_date2', type=str, help='end date for dataset2',
                        required=False)

    return parser.parse_args(args)


if __name__ == '__main__':

    print('Running atmospheric global mean biases diagnostic...')

    # change the current directory to the one of the CLI so that relative path works
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    if os.getcwd() != dname:
        os.chdir(dname)
        print(f'Moving from current directory to {dname} to run!')

    try:
        sys.path.insert(0, '../../')
        from atmglobalmean import compare_datasets_plev, seasonal_bias, plot_map_with_stats
    except ImportError as import_error:
        # Handle ImportError
        print(f"ImportError occurred: {import_error}")
        sys.exit(0)
    except Exception as custom_error:
        # Handle other custom exceptions if needed
        print(f"CustomError occurred: {custom_error}")
        sys.exit(0)

    # Aquiring arguments and configuration
    args = parse_arguments(sys.argv[1:])
    file = get_arg(args, 'config', 'config/atm_mean_bias_config.yaml')
    print('Reading configuration yaml file..')
    config = load_yaml(file)

    # Configure logging
    loglevel = get_arg(args, 'loglevel', config['loglevel'])
    logger = log_configure(log_level=loglevel, log_name='Atmglobalmean CLI')

    # Acquiring model, experiment and source
    model = get_arg(args, 'model', config['data']['model'])
    exp = get_arg(args, 'exp', config['data']['exp'])
    source = get_arg(args, 'source', config['data']['source'])

    # Acquiring start and end dates for dataset1 and dataset2
    start_date1 = get_arg(args, 'start_date1', None)
    end_date1 = get_arg(args, 'end_date1', None)
    start_date2 = get_arg(args, 'start_date2', None)
    end_date2 = get_arg(args, 'end_date2', None)

    logger.debug(f"Running for {model} {exp} {source}.")

    path_to_output = get_arg(
        args, 'outputdir', config['path']['path_to_output'])
    if path_to_output:
        outputdir = os.path.join(path_to_output, 'netcdf/')
        outputfig = os.path.join(path_to_output, 'pdf/')
    else:
        logger.error("No output directory provided.")
        logger.critical("Atmospheric global mean biases diagnostic is terminated.")
        sys.exit(0)

    logger.debug(f"outputdir: {outputdir}")
    logger.debug(f"outputfig: {outputfig}")

    # This is the model to compare with
    model_obs = config['data']['model_obs']
    exp_obs = config['data']['exp_obs']
    source_obs = config['data']['source_obs']

    logger.debug(f"Comparing with {model_obs} {exp_obs} {source_obs}.")

    variables_no_plev = config['diagnostic_attributes']['variables_no_plev']
    variables_with_plev = config['diagnostic_attributes']['variables_with_plev']
    plev = config['diagnostic_attributes']['plev']
    statistic = config['diagnostic_attributes']['statistic']
    seasonal_bias_bool = config['diagnostic_attributes']['seasonal_bias']
    compare_datasets_plev_bool = config['diagnostic_attributes']['compare_datasets_plev']
    plot_map_with_stats_bool = config['diagnostic_attributes']['plot_map_with_stats']
    start_date1 = config['diagnostic_attributes']['start_date1']
    end_date1 = config['diagnostic_attributes']['end_date1']
    start_date2 = config['diagnostic_attributes']['start_date2']
    end_date2 = config['diagnostic_attributes']['end_date2']

    model_label = model+'_'+exp
    model_label_obs = model_obs+'_'+exp_obs

    try:
        reader_obs = Reader(model=model_obs, exp=exp_obs, source=source_obs, loglevel=loglevel)
        data_obs = reader_obs.retrieve()
    except Exception as e:
        logger.error(f"No observation data found: {e}")

    try:
        reader = Reader(model=model, exp=exp, source=source, loglevel=loglevel)
        data = reader.retrieve()
    except Exception as e:
        logger.error(f"No model data found: {e}")
        logger.critical("Atmospheric global mean biases diagnostic is terminated.")
        sys.exit(0)

    if seasonal_bias_bool:
        for var_name in variables_no_plev:
            logger.info(f"Running seasonal bias diagnostic for {var_name}...")
            try:
                seasonal_bias(dataset1=data, dataset2=data_obs,
                              var_name=var_name, plev=plev, statistic=statistic,
                              model_label1=model_label, model_label2=model_label_obs,
                              start_date1=start_date1, end_date1=end_date1,
                              start_date2=start_date2, end_date2=end_date2,
                              outputdir=outputdir, outputfig=outputfig,
                              loglevel=loglevel)
            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}")

    if compare_datasets_plev_bool:
        for var_name in variables_with_plev:
            logger.info(f"Running compare datasets plev diagnostic for {var_name}...")
            try:
                compare_datasets_plev(dataset1=data, dataset2=data_obs, var_name=var_name,
                                      model_label1=model_label, model_label2=model_label_obs,
                                      start_date1=start_date1, end_date1=end_date1,
                                      start_date2=start_date2, end_date2=end_date2,
                                      outputdir=outputdir, outputfig=outputfig,
                                      loglevel=loglevel)
            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}")

    if plot_map_with_stats_bool:
        for var_name in variables_no_plev:
            logger.info(f"Running plot map with stats diagnostic for {var_name}...")
            try:
                plot_map_with_stats(dataset=data, var_name=var_name,  model_label=model_label,
                                    outputdir=outputdir, outputfig=outputfig, loglevel=loglevel)
            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}")

    logger.info("Atmospheric global mean biases diagnostic is terminated.")
