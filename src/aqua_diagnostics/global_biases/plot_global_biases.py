import pandas as pd
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from aqua.logger import log_configure
from aqua.util import ConfigPath, OutputSaver
from aqua.util import create_folder, select_season
from aqua.util import evaluate_colorbar_limits, ticks_round
from aqua.graphics import plot_single_map, plot_single_map_diff, plot_maps
from .util import select_pressure_level


class PlotGlobalBiases: 
    def __init__(self,
                 save_pdf=True, 
                 save_png=True, dpi=300, outdir='./',
                 loglevel='WARNING'):
        """
        Initialize the PlotGlobalBiases class
        """
        self.save_pdf = save_pdf
        self.save_png = save_png
        self.dpi = dpi
        self.outdir = outdir
        self.loglevel = loglevel

        self.logger = log_configure(log_level=loglevel, log_name='Global Biases')


    def _handle_pressure_level(self, data, var, plev):
        """
        Handles pressure level selection for the given variable.

        Args:
            data (xarray.Dataset): Input dataset.
            var (str): Name of the variable.
            plev (float, optional): Pressure level to select.

        Returns:
            xarray.Dataset: Dataset with pressure level selected if applicable.
        """
        if 'plev' in data.dims:
            if plev is None:
                self.logger.warning(
                    f"Variable {var} has multiple pressure levels, but no specific level was selected. "
                    "Skipping 2D plotting."
                )
                return None
            self.logger.info(f"Selecting pressure level {plev} for variable {var}.")
            return select_pressure_level(data, plev, var)

        elif plev is not None:
            self.logger.warning(f"Variable {var} does not have pressure levels!")

        return data



    def plot_climatology(self, data, var, plev=None, vmin=None, vmax=None):
        """
        Plots the climatology map for a given variable and time range.

        Args:
            data (xarray.Dataset): Climatology dataset to plot.
            var (str, optional): Variable name. If None, uses self.var.
            plev (float, optional): Pressure level to plot (if applicable).
            vmin (float, optional): Minimum color scale value.
            vmax (float, optional): Maximum color scale value.

        Returns:
            tuple: Matplotlib figure and axis objects.
        """
        self.logger.info('Plotting climatology.')
        
        data = self._handle_pressure_level(data, var, plev)
        if data is None:
            return None  # Nothing to plot

        title = (f"{var} map {data.model} {data.exp} {data.startdate}/{data.enddate}" 
                + (f" at {int(plev / 100)} hPa" if plev else ""))

        fig, ax = plot_single_map(
            data[var],
            return_fig=True,
            title=title,
            vmin=vmin,
            vmax=vmax
        )
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        return fig, ax


    def plot_bias(self, data, data_ref, var, plev=None, vmin=None, vmax=None ):

        self.logger.info('Plotting global biases.')

        data = self._handle_pressure_level(data, var, plev)
        data_ref = self._handle_pressure_level(data_ref, var, plev)

      #  if data or data_ref is None:
       #     return None  # Nothing to plot
        
        self.logger.info('Plotting bias map between two datasets.')

        # Set 'sym' to True if either 'vmin' or 'vmax' is None, indicating a symmetric colorbar.
        sym = vmin is None or vmax is None

        title = (f"{var} global bias of {data.model} {data.exp}\n"
                f"relative to {data_ref.model} climatology"
                + (f" at {int(plev / 100)} hPa" if plev else ""))

        fig, ax = plot_single_map_diff(data=data[var], 
                                    data_ref=data_ref[var],
                                    return_fig=True,
                                    contour=True, 
                                    title=title,
                                    sym=sym,
                                    vmin_fill=vmin, vmax_fill=vmax)
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")

        description = (
                f"Spatial map of the total bias of the variable {var} from {data.startdate} to {data.enddate} "
                f"for the {data.model} model, experiment {data.exp}, with {data_ref.model} used as reference data. "
        )
        metadata = {"Description": description}

        output_saver = OutputSaver(diagnostic='global_biases', model=data.model, exp=data.exp, loglevel=self.loglevel,
                    default_path=self.outdir)

        if self.save_pdf: output_saver.save_pdf(fig=fig, diagnostic_product='total_bias_map', path=self.outdir, metadata=metadata)
        if self.save_png: output_saver.save_png(fig=fig, diagnostic_product='total_bias_map', path=self.outdir, metadata=metadata)


    def plot_seasonal_bias(self, data, data_ref, var, plev=None, vmin=None, vmax=None):
            """
            Plots seasonal biases for each season (DJF, MAM, JJA, SON) and returns an xarray.Dataset
            containing the calculated seasonal biases.

            Args:
                seasons_stat (str): Statistic for seasonal analysis ('mean' by default).
                vmin (float, optional): Minimum colorbar value.
                vmax (float, optional): Maximum colorbar value.

            Returns:
                tuple: Matplotlib figure
            """

            self.logger.info('Plotting seasonal biases.')

            data = self._handle_pressure_level(data, var, plev)
            data_ref = self._handle_pressure_level(data_ref, var, plev)

            # Prepare seasonal data and compute biases
            season_list = ['DJF', 'MAM', 'JJA', 'SON']
            
            # Set 'sym' to True if either 'vmin' or 'vmax' is None, indicating a symmetric colorbar.
            sym = vmin is None or vmax is None
            # Plot seasonal biases
            plot_kwargs = {
                'maps': [data[var].sel(season=season) - data_ref[var].sel(season=season) for season in season_list],
                'return_fig': True,
                'titles': season_list,
                'contour': True,
                'sym': sym
            }
 
            if vmin is not None:
                plot_kwargs['vmin'] = vmin
            if vmax is not None:
                plot_kwargs['vmax'] = vmax

            fig = plot_maps(**plot_kwargs)
            
            description = (
                        f"Seasonal bias map of the variable {var} for the {data.model} model, experiment {data.exp}"
                        f", using {data_ref.model} as reference data. "
                        f"The bias is computed for each season over the period from {data.startdate} to {data.enddate}"
                    )
            metadata = {"Description": description}

            output_saver = OutputSaver(diagnostic='global_biases', model=data.model, exp=data.exp, loglevel=self.loglevel,
                        default_path=self.outdir)

            if self.save_pdf: output_saver.save_pdf(fig=fig, diagnostic_product='seasonal_bias_map', path=self.outdir, metadata=metadata)
            if self.save_png: output_saver.save_png(fig=fig, diagnostic_product='seasonal_bias_map', path=self.outdir, metadata=metadata)



    def plot_vertical_bias(self, data, data_ref, var, plev_min=None, plev_max=None, vmin=None, vmax=None, nlevels=18):
        """
        Calculates and plots the vertical bias between two datasets.

        Args:
            data (xarray.Dataset): Dataset to analyze.
            data_ref (xarray.Dataset): Reference dataset for comparison.
            var (str, optional): Variable name to analyze.
            plev_min (float, optional): Minimum pressure level.
            plev_max (float, optional): Maximum pressure level.
            vmin (float, optional): Minimum colorbar value.
            vmax (float, optional): Maximum colorbar value.
            nlevels (int, optional): Number of contour levels for the plot.
        """

        self.logger.info('Plotting vertical biases for variable: %s', var)

        # Calculate the bias between the two datasets
        self.logger.debug("Computing bias between input and reference datasets.")
        bias = data[var] - data_ref[var]

        # Determine pressure level bounds if not provided
        if plev_min is None:
            plev_min = bias['plev'].min().item()
        if plev_max is None:
            plev_max = bias['plev'].max().item()

        self.logger.debug("Selected pressure level range: %.2f - %.2f", plev_min, plev_max)

        # Slice pressure levels in decreasing order (assuming pressure decreases with height)
        bias = bias.sel(plev=slice(plev_max, plev_min))

        # Ensure reasonable number of levels
        nlevels = max(2, int(nlevels))

        # Calculate the zonal mean bias
        self.logger.debug("Computing zonal mean bias.")
        zonal_bias = bias.mean(dim='lon')

        # Determine colorbar limits if not provided
        if vmin is None or vmax is None:
            self.logger.debug("Determining colorbar limits from data.")
            vmin, vmax = float(zonal_bias.min()), float(zonal_bias.max())
            if vmin * vmax < 0:
                vmax = max(abs(vmin), abs(vmax))
                vmin = -vmax

        levels = np.linspace(vmin, vmax, nlevels)

        title = (
            f"{var} vertical bias of {data.model} {dat
