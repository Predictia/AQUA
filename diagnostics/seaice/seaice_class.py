from aqua import catalogue, reader

"""Sea ice diagnostics """

class SeaIceExtent():
    """Sea ice extent class"""
    def __init__(self, option=None, configdir=None):
        """The SeaIceExtent constructor."""

        self.option = option
        self.configdir = configdir

    def run(self):
        """The run method."""
        
        cat = catalogue(configdir=self.configdir)
        print(cat)

        # Experiment definition 
        # ---------------------
        model  = "FESOM"
        exp    = "tco2559-ng5"
        source = "original_2d"
        regrid = "r025"
        var    = "a_ice"

        year1 = 2020
        year2 = 2020

        reader = Reader(model   = model,
                        exp     = exp,
                        source  = source,
                        regrid  = regrid,
                        )
        print(reader)

        data = reader.retrieve(fix = True)
        data

        mesh = xr.open_dataset('/work/bm1235/a270046/meshes/NG5_griddes_nodes_IFS.nc')
        area = (mesh.cell_area * data.ci).sum(dim='nod2')
        area_comp = area.compute()
        area_comp.plot()
