#!/usr/bin/env python3

"""
SSH Variability Diagnostic CLI.

This script allows users to execute SSH variability diagnostics using command-line arguments.
By default, it will read configurations from 'config.yml' unless specified by the user.
"""

import argparse
import os
import sys

# Add the directory containing the `ssh` module to the Python path.
# Since the module is in the parent directory of this script, we calculate the script's directory
# and then move one level up.
script_dir = os.path.dirname(os.path.abspath(__file__))
ssh_module_path = os.path.join(script_dir, "../../")
sys.path.insert(0, ssh_module_path)

# Local module imports.
from ssh import sshVariability

# Imports related to the aqua package, which is installed and available globally.
from aqua import Reader
from aqua.util import get_arg

def parse_arguments(args):
    """
    Parse command line arguments.

    :param args: List of command line arguments.
    :return: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description='SSH variability CLI')
    
    # Define the default path for the configuration file.
    default_config_path = os.path.join(script_dir, 'config.yml')
    
    # Arguments for the CLI.
    parser.add_argument('--config', type=str, default=default_config_path,
                        help=f'yaml configuration file (default: {default_config_path})')
    parser.add_argument('--model', type=str, help='Model name')
    parser.add_argument('--exp', type=str, help='Experiment name')
    parser.add_argument('--source', type=str, help='Source name')
    parser.add_argument('--outputdir', type=str, help='Output directory')
    
    return parser.parse_args(args)

if __name__ == '__main__':
    print("Running SSH variability diagnostic...")

    # Parse the provided command line arguments.
    args = parse_arguments(sys.argv[1:])
    
    # Read configuration file.
    print('Reading configuration yaml file...')
    analyzer = sshVariability(args.config)
    
    # Override configurations with CLI arguments if provided.
    analyzer.config['models'][0]['name'] = get_arg(args, 'model', analyzer.config['models'][0]['name'])
    analyzer.config['models'][0]['experiment'] = get_arg(args, 'exp', analyzer.config['models'][0]['experiment'])
    analyzer.config['models'][0]['source'] = get_arg(args, 'source', analyzer.config['models'][0]['source'])
    analyzer.config['output_directory'] = get_arg(args, 'outputdir', analyzer.config['output_directory'])
    
    # Execute the analyzer.
    analyzer.run()
    print("SSH variability diagnostic completed!")
