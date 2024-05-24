#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
AQUA main command line
'''

import os
import argparse
import shutil
import sys
from aqua.util import load_yaml, dump_yaml, load_multi_yaml
from aqua.logger import log_configure
from aqua.util import ConfigPath
from aqua import __path__ as pypath
from aqua import __version__ as version

def parse_arguments():
    """Parse arguments for AQUA console"""

    parser = argparse.ArgumentParser(description='AQUA command line tool')
    subparsers = parser.add_subparsers(dest='command', help='Available AQUA commands')

    # Parser for the aqua main command
    parser.add_argument('--version', action='version',
                version=f'%(prog)s {version}', help="show AQUA version number and exit.")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Increase verbosity of the output to INFO loglevel')
    parser.add_argument('-vv', '--very-verbose', action='store_true',
                        help='Increase verbosity of the output to DEBUG loglevel')

    # List of the subparsers with actions
    # Corresponding to the different aqua commands available (see command map)
    install_parser = subparsers.add_parser("install")
    fixes_add_parser = subparsers.add_parser("fixes-add")
    grids_add_parser = subparsers.add_parser("grids-add")
    catalog_add_parser = subparsers.add_parser("add")
    catalog_remove_parser = subparsers.add_parser("remove")

    # subparser with no arguments
    subparsers.add_parser("uninstall")
    subparsers.add_parser("list")

    install_parser.add_argument('-p', '--path', type=str,
                help='Path where to install AQUA')
    install_parser.add_argument('-g', '--grids', type=str,
                help='Path where to be usef for AQUA grids (NOT WORKING FOR NOW)')
    install_parser.add_argument('-e', '--editable', type=str,
                help='Install AQUA in editable mode from the original source')

    catalog_add_parser.add_argument("catalog", metavar="CATALOG",
                help="Catalog to be installed")
    catalog_add_parser.add_argument('-e', '--editable', type=str,
                help='Install a catalog in editable mode from the original source: provide the Path')
    
    fixes_add_parser.add_argument("fixfile", metavar="fixfile",
                                    help="Fix file to be added")
    fixes_add_parser.add_argument("-e", "--editable", action="store_true",
                                    help="Add a fixes file in editable mode from the original path")

    grids_add_parser.add_argument("gridfile", metavar="gridfile",
                                    help="Fix file to be added")
    grids_add_parser.add_argument("-e", "--editable", action="store_true",
                                    help="Add a grids file in editable mode from the original path")
    
    catalog_remove_parser.add_argument("catalog", metavar="CATALOG",
                                    help="Catalog to be removed")
    
    return parser

class AquaConsole():
    """Class for AquaConsole, the AQUA command line interface for
    installation, catalog, grids and fixes editing"""

    def __init__(self):
        """The main AQUA command line interface"""

        parser = parse_arguments()
        args = parser.parse_args(sys.argv[1:])

        # Set the log level
        if args.very_verbose or (args.verbose and args.very_verbose):
            loglevel = 'DEBUG'
        elif args.verbose:
            loglevel = 'INFO'
        else:
            loglevel = 'WARNING'
        self.logger = log_configure(loglevel, 'AQUA')

        self.pypath = pypath[0]
        self.aquapath = os.path.join(os.path.dirname(self.pypath), 'config')
        self.configpath = None
        self.configfile = 'config-aqua.yaml'
        self.grids = None

        command_map = {
            'install': self.install,
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

    def install(self, args):
        """Install AQUA, find the folders and then install"""
        self.logger.info('Running the AQUA install')

        # define where to install AQUA
        if args.path is None:
            self._install_home()
        else:
            self._install_path(args.path)

        # define from where aqua is installed and copy/link the files
        if args.editable is None:
            self._install()
        else:
            self._install_editable(args.editable)

        self.grids = args.grids
        #TODO
        #if self.grids is None: 
        #    self.logger.warning('Grids directory undefined')
        #else:
        #self._grids_define()

    def _install_home(self):
        """Define the AQUA installation folder, by default inside $HOME"""

        if 'HOME' in os.environ:
            path = os.path.join(os.environ['HOME'], '.aqua')
            self.configpath = path
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
            else:
                self.logger.warning('AQUA already installed in %s', path)
                check = query_yes_no(f"Do you want to overwrite AQUA installation in {path}. "
                                        "You will lose all catalogs installed.", "no")
                if not check:
                    sys.exit()
                else:
                    self.logger.warning('Removing the content of %s', path)
                    shutil.rmtree(path)
                    os.makedirs(path, exist_ok=True)
        else:
            self.logger.error('$HOME not found.'
                            'Please specify a path where to install AQUA and define AQUA_CONFIG as environment variable')
            sys.exit()

    def _install_path(self, path):
        """Define the AQUA installation folder when a path is specified"""

        self.configpath = path
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        else:
            if not os.path.isdir(path):
                self.logger.error("Path chosen is not a directory")
                sys.exit()

        check = query_yes_no(f"Do you want to create a link in the $HOME/.aqua to {path}", "yes")
        if check:
            if 'HOME' in os.environ:
                link = os.path.join(os.environ['HOME'], '.aqua')
                if os.path.exists(link):
                    self.logger.warning('Removing the content of %s', link)
                    shutil.rmtree(link)
                os.symlink(path, link)
            else:
                self.logger.error('$HOME not found. Cannot create a link to the installation path')
                self.logger.warning('AQUA will be installed in %s, but please remember to define AQUA_CONFIG environment variable', path)
        else:
            self.logger.warning('AQUA will be installed in %s, but please remember to define AQUA_CONFIG environment variable', path)


    # def _grids_define(self):
    #     """add the grid definition into the aqua-config.yaml"""

    #     config_file = os.path.join(self.configpath, 'config-aqua.yaml')
    #     cfg = load_yaml(config_file)
    #     cfg['reader']['grids'] = self.grids
    #     self.logger.info('Defining grid path %s in config-aqua.yaml', self.grids)
    #     dump_yaml(config_file, cfg)

    def _install(self):
        """Copying the installation file"""

        print("Installing AQUA to", self.configpath)
        for file in ['config-aqua.yaml']:
            if not os.path.exists(os.path.join(self.configpath, file)):
                self.logger.info('Copying from %s to %s', self.aquapath, self.configpath)
                shutil.copy(f'{self.aquapath}/{file}', f'{self.configpath}/{file}')
        for directory in ['fixes', 'data_models', 'grids']:
            if not os.path.exists(os.path.join(self.configpath, directory)):
                self.logger.info('Copying from %s to %s',
                                 os.path.join(self.aquapath, directory), self.configpath)
                shutil.copytree(f'{self.aquapath}/{directory}', f'{self.configpath}/{directory}')
        os.makedirs(f'{self.configpath}/machines', exist_ok=True)

    def _install_editable(self, editable):
        """Linking the installation file in editable"""

        editable = os.path.abspath(editable)
        print("Installing AQUA with a link from ", editable," to ", self.configpath)
        for file in ['config-aqua.yaml']:
            if os.path.isfile(os.path.join(editable,file)):
                if not os.path.exists(os.path.join(self.configpath, file)):
                    self.logger.info('Linking from %s to %s', editable, self.configpath)
                    os.symlink(f'{editable}/{file}', f'{self.configpath}/{file}')
            else:
                self.logger.error('%s folder does not include AQUA configuration files. Please use AQUA/config', editable)
                os.rmdir(self.configpath)
                sys.exit()
        for directory in ['fixes', 'data_models', 'grids']:
            if not os.path.exists(os.path.join(self.configpath, directory)):
                self.logger.info('Linking from %s to %s',
                                 os.path.join(editable, directory), self.configpath)
                os.symlink(f'{editable}/{directory}', f'{self.configpath}/{directory}')
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
        compatible = self._check_file(kind='fixes', file=args.fixfile)
        if compatible:
            self._file_add(kind='fixes', file=args.fixfile, link=args.editable)

    def grids_add(self, args):
        """Add a grid file"""
        compatible = self._check_file(kind='grids', file=args.gridfile)
        if compatible:
            self._file_add(kind='grids', file=args.gridfile, link=args.editable)

    def _file_add(self, kind, file, link=False):
        """Add a personalized file to the fixes/grids folder
        
        Args:
            kind (str): the kind of file to be added, either 'fixes' or 'grids'
            file (str): the file to be added
            link (bool): whether to add the file as a link or not
        """

        if not os.path.exists(file):
            self.logger.error('%s is not a valid file!', file)
            sys.exit()
        file = os.path.abspath(file)
        self._check()
        basefile = os.path.basename(file)
        pathfile = f'{self.configpath}/{kind}/{basefile}'
        if not os.path.exists(pathfile):
            if link:
                self.logger.info('Linking %s to %s', file, pathfile)
                os.symlink(file, pathfile)
            else:
                self.logger.info('Installing %s to %s', file, pathfile)
                shutil.copy(file, pathfile)
        else:
            self.logger.error('%s for file %s already installed, or a file with the same name exists', kind, file)
            sys.exit()

    def add(self, args):
        """Add a catalog"""
        print('Adding the AQUA catalog', args.catalog)
        self._check()
        cdir = f'{self.configpath}/machines/{args.catalog}'
        sdir = f'{self.aquapath}/machines/{args.catalog}'
        if args.editable is not None:
            editable = os.path.abspath(args.editable)
            print('Installing catalog in editable mode from', editable, 'to', self.configpath)
            if os.path.exists(editable):
                if os.path.exists(cdir):
                    self.logger.error('Catalog %s already installed in %s, please consider `aqua remove`',
                                      args.catalog, cdir)
                    sys.exit()
                else:
                    os.symlink(editable, cdir)
            else:
                self.logger.error('Catalog %s cannot be found in %s', args.catalog, editable)
                sys.exit()
        else:
            if not os.path.exists(cdir):
                if os.path.isdir(sdir):
                    shutil.copytree(f'{self.aquapath}/machines/{args.catalog}', cdir)
                else:
                    self.logger.error('Catalog %s does not appear to exist in %s', args.catalog, sdir)
            else:
                self.logger.error("Catalog %s already installed in %s, please consider `aqua remove`.",
                                args.catalog, cdir)
                sys.exit()

        # once we get rid of machine dependence, this can be removed    
        self.logger.info('Setting machine name to %s', args.catalog)
        cfg = load_yaml(self.configfile)
        cfg['machine'] = args.catalog
        dump_yaml(self.configfile, cfg)
    
    def remove(self, args):
        """Remove a catalog"""
        self._check()
        cdir = f'{self.configpath}/machines/{args.catalog}'
        print('Remove the AQUA catalog', args.catalog, 'from', cdir)
        if os.path.exists(cdir):
            if os.path.islink(cdir):
                os.unlink(cdir)
            else:
                shutil.rmtree(cdir)
        else:
            self.logger.error('Catalog %s is not installed in %s, cannot remove it',
                              args.catalog, cdir)
            sys.exit()
            
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
            # Remove the AQUA installation both for folder and link case
            if os.path.islink(self.configpath):
                # Remove link and data in the linked folder
                self.logger.info('Removing the link %s', self.configpath)
                os.unlink(self.configpath)
            else:
                self.logger.info('Uninstalling AQUA from %s', self.configpath)
                shutil.rmtree(self.configpath)

    def _check_file(self, kind, file=None):
        """
        Check if a new file can be merged with AQUA load_multi_yaml()
        It works also without a new file to check that the existing files are compatible
        
        Args:
            kind (str): the kind of file to be added, either 'fixes' or 'grids'
            file (str): the file to be added
        """
        if kind not in ['fixes', 'grids']:
            raise ValueError('Kind must be either fixes or grids')

        self._check()
        try:
            load_multi_yaml(folder_path=f'{self.configpath}/{kind}',
                            filenames=[file]) if file is not None else load_multi_yaml(folder_path=f'{self.configpath}/{kind}')
            
            if file is not None:
                self.logger.debug('File %s is compatible with the existing files in %s', file, kind)
            
            return True
        except Exception as e:
            if file is not None:
                self.logger.error("It is not possible to add the file %s to the %s folder", file, kind)
            else:
                self.logger.error("Existing files in the %s folder are not compatible", kind)
            self.logger.error(e)
            return False


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
