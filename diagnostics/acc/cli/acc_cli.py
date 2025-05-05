import os
import sys
import argparse

# Add the directory containing the diagnostic module to the Python path.
script_dir = os.path.dirname(os.path.abspath(__file__))
# Assuming the structure is diagnostics/acc/cli and diagnostics/acc/acc
diagnostic_module_path = os.path.abspath(os.path.join(script_dir, os.pardir))
# Also need to add the parent directory of 'diagnostics' to find 'aqua'
aqua_root_path = os.path.abspath(os.path.join(script_dir, os.pardir, os.pardir, os.pardir))
sys.path.insert(0, diagnostic_module_path)
sys.path.insert(0, aqua_root_path) # Ensure aqua is found

def parse_arguments(args):
    """Parse command line arguments"""

    parser = argparse.ArgumentParser(description='ACC Diagnostic CLI') # Updated description

    # Require configuration file
    parser.add_argument('-c', '--config', type=str,
                        help='YAML configuration file for the ACC diagnostic', # Updated help
                        required=True)

    # Keep loglevel argument
    parser.add_argument('-l', '--loglevel', type=str, default='WARNING',
                        help='Log level [default: WARNING]')

    # Add flags for saving outputs
    parser.add_argument('--save-fig', action='store_true',
                        help='Save output figures')
    parser.add_argument('--save-netcdf', action='store_true',
                        help='Save output NetCDF data')

    return parser.parse_args(args)

if __name__ == '__main__':

    print('Running ACC Diagnostic CLI') # Updated print message
    args = parse_arguments(sys.argv[1:])

    try:
        from acc import ACC
        from aqua.logger import log_configure
        from aqua.util import load_yaml
        from aqua import __version__ as aqua_version

        loglevel = args.loglevel
        logger = log_configure(log_name='ACC CLI', log_level=loglevel) # Updated logger name
    except ImportError as e:
        print(f'Failed to import aqua or ACC diagnostic: {e}') # Updated message
        print("Ensure the AQUA package and the ACC diagnostic are correctly installed/discoverable.") # Updated message
        print(f"Diagnostic module path: {diagnostic_module_path}")
        print(f"Aqua root path: {aqua_root_path}")
        print(f"Sys path: {sys.path}")
        sys.exit(1)
    except Exception as e:
        print('Failed during initial setup: {}'.format(e))
        sys.exit(1)

    logger.info('Running aqua version {}'.format(aqua_version))

    # change the current directory to the one of the CLI so that relative path works
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    if os.getcwd() != dname:
        logger.info(f'Changing current directory to {dname} to run!')
        os.chdir(dname)

    config_file = args.config
    logger.info('Reading configuration from {}'.format(config_file))

    # Check if the config file exists relative to the current directory (which we just changed to)
    if not os.path.isabs(config_file):
        config_file_abs = os.path.join(dname, config_file)
    else:
        config_file_abs = config_file

    if not os.path.exists(config_file_abs):
        logger.error(f"Configuration file not found: {config_file_abs} (Original path: {config_file})")
        sys.exit(1)

    try:
        # Use the absolute path to load YAML
        config = load_yaml(config_file_abs)
    except Exception as e:
        logger.error(f"Failed to load or parse configuration file {config_file_abs}: {e}")
        sys.exit(1)

    # ACC Diagnostic Execution
    try:
        logger.info("Initializing ACC diagnostic...") # Updated message
        acc_diagnostic = ACC(config=config, loglevel=loglevel) # Instantiate ACC

        logger.info("Retrieving data...")
        acc_diagnostic.retrieve()

        logger.info("Calculating spatial ACC...") # Updated message
        acc_diagnostic.spatial_acc(save_fig=args.save_fig, save_netcdf=args.save_netcdf) # Call spatial_acc

        logger.info("Calculating temporal ACC...") # Updated message
        acc_diagnostic.temporal_acc(save_fig=args.save_fig, save_netcdf=args.save_netcdf) # Call temporal_acc

        logger.info('ACC diagnostic finished successfully!') # Updated message

    except ValueError as ve:
         logger.error(f"Configuration error in {config_file_abs}: {ve}")
         sys.exit(1)
    except FileNotFoundError as fnf_err:
        logger.error(f"Data file not found during retrieval: {fnf_err}")
        logger.critical("Check paths and availability in the data catalog specified in the config.")
        sys.exit(1)
    except Exception as e:
        logger.error('An error occurred during ACC diagnostic execution: {}'.format(e), exc_info=True) # Updated message
        logger.critical('ACC diagnostic failed.') # Updated message
        sys.exit(1)
