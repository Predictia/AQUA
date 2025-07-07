import matplotlib.pyplot as plt
import os
import xarray as xr
from aqua.logger import log_configure, log_history
from aqua.util import create_folder, add_pdf_metadata, add_png_metadata, update_metadata


class OutputSaver:
    """
    Class to manage saving outputs, including NetCDF, PDF, and PNG files, with
    customized naming based on provided parameters and metadata.
    """

    def __init__(self, diagnostic: str,
                 catalog: str = None, model: str = None, exp: str = None, realization: str = None,
                 catalog_ref: str = None, model_ref: str = None, exp_ref: str = None,
                 outdir: str = '.', loglevel: str = 'WARNING'):
        """
        Initialize the OutputSaver with diagnostic parameters and output directory.
        All the catalog, model, and experiment can be both a string or a list of strings.

        Args:
            diagnostic (str): Name of the diagnostic.
            catalog (str, optional): Catalog name.
            model (str, optional): Model name.
            exp (str, optional): Experiment name.
            realization (str, optional): Realization name, can be a string or a integer. 
                                         'r' is appended if it is an integer.
            catalog_ref (str, optional): Reference catalog name.
            model_ref (str, optional): Reference model name.
            exp_ref (str, optional): Reference experiment name.
            outdir (str, optional): Output directory. Defaults to current directory.
            loglevel (str, optional): Logging level. Defaults to 'WARNING'.
        """

        self.diagnostic = diagnostic
        self.catalog = catalog
        self.model = model
        self.exp = exp
        self.realization = self._format_realization(realization) if realization else None
        self._verify_arguments(['model', 'exp', 'realization'])

        self.catalog_ref = catalog_ref
        self.model_ref = model_ref
        self.exp_ref = exp_ref
        self._verify_arguments(['model_ref', 'exp_ref', 'catalog_ref'])

        self.outdir = outdir
        self.loglevel = loglevel
        self.logger = log_configure(log_level=self.loglevel, log_name='OutputSaver')

    @staticmethod
    def _format_realization(realization: str) -> str:
        """
        Format the realization string by prepending 'r' if it is a digit.

        Args:
            realization (str): The realization string.

        Returns:
            str: Formatted realization string.
        """
        return f'r{realization}' if realization.isdigit() else realization

    def _verify_arguments(self, attr_names):
        """
        Verify that the given attributes on obj are lists of the same length.

        Args:
            obj: The object to inspect.
            attr_names (list of str): Names of attributes to verify.

        Raises:
            ValueError if attributes are not all lists or lengths differ.
        """
        values = [getattr(self, name, None) for name in attr_names]

        # all strings, no problem
        if all(isinstance(value, (str, type(None))) for value in values):
            return True

        # all list, verify lengths
        if all(isinstance(value, (list, type(None))) for value in values):
            first_len = len(values[0])
            if all(len(item) == first_len for item in values if item is not None):
                return True
            raise ValueError(f"Attributes {attr_names} are lists of different lengths.")
            
        #mixed case, does not work
        raise ValueError(f"Attributes {attr_names} must be either all strings or all lists of the same length.")

    def generate_name(self, diagnostic_product: str, extra_keys: dict = None) -> str:
        """
        Generate a filename based on provided parameters and additional user-defined keywords

        Args:
            diagnostic_product (str, optional): Product of the diagnostic analysis.
            extra_keys (dict, optional): Dictionary of additional keys to include in the filename.

        Returns:
            str: A string representing the generated filename.
        """

        if not self.catalog or not self.model or not self.exp:
            raise ValueError("Catalog, model, and exp must be specified to generate a filename.")

        # handle multimodel case: we need to check if the 6 keys above are lists
        if isinstance(self.model, list):
            model_value = "multimodel" if len(self.model) > 1 else self.model[0]
            if isinstance(self.catalog, list):
                catalog_value = None if len(self.catalog) > 1 else self.catalog[0]
            if isinstance(self.exp, list):
                exp_value = None if len(self.exp) > 1 else self.exp[0]
        else:
            model_value = self.model
            catalog_value = self.catalog
            exp_value = self.exp

        # handle multiref case
        if isinstance(self.model_ref, list) and len(self.model_ref) > 0:
            model_ref_value = "multiref" if len(self.model_ref) > 1 else self.model_ref[0]
            if isinstance(self.catalog_ref, list):
                catalog_ref_value = None if len(self.catalog_ref) > 1 else self.catalog_ref[0]
            if isinstance(self.exp_ref, list):
                exp_ref_value = None if len(self.exp_ref) > 1 else self.exp_ref[0]
        elif isinstance(self.model_ref, list) and len(self.model_ref) == 0:
            model_ref_value = None
            catalog_ref_value = None
            exp_ref_value = None
        else:
            model_ref_value = self.model_ref
            catalog_ref_value = self.catalog_ref
            exp_ref_value = self.exp_ref

        parts_dict = {
            'diagnostic': self.diagnostic,
            'diagnostic_product': diagnostic_product,
            'catalog': catalog_value if model_value != "multimodel" else None,
            'model': model_value,
            'exp': exp_value if model_value != "multimodel" else None,
            'catalog_ref': catalog_ref_value if model_ref_value != "multiref" else None,
            'model_ref': model_ref_value,
            'exp_ref': exp_ref_value if model_ref_value != "multiref" else None,
        }

        # Add additional filename keys if provided
        if extra_keys:
            parts_dict.update(extra_keys)

        # Remove None values
        parts = [str(value) for value in parts_dict.values() if value is not None]

        # Join all parts
        filename = '.'.join(parts)

        self.logger.debug("Generated filename: %s", filename)
        return filename

    def save_netcdf(self, dataset: xr.Dataset, diagnostic_product: str, rebuild: bool = True, extra_keys: dict = None, metadata: dict = None):
        """
        Save an xarray Dataset as a NetCDF file with a generated filename.

        Args:
            dataset (xr.Dataset): The xarray Dataset to save.
            diagnostic_product (str): Product of the diagnostic analysis.
            rebuild (bool, optional): Whether to rebuild the output file if it already exists. Defaults to True.
            extra_keys (dict, optional): Dictionary of additional keys to include in the filename.
            metadata (dict, optional): Additional metadata to include in the NetCDF file.
        """
        filename = self.generate_name(diagnostic_product=diagnostic_product, extra_keys=extra_keys) + '.nc'

        folder = os.path.join(self.outdir, 'netcdf')
        create_folder(folder=str(folder), loglevel=self.loglevel)
        filepath = os.path.join(folder, filename)

        if not rebuild and os.path.exists(filepath):
            self.logger.info("File already exists and rebuild=False, skipping: %s", filepath)
            return filepath

        metadata = self.create_metadata(
            diagnostic_product=diagnostic_product, 
            extra_keys=extra_keys, metadata=metadata)
       
        # If metadata contains a history attribute, log the history
        if 'history' in metadata:
            log_history(data=dataset, msg=metadata['history'])
            # Remove the history attribute from the metadata dictionary
            metadata.pop('history')

        dataset.attrs.update(metadata)
        
        dataset.to_netcdf(filepath)

        self.logger.info("Saved NetCDF %s", filepath)
        return filepath
    
    def _save_figure(self, fig: plt.Figure, diagnostic_product: str, file_format: str,
                 rebuild: bool = True, extra_keys: dict = None, metadata: dict = None,
                 dpi: int = None):
        """
        Internal method to save a Matplotlib figure with common logic for PDF and PNG.

        Args:
            fig (plt.Figure): The Matplotlib figure to save.
            diagnostic_product (str): Product of the diagnostic analysis.
            file_format (str): 'pdf' or 'png'.
            rebuild (bool): Whether to overwrite existing files.
            extra_keys (dict): Extra keys for filename generation.
            metadata (dict): Metadata to embed.
            dpi (int): DPI setting for raster formats like PNG.
        """
        if file_format not in ['pdf', 'png']:
            raise ValueError("file_format must be either 'pdf' or 'png'.")
        
        filename = self.generate_name(
            diagnostic_product=diagnostic_product, extra_keys=extra_keys
            ) + f'.{file_format}'
        folder = os.path.join(self.outdir, file_format)
        create_folder(folder=str(folder), loglevel=self.loglevel)
        filepath = os.path.join(folder, filename)

        if not rebuild and os.path.exists(filepath):
            self.logger.info("File already exists and rebuild=False, skipping: %s", filepath)
            return filepath

        save_kwargs = {'format': file_format, 'bbox_inches': 'tight'}
        if file_format == 'png' and dpi is not None:
            save_kwargs['dpi'] = dpi

        fig.savefig(filepath, **save_kwargs)

        metadata = self.create_metadata(
            diagnostic_product=diagnostic_product, 
            extra_keys=extra_keys, metadata=metadata)

        if file_format == 'pdf':
            add_pdf_metadata(filepath, metadata, loglevel=self.loglevel)
        elif file_format == 'png':
            add_png_metadata(filepath, metadata, loglevel=self.loglevel)

        self.logger.info("Saved %s: %s", file_format.upper(), filepath)
        return filepath
    
    def save_pdf(self, fig: plt.Figure, diagnostic_product: str, rebuild: bool = True,
             extra_keys: dict = None, metadata: dict = None):
        """
        Save a Matplotlib figure as a PDF.
        """
        return self._save_figure(fig, diagnostic_product, 'pdf', rebuild, extra_keys, metadata)

    def save_png(self, fig: plt.Figure, diagnostic_product: str, rebuild: bool = True,
                extra_keys: dict = None, metadata: dict = None, dpi: int = 300):
        """
        Save a Matplotlib figure as a PNG.
        """
        return self._save_figure(fig, diagnostic_product, 'png', rebuild, extra_keys, metadata, dpi)


    def create_metadata(self, diagnostic_product: str, extra_keys: dict = None, metadata: dict = None) -> dict:
        """
        Create metadata dictionary for a plot or output file.

        Args:
            diagnostic_product (str): Product of the diagnostic analysis.
            extra_keys (dict, optional): Dictionary of additional keys to include in the filename.
            metadata (dict, optional): Additional metadata to include in the PNG file.
        """
        base_metadata = {
            'diagnostic': self.diagnostic,
            'diagnostic_product': diagnostic_product,
            'catalog': self.catalog,
            'model': self.model,
            'exp': self.exp,
            'catalog_ref': self.catalog_ref,
            'model_ref': self.model_ref,
            'exp_ref': self.exp_ref
        }

        # Remove None values
        base_metadata = {k: v for k, v in base_metadata.items() if v is not None}

        # Process extra keys safely
        if extra_keys:
            # Filter out None values
            filtered_keys = {k: v for k, v in extra_keys.items() if v is not None}

            processed_extra_keys = {
                key: ",".join(map(str, value)) if isinstance(value, list) else str(value)
                for key, value in extra_keys.items()
            }
            base_metadata.update(processed_extra_keys)

        # Merge with provided metadata
        metadata = update_metadata(base_metadata, metadata)
        return metadata
