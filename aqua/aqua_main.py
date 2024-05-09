#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
AQUA main command line
'''

import os
import argparse

def init(args):
    """Install AQUA"""
    print('Running the AQUA init')

    # define the home folder
    if args.path is None:
        if 'HOME' in os.environ:
            path = os.path.join(os.environ['HOME'], '.aqua')
        else:
            raise ValueError('$HOME not found. Please specify a path where to install AQUA')
    else:
        path = args.path
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        else:
            if not os.path.isdir(path):
                raise ValueError("Path chosen is not a directory")
    
    print("Installing AQUA to", path)

def catalogadd(args):
    """Add a catalog"""
    print('Adding the AQUA catalog', args.catalog)


def main():
    """The main AQUA command line interface"""
    parser = argparse.ArgumentParser(description='AQUA command line tool')
    subparsers = parser.add_subparsers(dest='command', help='Available AQUA commands')

    parser.add_argument('-l', '--loglevel', type=str,
                        help='log level [default: WARNING]')
    
    init_parser = subparsers.add_parser("init")
    catalog_add_parser = subparsers.add_parser("catalog-add")

    init_parser.add_argument('-p', '--path', type=str,
                help='Path where to install AQUA')
    init_parser.add_argument('-g', '--grids', type=str,
                help='Path where to install AQUA')
    
    catalog_add_parser.add_argument("catalog", metavar="CATALOG",
                                    help="Catalog to be installed")

    args = parser.parse_args()

    if args.command == 'init':
        init(args)
    elif args.command == 'catalog-add':
        catalogadd(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
