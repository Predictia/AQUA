from aqua.logger import log_configure, log_history

class OutputNamer:
    def __init__(self, diagnostic, model, exp, diagnostic_product=None, loglevel='WARNING', default_path='.'):
        """
        Initialize the OutputNamer class to manage output file naming.

        Parameters:
            diagnostic (str): Name of the diagnostic.
            model (str): Model used in the diagnostic.
            exp (str): Experiment identifier.
            diagnostic_product (str, optional): Product of the diagnostic analysis.
            loglevel (str, optional): Log level for the class's logger.
            default_path (str, optional): Default path where files will be saved.

        Returns:
            None.
        """
        self.diagnostic = diagnostic
        self.model = model
        self.exp = exp
        self.diagnostic_product = diagnostic_product
        self.loglevel = loglevel
        self.default_path = default_path
        self.logger = log_configure(log_level=self.loglevel, log_name='OutputNamer')
        self.logger.debug(f"OutputNamer initialized with diagnostic: {diagnostic}, model: {model}, exp: {exp}, default_path: {default_path}")

    def update_diagnostic_product(self, diagnostic_product):
        """
        Update the diagnostic product for the instance.

        Parameters:
            diagnostic_product (str): The new diagnostic product to be used.

        Returns:
            None.
        """
        if diagnostic_product is not None:
            self.diagnostic_product = diagnostic_product
            self.logger.debug(f"Diagnostic product updated to: {diagnostic_product}")

    def generate_name(self, diagnostic_product=None, var=None, model_2=None, exp_2=None, time_range=None, area=None, suffix='nc'):
        """
        Generate a filename based on provided parameters.

        Parameters:
            diagnostic_product (str, optional): Product of the diagnostic analysis.
            var (str, optional): Variable of interest.
            model_2 (str, optional): The second model, for comparative studies.
            exp_2 (str, optional): The experiment associated with the second model.
            time_range (str, optional): The time range for the data.
            area (str, optional): The geographical area covered by the data.
            suffix (str, optional): The file extension/suffix indicating file type.

        Returns:
            str: A string representing the generated filename.
        """
        self.update_diagnostic_product(diagnostic_product)

        if not self.diagnostic_product:
            msg = "diagnostic_product is required."
            self.logger.error(msg)
            raise ValueError(msg)

        parts = [part for part in [self.diagnostic, self.diagnostic_product, var, self.model, self.exp, model_2, exp_2, area, time_range] if part]
        parts.append(suffix)

        filename = '.'.join(parts)
        self.logger.debug(f"Generated filename: {filename}")
        return filename

    def save_nc(self, path=None, diagnostic_product=None, var=None, model_2=None, exp_2=None, time_range=None, area=None):
        """
        Simulate saving a netCDF file to the provided path.

        Parameters:
            path (str, optional): The path where the netCDF file will be saved.
            Additional parameters are passed to generate_name.

        Returns:
            str: The full path to where the netCDF file would be simulated to save.
        """
        if path is None:
            path = self.default_path
        filename = self.generate_name(diagnostic_product, var, model_2, exp_2, time_range, area, suffix='nc')
        full_path = f"{path}/{filename}"
        self.logger.info(f"Simulated saving netCDF file at: {full_path}")
        return full_path

    def save_pdf(self, path=None, diagnostic_product=None, var=None, model_2=None, exp_2=None, time_range=None, area=None):
        """
        Simulate saving a PDF file to the provided path.

        Parameters:
            path (str, optional): The path where the PDF file will be saved.
            Additional parameters are passed to generate_name.

        Returns:
            str: The full path to where the PDF file would be simulated to save.
        """
        if path is None:
            path = self.default_path
        filename = self.generate_name(diagnostic_product, var, model_2, exp_2, time_range, area, suffix='pdf')
        full_path = f"{path}/{filename}"
        self.logger.info(f"Simulated saving PDF file at: {full_path}")
        return full_path


