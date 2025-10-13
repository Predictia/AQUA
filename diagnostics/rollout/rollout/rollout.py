"""Rollout diagnostic.

This diagnostic reproduces the behaviour of the simple rollout plotting
script previously used in the MLFlow evaluation workflow. It retrieves the
target (reference) and experiment datasets, computes area-weighted spatial
means, and generates comparative time series plots for each configured
variable/level pair.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Iterable, List, Optional, Tuple

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import xarray as xr

from aqua.logger import log_configure
from aqua.reader import Reader
from aqua.util import load_yaml
from smmregrid import GridInspector


class Rollout:
    """Diagnostic that compares spatial means of target vs experiment."""

    def __init__(self, config: Any, loglevel: str = "WARNING") -> None:
        self.loglevel = loglevel
        self.logger = log_configure(self.loglevel, "Rollout")

        if isinstance(config, str):
            self.logger.debug("Loading configuration file %s", config)
            self.config: Dict[str, Any] = load_yaml(config)
        else:
            self.logger.debug("Configuration provided as dictionary")
            self.config = config

        self._validate_config()

        self.startdate = self.config["dates"]["startdate"]
        self.enddate = self.config["dates"]["enddate"]

        self.outputdir_fig = self.config.get("outputdir_fig", "./figs_rollout")
        self.outputdir_data = self.config.get("outputdir_data", "./data_rollout")
        self.figure_format = self._normalise_extension(
            self.config.get("figure_format", "pdf")
        )

        os.makedirs(self.outputdir_fig, exist_ok=True)
        if self.outputdir_data:
            os.makedirs(self.outputdir_data, exist_ok=True)

        self._reader()

    def _validate_config(self) -> None:
        required_sections = ["data", "data_ref", "dates", "variables"]
        missing = [section for section in required_sections if section not in self.config]
        if missing:
            raise ValueError(
                "Missing required configuration sections: " + ", ".join(missing)
            )

        for key in ("startdate", "enddate"):
            if not self.config["dates"].get(key):
                raise ValueError(f"'dates.{key}' must be provided in the configuration.")

    def _reader(self) -> None:
        """Initialise Reader instances for experiment and reference data."""

        config_data = self.config.get("data", {})
        config_data_ref = self.config.get("data_ref", {})

        self.reader_data = Reader(
            catalog=config_data.get("catalog"),
            model=config_data.get("model"),
            exp=config_data.get("exp"),
            source=config_data.get("source"),
            regrid=config_data.get("regrid"),
            fix=config_data.get("fix"),
            startdate=self.startdate,
            enddate=self.enddate,
            loglevel=self.loglevel,
        )

        self.reader_data_ref = Reader(
            catalog=config_data_ref.get("catalog"),
            model=config_data_ref.get("model"),
            exp=config_data_ref.get("exp"),
            source=config_data_ref.get("source"),
            regrid=config_data_ref.get("regrid"),
            fix=config_data_ref.get("fix"),
            startdate=self.startdate,
            enddate=self.enddate,
            loglevel=self.loglevel,
        )

    def retrieve(self) -> None:
        """Retrieve all variables defined in the configuration.
        If regridding is configured, data will be regridded automatically after retrieval.
        """

        variables = self.config.get("variables", [])
        if not variables:
            self.logger.warning("No variables defined in configuration; nothing to retrieve.")
            self.retrieved_data = {}
            self.retrieved_data_ref = {}
            return

        self.retrieved_data: Dict[str, xr.Dataset] = {}
        self.retrieved_data_ref: Dict[str, xr.Dataset] = {}

        for var_cfg in variables:
            var_name = var_cfg.get("name")
            if not var_name:
                self.logger.warning("Skipping variable entry without 'name': %s", var_cfg)
                continue

            for level in self._normalise_levels(var_cfg.get("level")):
                key = self._build_key(var_name, level)
                retrieve_args = {"var": var_name}
                if level is not None:
                    retrieve_args["level"] = level

                try:
                    data_ref = self.reader_data_ref.retrieve(**retrieve_args)
                    if level is not None and "plev" in data_ref.coords:
                        data_ref = data_ref.isel(plev=0, drop=True)
                    # Apply regridding if configured
                    if self.reader_data_ref.tgt_grid_name is not None:
                        self.logger.debug(f"Applying regridding to reference data for {key}")
                        data_ref = self.reader_data_ref.regrid(data_ref)
                    self.retrieved_data_ref[key] = data_ref
                    self.logger.debug("Retrieved reference data for %s", key)
                except Exception as exc:  # pragma: no cover - retrieval depends on I/O
                    self.logger.error(
                        "Failed to retrieve reference data for %s: %s", key, exc, exc_info=True
                    )
                    continue

                try:
                    data = self.reader_data.retrieve(**retrieve_args)
                    if level is not None and "plev" in data.coords:
                        data = data.isel(plev=0, drop=True)
                    # Apply regridding if configured
                    if self.reader_data.tgt_grid_name is not None:
                        self.logger.debug(f"Applying regridding to experiment data for {key}")
                        data = self.reader_data.regrid(data)
                    self.retrieved_data[key] = data
                    self.logger.debug("Retrieved experiment data for %s", key)
                except Exception as exc:  # pragma: no cover - retrieval depends on I/O
                    self.logger.error(
                        "Failed to retrieve experiment data for %s: %s", key, exc, exc_info=True
                    )
                    self.retrieved_data_ref.pop(key, None)

        missing = set(self.retrieved_data_ref) ^ set(self.retrieved_data)
        if missing:
            for key in missing:
                self.retrieved_data_ref.pop(key, None)
                self.retrieved_data.pop(key, None)
            self.logger.warning("Dropped variables with incomplete data: %s", sorted(missing))

        self.logger.info("Retrieved data for keys: %s", sorted(self.retrieved_data.keys()))
        # Log regridding information
        if self.reader_data_ref.tgt_grid_name is not None:
            self.logger.info(f"Reference data regridded to: {self.reader_data_ref.tgt_grid_name}")
        if self.reader_data.tgt_grid_name is not None:
            self.logger.info(f"Experiment data regridded to: {self.reader_data.tgt_grid_name}")

    def compute_rollout(
        self, save_fig: bool = True, save_data: bool = False
    ) -> Dict[str, xr.Dataset]:
        """Compute rollout plots and optionally save outputs."""

        if not hasattr(self, "retrieved_data") or not hasattr(self, "retrieved_data_ref"):
            raise RuntimeError("Data not retrieved. Call 'retrieve' before computing rollouts.")

        results: Dict[str, xr.Dataset] = {}
        config_data = self.config.get("data", {})
        config_data_ref = self.config.get("data_ref", {})

        for key in sorted(self.retrieved_data):
            if key not in self.retrieved_data_ref:
                continue

            data = self.retrieved_data[key]
            data_ref = self.retrieved_data_ref[key]

            base_var, level = self._parse_processed_key(key)
            if base_var not in data or base_var not in data_ref:
                self.logger.warning(
                    "Variable '%s' not present in datasets for key '%s'; skipping.",
                    base_var,
                    key,
                )
                continue

            # Identify horizontal dimensions for spatial averaging
            fldmean_kwargs = {}
            horizontal_dims = []
            try:
                grid_types = GridInspector(data).get_gridtype()
                if grid_types:
                    horizontal_dims = [dim for dim in grid_types[0].horizontal_dims if dim in data.dims]
                    if not horizontal_dims:
                        self.logger.warning(
                            "GridInspector did not return usable horizontal dims for %s. Falling back to non-time dims.",
                            key,
                        )
            except Exception as exc:
                self.logger.warning(
                    "Could not infer horizontal dims for fldmean on %s: %s",
                    key,
                    exc,
                )

            if horizontal_dims:
                fldmean_kwargs["dims"] = horizontal_dims
                # Synchronise the underlying FldStat horizontal dims with the data
                fldstat_obj_data = self.reader_data.tgt_fldstat or self.reader_data.src_fldstat
                if fldstat_obj_data is not None:
                    fldstat_obj_data.horizontal_dims = horizontal_dims
                fldstat_obj_ref = self.reader_data_ref.tgt_fldstat or self.reader_data_ref.src_fldstat
                if fldstat_obj_ref is not None:
                    fldstat_obj_ref.horizontal_dims = horizontal_dims
            
            self.logger.debug(f"Using fldmean_kwargs for {key}: {fldmean_kwargs}")
            ts_target = self.reader_data_ref.fldmean(data_ref, **fldmean_kwargs)
            ts_exp = self.reader_data.fldmean(data, **fldmean_kwargs)

            # Ensure residual spatial dims are collapsed (e.g. ncells)
            for dim in horizontal_dims:
                if dim in ts_target.dims:
                    self.logger.debug(
                        "Residual dimension %s present after fldmean for %s (target). Applying mean.",
                        dim,
                        key,
                    )
                    ts_target = ts_target.mean(dim=dim)
                if dim in ts_exp.dims:
                    self.logger.debug(
                        "Residual dimension %s present after fldmean for %s (experiment). Applying mean.",
                        dim,
                        key,
                    )
                    ts_exp = ts_exp.mean(dim=dim)

            try:
                ts_target = ts_target.sel(time=slice(self.startdate, self.enddate))
                ts_exp = ts_exp.sel(time=slice(self.startdate, self.enddate))
            except Exception as exc:
                self.logger.warning(
                    "Failed to subset time range for %s; proceeding with original data: %s",
                    key,
                    exc,
                )

            try:
                da_target = ts_target[base_var]
                da_exp = ts_exp[base_var]
            except KeyError:
                self.logger.warning(
                    "Spatial means do not contain variable '%s' for key '%s'; skipping.",
                    base_var,
                    key,
                )
                continue

            try:
                da_target, da_exp = xr.align(da_target, da_exp, join="inner")
            except Exception as exc:
                self.logger.error(
                    "Failed to align time series for %s: %s", key, exc, exc_info=True
                )
                continue

            if da_target.size == 0:
                self.logger.warning("No overlapping timestamps for %s; skipping.", key)
                continue

            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(
                da_target["time"].values,
                da_target.values,
                label=config_data_ref.get("label", "Target"),
                color="black",
                linewidth=2,
            )
            ax.plot(
                da_exp["time"].values,
                da_exp.values,
                label=config_data.get("label", "Experiment"),
                color="blue",
            )

            ax.set_xlabel("Time")
            units = da_target.attrs.get("units") or da_exp.attrs.get("units")
            ylabel = f"{base_var} ({units})" if units else base_var
            ax.set_ylabel(ylabel)

            title = self._build_title(base_var, level, config_data, config_data_ref)
            ax.set_title(title)
            ax.legend()
            ax.grid(True)

            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
            fig.autofmt_xdate()
            fig.tight_layout()

            combined = xr.Dataset({
                "target": da_target,
                "experiment": da_exp,
            })
            combined.attrs["variable"] = base_var
            if level is not None:
                combined.attrs["level"] = level

            results[key] = combined

            if save_fig:
                self._save_figure(fig, key)
            if save_data:
                self._save_data(combined, key)

            plt.close(fig)

        return results

    def _build_title(
        self,
        base_var: str,
        level: Optional[int],
        config_data: Dict[str, Any],
        config_data_ref: Dict[str, Any],
    ) -> str:
        model = config_data.get("model", "N/A")
        exp = config_data.get("exp", "N/A")
        source = config_data.get("source", "N/A")
        model_ref = config_data_ref.get("model", "N/A")
        exp_ref = config_data_ref.get("exp", "N/A")
        source_ref = config_data_ref.get("source", "N/A")

        level_part = f" at level {level}" if level is not None else ""
        return (
            f"Rollout Comparison: {base_var}{level_part}\n"
        )

    @staticmethod
    def _normalise_levels(levels: Any) -> Iterable[Optional[int]]:
        if levels is None:
            return [None]
        if isinstance(levels, (int, float)):
            return [int(levels)]
        if isinstance(levels, list):
            return [int(level) for level in levels]
        raise ValueError(f"Unsupported level specification: {levels}")

    @staticmethod
    def _build_key(var_name: str, level: Optional[int]) -> str:
        return f"{var_name}_{level}" if level is not None else var_name

    @staticmethod
    def _parse_processed_key(key: str) -> Tuple[str, Optional[int]]:
        parts = key.split("_")
        if len(parts) > 1 and parts[-1].isdigit():
            try:
                level = int(parts[-1])
                base = "_".join(parts[:-1])
                return base, level
            except ValueError:
                return key, None
        return key, None

    @staticmethod
    def _normalise_extension(extension: str) -> str:
        ext = extension.lower().lstrip(".")
        if not ext:
            return "pdf"
        return ext

    def _save_figure(self, fig: plt.Figure, processed_key: str) -> None:
        filename = self._generate_filename(processed_key, "figure", "rollout")
        try:
            fig.savefig(filename)
            self.logger.info("Saved rollout figure to %s", filename)
        except Exception as exc:  # pragma: no cover - depends on filesystem
            self.logger.error("Failed to save figure %s: %s", filename, exc, exc_info=True)

    def _save_data(self, data: xr.Dataset, processed_key: str) -> None:
        if not self.outputdir_data:
            self.logger.warning(
                "Output data directory not configured; skipping NetCDF save for %s.",
                processed_key,
            )
            return

        filename = self._generate_filename(processed_key, "netcdf", "rollout_timeseries")
        try:
            data.to_netcdf(filename)
            self.logger.info("Saved rollout data to %s", filename)
        except Exception as exc:  # pragma: no cover - depends on filesystem
            self.logger.error("Failed to save NetCDF %s: %s", filename, exc, exc_info=True)

    def _generate_filename(self, processed_key: str, output_type: str, suffix: str) -> str:
        data_cfg = self.config.get("data", {})
        ref_cfg = self.config.get("data_ref", {})

        filename_parts = [
            self._sanitize_filename_part(data_cfg.get("model", "model")),
            self._sanitize_filename_part(data_cfg.get("exp", "exp")),
            self._sanitize_filename_part(data_cfg.get("source", "src")),
            "vs",
            self._sanitize_filename_part(ref_cfg.get("model", "refmodel")),
            self._sanitize_filename_part(ref_cfg.get("exp", "refexp")),
            processed_key,
            self._sanitize_filename_part(self.startdate),
            self._sanitize_filename_part(self.enddate),
            suffix,
        ]

        filename = "_".join(filter(None, filename_parts))

        if output_type == "figure":
            extension = f".{self.figure_format}"
            directory = self.outputdir_fig
        elif output_type == "netcdf":
            extension = ".nc"
            directory = self.outputdir_data
        else:
            raise ValueError(f"Unsupported output type '{output_type}'.")

        if directory is None:
            directory = "."

        return os.path.join(directory, f"{filename}{extension}")

    @staticmethod
    def _sanitize_filename_part(value: Any) -> str:
        text = str(value) if value is not None else ""
        for char in [' ', '/', '\\', ':', '*', '?', '"', '<', '>', '|', '.']:
            text = text.replace(char, "_")
        return text


__all__ = ["Rollout"]


