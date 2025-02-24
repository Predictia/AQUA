#!/usr/bin/env python3
"""
Command-line interface for Timeseries diagnostic.

This CLI allows to run the Timeseries, SeasonalCycles and GregoryPlot
diagnostics.
Details of the run are defined in a yaml configuration file for a
single or multiple experiments.
"""
import argparse
import sys

from aqua.logger import log_configure
from aqua.util import get_arg
from aqua.version import __version__ as aqua_version
from aqua.diagnostics.core import template_parser, open_cluster, close_cluster
from aqua.diagnostics.timeseries import Timeseries

def parse_arguments(args):
    """
    Parse command-line arguments for Timeseries diagnostic.
    
    Args:
        args (list): list of command-line arguments to parse.
    """
    parser = argparse.ArgumentParser(description='Timeseries CLI')
    parser = template_parser(parser)
    return parser.parse_args(args)

if __name__ == '__main__':
    args = parse_arguments(sys.args[1:])

    loglevel = get_arg(args, 'loglevel', 'WARNING')
    logger = log_configure(log_level=loglevel, log_name='Timeseries CLI')
    logger.info(f"Running Timeseries diagnostic with AQUA version {aqua_version}")

    cluster = get_arg(args, 'cluster', None)
    nworkers = get_arg(args, 'nworkers', None)

    client, cluster, private_cluster, = open_cluster(nworkers=nworkers, cluster=cluster, loglevel=loglevel)

    close_cluster(client=client, cluster=cluster, private_cluster=private_cluster, loglevel=loglevel)

    logger.info("Timeseries diagnostic completed.")