#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
AQUA analysis checker command line interface.
Check that the imports are correct and the requested model is available in the
Reader catalog.
'''
import sys
import os
import argparse
import yaml

from aqua.diagnostics.core import template_parse_arguments


def parse_arguments(args):
    """Parse command line arguments

    Arguments:
        args {list} -- list of arguments

    Returns:
        argparse.Namespace -- parsed arguments
    """

    parser = argparse.ArgumentParser(description='Check setup CLI')
    parser = template_parse_arguments(parser)

    parser.add_argument("--yaml", type=str,
                        required=False, help="write an experiment.yaml file to a given directory")
    parser.add_argument("--no-read", action="store_false",
                        required=False, help="do not attempt to read data (used with --yaml to speed up when creating only yaml)") # noqa
    parser.add_argument("--no-rebuild", action="store_false",
                        required=False, help="by default rebuild of areas is forced, this prevents it")

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
    # For some diagnostics the regrid is required, so we set a default
    # which is 1 degree for the regrid. The user can override it
    # with the --regrid argument.
    regrid = get_arg(args, 'regrid', 'r100')
    yamldir = get_arg(args, 'yaml', None)
    fread = args.no_read
    frebuild = args.no_rebuild

    if model is None or exp is None or source is None:
        raise ValueError('model, exp and source are required arguments')
    if catalog is None:
        logger.warning('No catalog provided, determining the catalog with the Reader')

    try:
        reader = Reader(catalog=catalog, model=model, exp=exp, source=source,
                        loglevel=loglevel, rebuild=frebuild, regrid=regrid)

        # extract metadata from catalog
        if yamldir:
            logger.info('Creating experiment.yaml')
            metadata = reader.expcat.metadata
            metadata.pop("catalog_dir", None)
            metadata['description'] = reader.expcat.description
            metadata['catalog'] = catalog
            metadata['model'] = model
            metadata['experiment'] = exp
            yaml_path = os.path.join(yamldir, "experiment.yaml")
            with open(yaml_path, "w") as file:
                yaml.dump(metadata, file, default_flow_style=False)

        if not fread:
            reader.retrieve(sample=True)

    except Exception as e:
        logger.error('Failed to retrieve data: {}'.format(e))
        logger.error('Check that the model is available in the Reader catalog.')
        raise NoDataError('Failed to retrieve data: {}'.format(e))

    logger.info('Check is terminated, diagnostics can run!')
