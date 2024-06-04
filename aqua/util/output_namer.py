from aqua.logger import log_configure, log_history
from aqua.util import add_pdf_metadata, add_png_metadata, update_metadata_with_date
import os
import xarray as xr
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class OutputNamer:
    def __init__(self, diagnostic: str, model: str, exp: str, diagnostic_product: str = None, loglevel: str = 'WARNING',
                 default_path: str = '.', rebuild: bool = True):
        """
        Initialize the OutputNamer class to manage output file naming.

        Args:
            diagnostic (str): Name of the diagnostic.
            model (str): Model used in the diagnostic.
            exp (str): Experiment identifier.
            diagnostic_product (str, optional): Product of the diagnostic analysis.
            loglevel (str, optional): Log level for the class's logger.
            default_path (str, optional): Default path where files will be saved.
            rebuild (bool, optional): If True, overwrite the existing files. If False, do not overwrite. Default is True.
        """
        self.diagnostic = diagnostic
        self.model = model
        self.exp = exp
        self.diagnostic_product = diagnostic_product
        self.loglevel = loglevel
        self.default_path = default_path
        self.rebuild = rebuild
        self.logger = log_configure(log_level=self.loglevel, log_name='OutputNamer')

    def update_diagnostic_product(self, diagnostic_product: str):
        """
        Update the diagnostic product for the instance.

        Args:
            diagnostic_product (str): The new diagnostic product to be used.
        """
        if diagnostic_product is not None:
            self.diagnostic_product = diagnostic_product

    def generate_name(self, diagnostic_product: str = None, var: str = None, model_2: str = None, exp_2: str = None,
                      time_start: str = None, time_end: str = None, time_precision: str = 'ymd', area: str = None,
                      suffix: str = 'nc', **kwargs) -> str:
        """
        Generate a filename based on provided parameters and additional user-defined keywords,
        including precise time intervals.

        Args:
            diagnostic_product (str, optional): Product of the diagnostic analysis.
            var (str, optional): Variable of interest.
            model_2 (str, optional): The second model, for comparative studies.
            exp_2 (str, optional): The experiment associated with the second model.
            time_start (str, optional): The start time for the data, in format consistent with time_precision.
            time_end (str, optional): The finish (end) time for the data, in format consistent with time_precision.
            time_precision (str, optional): Precision for time representation ('y', 'ym', 'ymd', 'ymdh', etc.).
            area (str, optional): The geographical area covered by the data.
            suffix (str, optional): The file extension/suffix indicating file type.
            **kwargs: Arbitrary keyword arguments provided by the user for additional customization.

        Returns:
            str: A string representing the generated filename.

        Raises:
            ValueError: If diagnostic_product is not provided.
        """
        self.update_diagnostic_product(diagnostic_product)

        if not self.diagnostic_product:
            msg = "diagnostic_product is required."
            raise ValueError(msg)

        # Handle time formatting based on the specified precision
        time_parts = []
        if time_start and time_end:
            if time_precision == 'y':
                time_parts = [time_start[:4], time_end[:4]]
            elif time_precision == 'ym':
                time_parts = [time_start[:7].replace('-', ''), time_end[:7].replace('-', '')]
            elif time_precision == 'ymd':
                time_parts = [time_start.replace('-', ''), time_end.replace('-', '')]

        additional_parts = [f"{key}_{value}" for key, value in sorted(kwargs.items())]

        parts = [part for part in [self.diagnostic, self.diagnostic_product, var,
                                   self.model, self.exp, model_2, exp_2, area] if part]
        parts.extend(time_parts)
        parts.extend(additional_parts)
        parts.append(suffix)

        filename = '.'.join(parts)
        self.logger.debug(f"Generated filename: {filename}")
        return filename

    def save_netcdf(self, dataset: xr.Dataset, path: str = None, diagnostic_product: str = None, var: str = None,
                    model_2: str = None, exp_2: str = None, time_start: str = None, time_end: str = None,
                    time_precision: str = 'ymd', area: str = None, metadata: dict = None, **kwargs) -> str:
        """
        Save a netCDF file with a dataset to a specified path, with support for additional filename keywords and
        precise time intervals.

        Args:
            dataset (xr.Dataset): The xarray dataset to be saved as a netCDF file.
            path (str, optional): The absolute path where the netCDF file will be saved.
            diagnostic_product (str, optional): Product of the diagnostic analysis.
            var (str, optional): Variable of interest.
            model_2 (str, optional): The second model, for comparative studies.
            exp_2 (str, optional): The experiment associated with the second model.
            time_start (str, optional): The start time for the data, in format consistent with time_precision.
            time_end (str, optional): The finish (end) time for the data, in format consistent with time_precision.
            time_precision (str, optional): Precision for time representation ('y', 'ym', 'ymd', 'ymdh', etc.).
            area (str, optional): The geographical area covered by the data.
            metadata (dict, optional): Additional metadata to include in the netCDF file.
            **kwargs: Additional keyword arguments for more flexible filename customization.

        Returns:
            str: The absolute path where the netCDF file has been saved.
        """
        filename = self.generate_name(diagnostic_product=diagnostic_product, var=var,
                                      model_2=model_2, exp_2=exp_2, time_start=time_start, time_end=time_end,
                                      time_precision=time_precision, area=area, suffix='nc', **kwargs)

        if path is None:
            path = self.default_path
        full_path = os.path.join(path, filename)

        if not self.rebuild and os.path.exists(full_path):
            self.logger.info(f"File already exists and rebuild is set to False: {full_path}")
            return full_path

        # Add metadata if provided, including the current time
        metadata = update_metadata_with_date(metadata)

        # If metadata contains a history attribute, log the history
        if 'history' in metadata:
            log_history(data=dataset, msg=metadata['history'])
            # Remove the history attribute from the metadata dictionary
            metadata.pop('history')

        dataset.attrs.update(metadata)
        self.logger.debug(f"Metadata added: {metadata}")

        # Save the dataset to the specified path
        dataset.to_netcdf(full_path, mode='w')

        self.logger.info(f"Saved netCDF file to path: {full_path}")
        return full_path

    def save_pdf(self, fig: Figure, path: str = None, diagnostic_product: str = None, var: str = None,
                 model_2: str = None, exp_2: str = None, time_start: str = None, time_end: str = None,
                 time_precision: str = 'ymd', area: str = None, metadata: dict = None, dpi: int = 300, **kwargs) -> str:
        """
        Save a PDF file with a matplotlib figure to the provided path, with support for additional filename keywords and
        precise time intervals.

        Args:
            fig (Figure): The matplotlib figure object to be saved as a PDF.
            path (str, optional): The path where the PDF file will be saved.
            diagnostic_product (str, optional): Product of the diagnostic analysis.
            var (str, optional): Variable of interest.
            model_2 (str, optional): The second model, for comparative studies.
            exp_2 (str, optional): The experiment associated with the second model.
            time_start (str, optional): The start time for the data, in format consistent with time_precision.
            time_end (str, optional): The finish (end) time for the data, in format consistent with time_precision.
            time_precision (str, optional): Precision for time representation ('y', 'ym', 'ymd', 'ymdh', etc.).
            area (str, optional): The geographical area covered by the data.
            metadata (dict, optional): Additional metadata to include in the PDF file.
            dpi (int, optional): The resolution of the saved PDF file. Default is 300.
            **kwargs: Additional keyword arguments for more flexible filename customization.

        Returns:
            str: The full path to where the PDF file was saved.

        Raises:
            ValueError: If the provided fig parameter is not a valid matplotlib Figure.
        """
        if path is None:
            path = self.default_path
        filename = self.generate_name(diagnostic_product=diagnostic_product, var=var, model_2=model_2, exp_2=exp_2,
                                      time_start=time_start, time_end=time_end, time_precision=time_precision, area=area,
                                      suffix='pdf', **kwargs)
        full_path = os.path.join(path, filename)

        if not self.rebuild and os.path.exists(full_path):
            self.logger.info(f"File already exists and rebuild is set to False: {full_path}")
            return full_path

        # Ensure fig is a Figure object
        if isinstance(fig, plt.Axes):
            fig = fig.figure
        # Save the figure as a PDF
        if isinstance(fig, (plt.Figure, Figure)):
            fig.savefig(full_path, dpi=dpi)
        else:
            raise ValueError("The provided fig parameter is not a valid matplotlib Figure or pyplot figure.")

        # Update metadata with the current date and time
        metadata = update_metadata_with_date(metadata)
        add_pdf_metadata(full_path, metadata, loglevel=self.loglevel)

        self.logger.info(f"Saved PDF file at: {full_path}")
        return full_path

    def save_png(self, fig: Figure, path: str = None, diagnostic_product: str = None, var: str = None,
                 model_2: str = None, exp_2: str = None, time_start: str = None, time_end: str = None,
                 time_precision: str = 'ymd', area: str = None, metadata: dict = None, dpi: int = 300, **kwargs) -> str:
        """
        Save a PNG file with a matplotlib figure to a provided path, with support for additional filename keywords and
        precise time intervals.

        Args:
            fig (Figure): The matplotlib figure object to be saved as a PNG.
            path (str, optional): The path where the PNG file will be saved.
            diagnostic_product (str, optional): Product of the diagnostic analysis.
            var (str, optional): Variable of interest.
            model_2 (str, optional): The second model, for comparative studies.
            exp_2 (str, optional): The experiment associated with the second model.
            time_start (str, optional): The start time for the data, in format consistent with time_precision.
            time_end (str, optional): The finish (end) time for the data, in format consistent with time_precision.
            time_precision (str, optional): Precision for time representation ('y', 'ym', 'ymd', 'ymdh', etc.).
            area (str, optional): The geographical area covered by the data.
            metadata (dict, optional): Additional metadata to include in the PNG file.
            dpi (int, optional): The resolution of the saved PNG file. Default is 300.
            **kwargs: Additional keyword arguments for more flexible filename customization.

        Returns:
            str: The full path to where the PNG file has been saved.

        Raises:
            ValueError: If the provided fig parameter is not a valid matplotlib Figure.
        """
        filename = self.generate_name(diagnostic_product=diagnostic_product, var=var, model_2=model_2, exp_2=exp_2,
                                      time_start=time_start, time_end=time_end, time_precision=time_precision,
                                      area=area, suffix='png', **kwargs)

        if path is None:
            path = self.default_path
        full_path = os.path.join(path, filename)

        if not self.rebuild and os.path.exists(full_path):
            self.logger.info(f"File already exists and rebuild is set to False: {full_path}")
            return full_path

        # Ensure fig is a Figure object
        if isinstance(fig, plt.Axes):
            fig = fig.figure
        # Save the figure to the specified path
        if isinstance(fig, (plt.Figure, Figure)):
            fig.savefig(full_path, format='png', dpi=dpi)
        else:
            raise ValueError("The provided fig parameter is not a valid matplotlib Figure or pyplot figure.")

        # Update metadata with the current date and time
        metadata = update_metadata_with_date(metadata)
        add_png_metadata(full_path, metadata, loglevel=self.loglevel)

        self.logger.info(f"Saved PNG file to path: {full_path}")
        return full_path
