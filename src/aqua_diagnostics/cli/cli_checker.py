#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
AQUA analysis checker command line interface.
Check that the imports are correct and the requested model is available in the
Reader catalog.
'''
import sys
import argparse


def parse_arguments(args):
    """Parse command line arguments"""

    parser = argparse.ArgumentParser(description='Check setup CLI')

    parser.add_argument("--loglevel", "-l", type=str,
                        required=False, help="loglevel")
    parser.add_argument("--catalog", type=str,
                        required=False, help="catalog name")
    parser.add_argument("--model", type=str,
                        required=False, help="model name")
    parser.add_argument("--exp", type=str,
                        required=False, help="experiment name")
    parser.add_argument("--source", type=str,
                        required=False, help="source name")

    return parser.parse_args(args)


if __name__ == '__main__':

    print('Running Check setup CLI')
    args = parse_arguments(sys.argv[1:])

    try:
        from aqua.__init__ import __version__ as aqua_version
        from aqua import Reader
        from aqua.logger import log_configure
        from aqua.util import get_arg
        from aqua.exceptions import NoDataError

        loglevel = get_arg(args, 'loglevel', 'WARNING')
        logger = log_configure(log_name='Setup check', log_level=loglevel)
    except ImportError:
        raise ImportError('Failed to import aqua. Check that you have installed aqua.'
                          'If you are using a conda environment, check that you have activated it.'
                          'If you are using a container, check that you have started it.')
    except Exception as e:
        raise ImportError('Failed to import aqua: {}'.format(e))

    logger.info('Running aqua version {}'.format(aqua_version))

    catalog = get_arg(args, 'catalog', None)
    model = get_arg(args, 'model', None)
    exp = get_arg(args, 'exp', None)
    source = get_arg(args, 'source', None)

    if model is None or exp is None or source is None:
        raise ValueError('model, exp and source are required arguments')
    if catalog is None:
        logger.warning('No catalog provided, determining the catalog with the Reader')

    try:
        reader = Reader(catalog=catalog, model=model, exp=exp, source=source,
                        loglevel=loglevel, rebuild=True)
        reader.retrieve()
    except Exception as e:
        logger.error('Failed to retrieve data: {}'.format(e))
        logger.error('Check that the model is available in the Reader catalog.')
        raise NoDataError('Failed to retrieve data: {}'.format(e))

    logger.info('Check is terminated, diagnostics can run!')
