# All necessary import for a cli diagnostic
import sys
import os
import argparse
from dask.distributed import Client, LocalCluster

from aqua.util import load_yaml, get_arg, OutputSaver, create_folder
from aqua import Reader
from aqua.exceptions import NotEnoughDataError, NoDataError, NoObservationError
from aqua.logger import log_configure
from aqua.diagnostics import GlobalBiases

def parse_arguments(args):
    """Parse command line arguments"""

    parser = argparse.ArgumentParser(description='Global biases CLI')
    parser.add_argument('-c', '--config', type=str,
                        help='yaml configuration file')
    parser.add_argument('-n', '--nworkers', type=int,
                        help='number of dask distributed workers')
    parser.add_argument("--loglevel", "-l", type=str,
                        required=False, help="loglevel")                  

    # This arguments will override the configuration file if provided
    parser.add_argument("--catalog", type=str,
                        required=False, help="catalog name")
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

    loglevel = get_arg(args, "loglevel", "WARNING")
    logger = log_configure(loglevel, 'CLI Global Biases')
    logger.info("Running Global Biases diagnostic")

    # Moving to the current directory so that relative paths work
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    if os.getcwd() != dname:
        os.chdir(dname)
        logger.info(f"Changing directory to {dname}")

    # Dask distributed cluster
    nworkers = get_arg(args, 'nworkers', None)
    if nworkers:
        cluster = LocalCluster(n_workers=nworkers, threads_per_worker=1)
        client = Client(cluster)
        logger.info(f"Running with {nworkers} dask distributed workers.")

    # Aquiring the configuration
    file = get_arg(args, "config", "global_bias_config.yaml")
    logger.info(f"Reading configuration file {file}")
    config = load_yaml(file)

    # Acquiring model, experiment and source
    catalog_data = get_arg(args, 'catalog', config['data']['catalog'])
    model_data = get_arg(args, 'model', config['data']['model'])
    exp_data = get_arg(args, 'exp', config['data']['exp'])
    source_data = get_arg(args, 'source', config['data']['source'])
    startdate_data = config['diagnostic_attributes'].get('startdate_data', None) 
    enddate_data = config['diagnostic_attributes'].get('enddate_data', None)

    # Acquiring model, experiment and source for reference data
    catalog_obs = config['obs']['catalog']
    model_obs = config['obs']['model']
    exp_obs = config['obs']['exp']
    source_obs = config['obs']['source']
    startdate_obs = config['diagnostic_attributes'].get('startdate_obs', None) 
    enddate_obs = config['diagnostic_attributes'].get('enddate_obs', None)

    #creating output directory
    outputdir = get_arg(args, "outputdir", config["outputdir"])
    out_pdf = os.path.join(outputdir, 'pdf')
    out_netcdf = os.path.join(outputdir, 'netcdf')
    create_folder(out_pdf, loglevel )
    create_folder(out_netcdf, loglevel)

    variables = config['diagnostic_attributes'].get('variables', [])
    plev = config['diagnostic_attributes'].get('plev', None)
    logger.info(f"plev: {plev}")
    seasons_bool = config['diagnostic_attributes'].get('seasons', False)
    seasons_stat = config['diagnostic_attributes'].get('seasons_stat', 'mean')
    vertical = config['diagnostic_attributes'].get('vertical', False)

    names = OutputSaver(diagnostic='global_biases', model=model_data, exp=exp_data, loglevel=loglevel)

    try:
        reader = Reader(catalog = catalog_data, model=model_data, exp=exp_data, source=source_data, startdate=startdate_data, enddate=enddate_data)
        data = reader.retrieve()
    except Exception as e:
        logger.error(f"No model data found: {e}")
        logger.critical("Global mean biases diagnostic is terminated.")
        sys.exit(0)

    try:
        reader_obs = Reader(catalog = catalog_obs, model=model_obs, exp=exp_obs, source=source_obs, startdate=startdate_obs, enddate=enddate_obs, loglevel=loglevel)
        data_obs = reader_obs.retrieve()
    except Exception as e:
        logger.error(f"No observation data found: {e}")

    startdate_data = startdate_data or data.time[0].values
    enddate_data = enddate_data or data.time[-1].values
    startdate_obs = startdate_obs or data_obs.time[0].values
    enddate_obs = enddate_obs or data_obs.time[-1].values

    # Loop on varibables
    for var_name in variables:
        logger.info(f"Running Global Biases diagnostic for {var_name}...")
        var_attributes = config["biases_plot_params"]['bias_maps'].get(var_name, {})
        vmin = var_attributes.get('vmin', None)
        vmax = var_attributes.get('vmax', None)
        logger.debug(f"var: {var_name}, vmin: {vmin}, vmax: {vmax}")

        try:
            global_biases = GlobalBiases(data=data, data_ref=data_obs, var_name=var_name, plev=plev, loglevel=loglevel,
                                        model= model_data, exp=exp_data, startdate_data=startdate_data, enddate_data=enddate_data,
                                        model_obs=model_obs, startdate_obs=startdate_obs, enddate_obs=enddate_obs)                               
            # Total bias
            result = global_biases.plot_bias(vmin=vmin, vmax=vmax)
            
            if result is not None:
                fig, ax = result 
                names.generate_name(diagnostic_product='total_bias_map', var=var_name)
                names.save_pdf(fig, path=out_pdf, var=var_name)
                
            else:
                logger.warning(f"No total bias plot generated for {var_name}. Skipping save.")

            # Seasonal bias
            result = global_biases.plot_seasonal_bias(vmin=vmin, vmax=vmax)
            if result is not None:
                fig, ax = result 
                names.generate_name(diagnostic_product='seasonal_bias_map', var=var_name)
                names.save_pdf(fig, path=out_pdf, var=var_name)
            else:
                logger.warning(f"No seasonal bias plot generated for {var_name}. Skipping save.") 

            # Vertical bias
            if vertical and 'plev' in data[var_name].dims:
                var_attributes_vert = config["biases_plot_params"]['vertical_plev'].get(var_name, {})
                vmin = var_attributes_vert.get('vmin', None)
                vmax = var_attributes_vert.get('vmax', None)
                logger.debug(f"var: {var_name}, vmin: {vmin}, vmax: {vmax}")

                result = global_biases.plot_vertical_bias(var_name=var_name, vmin=vmin, vmax=vmax)
                if result is not None:
                    fig, ax = result  # Only unpack if result is not None
                    names.generate_name(diagnostic_product='vertical_bias', var=var_name)
                    names.save_pdf(fig, path=out_pdf, var=var_name)
                else:
                    logger.warning(f"No vertical bias plot generated for {var_name}. Skipping save.")

        except Exception as e:
            logger.error(f"An unexpected error occurred while processing {var_name}: {e}")

    logger.info("Global Biases diagnostic is terminated.")

