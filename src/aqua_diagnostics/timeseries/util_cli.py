from aqua.logger import log_configure
from aqua.diagnostics.timeseries import Timeseries, SeasonalCycles


class MixinCLI():

    def __init__(self, config_dict: dict, var: str, formula: bool = False,
                 loglevel: str = 'WARNING'):
        """
        Initialize the TimeseriesCLI class.
        
        Args:
            config_dict (dict): The configuration dictionary.
            var (str): The variable to run the timeseries diagnostics for.
            formulae (bool): Whether the requested variable is a formula.
            loglevel (str): The logging level. Default is 'WARNING'.
        """
        
        self.logger = log_configure(log_level=loglevel, log_name='Timeseries CLI')
        self.loglevel = loglevel
        self.config_dict = config_dict
        # We need the lengths to have a list of results with the correct length
        self.len_datasets = len(self.config_dict['datasets'])
        self.len_references = len(self.config_dict['references'])
        self.diag_datasets = []
        self.diag_references = []
        self.var = var
        self.formula = formula

class TimeseriesCLI(MixinCLI):
    """
    Class that helps to run the timeseries diagnostics for a given variable and configuration.
    It runs many Timeseries instances, one for each dataset and reference.
    """
    def run(self, regrid: str = None, std_startdate: str = None, std_enddate: str = None,
            region: str = None, long_name: str = None, units: str = None,
            standard_name: str = None, freq: list = ['monthly', 'annual'],
            outputdir: str = './', rebuild: bool = True):
        """
        Run the timeseries diagnostics for the given variable and configuration.

        Args:
            regrid (str): The regridding resolution. Default is None.
            std_startdate (str): The start date for the standardization. Default is None.
            std_enddate (str): The end date for the standardization. Default is None.
            region (str): The region to run the diagnostics for. Default is None.
            long_name (str): The long name of the variable, if different from the variable name.
            units (str): The units of the variable, if different from the original units.
            standard_name (str): The standard name of the variable, if different from the variable name.
            freq (list): The frequency of the diagnostics. Default is ['monthly', 'annual'].
            outputdir (str): The output directory. Default is './'.
            rebuild (bool): If True, rebuild the data.
        """
        init_args = {'region': region, 'loglevel': self.loglevel}
        run_args = {'var': self.var, 'formula': self.formula, 'long_name': long_name,
                    'units': units, 'standard_name': standard_name, 'freq': freq,
                    'outputdir': outputdir, 'rebuild': rebuild}

        # Run the datasets
        for i, dataset in enumerate(self.config_dict['datasets']):
            self.logger.debug(f'Running dataset: {dataset}, variable: {self.var}')
            dataset_args = {'catalog': dataset['catalog'], 'model': dataset['model'],
                    'exp': dataset['exp'], 'source': dataset['source'],
                    'regrid': dataset.get('regrid', regrid)}
            timeseries = Timeseries(**dataset_args, **init_args)
            self.diag_datasets.append(timeseries)
            self.diag_datasets[i].run(**run_args)
        
        # Run the references
        for i, reference in enumerate(self.config_dict['references']):
            self.logger.debug(f'Running reference: {reference}, variable: {self.var}')
            reference_args = {'catalog': reference['catalog'], 'model': reference['model'],
                              'exp': reference['exp'], 'source': reference['source'],
                              'regrid': reference.get('regrid', regrid),
                              'std_startdate': std_startdate, 'std_enddate': std_enddate}
            timeseries = Timeseries(**reference_args, **init_args)
            self.diag_references.append(timeseries)
            self.diag_references[i].run(**run_args)


class SeasonalCyclesCLI(MixinCLI):
    """
    Class that helps to run the seasonal cycles diagnostics for a given variable and configuration.
    It runs many SeasonalCycles instances, one for each dataset and reference.
    """
    def run(self, regrid: str = None, std_startdate: str = None, std_enddate: str = None,
            region: str = None, long_name: str = None, units: str = None,
            standard_name: str = None, outputdir: str = './', rebuild: bool = True):
        """
        Run the seasonal cycles diagnostics for the given variable and configuration.

        Args:ß
            regrid (str): The regridding resolution. Default is None.
            std_startdate (str): The start date for the standardization. Default is None.
            std_enddate (str): The end date for the standardization. Default is None.
            region (str): The region to run the diagnostics for. Default is None.
            long_name (str): The long name of the variable, if different from the variable name.
            units (str): The units of the variable, if different from the original units.
            standard_name (str): The standard name of the variable, if different from the variable name.
            outputdir (str): The output directory. Default is './'.
            rebuild (bool): If True, rebuild the data.
        """
        init_args = {'region': region, 'loglevel': self.loglevel}
        run_args = {'var': self.var, 'formula': self.formula, 'long_name': long_name,
                    'units': units, 'standard_name': standard_name,
                    'outputdir': outputdir, 'rebuild': rebuild}

        # Run the datasets
        for i, dataset in enumerate(self.config_dict['datasets']):
            self.logger.debug(f'Running dataset: {dataset}, variable: {self.var}')
            dataset_args = {'catalog': dataset['catalog'], 'model': dataset['model'],
                            'exp': dataset['exp'], 'source': dataset['source'],
                            'regrid': dataset.get('regrid', regrid)}
            seasonal_cycles = SeasonalCycles(**dataset_args, **init_args)
            self.diag_datasets.append(seasonal_cycles)
            self.diag_datasets[i].run(**run_args)
        
        # Run the references
        for i, reference in enumerate(self.config_dict['references']):
            self.logger.debug(f'Running reference: {reference}, variable: {self.var}')
            reference_args = {'catalog': reference['catalog'], 'model': reference['model'],
                              'exp': reference['exp'], 'source': reference['source'],
                              'regrid': reference.get('regrid', regrid),
                              'std_startdate': std_startdate, 'std_enddate': std_enddate}
            seasonal_cycles = SeasonalCycles(**reference_args, **init_args)
            self.diag_references.append(seasonal_cycles)
            self.diag_references[i].run(**run_args)


def load_var_config(config_dict: dict, var: str, diagnostic: str = 'timeseries'):
    """
    Load the variable configuration from the configuration dictionary.
    
    Args:
        config_dict (dict): The configuration dictionary.
        var (str): The variable to load the configuration for.
        diagnostic (str): The diagnostic to load the configuration for. Default is 'timeseries'.

    Returns:
        var_config (dict): The variable configuration dictionary
    """
    default_dict = config_dict['diagnostics']['timeseries']['params']['default']

    if var in config_dict['diagnostics']['timeseries']['params']:
        var_config = config_dict['diagnostics']['timeseries']['params'][var]
    else:
        var_config = {}

    # Merge the default and variable specific configuration
    # with the variable specific configuration taking precedence
    var_config = {**default_dict, **var_config}

    # Take hourly, daily, monthly, annual and make a list of the True
    # ones, dropping the individual keys
    if diagnostic == 'timeseries':
        freq = []
        for key in ['hourly', 'daily', 'monthly', 'annual']:
            if var_config[key]:
                freq.append(key)
            if var_config[key] is not None:
                del var_config[key]
        var_config['freq'] = freq
    elif diagnostic == 'seasonalcycles':
        for key in ['hourly', 'daily', 'monthly', 'annual']:
            if var_config[key] is not None:
                del var_config[key]

    # Get the regions
    regions = [None]
    if var_config.get('regions') is not None:
        regions.extend([region for region in var_config['regions'] if region is not None])
        del var_config['regions']

    return var_config, regions