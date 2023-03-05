import intake
import os

def catalogue(verbose=True, configdir=None):

    """Catalogue of available NextGEMS data (on Levante for now)"""

    if configdir:
        catalog_file = os.path.join(configdir, "catalog.yaml")
    else:
        homedir = os.environ['HOME']
        for configdir in ['./config', '../config', '../../config', os.path.join(homedir, ".aqua/config")]:
            catalog_file = os.path.join(configdir, "catalog.yaml")
            if os.path.exists(catalog_file):
                break

    cat = intake.open_catalog(catalog_file)
    if verbose:
        for model,vm in cat.items():
            for exp,ve in vm.items():
                print(model + '\t' + exp + '\t' + cat[model][exp].description)
                if exp != "grids":
                    for k in cat[model][exp]:
                        print('\t' + '- ' + k + '\t' + cat[model][exp][k].description)
            print()
    return cat