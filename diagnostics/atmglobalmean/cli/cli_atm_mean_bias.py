print("Atmospheric global mean biases diagnostic is started.")

# All necessary import for a cli diagnostic
import sys
try:
    from aqua.util import load_yaml, get_arg
    import os
    import yaml
    import argparse
    from aqua import Reader
    sys.path.insert(0, '../../')
    from atmglobalmean import compare_datasets_plev, seasonal_bias, plot_map_with_stats
except ImportError as import_error:
    # Handle ImportError
    print(f"ImportError occurred: {import_error}")
    sys.exit(0)
except OtherCustomError as custom_error:
    # Handle other custom exceptions if needed
    print(f"CustomError occurred: {custom_error}")
    sys.exit(0)
else:
    # Code to run if the import was successful (optional)
    print("Modules imported successfully.")


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

    return parser.parse_args(args)


if __name__ == '__main__':

    print('Running atmospheric global mean biases diagnostic...')
    args = parse_arguments(sys.argv[1:])

    file = get_arg(args, 'config', 'config/atm_mean_bias_config.yml')
    print('Reading configuration yaml file..')
    config = load_yaml(file)

    model = get_arg(args, 'model', config['data']['model'])
    exp = get_arg(args, 'exp', config['data']['exp'])
    source = get_arg(args, 'source', config['data']['source'])

    path_to_output = get_arg(
        args, 'outputdir', config['path']['path_to_output'])
    if path_to_output is not None:
        outputdir = os.path.join(path_to_output, 'NetCDF/')
        outputfig = os.path.join(path_to_output, 'PDF/')

    model2 = config['data']['model2']
    exp2 = config['data']['exp2']
    source2 = config['data']['source2']

    start_date1 = config['time_frame']['start_date1']
    end_date1 = config['time_frame']['end_date1']
    start_date2 = config['time_frame']['start_date2']
    end_date2 = config['time_frame']['end_date2']

    var_name = config['diagnostic_attributes']['var_name']
    variables = config['diagnostic_attributes']['variables']
    plev = config['diagnostic_attributes']['plev']
    statistic = config['diagnostic_attributes']['statistic']
    seasonal_bias_bool = config['diagnostic_attributes']['seasonal_bias']
    compare_datasets_plev_bool = config['diagnostic_attributes']['compare_datasets_plev']
    plot_map_with_stats_bool = config['diagnostic_attributes']['plot_map_with_stats']

    model_label1 = config['plot']['model_label1']
    model_label2 = config['plot']['model_label2']

    reader_obs = Reader(model=model2, exp=exp2, source=source2)
    data_obs = reader_obs.retrieve()

    reader = Reader(model=model, exp=exp, source=source)
    data = reader.retrieve()

    dataset1 = data
    dataset2 = data_obs

    if seasonal_bias_bool:
        for var_name in variables:
            try:
                seasonal_bias(dataset1, dataset2, var_name, plev, statistic, model_label1,
                              model_label2, start_date1, end_date1, start_date2, end_date2, outputdir, outputfig)
                print(
                    f"The seasonal bias maps were calculated and plotted for {var_name} variable.")
            except ZeroDivisionError as zd_error:
                # Handle ZeroDivisionError
                print(f"ZeroDivisionError occurred: {zd_error}")
            except ValueError as value_error:
                # Handle ValueError
                print(f"ValueError occurred: {value_error}")
            except KeyError as key_error:
                # Handle KeyError
                print(f"KeyError occurred: {key_error}")
            except FileNotFoundError as file_error:
                # Handle FileNotFoundError
                print(f"FileNotFoundError occurred: {file_error}")
            except Exception as e:
                # Handle other exceptions
                print(f"An unexpected error occurred: {e}")

    if compare_datasets_plev_bool:
        for var_name in variables:
            try:
                compare_datasets_plev(dataset1, dataset2, var_name, start_date1, end_date1,
                                      start_date2, end_date2, model_label1, model_label2, outputdir, outputfig)
                print(
                    f"The comparison of the two datasets is calculated and plotted for {var_name} variable.")
            except ZeroDivisionError as zd_error:
                # Handle ZeroDivisionError
                print(f"ZeroDivisionError occurred: {zd_error}")
            except ValueError as value_error:
                # Handle ValueError
                print(f"ValueError occurred: {value_error}")
            except KeyError as key_error:
                # Handle KeyError
                print(f"KeyError occurred: {key_error}")
            except FileNotFoundError as file_error:
                # Handle FileNotFoundError
                print(f"FileNotFoundError occurred: {file_error}")
            except Exception as e:
                # Handle other exceptions
                print(f"An unexpected error occurred: {e}")

    if plot_map_with_stats_bool:
        for var_name in variables:
            try:
                plot_map_with_stats(dataset1, var_name, start_date1,
                                    end_date1, model_label1, outputdir, outputfig)
                print(
                    f"The map of a chosen variable from a dataset is calculated and plotted for {var_name} variable.")
            except ZeroDivisionError as zd_error:
                # Handle ZeroDivisionError
                print(f"ZeroDivisionError occurred: {zd_error}")
            except ValueError as value_error:
                # Handle ValueError
                print(f"ValueError occurred: {value_error}")
            except KeyError as key_error:
                # Handle KeyError
                print(f"KeyError occurred: {key_error}")
            except FileNotFoundError as file_error:
                # Handle FileNotFoundError
                print(f"FileNotFoundError occurred: {file_error}")
            except Exception as e:
                # Handle other exceptions
                print(f"An unexpected error occurred: {e}")

    print("Atmospheric global mean biases diagnostic is terminated.")
