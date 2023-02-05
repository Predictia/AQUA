import intake
import xarray as xr
import os
from metpy.units import units
import smmregrid as rg
from aqua.util import load_yaml

class Reader():
    """General reader for NextGEMS data (on Levante for now)"""

    def __init__(self, model="ICON", exp="tco2559-ng5", source=None, regrid=None, method="ycon", zoom=None):
        self.exp = exp
        self.model = model
        self.targetgrid = regrid
        self.zoom = zoom

        catalog_file = "config/catalog.yaml"
        self.cat = intake.open_catalog(catalog_file)

        cfg_regrid = load_yaml("config/regrid.yaml")

        if source:
            self.source = source
        else:
            self.source = list(self.cat[model][exp].keys())[0]  # take first source if none provided
        
        if regrid:
            self.weightsfile =os.path.join(
                cfg_regrid["weights"]["path"],
                cfg_regrid["weights"]["template"].format(model=model,
                                                    exp=exp, 
                                                    method=method, 
                                                    target=regrid))
            if os.path.exists(self.weightsfile):
                self.weights = xr.open_mfdataset(self.weightsfile)
            else:
                print("Weights file not found:", self.weightsfile)
                print("Attempting to generate it ...")

                weights = rg.cdo_generate_weights(source_grid=cfg_regrid["source_grids"][exp]["path"],
                                                      target_grid=cfg_regrid["target_grids"][regrid], 
                                                      method='ycon', 
                                                      gridpath=cfg_regrid["paths"]["grids"],
                                                      icongridpath=cfg_regrid["paths"]["icon"],
                                                      extra=cfg_regrid["source_grids"][exp].get("extra", None))
                weights.to_netcdf(self.weightsfile)
                self.weights = weights
                print("Success!")

            self.regridder = rg.Regridder(weights=self.weights)

               
    def retrieve(self, regrid=False, fix=True):
        if self.zoom:
            data = self.cat[self.model][self.exp][self.source](zoom=self.zoom).to_dask()
        else:
            data = self.cat[self.model][self.exp][self.source].to_dask()
        if self.targetgrid and regrid:
            data = self.regridder.regrid(data)
        if fix:
            data = self.fixer(data)
        return data

    def regrid(self, data):
        # save attributes (not conserved by smmregrid)
        out = self.regridder.regrid(data)
        out.attrs = data.attrs
        return out
    
    def fixer(self, data):
        fixes = load_yaml("config/fixes.yaml")
        model=self.model

        fix = fixes["models"].get(model, None)
        if not fix:
            print("No fixes defined for model ", model)
            return data

        self.deltat = fix.get("deltat", 1)
        fixd = {}
        allvars = data.variables
        for var in fix["vars"]:
                    shortname = fix["vars"][var]["short_name"]
                    if var in allvars: 
                        fixd.update({f"{var}": f"{shortname}"})
                        src_units = fix["vars"][var].get("src_units", None)
                        if src_units:
                            data[var].attrs.update({"units": "degC"})
                        units = fix["vars"][var]["units"]
                        if units.count('{'):
                            units = fixes["defaults"]["units"][units.replace('{','').replace('}','')]                
                        data[var].attrs.update({"target_units": units})
                        factor, offset = self.convert_units(data[var].units, units, var)
                        data[var].attrs.update({"factor": factor})
                        data[var].attrs.update({"offset": offset})

        allcoords = data.coords
        for coord in fix["coords"]:
                    newcoord = fix["coords"][coord]["name"]
                    newcoord = fixes["defaults"]["coords"][newcoord.replace('{','').replace('}','')] 
                    if coord in allcoords: 
                        fixd.update({f"{coord}": f"{newcoord}"})

        return data.rename(fixd)

    def convert_units(self, src, dst, var="input var"):
        factor = units(src).to_base_units() / units(dst).to_base_units()
        offset = ((0 * units(src)) - (0 * units(dst))).to(units(dst))
        
        if factor.units != units("dimensionless").units:
            if factor.units == "meter ** 3 / kilogram":
                # Density of water was missing
                factor = factor * 1000 * units("kg m-3")
                print(f"{var}: corrected multiplying by density of water 1000 kg m-3")
            if factor.units == "meter ** 3 * second / kilogram":
                # Density of water and accumulation time were missing
                factor = factor * 1000 * units("kg m-3") / (self.deltat * units("s"))
                print(f"{var}: corrected multiplying by density of water 1000 kg m-3")
                print(f"{var}: corrected dividing by accumulation time {self.deltat} s")
            else:
                print(f"{var}: incommensurate units converting {src} to {dst} --> {factor.units}")

        if offset.magnitude != 0:
            factor = None
            offset = offset.magnitude
        else:
            offset = None
            factor = factor.magnitude
        return factor, offset
    
