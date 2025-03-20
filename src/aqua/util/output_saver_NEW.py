import matplotlib.pyplot as plt
import os
import xarray as xr
from aqua.logger import log_configure, log_history
from aqua.util import add_pdf_metadata, add_png_metadata, update_metadata



class OutputSaver_NEW:
    """
    Class to manage saving outputs, including NetCDF, PDF, and PNG files, with
    customized naming based on provided parameters and metadata.
    """

    def __init__(self, diagnostic: str, model: str, exp: str, catalog: str = None,
                 outdir: str = '.', rebuild: bool = True, loglevel: str = 'WARNING',):
                 
        self.diagnostic = diagnostic
        self.catalog = catalog  #MANDATORY OR NOT?
        self.model = model
        self.exp = exp
        self.outdir = outdir
        self.rebuild = rebuild

        self.log_level = loglevel
        self.logger = log_configure(log_level=self.log_level, log_name='OutputSaver')

    def generate_name(self, diagnostic_product: str, var: str, 
                  extra_keys: dict = None) -> str:
        """
        Generate a filename based on provided parameters and additional user-defined keywords,
        including precise time intervals.

        Args:
            diagnostic_product (str, optional): Product of the diagnostic analysis.
            var (str, optional): Variable of interest.
            extra_keys (dict, optional): Dictionary of additional keys to include in the filename.

        Returns:
            str: A string representing the generated filename.
        """
        
        parts_dict = {
            'diagnostic': self.diagnostic,
            'diagnostic_product': diagnostic_product,
            'catalog': self.catalog,
            'model': self.model,
            'exp': self.exp,
            'var': var
        }
        
        # Add additional filename keys if provided
        if extra_keys:
            parts_dict.update(extra_keys)
        
        # Remove None values
        parts = [str(value) for value in parts_dict.values() if value is not None]
        
        # Join all parts with underscores
        filename = '.'.join(parts)
        
        self.logger.debug(f"Generated filename: {filename}")
        return filename


    def save_pdf(self, fig: plt.Figure, diagnostic_product: str, var: str, extra_keys: dict = None):
        """
        Save a Matplotlib figure as a PDF file with a generated filename.

        Args:
            fig (plt.Figure): The Matplotlib figure to save.
            diagnostic_product (str): Product of the diagnostic analysis.
            var (str): Variable of interest.
            extra_keys (dict, optional): Dictionary of additional keys to include in the filename.
        """
        filename = self.generate_name(diagnostic_product, var, extra_keys) + '.pdf'
        filepath = os.path.join(self.outdir, filename)
        
        fig.savefig(filepath, format='pdf', bbox_inches='tight')
        self.logger.info(f"Saved PDF: {filepath}")


    def save_png(self, fig: plt.Figure, diagnostic_product: str, var: str, extra_keys: dict = None):
        """
        Save a Matplotlib figure as a PNG file with a generated filename.

        Args:
            fig (plt.Figure): The Matplotlib figure to save.
            diagnostic_product (str): Product of the diagnostic analysis.
            var (str): Variable of interest.
            extra_keys (dict, optional): Dictionary of additional keys to include in the filename.
        """
        filename = self.generate_name(diagnostic_product, var, extra_keys) + '.png'
        filepath = os.path.join(self.outdir, filename)
        
        fig.savefig(filepath, format='png', dpi=300, bbox_inches='tight')
        self.logger.info(f"Saved PNG: {filepath}")

    
    def save_netcdf(self, dataset: xr.Dataset, diagnostic_product: str, var: str, extra_keys: dict = None):
        """
        Save an xarray Dataset as a NetCDF file with a generated filename.

        Args:
            dataset (xr.Dataset): The xarray Dataset to save.
            diagnostic_product (str): Product of the diagnostic analysis.
            var (str): Variable of interest.
            extra_keys (dict, optional): Dictionary of additional keys to include in the filename.
        """
        filename = self.generate_name(diagnostic_product, var, extra_keys) + '.nc'
        filepath = os.path.join(self.outdir, filename)
        
        dataset.to_netcdf(filepath)
        self.logger.info(f"Saved NetCDF: {filepath}")
