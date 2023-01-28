import intake
import xarray as xr
import os
from aqua import regrid as rg
from aqua.util import load_yaml

class Reader():
    """General reader for NextGEMS data (on Levante for now)"""

    def __init__(self, model="ICON", exp="tco2559-ng5", source=None, regrid=None, method="ycon"):
        self.exp = exp
        self.model = model
        self.targetgrid = regrid

        catalog_file = "config/catalog.yaml"
        self.cat = intake.open_catalog(catalog_file)

        cfg = load_yaml("config/retrieve.yaml")

        if source:
            self.source = source
        else:
            self.source = list(self.cat[model][exp].keys())[0]  # take first source if none provided
        
        if regrid:
            self.weightsfile =os.path.join(
                cfg["regrid"]["weightsdir"],
                cfg["regrid"]["weightsfile"].format(model=model, method=method, regrid=regrid))
            try: 
                self.weights = xr.open_mfdataset(self.weightsfile)
                self.regridder = rg.Regridder(weights=self.weights)
            except OSError:
                print("Weights file not found:", self.weightsfile)
               
    def retrieve(self, regrid=False):
        data = self.cat[self.model][self.exp][self.source].to_dask()
        if self.targetgrid and regrid:
            data = self.regridder.regrid(data)
        return data

    def regrid(self, data):
        return self.regridder.regrid(data)

