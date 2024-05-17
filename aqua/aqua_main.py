#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
AQUA main command line
'''

import os
import argparse
import shutil
import sys
from aqua.util import load_yaml, dump_yaml
from aqua.logger import log_configure
from aqua.util import ConfigPath
from aqua import __path__ as pypath
from aqua import __version__ as version

class AquaConsole():
    """Class for AquaConsole"""

    def __init__(self):
        """The main AQUA command line interface"""
        parser = argparse.ArgumentParser(description='AQUA command line tool')
        subparsers = parser.add_subparsers(dest='command', help='Available AQUA commands')

        # Parser for the aqua main command
        # NOTE: the loglevel is not used in the main command, but it is passed to the subparsers
        #       unless the subparser has its own loglevel argument, that will override the main one
        #       This is done to allow both "aqua -l INFO init" and "aqua init -l INFO" syntaxes
        parser.add_argument('-l', '--loglevel', type=str,
                            help='log level [default: WARNING]')
        parser.add_argument('-v', '--version', action='version',
                    version=f'%(prog)s {version}', help="show AQUA version number and exit.")
  
        # List of the subparsers, corresponding to the different aqua commands available (see command map)
        init_parser = subparsers.add_parser("init")
        uninstall_parser = subparsers.add_parser("uninstall")
        list_parser = subparsers.add_parser("list")
        fixes_add_parser = subparsers.add_parser("fixes-add")
        grids_add_parser = subparsers.add_parser("grids-add")
        catalog_add_parser = subparsers.add_parser("add")
        catalog_remove_parser = subparsers.add_parser("remove")

        init_parser.add_argument('-p', '--path', type=str,
                    help='Path where to install AQUA')
        init_parser.add_argument('-g', '--grids', type=str,
                    help='Path where to install AQUA')
        init_parser.add_argument('-e', '--editable', type=str,
                    help='Install AQUA in editable mode from the original source')
        init_parser.add_argument('-l', '--loglevel', type=str,
                    help='log level [default: WARNING]')
        
        uninstall_parser.add_argument('-l', '--loglevel', type=str,
                    help='log level [default: WARNING]')
        
        list_parser.add_argument('-l', '--loglevel', type=str,
                    help='log level [default: WARNING]')

        catalog_add_parser.add_argument("catalog", metavar="CATALOG",
                    help="Catalog to be installed")
        catalog_add_parser.add_argument('-e', '--editable', type=str,
                    help='Install a catalog in editable mode from the original source: provide the Path')
        catalog_add_parser.add_argument('-l', '--loglevel', type=str,
                    help='log level [default: WARNING]')
        
        fixes_add_parser.add_argument("fixfile", metavar="fixfile",
                                        help="Fix file to be added")
        fixes_add_parser.add_argument("-e", "--editable", type=str,
                                        help="Add a fixes file in editable mode from the original source: provide the Path")
        fixes_add_parser.add_argument("-l", "--loglevel", type=str,
                                        help="log level [default: WARNING]")

        grids_add_parser.add_argument("gridfile", metavar="gridfile",
                                        help="Fix file to be added")
        grids_add_parser.add_argument("-e", "--editable", type=str,
                                        help="Add a grids file in editable mode from the original source: provide the Path")
        grids_add_parser.add_argument("-l", "--loglevel", type=str,
                                        help="log level [default: WARNING]")
        
        catalog_remove_parser.add_argument("catalog", metavar="CATALOG",
                                        help="Catalog to be removed")
        catalog_remove_parser.add_argument("-l", "--loglevel", type=str,
                                        help="log level [default: WARNING]")
        
        args = parser.parse_args()

        # Set the log level giving priority to the subparser
        if args.command and getattr(args, 'loglevel', None):
            loglevel = args.loglevel
        else:
            loglevel = 'WARNING'

        self.logger = log_configure(loglevel, 'AQUA')
        self.pypath = pypath[0]
        self.aquapath = os.path.join(os.path.dirname(self.pypath), 'config')
        self.configpath = None
        self.configfile = 'config-aqua.yaml'
        self.grids = None

        command_map = {
            'init': self.init,
            'add': self.add,
            'fixes-add': self.fixes_add,
            'grids-add': self.grids_add,
            'remove': self.remove,
            'uninstall': self.uninstall,
            'list': self.list
        }

        command = args.command
        method = command_map.get(command, parser.print_help)
        if command not in command_map:
            parser.print_help()
        else: # The command is in the command_map
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
                    check = query_yes_no(f"Do you want to overwrite AQUA installation in {path}. "
                                         "You will lose all catalogs installed.", "no")
                    if not check:
                        sys.exit(0)
                    else:
                        self.logger.warning('Removing the content of %s', path)
                        shutil.rmtree(path)
                        os.makedirs(path, exist_ok=True)
            else:
                raise ValueError('$HOME not found.'
                                 'Please specify a path where to install AQUA and define AQUA_CONFIG as environment variable')
        else:
            path = args.path
            self.logger.warning('AQUA will be installed in %s, but please remember to define AQUA_CONFIG environment variable', path)
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
            else:
                if not os.path.isdir(path):
                    raise ValueError("Path chosen is not a directory")

        self.configpath = path
        self.grids = args.grids
        self._install()

        if self.grids is None:
            self.logger.warning('Grids directory undefined')
        else:
            self._grids_define()

    def _grids_define(self):
        """add the grid definition into the aqua-config.yaml"""

        config_file = os.path.join(self.configpath, 'config-aqua.yaml')
        cfg = load_yaml(config_file)
        cfg['reader']['grids'] = self.grids
        self.logger.info('Defining grid path %s in config-aqua.yaml', self.grids)
        dump_yaml(config_file, cfg)

    def _install(self):
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
        os.makedirs(f'{self.configpath}/machines', exist_ok=True)

    def list(self, args):
        """List installed catalogs"""

        self.configpath = ConfigPath().configdir
        cdir = f'{self.configpath}/machines'
        contents = os.listdir(cdir)

        print('AQUA current installed catalogs in', cdir, ':')
        for item in contents:
            file_path = os.path.join(cdir, item)
            if os.path.islink(file_path):
                print(f"\t - {item} (editable)")
            else:
                print(f"\t - {item}")

    def fixes_add(self, args):
        """Add a fix file"""
        
        self._file_add('fixes', args.fixfile)

    def grids_add(self, args):
        """Add a grid file"""

        self._file_add('grids', args.gridfile)


    def _file_add(self, kind, file):
        """Add a personalized file to the fixes/grids folder"""

        if not os.path.exists(file):
            self.logger.error('%s is not a valid file!', file)
            return
        self._check()
        basefile = os.path.basename(file)
        pathfile = f'{self.configpath}/{kind}/{basefile}'
        if not os.path.exists(pathfile):
            self.logger.info('Installing %s to %s', file, pathfile)
            shutil.copy(file, pathfile)
        else:
            self.logger.error('%s for file %s already installed, or a file with same name exist', kind, file)
                 
    def add(self, args):
        """Add a catalog"""
        print('Adding the AQUA catalog', args.catalog)
        self._check()
        cdir = f'{self.configpath}/machines/{args.catalog}'
        sdir = f'{self.aquapath}/machines/{args.catalog}'
        self.logger.info('Installing to %s', self.configpath)
        if args.editable is not None:
            if os.path.exists(args.editable):
                os.symlink(args.editable, cdir)
            else:
                self.logger.error('Catalog %s cannot be found in %s', args.catalog, args.editable)
        else:
            if not os.path.exists(cdir):
                if os.path.isdir(sdir):
                    shutil.copytree(f'{self.aquapath}/machines/{args.catalog}', cdir)
                else:
                    self.logger.error('Catalog %s does not appear to exist in %s', args.catalog, sdir)
            else:
                self.logger.error("Catalog %s already installed in %s, please consider `aqua update`. "
                                  "Which does not exist hahaha!",
                                args.catalog, cdir)

        # once we get rid of machine dependence, this can be removed    
        self.logger.info('Setting machine name to %s', args.catalog)
        cfg = load_yaml(self.configfile)
        cfg['machine'] = args.catalog
        dump_yaml(self.configfile, cfg)
    
    def remove(self, args):
        """Remove a catalog"""
        print('Remove the AQUA catalog', args.catalog)
        self._check()
        cdir = f'{self.configpath}/machines/{args.catalog}'
        if os.path.exists(cdir):
            shutil.rmtree(cdir)
        else:
            self.logger.error('Catalog %s is not installed in %s, cannot remove it',
                              args.catalog, cdir)
            
    def _check(self):
        """check installation"""
        try:
            self.configpath = ConfigPath().configdir
            self.configfile = os.path.join(self.configpath, 'config-aqua.yaml')
        except FileNotFoundError:
            self.logger.error('No AQUA installation found!')
            sys.exit()

    def uninstall(self, args):
        """Remove AQUA"""
        print('Remove the AQUA installation')
        self._check()
        check = query_yes_no(f"Do you want to uninstall AQUA from {self.configpath}", "no")
        if check:
            self.logger.info('Uninstalling AQUA from %s', self.configpath)
            shutil.rmtree(self.configpath)


def main():
    """AQUA main installation tool"""
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
