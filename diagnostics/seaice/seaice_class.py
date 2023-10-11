"""Sea ice diagnostics"""

import matplotlib.pyplot as plt
import xarray as xr
from aqua import Reader, util
from aqua.util import load_yaml, create_folder
from aqua.logger import log_configure
import os

class SeaIceExtent:
    """Sea ice extent class"""

    def __init__(self, config_file, loglevel: str = 'ERROR', threshold=0.15,
            regions_definition_file=None):
        """
        The SeaIceExtent constructor.

        Args:
            config_file (str):  Path to the YAML configuration file

            loglevel (str):     The log level
                                Default: WARNING
            threshold (float):  The sea ice extent threshold
                                Default: 0.15
            regions_definition_file (str):      The path to the file that specifies the regions boundaries
                                Default: ./regions_definition.yml

        Returns:
            A SeaIceExtent object.

        """
        # Configure logger
        self.loglevel = loglevel
        self.logger = log_configure(self.loglevel, 'Seaice')
        if regions_definition_file is None:
            regions_definition_file = os.path.dirname(os.path.abspath(__file__)) + "/regions_definition.yml"

        self.regionDict = load_yaml(regions_definition_file)
        self.thresholdSeaIceExtent = threshold

        self.logger.debug("Reading configuration file %s", config_file)
        self.config = load_yaml(config_file)
        self.logger.warning("CONFIG:" + str(self.config))

        self.outputdir = self.config['output_directory']
        print(";;;;;;;;=========,,,,,,,,,")
        print(self.outputdir)

    def run(self, **kwargs):
        """
        The run diagnostic method.

        kwargs:
            myConfig
                      A config specifying data to plot and regions 

            The method produces as output a figure with the seasonal cycles
            of sea ice extent in the regions for the setups and a netcdf file
            containing the time series of sea ice extent in the regions for
            each setup.
        """
        self.computeExtent()
        self.plotExtent()
        self.createNetCDF()

    def computeExtent(self):
        """
        Method which computes the seaice extent.
        """
        # Convert the config yaml object to "setup" variable
        nModels = len(self.config['models'])
        self.outputdir = self.config['output_directory']
        self.mySetups = [[self.config['models'][jModels]['name'], self.config['models'][jModels]['experiment'], self.config['models'][jModels]['source']] for jModels in range(nModels)]

        self.myRegions = self.config['regions']
        self.nRegions = len(self.myRegions)

        # Instantiate the various readers (one per setup) and retrieve the
        # corresponding data
        self.myExtents = list()
        for _, setup in enumerate(self.mySetups):
            model, exp, source = setup[0], setup[1], setup[2]

            # Instantiate reader
            reader = Reader(model=model, exp=exp, source=source)

            self.logger.info("\t".join([s.ljust(20) for s in setup]))
            data = reader.retrieve()

            if model == "OSI-SAF":
                data = data.rename({"siconc": "ci"})

            areacello = reader.grid_area
            lat = data.coords["lat"]
            lon = data.coords["lon"]

            # Important: recenter the lon in the conventional 0-360 range
            lon = (lon + 360) % 360
            lon.attrs["units"] = "degrees"

            # Create mask based on threshold
            ci_mask = data.ci.where((data.ci > self.thresholdSeaIceExtent) &
                                    (data.ci < 1.0))

            self.regionExtents = list()  # Will contain the time series
            # for each region and for that setup
            # Iterate over regions
            for jr, region in enumerate(self.myRegions):
                self.logger.info("\tProducing diagnostic for region %s", region)
                # Create regional mask
                try:
                    latS, latN, lonW, lonE = (
                        
                        self.regionDict[region]["latS"],
                        self.regionDict[region]["latN"],
                        self.regionDict[region]["lonW"],
                        self.regionDict[region]["lonE"],
                    )
                except KeyError:
                    self.logger.info("Error: region not defined")
                    print("Region " + region + " does not exist in regions_definition.yml")
                    exit(1)

                # Dealing with regions straddling the 180° meridian
                if lonW > lonE:
                    regionMask = (
                        (lat >= latS)
                        & (lat <= latN)
                        & ((lon >= lonW) | (lon <= lonE))
                    )
                else:
                    regionMask = (
                        (lat >= latS)
                        & (lat <= latN)
                        & (lon >= lonW)
                        & (lon <= lonE)
                    )

                # Print area of region

                if source == "lra-r100-monthly" or model == "OSI-SAF":
                    if source == "lra-r100-monthly":
                        dim1Name, dim2Name = "lon", "lat"
                    elif model == "OSI-SAF":
                        dim1Name, dim2Name = "xc", "yc"
                    myExtent = areacello.where(regionMask).where(
                        ci_mask.notnull()).sum(dim=[dim1Name, dim2Name]) / 1e12
                else:
                    myExtent = areacello.where(regionMask).where(
                        ci_mask.notnull()).sum(dim="value") / 1e12

                myExtent.attrs["units"] = "million km^2"
                myExtent.attrs["long_name"] = "Sea ice extent"
                self.regionExtents.append(myExtent)

            # Save set of diagnostics for that setup
            self.myExtents.append(self.regionExtents)

    def plotExtent(self):
        """
        Method to produce figures plotting seaice extent.
        """

        fig, ax = plt.subplots(self.nRegions, figsize=(13, 3 * self.nRegions))

        for jr, region in enumerate(self.myRegions):
            for js, setup in enumerate(self.mySetups):
                label = " ".join([s for s in setup])
                extent = self.myExtents[js][jr]

                # Don't plot osisaf nh in the south and conversely
                if (setup[0] == "OSI-SAF" and setup[2][:2] == "nh" and
                    self.regionDict[region]["latN"] < 20.0) or (
                        setup[0] == "OSI-SAF" and setup[2][:2] == "sh"
                        and self.regionDict[region]["latS"] > -20.0):
                    pass
                else:
                    ax[jr].plot(extent.time, extent, label=label)

            ax[jr].set_title("Sea ice extent: region " + region)

            ax[jr].legend(fontsize=8, ncols=6, loc="best")
            ax[jr].set_ylabel(extent.units)
            ax[jr].grid()

        fig.tight_layout()
        for fmt in ["png", "pdf"]:
            outputdir = self.outputdir + "./PDF/" + str(fmt) + "/"
            create_folder(outputdir, loglevel=self.loglevel)
            figName = "SeaIceExtent_" + "all_models" + "." + fmt
            fig.savefig(outputdir + "/" + figName, dpi=300)

    def createNetCDF(self):
        """
        Method to create NetCDF files.
        """

        # NetCDF creation (one per setup)
        for js, setup in enumerate(self.mySetups):
            dataset = xr.Dataset()
            for jr, region in enumerate(self.myRegions):

                if (setup[0] == "OSI-SAF" and setup[2][:2] == "nh" and
                    self.regionDict[region]["latN"] < 20.0) or (
                        setup[0] == "OSI-SAF" and setup[2][:2] == "sh"
                        and self.regionDict[region]["latS"] > -20.0):
                    pass
                else:
                    # NetCDF variable
                    varName = f"{setup[0]}_{setup[1]}_{setup[2]}_{region.replace(' ', '')}"
                    dataset[varName] = self.myExtents[js][jr]

                    outputdir = self.outputdir
                    create_folder(outputdir, loglevel=self.loglevel)

                    dataset.to_netcdf(outputdir + "/" + "seaIceExtent_" +
                                      "_".join([s for s in setup]) + ".nc")
