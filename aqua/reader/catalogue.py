"""Simple catalogue utility"""

import intake
from aqua.util import get_config_dir, get_machine, get_reader_filenames


def catalogue(verbose=True, configdir=None):
    """Catalogue of available data.

    Args:
        verbose (bool, optional): If True, prints the catalog information to the console. Defaults to True.
        configdir (str, optional): The directory containing the configuration files. If not provided,
            the default configuration directory is used.

    Returns:
        cat (intake.catalog.local.LocalCatalog): The catalog object containing the NextGEMS data.

    """
    

    # get the config dir and the machine
    if not configdir:
        configdir = get_config_dir()
    machine = get_machine(configdir)

    # get configuration from the machine
    catalog_file, _, _ = get_reader_filenames(configdir, machine)

    cat = intake.open_catalog(catalog_file)
    if verbose:
        for model, vm in cat.items():
            for exp, _ in vm.items():
                print(model + '\t' + exp + '\t' + cat[model][exp].description)
                if exp != "grids":
                    for k in cat[model][exp]:
                        print('\t' + '- ' + k + '\t' + cat[model][exp].walk()[k]._description)  # pylint: disable=W0212
            print()
    return cat
