class OutputNamer:
    def __init__(self, diag, diag_product, model, exp):
        self.diag = diag
        self.diag_product = diag_product
        self.model = model
        self.exp = exp

    def generate_nc_name(self, exp_kwargs='', diag_kwargs=''):
        """
        Generate a name for a netCDF file based on provided parameters.
        
        Args:
            exp_kwargs: Experiment-specific keyword arguments (e.g., resolution).
            diag_kwargs: Diagnostic-specific keyword arguments (e.g., variable name).
        
        Returns:
            A string representing the filename.
        """
        return f"{self.diag}.{self.diag_product}.{self.model}.{self.exp}.{exp_kwargs}.{diag_kwargs}.nc"

    def generate_pdf_name(self, exp_kwargs='', diag_kwargs=''):
        """
        Generate a name for a PDF file based on provided parameters.
        
        Args:
            exp_kwargs: Experiment-specific keyword arguments.
            diag_kwargs: Diagnostic-specific keyword arguments.
        
        Returns: 
            A string representing the filename.
        """
        return f"{self.diag}.{self.diag_product}.{self.model}.{self.exp}.{exp_kwargs}.{diag_kwargs}.pdf"
    
    def save_nc(self, path, exp_kwargs='', diag_kwargs=''):
        """
        Simulate saving a netCDF file to the provided path based on generated name.
        
        Args:
            path: The path where the netCDF file will be saved.
            exp_kwargs: Experiment-specific keyword arguments.
            diag_kwargs: Diagnostic-specific keyword arguments.
        
        Returns:
            The full path to where the netCDF file would be saved.
        """
        filename = self.generate_nc_name(exp_kwargs, diag_kwargs)
        full_path = f"{path}/{filename}"
        print(f"Simulated saving netCDF file at: {full_path}")
        return full_path

    def save_pdf(self, path, exp_kwargs='', diag_kwargs=''):
        """
        Simulate saving a PDF file to the provided path based on generated name.
        
        Args:
            path: The path where the PDF file will be saved.
            exp_kwargs: Experiment-specific keyword arguments.
            diag_kwargs: Diagnostic-specific keyword arguments.
        
        Returns:
            The full path to where the PDF file would be saved.
        """
        filename = self.generate_pdf_name(exp_kwargs, diag_kwargs)
        full_path = f"{path}/{filename}"
        print(f"Simulated saving PDF file at: {full_path}")
        return full_path