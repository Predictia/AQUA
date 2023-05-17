from aqua import Reader, catalogue, inspect_catalogue
from seaice_commondiags import *
import xarray as xr
from dask.distributed import Client
import dask
import matplotlib.pyplot as plt

class DataAnalyzer:
    def __init__(self):
        self.cat = catalogue()
        self.mesh = xr.open_dataset('/work/bm1235/a270046/meshes/NG5_griddes_nodes_IFS.nc')
        self.client = Client(n_workers=20, threads_per_worker=1, memory_limit='4GB')

    def inspect_catalog(self):
        inspect_catalogue(self.cat)

    def retrieve_data(self):
        reader = Reader(model="FESOM",
                        exp="tco2559-ng5",
                        source="original_2d",
                        regrid="r025",
                        var="a_ice")
        data = reader.retrieve(fix=True)
        return data

    def compute_area(self, data):
        area = (self.mesh.cell_area * data.ci).sum(dim='nod2')
        area_comp = area.compute()
        return area_comp

    def plot_area(self, area_comp):
        area_comp.plot()
        plt.show()

# Create an instance of DataAnalyzer class
analyzer = DataAnalyzer()

# Inspect the catalogue
analyzer.inspect_catalog()

# Retrieve the data
data = analyzer.retrieve_data()

# Compute the area
area_comp = analyzer.compute_area(data)

# Plot the area
analyzer.plot_area(area_comp)
