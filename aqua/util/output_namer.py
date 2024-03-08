class OutputNamer:
    def __init__(self, diagnostic, diagnostic_product, model, exp, var=None):
        self.diagnostic = diagnostic
        self.diagnostic_product = diagnostic_product
        self.model = model
        self.exp = exp
        self.var = var  # 'var' is optional

    def generate_name(self, model_2=None, exp_2=None, time_range=None, area=None, suffix=None):
        """
        Generate a filename based on provided parameters, with support for optional components.
        
        Args:
            model_2: The second model, for comparative studies (optional).
            exp_2: The experiment associated with the second model (optional).
            time_range: The time range for the data (optional).
            area: The geographical area covered by the data (optional).
            suffix: The file extension/suffix indicating file type (e.g., 'nc', 'pdf').
        
        Returns:
            A string representing the filename.
        """
        parts = [self.diagnostic, self.diagnostic_product]
        if self.var:  # Include 'var' if provided
            parts.append(self.var)
        parts.extend([self.model, self.exp])
        if model_2 and exp_2:  # Include model_2 and exp_2 if provided
            parts.extend([model_2, exp_2])
        if area:  # Include 'area' if provided
            parts.append(area)
        if time_range:  # Include 'time_range' if provided
            parts.append(time_range)
        if suffix:  # Add suffix if provided
            parts.append(suffix)
        
        return '.'.join(parts)

    def save_nc(self, path, model_2=None, exp_2=None, time_range=None, area=None):
        """
        Simulate saving a netCDF file to the provided path based on generated name, with support for optional components.
        
        Args:
            path: The path where the netCDF file will be saved.
            model_2, exp_2, time_range, area: Optional parameters for filename generation.
        
        Returns:
            The full path to where the netCDF file would be saved.
        """
        filename = self.generate_name(model_2=model_2, exp_2=exp_2, time_range=time_range, area=area, suffix='nc')
        full_path = f"{path}/{filename}"
        print(f"Simulated saving netCDF file at: {full_path}")
        return full_path

    def save_pdf(self, path, model_2=None, exp_2=None, time_range=None, area=None):
        """
        Simulate saving a PDF file to the provided path based on generated name, with support for optional components.
        
        Args:
            path: The path where the PDF file will be saved.
            model_2, exp_2, time_range, area: Optional parameters for filename generation.
        
        Returns:
            The full path to where the PDF file would be saved.
        """
        filename = self.generate_name(model_2=model_2, exp_2=exp_2, time_range=time_range, area=area, suffix='pdf')
        full_path = f"{path}/{filename}"
        print(f"Simulated saving PDF file at: {full_path}")
        return full_path
