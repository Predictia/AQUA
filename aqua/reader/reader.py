import intake
import sys
import yaml
import xarray as xr
import os
from aqua import regrid

def load_yaml(infile):
    """Load generic yaml file"""

    try:
        with open(infile, 'r', encoding='utf-8') as file:
            cfg = yaml.load(file, Loader=yaml.FullLoader)
    except IOError:
        sys.exit(f'ERROR: {infile} not found: you need to have this configuration file!')
    return cfg


class Reader():
    """General reader for NextGEMS data (on Levante for now)"""

    def __init__(self, model="ICON", exp="R02B09", target=None, method="ycon"):
        self.exp = exp
        self.model = model

        catalog_file = "config/catalog.yaml"
        self.cat = intake.open_catalog(catalog_file)

        cfg = load_yaml("config/retrieve.yaml")

        self.mod = model
        self.expid = cfg["exp"][model][exp]["expid"]
        self.dataid = cfg["exp"][model][exp]["dataid"]

        if target:
            self.weightsfile =os.path.join(
                cfg["regrid"]["weightsdir"],
                cfg["regrid"]["weightsfile"].format(model=model, method=method, target=target))
            try: 
                self.weights = xr.open_mfdataset(self.weightsfile)
                self.regridder = regrid.Regridder(weights=self.weights)
            except OSError:
                print("Weights file not found:", self.weightsfile)
               
    def retrieve(self):
        data = self.cat[self.mod][self.expid][self.dataid].to_dask()
        return data

    def regrid(self, data):
        return self.regridder.regrid(data)

