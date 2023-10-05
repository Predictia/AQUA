print("Radiation Budget Diagnostic diagnostic is started.")

# All nesessarry import for a cli diagnostic
import sys
try:
    from aqua.util import load_yaml, get_arg
    import os
    import dask
    import argparse
    sys.path.insert(0, '../')
    from functions import process_ceres_data, process_model_data, process_era5_data, process_ceres_sfc_data
    from functions import barplot_model_data, plot_bias, plot_maps, plot_mean_bias, gregory_plot, plot_model_comparison_timeseries
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

    parser = argparse.ArgumentParser(description='Tropical Rainfall CLI')
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

    print('Running tropical rainfall diagnostic...')
    args = parse_arguments(sys.argv[1:])

    file = get_arg(args, 'config', 'config/radiation_config.yml')
    print('Reading configuration yaml file..')
    config = load_yaml(file)

    model = get_arg(args, 'model', config['data']['model'])
    exp = get_arg(args, 'exp', config['data']['exp'])
    source = get_arg(args, 'source', config['data']['source'])

    model_icon = config['data']['model_icon']
    exp_icon = config['data']['exp_icon']
    source_icon = config['data']['source_icon']

    exp_ceres = config['data']['exp_ceres']
    source_ceres = config['data']['source_ceres']

    exp_era5 = config['data']['exp_era5']
    source_era5 = config['data']['source_era5']

    path_to_output = get_arg(
        args, 'outputdir', config['path']['path_to_output'])
    if path_to_output is not None:
        outputdir = os.path.join(path_to_output, 'NetCDF/')
        outputfig = os.path.join(path_to_output, 'PDF/')

    bar_plot_bool = config['diagnostic_attributes']['bar_plot']
    bias_maps_bool = config['diagnostic_attributes']['bias_maps']
    gregory_bool = config['diagnostic_attributes']['gregory']
    time_series_bool = config['diagnostic_attributes']['time_series']

    bar_plot_year = config['time_frame']['bar_plot_year']
    era5_start_date = config['time_frame']['era5_start_date']
    era5_end_date = config['time_frame']['era5_end_date']
    model_start_date = config['time_frame']['model_start_date']
    model_end_date = config['time_frame']['model_end_date']

    model_label = config['plot']['model_label']
    icon_label = config['plot']['icon_label']
    ceres_label = config['plot']['ceres_label']
    obs_label = config['plot']['obs_label']

    if bar_plot_bool:
        try:
            TOA_gm, reader, data, TOA, TOA_r360x180 = process_model_data(
                model=model, exp=exp, source=source)
            TOA_icon_gm, reader_icon, data_icon, TOA_icon, TOA_icon_r360x180 = process_model_data(
                model=model_icon, exp=exp_icon, source=source_icon)
            # Call the method to retrieve CERES data
            TOA_ceres_clim_gm, TOA_ceres_ebaf_gm, TOA_ceres_diff_samples_gm, reader_ceres_toa, TOA_ceres_clim, TOA_ceres_diff_samples = process_ceres_data(
                exp=exp_ceres, source=source_ceres, TOA_icon_gm=TOA_icon_gm)
            datasets = [TOA_ceres_clim_gm, TOA_icon_gm, TOA_ifs_4km_gm]
            model_names = [ceres_label, icon_label, model_label]

            barplot_model_data(datasets, model_names,
                               outputdir, outputfig, year=bar_plot_year)
            print("The Bar Plot with various models and CERES was created and saved. Variables ttr and tsr are plotted to show imbalances.")
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

    if bias_maps_bool:
        for var in ['ttr', 'tsr', 'tnr']:
            try:
                TOA_gm, reader, data, TOA, TOA_r360x180 = process_model_data(
                    model=model, exp=exp, source=source)
                TOA_icon_gm, reader_icon, data_icon, TOA_icon, TOA_icon_r360x180 = process_model_data(
                    model=model_icon, exp=exp_icon, source=source_icon)
                TOA_ceres_clim_gm, TOA_ceres_ebaf_gm, TOA_ceres_diff_samples_gm, reader_ceres_toa, TOA_ceres_clim, TOA_ceres_diff_samples = process_ceres_data(
                    exp=exp_ceres, source=source_ceres, TOA_icon_gm=TOA_icon_gm)

                plot_mean_bias(TOA, var, model_label, TOA_ceres_clim,
                               model_start_date, model_end_date, outputdir, outputfig)
                print(
                    f"The mean bias of the data over the specified time range is calculated, plotted, and saved for {var} variable.")
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

    if gregory_bool:
        try:
            TOA_gm, reader, data, TOA, TOA_r360x180 = process_model_data(
                model=model, exp=exp, source=source)
            data_era5, reader_era5 = process_era5_data(
                exp=exp_era5, source=source_era5)
            # Assuming you have the observational data in an xarray.Dataset object called `obs_data`
            obs_data = data_era5
            obs_reader = reader_era5
            obs_time_range = (era5_start_date, era5_end_date)
            model_label_obs = obs_label
            # Define the list of models to include
            model_list = [model_label]
            # Define the reader dictionary for each model
            reader_dict = {
                model_label: reader,
            }
            # Call the gregory_plot function

            gregory_plot(obs_data, obs_reader, obs_time_range, model_label_obs,
                         model_list, reader_dict, outputdir, outputfig)
            print(
                "Gregory Plot was created and saved with various models and an observational dataset.")
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

    if time_series_bool:
        try:
            TOA_gm, reader, data, TOA, TOA_r360x180 = process_model_data(
                model=model, exp=exp, source=source)
            TOA_icon_gm, reader_icon, data_icon, TOA_icon, TOA_icon_r360x180 = process_model_data(
                model=model_icon, exp=exp_icon, source=source_icon)
            # Call the method to retrieve CERES data
            TOA_ceres_clim_gm, TOA_ceres_ebaf_gm, TOA_ceres_diff_samples_gm, reader_ceres_toa, TOA_ceres_clim, TOA_ceres_diff_samples = process_ceres_data(
                exp=exp_ceres, source=source_ceres, TOA_icon_gm=TOA_icon_gm)
            data_era5, reader_era5 = process_era5_data(
                exp=exp_era5, source=source_era5)
            models = [TOA_icon_gm.squeeze(), TOA_gm.squeeze()]
            linelabels = [icon_label, model_label]

            plot_model_comparison_timeseries(
                models, linelabels, TOA_ceres_diff_samples_gm, TOA_ceres_clim_gm, outputdir, outputfig)
            print(
                "The time series bias plot with various models and CERES was created and saved.")
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

    print("Radiation Budget Diagnostic is terminated.")
