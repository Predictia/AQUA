import intake
import xarray as xr
import os
from aqua import regrid as rg
from aqua.util import load_yaml

def catalogue(verbose=True):

    """Catalogue of available NextGEMS data (on Levante for now)"""

    catalog_file = "config/catalog.yaml"
    cfg = load_yaml("config/retrieve.yaml")
    cat = intake.open_catalog(catalog_file)
    if verbose:
        for model in cfg["exp"]:
            for exp in cfg["exp"][model]:
                expid = cfg["exp"][model][exp]["expid"]
                print(model + '\t' + exp + '\t' + cat[model][expid].description)
    return cat