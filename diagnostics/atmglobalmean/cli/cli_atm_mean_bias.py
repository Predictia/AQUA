# All nesessarry import for a cli diagnostic 
from aqua.util import load_yaml, get_arg
import sys
import os
import yaml
import argparse
from aqua import Reader
sys.path.insert(0, '../../')

from atmglobalmean import compare_datasets_plev, seasonal_bias, plot_map_with_stats

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

    file = get_arg(args, 'config', 'config/atm_mean_bias_config.yml')
    print('Reading configuration yaml file..')
    config = load_yaml(file)

    model = get_arg(args, 'model', config['data']['model'])
    exp = get_arg(args, 'exp', config['data']['exp'])
    source = get_arg(args, 'source', config['data']['source'])

    path_to_output = get_arg(args, 'outputdir', config['path']['path_to_output'])
    if path_to_output is not None: 
        outputdir = os.path.join(path_to_output , 'NetCDF')
        outputfig = os.path.join(path_to_output, 'PDF')
    outputdir  = config['path']['outputdir']
    outputfig  = config['path']['outputfig']

    line1 = 'outputfig: "'+str(outputfig)+'"\n'
    line2 = 'outputdir: "'+str(outputdir)+'"\n'

    # Define the filename
    filename = '../config.yaml'

    # Open the file in write mode and write the lines
    with open(filename, 'w') as configfile:
        configfile.write(line1)
        configfile.write(line2)

    model2 = config['data']['model2']
    exp2 = config['data']['exp2']
    source2 = config['data']['source2']

    start_date1 = config['time_frame']['start_date1']
    end_date1   = config['time_frame']['end_date1']
    start_date2 = config['time_frame']['start_date2']
    end_date2   = config['time_frame']['end_date2']

    var_name  = config['diagnostic_attributes']['var_name'] 
    plev        = config['diagnostic_attributes']['plev']
    statistic = config['diagnostic_attributes']['statistic']

    model_label1 = config['plot']['model_label1']
    model_label2 = config['plot']['model_label2']

    reader_obs = Reader(model=model2, exp=exp2, source=source2)
    data_obs = reader_obs.retrieve()

    reader = Reader(model=model, exp=exp, source=source)
    data = reader.retrieve()


    dataset1 = data
    dataset2 = data_obs
    print('Done')
    seasonal_bias(dataset1, dataset2, var_name, plev, statistic, model_label1, model_label2, start_date1, end_date1, start_date2, end_date2, outputdir, outputfig)

    print('Done')
    var_name = '2t'
    compare_datasets_plev(dataset1, dataset2, var_name, start_date1, end_date1, start_date2, end_date2, model_label1, model_label2)