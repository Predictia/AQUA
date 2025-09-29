import os
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import numpy.fft as fft

from aqua.logger import log_configure
from aqua.util import load_yaml
from aqua.reader import Reader


class PSD:
    """Power Spectral Density (PSD) diagnostic"""

    def __init__(self, config, loglevel: str = 'WARNING'):
        """Initialize the PSD diagnostic class."""
        self.loglevel = loglevel
        self.logger = log_configure(self.loglevel, 'PSD')

        if isinstance(config, str):
            self.logger.debug("Reading configuration file %s", config)
            self.config = load_yaml(config)
        else:
            self.logger.debug("Configuration is a dictionary")
            self.config = config

        self.startdate = self.config.get('dates', {}).get('startdate')
        self.enddate = self.config.get('dates', {}).get('enddate')

        if self.startdate is None or self.enddate is None:
            self.logger.error("Both startdate and enddate must be provided")
            raise ValueError("Both startdate and enddate must be provided")

        self._reader()

    def _reader(self):
        """Initializes the Reader class for reference and main data."""
        config_data_ref = self.config.get('data_ref', {})
        config_data = self.config.get('data', {})
        self.reader_data_ref = Reader(
            **config_data_ref,
            startdate=self.startdate, enddate=self.enddate, loglevel=self.loglevel)
        self.reader_data = Reader(
            **config_data,
            startdate=self.startdate, enddate=self.enddate, loglevel=self.loglevel)
        self.logger.debug('Reader classes initialized for data_ref and data')

    def retrieve(self):
        """Retrieves data for all variables specified in the configuration."""
        self.retrieved_data_ref = {}
        self.retrieved_data = {}
        variables_to_process = self.config.get('variables', [])
        self.logger.info("Starting data retrieval...")

        for var_info in variables_to_process:
            var_name = var_info.get('name')
            levels = var_info.get('level')
            levels_to_iterate = [None] if levels is None else np.atleast_1d(levels).astype(int)

            for level in levels_to_iterate:
                data_key = f"{var_name}_{level}" if level is not None else var_name
                log_msg_suffix = f" at level {level}" if level is not None else " (surface)"
                retrieve_args = {'var': var_name}
                if level is not None:
                    retrieve_args['level'] = level

                try:
                    self.logger.debug(f"Retrieving reference data for {var_name}{log_msg_suffix}")
                    # data_ref = self.reader_data_ref.retrieve(**retrieve_args).sel(plev=level, drop=True) if level is not None and 'plev' in self.reader_data_ref.retrieve(**retrieve_args).coords else self.reader_data_ref.retrieve(**retrieve_args)
                    if level is not None and 'plev' in self.reader_data_ref.retrieve(**retrieve_args).coords:
                        data_ref = self.reader_data_ref.retrieve(**retrieve_args).isel(plev=0, drop=True)
                    else:
                        data_ref = self.reader_data_ref.retrieve(**retrieve_args)
                    self.retrieved_data_ref[data_key] = data_ref

                    self.logger.debug(f"Retrieving main data for {var_name}{log_msg_suffix}")
                    # data = self.reader_data.retrieve(**retrieve_args).sel(plev=level, drop=True) if level is not None and 'plev' in self.reader_data.retrieve(**retrieve_args).coords else self.reader_data.retrieve(**retrieve_args)
                    if level is not None and 'plev' in self.reader_data.retrieve(**retrieve_args).coords:
                        data = self.reader_data.retrieve(**retrieve_args).isel(plev=0, drop=True)
                    else:
                        data = self.reader_data.retrieve(**retrieve_args)
                    self.retrieved_data[data_key] = data
                except Exception as e:
                    self.logger.error(f"Failed to retrieve data for {data_key}: {e}", exc_info=True)
                    if data_key in self.retrieved_data_ref: del self.retrieved_data_ref[data_key]
                    if data_key in self.retrieved_data: del self.retrieved_data[data_key]

        self.logger.info("Data retrieval finished.")
        self.logger.info(f"Retrieved reference data for keys: {list(self.retrieved_data_ref.keys())}")
        self.logger.info(f"Retrieved main data for keys: {list(self.retrieved_data.keys())}")

    @staticmethod
    def _radial_average(power_2d):
        """Calculates the radial average of a 2D power spectrum."""
        y_center, x_center = np.array(power_2d.shape) // 2
        y, x = np.indices(power_2d.shape)
        r = np.sqrt((x - x_center)**2 + (y - y_center)**2)
        r = r.astype(np.int32)

        tbin = np.bincount(r.ravel(), power_2d.ravel())
        nr = np.bincount(r.ravel())
        
        # Avoid division by zero
        radial_profile = np.divide(tbin, nr, out=np.zeros_like(tbin, dtype=float), where=nr!=0)
        
        return radial_profile

    def _parse_processed_key(self, processed_key):
        parts = processed_key.split('_')
        level = None
        base_var_name = processed_key
        if len(parts) > 1 and parts[-1].isdigit():
            level = int(parts[-1])
            base_var_name = '_'.join(parts[:-1])
        return base_var_name, level

    def _sanitize_filename_part(self, part):
        if not isinstance(part, str): part = str(part)
        return "".join(c if c.isalnum() else "_" for c in part)

    def _generate_filename(self, processed_key, output_type, calculation_type):
        data_cfg = self.config.get('data', {})
        ref_cfg = self.config.get('data_ref', {})
        dates_cfg = self.config.get('dates', {})
        
        parts = [
            data_cfg.get('model'), data_cfg.get('exp'), data_cfg.get('source'), 'vs',
            ref_cfg.get('model'), dates_cfg.get('startdate'), dates_cfg.get('enddate'),
            processed_key, calculation_type
        ]
        base_filename = '_'.join(self._sanitize_filename_part(p) for p in parts if p)
        
        if output_type == 'figure':
            output_dir = self.config.get('outputdir_fig', './figs_psd')
            ext = '.pdf'
        elif output_type == 'netcdf':
            output_dir = self.config.get('outputdir_data', './data_psd')
            ext = '.nc'
        
        os.makedirs(output_dir, exist_ok=True)
        return os.path.join(output_dir, f"{base_filename}{ext}")

    def _save_figure(self, fig, processed_key, calculation_type):
        filename = self._generate_filename(processed_key, 'figure', calculation_type)
        try:
            fig.savefig(filename)
            self.logger.info(f"Figure saved to {filename}")
        except Exception as e:
            self.logger.error(f"Failed to save figure {filename}: {e}", exc_info=True)

    def _save_netcdf(self, data, processed_key, calculation_type):
        filename = self._generate_filename(processed_key, 'netcdf', calculation_type)
        try:
            data.to_netcdf(filename)
            self.logger.info(f"NetCDF data saved to {filename}")
        except Exception as e:
            self.logger.error(f"Failed to save NetCDF {filename}: {e}", exc_info=True)

    def calculate_and_plot_psd(self, save_fig: bool = False, save_netcdf: bool = False):
        self.logger.info('Calculating and plotting PSD.')
        if not hasattr(self, 'retrieved_data') or not hasattr(self, 'retrieved_data_ref'):
             self.logger.error("Data has not been retrieved. Call retrieve() first.")
             return {}
        
        common_keys = set(self.retrieved_data.keys()) & set(self.retrieved_data_ref.keys())
        if not common_keys:
            self.logger.warning("No common data keys found. Cannot calculate PSD.")
            return {}

        psd_calcs = self.config.get('psd_calculations', {})
        do_time_averaged_psd = psd_calcs.get('time_averaged_psd', True)
        do_psd_of_time_mean = psd_calcs.get('psd_of_time_mean', True)

        if not do_time_averaged_psd and not do_psd_of_time_mean:
            self.logger.warning("No PSD calculations enabled in config. Skipping.")
            return {}

        results = {}
        if do_time_averaged_psd: results['time_averaged_psd'] = {}
        if do_psd_of_time_mean: results['psd_of_time_mean'] = {}

        data_cfg = self.config.get('data', {})
        ref_cfg = self.config.get('data_ref', {})

        for key in common_keys:
            base_var, level = self._parse_processed_key(key)
            self.logger.info(f"Processing PSD for key: {key}")
            data_da = self.retrieved_data[key][base_var]
            data_ref_da = self.retrieved_data_ref[key][base_var]

            # Check for nans in the data
            has_nans = np.isnan(data_da.values).any()
            if has_nans:
                self.logger.warning(f"Emulator data for {key} contains NaNs. Replacing them with 0.")

            has_nans_ref = np.isnan(data_ref_da.values).any()
            if has_nans_ref:
                self.logger.warning(f"Reference data for {key} contains NaNs. Replacing them with 0.")

            # Time-Averaged PSD
            if do_time_averaged_psd:
                try:
                    self.logger.info(f"  Calculating time-averaged PSD for {key}...")
                    
                    data_np = data_da.values
                    data_np = np.nan_to_num(data_np, nan=0.0) if has_nans else data_np

                    fft_2d_stack = fft.fft2(data_np, axes=(-2, -1))
                    shifted_fft_stack = fft.fftshift(fft_2d_stack, axes=(-2, -1))
                    power_2d_stack = np.abs(shifted_fft_stack)**2
                    psd_1d_list = [self._radial_average(power_2d) for power_2d in power_2d_stack]
                    avg_psd_1d = np.mean(psd_1d_list, axis=0)

                    data_ref_np = data_ref_da.values
                    data_ref_np = np.nan_to_num(data_ref_np, nan=0.0) if has_nans_ref else data_ref_np

                    fft_2d_stack_ref = fft.fft2(data_ref_np, axes=(-2, -1))
                    shifted_fft_stack_ref = fft.fftshift(fft_2d_stack_ref, axes=(-2, -1))
                    power_2d_stack_ref = np.abs(shifted_fft_stack_ref)**2
                    psd_1d_ref_list = [self._radial_average(power_2d) for power_2d in power_2d_stack_ref]
                    avg_psd_1d_ref = np.mean(psd_1d_ref_list, axis=0)

                    fig, ax = plt.subplots(figsize=(10, 6))
                    wavenumber = np.arange(len(avg_psd_1d))
                    wavenumber_ref = np.arange(len(avg_psd_1d_ref))
                    ax.loglog(wavenumber, avg_psd_1d, label=f"{data_cfg.get('model', 'Target')}")
                    ax.loglog(wavenumber_ref, avg_psd_1d_ref, label=f"{ref_cfg.get('model', 'Reference')}", linestyle='--')
                    ax.set_xlabel("Wavenumber")
                    ax.set_ylabel("Power Spectral Density")
                    ax.set_title(f"Time-Averaged Power Spectrum: {base_var}" + (f" at {int(level/100)} hPa" if level else ""))
                    ax.legend()
                    ax.grid(True, which="both", ls="-", alpha=0.5)
                    fig.tight_layout()

                    max_len = max(len(avg_psd_1d), len(avg_psd_1d_ref))
                    wavenumbers = np.arange(max_len)
                    psd_ds = xr.Dataset({
                        'psd_target': (('wavenumber'), np.pad(avg_psd_1d, (0, max_len - len(avg_psd_1d)), 'constant', constant_values=np.nan)),
                        'psd_reference': (('wavenumber'), np.pad(avg_psd_1d_ref, (0, max_len - len(avg_psd_1d_ref)), 'constant', constant_values=np.nan)),
                    }, coords={'wavenumber': wavenumbers})
                    results['time_averaged_psd'][key] = (fig, ax, psd_ds)

                except Exception as e:
                    self.logger.error(f"Failed to process time-averaged PSD for key {key}: {e}", exc_info=True)

            # PSD of Time-Mean
            if do_psd_of_time_mean:
                try:
                    self.logger.info(f"  Calculating PSD of time-mean for {key}...")

                    data_mean = self.reader_data.timmean(data_da).values
                    data_mean = np.nan_to_num(data_mean, nan=0.0) if has_nans else data_mean
                    psd_1d = self._radial_average(np.abs(fft.fftshift(fft.fft2(data_mean)))**2)

                    data_ref_mean = self.reader_data_ref.timmean(data_ref_da).values
                    data_ref_mean = np.nan_to_num(data_ref_mean, nan=0.0) if has_nans_ref else data_ref_mean
                    psd_1d_ref = self._radial_average(np.abs(fft.fftshift(fft.fft2(data_ref_mean)))**2)

                    fig, ax = plt.subplots(figsize=(10, 6))
                    wavenumber = np.arange(len(psd_1d))
                    wavenumber_ref = np.arange(len(psd_1d_ref))
                    ax.loglog(wavenumber, psd_1d, label=f"{data_cfg.get('model', 'Target')}")
                    ax.loglog(wavenumber_ref, psd_1d_ref, label=f"{ref_cfg.get('model', 'Reference')}", linestyle='--')
                    ax.set_xlabel("Wavenumber")
                    ax.set_ylabel("Power Spectral Density")
                    ax.set_title(f"Power Spectrum of Time-Mean: {base_var}" + (f" at {int(level/100)} hPa" if level else ""))
                    ax.legend()
                    ax.grid(True, which="both", ls="-", alpha=0.5)
                    fig.tight_layout()

                    max_len = max(len(psd_1d), len(psd_1d_ref))
                    wavenumbers = np.arange(max_len)
                    psd_ds = xr.Dataset({
                        'psd_target': (('wavenumber'), np.pad(psd_1d, (0, max_len - len(psd_1d)), 'constant', constant_values=np.nan)),
                        'psd_reference': (('wavenumber'), np.pad(psd_1d_ref, (0, max_len - len(psd_1d_ref)), 'constant', constant_values=np.nan)),
                    }, coords={'wavenumber': wavenumbers})
                    results['psd_of_time_mean'][key] = (fig, ax, psd_ds)

                except Exception as e:
                    self.logger.error(f"Failed to process PSD of time-mean for key {key}: {e}", exc_info=True)

        if save_fig:
            self.logger.info("Saving figures...")
            for calc_type, res_dict in results.items():
                if not res_dict: continue
                self.logger.info(f"  Saving {calc_type.replace('_', ' ')} figures...")
                for key, (fig, _, _) in res_dict.items():
                    if fig: self._save_figure(fig, key, calc_type)

        if save_netcdf:
            self.logger.info("Saving NetCDF data...")
            for calc_type, res_dict in results.items():
                if not res_dict: continue
                self.logger.info(f"  Saving {calc_type.replace('_', ' ')} netcdf files...")
                for key, (_, _, ds) in res_dict.items():
                    if ds: self._save_netcdf(ds, key, calc_type)
                
        return {
            calc_type: {key: ds for key, (_, _, ds) in res_dict.items() if ds is not None}
            for calc_type, res_dict in results.items()
        }
