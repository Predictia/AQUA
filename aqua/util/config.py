"""Utility functions for getting the configuration files"""
import os
import platform
import intake
from .yaml import load_yaml
from .util import to_list

class ConfigPath():

    """
    Class to set the configuration path and dir in a robust way
    """

    def __init__(self, configdir=None, filename='config-aqua.yaml', catalog=None):

        # self.catalog_available is a list
        # self.catalog is a string
        # self.base_availabe is a dictionary for all self.catalog_available
        # self.base is dictionary for self.catalog

        self.filename = filename
        if configdir is None:
            self.configdir = self.get_config_dir()
        else:
            self.configdir = configdir
        self.config_file = os.path.join(self.configdir, self.filename)

        if catalog is None:
            self.catalog_available = to_list(self.get_catalog())
        else:
            self.catalog_available = to_list(catalog)
        self.catalog = self.catalog_available[0]

        if self.catalog_available is not None:
            self.base_available = self.get_base()
        else:
            self.base_available = None
        
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
        #aquadir = os.environ.get('AQUA')
        #if aquadir:
        #    configdirs.append(os.path.join(aquadir, 'config'))

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
            if not base['catalog']:
                return None
            
            return base['catalog']
        else:
            raise FileNotFoundError(f'Cannot find the basic configuration file {self.config_file}!')

    def browse_catalogs(self, model:str, exp:str, source:str):
        """
        Given a list of catalog installed set the first one
        """

        if self.catalog_available is None:
            return None

        if all(v is not None for v in [model, exp, source]):
            out = []
            for catalog in self.catalog_available:
                print('Browsing catalog:', catalog)
                check = self.inspect_catalogue(catalog=catalog, model=model, exp=exp,
                                               source=source, verbose=False)
                if check is True:
                    out.append(catalog)
            return out
        
        raise KeyError('Need to defined the triplet model, exp and source')
    
    def set_catalog(self, model, exp, source, catalog=None):
        
        matched = self.browse_catalogs(model=model, exp=exp, source=source)
        if catalog is not None:
            if catalog in matched:
                self.catalog = catalog
            else:
                raise KeyError('Cannot find triplet in the required catalog')
        else:
            if matched: 
                self.catalog = matched[0]
            else:
                raise KeyError('Cannot find the triplet in any catalog')
            
        catalog_file, machine_file = self.get_catalog_filenames(self.catalog)
        return intake.open_catalog(catalog_file), machine_file

      
    def get_base(self):
        """
        Get all the possible base configurations available
        """

        base = {}
        if os.path.exists(self.config_file):
            for catalog in self.catalog_available:
                definitions = {'catalog': catalog, 'configdir': self.configdir}
                base[catalog] = load_yaml(infile=self.config_file, definitions=definitions, jinja=True)
        else:
            raise FileNotFoundError(f'Cannot find the basic configuration file {self.config_file}!')
        return base

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

    def get_catalog_filenames(self, catalog=None):
        """
        Extract the filenames

        Returns:
            Two strings for the path of the fixer, regrid and config files
        """

        if self.catalog is None:
            raise KeyError('No AQUA catalog is installed. Please run "aqua add CATALOG_NAME"')

        if catalog is None:
            catalog = self.catalog

        catalog_file = self.base_available[catalog]['reader']['catalog']
        if not os.path.exists(catalog_file):
            raise FileNotFoundError(f'Cannot find catalog file in {catalog_file}. Did you install it with "aqua add {catalog}"?')
        machine_file = self.base_available[catalog]['reader']['machine']
        if not os.path.exists(machine_file):
            raise FileNotFoundError(f'Cannot find machine file for {catalog} in {machine_file}')

        return catalog_file, machine_file

    def get_reader_filenames(self, catalog=None):
        """
        Extract the filenames for the reader for catalog, regrid and fixer

        Returns:
            Three strings for the path of the fixer, regrid and config files
        """
        if catalog is None:
            catalog = self.catalog

        fixer_folder = self.base_available[catalog]['reader']['fixer']
        if not os.path.exists(fixer_folder):
            raise FileNotFoundError(f'Cannot find the fixer folder in {fixer_folder}')
        grids_folder = self.base_available[catalog]['reader']['regrid']
        if not os.path.exists(grids_folder):
            raise FileNotFoundError(f'Cannot find the regrid folder in {grids_folder}')
        

        return fixer_folder, grids_folder

    def inspect_catalogue(self, catalog=None, model=None, exp=None, source=None, verbose=True):
        """
        Basic function to simplify catalog inspection.
        If a partial match between model, exp and source is provided, then it will return a list
        of models, experiments or possible sources. If all three are specified it returns False if that
        combination does not exist, a list of variables if the source is a FDB/GSV source and it exists and
        True if it exists but is not a FDB source.

        Args:
            cat (intake.catalog.local.LocalCatalog, optional): The catalog object containing the data.
            model (str, optional): The model ID to filter the catalog.
                If None, all models are returned. Defaults to None.
            exp (str, optional): The experiment ID to filter the catalog.
                If None, all experiments are returned. Defaults to None.
            source (str, optional): The source ID to filter the catalog.
                If None, all sources are returned. Defaults to None.
            verbose (bool, optional): Print the catalog information to the console. Defaults to True.

        Returns:
            list:   A list of available items in the catalog, depending on the
                    specified model and/or experiment, a list of variables or True/False.

        Raises:
            KeyError: If the input specifications are incorrect.
        """

               # get configuration from the catalog
        catalog_file, _ = self.get_catalog_filenames(catalog)

        cat = intake.open_catalog(catalog_file)

        if model and exp and not source:
            if is_in_cat(cat, model, exp, None):
                if verbose:
                    print(f"Sources available in catalogue for model {model} and exp {exp}:")
                return list(cat[model][exp].keys())
        elif model and not exp:
            if is_in_cat(cat, model, None, None):
                if verbose:
                    print(f"Experiments available in catalogue for model {model}:")
                return list(cat[model].keys())
        elif not model:
            if verbose:
                print("Models available in catalog:")
            return list(cat.keys())

        elif model and exp and source:
            # Check if variables can be explored
            # Added a try/except to avoid the KeyError when the source is not in the catalogue
            # because model or exp are not in the catalogue
            # This allows to always have a True/False or var list return
            # when model/exp/source are provided
            try:
                if is_in_cat(cat, model, exp, source):
                    # Ok, it exists, but does it have metadata?
                    #try:
                    #    variables = cat[model][exp][source].metadata['variables']
                    #    if verbose:
                    #        print(f"The following variables are available for model {model}, exp {exp}, source {source}:")
                    #    return variables
                    #except KeyError:
                    return True
            except KeyError:
                pass  # go to return False

        if verbose:
            print(f"The combination model={model}, exp={exp}, source={source} is not available in the catalogue.")
            if model:
                if is_in_cat(cat, model, None, None):
                    if exp:
                        if is_in_cat(cat, model, exp, None):
                            print(f"Available sources for model {model} and exp {exp}:")
                            return list(cat[model][exp].keys())
                        else:
                            print(f"Experiment {exp} is not available for model {model}.")
                            print(f"Available experiments for model {model}:")
                            return list(cat[model].keys())
                    else:
                        print(f"Available experiments for model {model}:")
                        return list(cat[model].keys())
                else:
                    print(f"Model {model} is not available.")
                    print("Available models:")
                    return list(cat.keys())

        return False


def is_in_cat(cat, model, exp, source):
    """
    Check if the model, experiment and source are in the catalog.
    """
    if source:
        try:
            return source in cat[model][exp].keys()
        except KeyError:
            return False
    elif exp:
        try:
            return exp in cat[model].keys()
        except KeyError:
            return False
    else:
        try:
            return model in cat.keys()
        except KeyError:
            return False