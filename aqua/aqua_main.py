#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
AQUA main command line
'''

import os
import argparse
import shutil
from aqua.logger import log_configure
from aqua.util import ConfigPath
from aqua import __path__ as pypath


class AquaConsole():
    """Class for AquaConsole"""

    def __init__(self):
        """The main AQUA command line interface"""
        parser = argparse.ArgumentParser(description='AQUA command line tool')
        subparsers = parser.add_subparsers(dest='command', help='Available AQUA commands')

        parser.add_argument('-l', '--loglevel', type=str,
                            help='log level [default: WARNING]')
        
        init_parser = subparsers.add_parser("init")
        catalog_add_parser = subparsers.add_parser("add")
        catalog_remove_parser = subparsers.add_parser("remove")

        init_parser.add_argument('-p', '--path', type=str,
                    help='Path where to install AQUA')
        init_parser.add_argument('-g', '--grids', type=str,
                    help='Path where to install AQUA')
        
        catalog_add_parser.add_argument("catalog", metavar="CATALOG",
                                        help="Catalog to be installed")
        
        catalog_remove_parser.add_argument("catalog", metavar="CATALOG",
                                        help="Catalog to be removed")
        
        args = parser.parse_args()

        self.logger = log_configure(args.loglevel, 'AQUA')
        self.pypath = pypath[0]
        self.aquapath = os.path.join(os.path.dirname(self.pypath), 'config')
        self.configpath = None

        if args.command == 'init':
            self.init(args)
        elif args.command == 'add':
            self.add(args)
        elif args.command == 'remove':
            self.remove(args)
        elif args.command == 'uninstall':
            self.uninstall(args)
        else:
            parser.print_help()

    def init(self, args):
        """Install AQUA"""
        self.logger.info('Running the AQUA init')

        # define the home folder
        if args.path is None:
            if 'HOME' in os.environ:
                path = os.path.join(os.environ['HOME'], '.aqua')
                if not os.path.exists(path):
                    os.makedirs(path, exist_ok=True)
            else:
                raise ValueError('$HOME not found. Please specify a path where to install AQUA')
        else:
            path = args.path
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
            else:
                if not os.path.isdir(path):
                    raise ValueError("Path chosen is not a directory")
        
        self.configpath = path
        print("Installing AQUA to", path)
        for file in ['config-aqua.yaml', 'aqua-grids.yaml']:
            if not os.path.exists(os.path.join(self.configpath, file)):
                self.logger.info('Copying from %s to %s', self.aquapath, self.configpath)
                shutil.copy(f'{self.aquapath}/{file}', f'{self.configpath}/{file}')
        for directory in ['fixes', 'data_models']:
            if not os.path.exists(os.path.join(self.configpath, directory)):
                self.logger.info('Copying from %s to %s', os.path.join(self.aquapath, directory), self.configpath)
                shutil.copytree(f'{self.aquapath}/{directory}', f'{self.configpath}/{directory}')
        os.makedirs(f'{self.configpath}/catalog', exist_ok=True)
        

    def add(self, args):
        """Add a catalog"""
        self.logger.info('Adding the AQUA catalog %s', args.catalog)
        self.configpath = ConfigPath().configdir
        cdir = f'{self.configpath}/catalog/{args.catalog}'
        self.logger.info('Installing to %s', self.configpath)
        shutil.copytree(f'{self.aquapath}/machines/{args.catalog}', cdir)
    
    def remove(self, args):
        """Remove a catalog"""
        self.logger.info('Remove the AQUA catalog %s', args.catalog)
        self.configpath = ConfigPath().configdir
        cdir = f'{self.configpath}/catalog/{args.catalog}'
        shutil.rmtree(cdir)

    def uninstall(self, args):
        """Remove AQUA"""
        self.logger.info('Remove the AQUA installation')
        self.configpath = ConfigPath().configdir
        shutil.rmtree(self.configpath) 


def main():
    """temporary hack"""
    AquaConsole()

if __name__ == '__main__':
    AquaConsole()
