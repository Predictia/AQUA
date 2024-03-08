from aqua.logger import log_configure, log_history

class OutputNamer:
    def __init__(self, diagnostic, model, exp, diagnostic_product=None, loglevel='WARNING', default_path='.'):
        self.diagnostic = diagnostic
        self.model = model
        self.exp = exp
        self.diagnostic_product = diagnostic_product
        self.loglevel = loglevel
        self.default_path = default_path  # Default path as an optional attribute
        self.logger = log_configure(log_level=self.loglevel, log_name='OutputNamer')

    def update_diagnostic_product(self, diagnostic_product):
        if diagnostic_product is not None:
            self.diagnostic_product = diagnostic_product

    def generate_name(self, diagnostic_product=None, var=None, model_2=None, exp_2=None, time_range=None, area=None, suffix='nc'):
        self.update_diagnostic_product(diagnostic_product)

        if not self.diagnostic_product:
            self.logger.error("diagnostic_product is required.")
            raise ValueError("diagnostic_product is required.")

        parts = [part for part in [self.diagnostic, self.diagnostic_product, var, self.model, self.exp, model_2, exp_2, area, time_range] if part]
        parts.append(suffix)

        return '.'.join(parts)

    def save_nc(self, path=None, diagnostic_product=None, var=None, model_2=None, exp_2=None, time_range=None, area=None):
        if path is None:
            path = self.default_path
        filename = self.generate_name(diagnostic_product, var, model_2, exp_2, time_range, area, suffix='nc')
        full_path = f"{path}/{filename}"
        self.logger.info(f"Simulated saving netCDF file at: {full_path}")
        return full_path

    def save_pdf(self, path=None, diagnostic_product=None, var=None, model_2=None, exp_2=None, time_range=None, area=None):
        if path is None:
            path = self.default_path
        filename = self.generate_name(diagnostic_product, var, model_2, exp_2, time_range, area, suffix='pdf')
        full_path = f"{path}/{filename}"
        self.logger.info(f"Simulated saving PDF file at: {full_path}")
        return full_path

