#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
AQUA main command line
'''

import os
import argparse
import shutil
import sys
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
        uninstall_parser = subparsers.add_parser("uninstall")
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

        command_map = {
            'init': self.init,
            'add': self.add,
            'remove': self.remove,
            'uninstall': self.uninstall,
        }

        command = args.command
        method = command_map.get(command, parser.print_help)
        method(args)

    def init(self, args):
        """Initialize AQUA, find the folders and the install"""
        self.logger.info('Running the AQUA init')

        # define the home folder
        if args.path is None:
            if 'HOME' in os.environ:
                path = os.path.join(os.environ['HOME'], '.aqua')
                if not os.path.exists(path):
                    os.makedirs(path, exist_ok=True)
                else:
                    self.logger.warning('AQUA already installed in %s', path)
                    check = query_yes_no(f"Do you want to overwrite AQUA installation in {path}. You will lose all catalogs installed.", "no")
                    if not check:
                        sys.exit(0)
                    else:
                        self.logger.warning('Removing the content of %s', path)
                        shutil.rmtree(path)
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
        self.install()  

    def install(self):
        """Copying the installation file"""

        print("Installing AQUA to", self.configpath)
        for file in ['config-aqua.yaml', 'aqua-grids.yaml']:
            if not os.path.exists(os.path.join(self.configpath, file)):
                self.logger.info('Copying from %s to %s', self.aquapath, self.configpath)
                shutil.copy(f'{self.aquapath}/{file}', f'{self.configpath}/{file}')
        for directory in ['fixes', 'data_models']:
            if not os.path.exists(os.path.join(self.configpath, directory)):
                self.logger.info('Copying from %s to %s', 
                                 os.path.join(self.aquapath, directory), self.configpath)
                shutil.copytree(f'{self.aquapath}/{directory}', f'{self.configpath}/{directory}')
        os.makedirs(f'{self.configpath}/catalog', exist_ok=True)

        
    def add(self, args):
        """Add a catalog"""
        self.logger.info('Adding the AQUA catalog %s', args.catalog)
        self.configpath = ConfigPath().configdir
        cdir = f'{self.configpath}/catalog/{args.catalog}'
        self.logger.info('Installing to %s', self.configpath)
        if not os.path.exists(cdir):
            shutil.copytree(f'{self.aquapath}/machines/{args.catalog}', cdir)
        else:
            self.logger.error('Catalog %s already installed in %s, please consider `aqua update`', 
                              args.catalog, cdir)
    
    def remove(self, args):
        """Remove a catalog"""
        self.logger.info('Remove the AQUA catalog %s', args.catalog)
        self.configpath = ConfigPath().configdir
        cdir = f'{self.configpath}/catalog/{args.catalog}'
        if os.path.exists(cdir):
            shutil.rmtree(cdir)
        else:
            self.logger.error('Catalog %s is not installed in %s, cannot remove it', 
                              args.catalog, cdir)

    def uninstall(self, args):
        """Remove AQUA"""
        print('Remove the AQUA installation')
        try:
            self.configpath = ConfigPath().configdir
        except FileNotFoundError:
            self.logger.error('No AQUA installation found!')
            sys.exit(1)
        check = query_yes_no(f"Do you want to uninstall AQUA from {self.configpath}", "no")
        if check:
            self.logger.info('Uninstalling AQUA from %s', self.configpath)
            shutil.rmtree(self.configpath)


def main():
    """temporary hack to be removed"""
    AquaConsole()

if __name__ == '__main__':
    AquaConsole()

def query_yes_no(question, default="yes"):
    # from stackoverflow
    """Ask a yes/no question via input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    The return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError(f"invalid default answer: {default}")

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            print("Please respond with 'yes' or 'no' (or 'y' or 'n').")
