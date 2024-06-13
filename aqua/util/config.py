"""Utility functions for getting the configuration files"""
import os
import platform
from .yaml import load_yaml

class ConfigPath():

    """
    Class to set the configuration path and dir in a robust way
    """

    def __init__(self, configdir=None, filename='config-aqua.yaml', catalog=None):

        self.filename = filename
        if not configdir:
            self.configdir = self.get_config_dir()
        else:
            self.configdir = configdir
        self.config_file = os.path.join(self.configdir, self.filename)
        if not catalog:
            self.catalog = self.get_catalog()
        else:
            self.catalog = catalog
        
        definitions = {'catalog': self.catalog, 'configdir': self.configdir}

        if os.path.exists(self.config_file):
            self.base = load_yaml(infile=self.config_file, definitions=definitions, jinja=True)
        else:
            raise FileNotFoundError(f'Cannot find the basic configuration file {self.config_file}!')

        
    def get_config_dir(self):
        """
        Return the path to the configuration directory,
        searching in a list of pre-defined directories.

        Generalized to work for config files with different names.

        Returns:
            configdir (str): the dir of the catalog file and other config files

        Raises:
            FileNotFoundError: if no config file is found in the predefined folders
        """

        configdirs = []

        # Check first if AQUA_CONFIG is defined
        aquaconfigdir = os.environ.get('AQUA_CONFIG')
        if aquaconfigdir:
            configdirs.append(aquaconfigdir)

        # Then if the home is defined
        homedir = os.environ.get('HOME')
        if homedir:
            configdirs.append(os.path.join(homedir, '.aqua'))

        # Finally for developers if AQUA is defined
        aquadir = os.environ.get('AQUA')
        if aquadir:
            configdirs.append(os.path.join(aquadir, 'config'))

        # Autosearch for the config folder
        for configdir in configdirs:
            if os.path.exists(os.path.join(configdir, self.filename)):
                return configdir

        raise FileNotFoundError(f"No config file {self.filename} found in {configdirs}")

    def get_catalog(self):
        """
        Extract the name of the catalog from the configuration file

        Returns:
            The name of the catalog read from the configuration file
        """

        if os.path.exists(self.config_file):
            base = load_yaml(self.config_file)
            if 'catalog' not in base:
                raise KeyError(f'Cannot find catalog information in {self.config_file}')
            
            return base['catalog']
        else:
            raise FileNotFoundError(f'Cannot find the basic configuration file {self.config_file}!')
        
    def get_machine(self):
        """
        Extract the name of the machine from the configuration file

        Returns:
            The name of the machine read from the configuration file
        """

        if os.path.exists(self.config_file):
            base = load_yaml(self.config_file)
            # if we do not know the machine we assume is "unknown"
            machine = 'unknown'
            # if the configuration file has a machine entry, use it
            if 'machine' in base:
                machine = base['machine']
            # if the entry is auto, or the machine unknown, try autodetection
            if machine in ['auto', 'unknown']:
                machine = self._auto_detect_machine()
            return machine
        else:
            raise FileNotFoundError(f'Cannot find the basic configuration file {self.config_file}!')
    
    def _auto_detect_machine(self):
        """Tentative method to identify the machine from the hostname"""

        platform_name = platform.node()

        if os.getenv('GITHUB_ACTIONS'):
            return 'github'

        platform_dict = {
            'uan': 'lumi',
            'levante': 'levante',
        }

        # Search for the dictionary key in the key_string
        for key in platform_dict:
            if key in platform_name:
                return platform_dict[key]
        
        return None

    def get_catalog_filenames(self):
        """
        Extract the filenames

        Returns:
            Two strings for the path of the fixer, regrid and config files
        """


        catalog_file = self.base['reader']['catalog']
        if not os.path.exists(catalog_file):
            raise FileNotFoundError(f'Cannot find catalog file in {catalog_file}')
        machine_file = self.base['reader']['machine']
        if not os.path.exists(machine_file):
            raise FileNotFoundError(f'Cannot find machine file for {self.catalog} in {machine_file}')

        return catalog_file, machine_file

    def get_reader_filenames(self):
        """
        Extract the filenames for the reader for catalog, regrid and fixer

        Returns:
            Three strings for the path of the fixer, regrid and config files
        """

        fixer_folder = self.base['reader']['fixer']
        if not os.path.exists(fixer_folder):
            raise FileNotFoundError(f'Cannot find the fixer folder in {fixer_folder}')
        grids_folder = self.base['reader']['regrid']
        if not os.path.exists(grids_folder):
            raise FileNotFoundError(f'Cannot find the regrid folder in {grids_folder}')

        return fixer_folder, grids_folder
