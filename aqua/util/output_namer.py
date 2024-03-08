from aqua.logger import log_configure, log_history

class OutputNamer:
    def __init__(self, diagnostic, model, exp, diagnostic_product=None, loglevel='WARNING'):
        self.diagnostic = diagnostic
        self.model = model
        self.exp = exp
        # Optional at initialization, can be used as a default if not overridden in method calls
        self.diagnostic_product = diagnostic_product
        self.loglevel = loglevel
        self.logger = log_configure(log_level=self.loglevel, log_name='OutputNamer')

    def update_diagnostic_product(self, diagnostic_product):
        if diagnostic_product is not None:
            self.diagnostic_product = diagnostic_product

    def generate_name(self, diagnostic_product=None, var=None, model_2=None, exp_2=None, time_range=None, area=None, suffix='nc'):
        """
        Generate a filename based on provided parameters. Updates 'diagnostic_product' attribute if provided.
        """
        self.update_diagnostic_product(diagnostic_product)

        if self.diagnostic_product is None:
            self.logger.error("diagnostic_product is required.")
            raise ValueError("diagnostic_product is required.")

        parts = [self.diagnostic, self.diagnostic_product]
        
        if var:
            parts.append(var)
        
        parts.append(self.model)
        parts.append(self.exp)
        
        if model_2 and exp_2:
            parts.extend([model_2, exp_2])
        
        if area:
            parts.append(area)
        
        if time_range:
            parts.append(time_range)
        
        parts.append(suffix)
        
        return '.'.join(parts)

    def save_nc(self, path, diagnostic_product=None, var=None, model_2=None, exp_2=None, time_range=None, area=None):
        """
        Simulate saving a netCDF file to the provided path. Updates 'diagnostic_product' attribute if provided.
        """
        filename = self.generate_name(diagnostic_product, var, model_2, exp_2, time_range, area, suffix='nc')
        full_path = f"{path}/{filename}"
        self.logger.info(f"Simulated saving netCDF file at: {full_path}")
        return full_path

    def save_pdf(self, path, diagnostic_product=None, var=None, model_2=None, exp_2=None, time_range=None, area=None):
        """
        Simulate saving a PDF file to the provided path. Updates 'diagnostic_product' attribute if provided.
        """
        filename = self.generate_name(diagnostic_product, var, model_2, exp_2, time_range, area, suffix='pdf')
        full_path = f"{path}/{filename}"
        self.logger.info(f"Simulated saving PDF file at: {full_path}")
        return full_path
