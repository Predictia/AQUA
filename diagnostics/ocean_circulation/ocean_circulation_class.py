from aqua import Reader,catalogue, inspect_catalogue
import ocean_circulation_func as fn
from aqua.util import load_yaml

class Ocean_circulationDiagnostic:
    def __init__(self, model, exp, source):
        self.config = load_yaml("config.yaml")
        self.stratification_params = self.config['stratification']
        self.MLD_params = self.config['MLD']

        self.reader = Reader(model=self.config["model"], exp=self.config["exp"], source=self.config["source"])
        self.data = self.reader.retrieve()
        self.data = self.data.rename({"nz1":"lev"})
        self.data = self.data.rename({"ocpt":"thetao"})
        self.data = self.data[["thetao","so"]]
        
    def process_data(self):
        self.data = self.data.resample(time="M").mean()
         
    def plot_profile(self):
        fn.plot_stratification(self.data, region= self.stratification_params["region"],
                               time = self.stratification_params["time"],
                               output= self.stratification_params["output"],
                               output_dir=self.stratification_params["output_dir"])
        
        fn.plot_spatial_mld(self.data, region= self.MLD_params["region"],
                               time = self.MLD_params["time"],
                               output= self.MLD_params["output"],
                               output_dir=self.MLD_params["output_dir"])
    
    def run_diagnostics(self):
        self.process_data()
        self.plot_profile()