"""Simple catalog utility"""

import intake
from aqua.util import ConfigPath

def catalog(verbose=True, configdir=None, catalog=None):
    """
    Catalogue of available data.

    Args:
        verbose (bool, optional):       If True, prints the catalog
                                        information to the console.
                                        Defaults to True.
        configdir (str, optional):      The directory containing the
                                        configuration files.
                                        If not provided, get_config_dir
                                        is used to find it.

    Returns:
        cat (intake.catalog.local.LocalCatalog):    The catalog object
                                                    containing the data.
    """

    # get the config dir and the catalog
    Configurer = ConfigPath(configdir=configdir, catalog=catalog)

    # get configuration from the catalog
    catalog_file, _ = Configurer.get_catalog_filenames()

    cat = intake.open_catalog(catalog_file)
    if verbose:
        print('Catalog: ' + Configurer.catalog)
        for model, vm in cat.items():
            for exp, _ in vm.items():
                print(model + '\t' + exp + '\t' + cat[model][exp].description)
                if exp != "grids":
                    for k in cat[model][exp]:
                        print('\t' + '- ' + k + '\t' + cat[model][exp].walk()[k]._description)  # pylint: disable=W0212
            print()
    return cat
