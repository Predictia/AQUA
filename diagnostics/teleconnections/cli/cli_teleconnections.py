#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
AQUA dummy diagnositc command line interface. Reads configuration file and performs dummy 
diagnostic
'''
import sys
import argparse

from aqua.util import load_yaml, get_arg
from teleconnections.tc_class import Teleconnection

def parse_arguments(args):
    """
    Parse command line arguments
    """

    parser = argparse.ArgumentParser(description='Teleconnections diagnostic CLI')
    parser.add_argument('-c', '--config', type=str,
                        help='yaml configuration file')
    parser.add_argument('-d', '--definitive', type=bool,
                        help='if True, files are saved, default is False')
    parser.add_argument('-l', '--loglevel', type=str,
                        help='log level [default: WARNING]')

    return parser.parse_args(args)


if __name__ == '__main__':

    print('Running teleconnections diagnostic...')
    args = parse_arguments(sys.argv[1:])

    # Read configuration file
    file = get_arg(args, 'config', 'teleconnections_config.yaml')
    print('Reading configuration yaml file..')
    config = load_yaml(file)

    loglevel = get_arg(args, 'loglevel', 'WARNING')
    model = config['model']
    exp = config['exp']
    source = config['source']

    savefig = get_arg(args, 'definitive', False)
    savefile = get_arg(args, 'definitive', False)

    try:
        outputfig = config['outputfig']
    except KeyError:
        outputfig = None
    
    try:
        outputfile = config['outputfile']
    except KeyError:
        outputfile = None
    
    try:
        filename = config['filename']
    except KeyError:
        filename = None

    teleconnection = Teleconnection(model=model, exp=exp, source=source,
                                    savefig=savefig, savefile=savefile,
                                    outputfig=outputfig, outputfile=outputfile,
                                    filename=filename, loglevel=loglevel)
    
    teleconnection.retrieve()
    teleconnection.evaluate_index()
    # teleconnection.evaluate_correlation()
    # teleconnection.evaluate_regression()
    teleconnection.plot_index()

    print('Teleconnections diagnostic test run completed.')
