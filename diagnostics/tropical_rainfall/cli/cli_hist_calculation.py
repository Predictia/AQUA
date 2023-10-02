# Importing the aqua.slurm module and slurm supporting functions nedeed for your script
from aqua.slurm import slurm 
from config.slurm_supporting_func import get_job_status, waiting_for_slurm_response

from aqua.util import load_yaml, get_arg
# All nesessarry import for a cli diagnostic 
####################################################################
import sys
import os
import yaml
import argparse
from aqua import Reader
sys.path.insert(0, '../../')
from tropical_rainfall import Tropical_Rainfall
####################################################################


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

    print('Running tropical rainfall diagnostic...')
    args = parse_arguments(sys.argv[1:])

    file = get_arg(args, 'config', 'config/trop_rainfall_config.yml')
    print('Reading configuration yaml file..')
    config = load_yaml(file)

    loglevel = get_arg(args, 'loglevel', config['loglevel'])

    model = get_arg(args, 'model', config['data']['model'])
    exp = get_arg(args, 'exp', config['data']['exp'])
    source = get_arg(args, 'source', config['data']['source'])

    path_to_output = get_arg(args, 'outputdir', config['path']['path_to_output'])
    if path_to_output is not None: 
        path_to_netcdf = os.path.join(path_to_output , 'NetCDF')
        path_to_pdf = os.path.join(path_to_output, 'PDF')
    name_of_netcdf  = config['path']['name_of_netcdf']
    name_of_pdf  = config['path']['name_of_pdf']

    trop_lat        = config['class_attributes']['trop_lat']
    num_of_bins     = config['class_attributes']['num_of_bins']
    first_edge      = config['class_attributes']['first_edge']
    width_of_bin    = config['class_attributes']['width_of_bin']

    model_variable  = config['model_variable'] 
    new_unit        = config['new_unit']


    color = config['plot']['color']
    figsize = config['plot']['figsize']
    legend = config['plot']['legend']
    xmax = config['plot']['xmax']
    plot_title = config['plot']['plot_title']
    loc = config['plot']['loc']
    pdf_format = config['plot']['pdf_format']

    reader          = Reader(model = model, exp = exp, source = source)
    data            = reader.retrieve(var=model_variable)

    print(data.tprate.units)
    diag            = Tropical_Rainfall(trop_lat = trop_lat,       num_of_bins = num_of_bins, 
                                        first_edge = first_edge,   width_of_bin = width_of_bin, loglevel=loglevel)
    
    
    hist = diag.histogram(data, model_variable=model_variable,  new_unit=new_unit,  path_to_histogram = path_to_netcdf+'/histograms/', name_of_file=name_of_netcdf)

    diag.histogram_plot(hist, figsize=figsize, new_unit=new_unit,
                legend=legend, color=color, xmax=xmax, plot_title=plot_title, loc=loc,
                path_to_pdf=path_to_pdf, pdf_format=pdf_format, name_of_file=name_of_pdf)



