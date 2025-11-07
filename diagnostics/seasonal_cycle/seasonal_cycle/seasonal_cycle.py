import os
from typing import Any, Dict, Iterable, List, Optional, Tuple

import matplotlib.pyplot as plt
import xarray as xr

from aqua.exceptions import NotEnoughDataError
from aqua.logger import log_configure
from aqua.reader import Reader
from aqua.util import load_yaml
from aqua.util.sci_util import area_selection


class SeasonalCycle:
    def __init__(self, config: Any, loglevel: str = "WARNING") -> None:
        self.loglevel = loglevel
        self.logger = log_configure(self.loglevel, "SeasonalCycle")

        if isinstance(config, str):
            self.config: Dict[str, Any] = load_yaml(config)
        else:
            self.config = config

        self._validate_config()

        self.startdate = self.config["dates"]["startdate"]
        self.enddate = self.config["dates"]["enddate"]

        self.outputdir_fig = self.config.get("outputdir_fig", "./figs_seasonal_cycle")
        self.outputdir_data = self.config.get("outputdir_data", "./data_seasonal_cycle")
        self.figure_format = self._normalise_extension(self.config.get("figure_format", "pdf"))

        os.makedirs(self.outputdir_fig, exist_ok=True)
        if self.outputdir_data:
            os.makedirs(self.outputdir_data, exist_ok=True)

        self.data_label = self._infer_label(self.config.get("data", {}))
        self.data_ref_label = self._infer_label(self.config.get("data_ref", {}))
        self.regions = self._parse_regions(self.config.get("regions"))

        self._reader()

    def _validate_config(self) -> None:
        required = ["data", "data_ref", "dates", "variables"]
        missing = [section for section in required if section not in self.config]
        if missing:
            raise ValueError(f"Missing required configuration sections: {', '.join(missing)}")

        for key in ("startdate", "enddate"):
            if not self.config["dates"].get(key):
                raise ValueError(f"Configuration must provide dates.{key}")

        variables = self.config.get("variables", [])
        if not isinstance(variables, list) or not variables:
            raise ValueError("Configuration must provide a non-empty 'variables' list")

    def _reader(self) -> None:
        cfg_data = self.config.get("data", {})
        cfg_ref = self.config.get("data_ref", {})

        self.reader_data = Reader(
            catalog=cfg_data.get("catalog"),
            model=cfg_data.get("model"),
            exp=cfg_data.get("exp"),
            source=cfg_data.get("source"),
            regrid=cfg_data.get("regrid"),
            fix=cfg_data.get("fix"),
            areas=cfg_data.get("areas"),
            startdate=self.startdate,
            enddate=self.enddate,
            loglevel=self.loglevel,
        )

        self.reader_data_ref = Reader(
            catalog=cfg_ref.get("catalog"),
            model=cfg_ref.get("model"),
            exp=cfg_ref.get("exp"),
            source=cfg_ref.get("source"),
            regrid=cfg_ref.get("regrid"),
            fix=cfg_ref.get("fix"),
            areas=cfg_ref.get("areas"),
            startdate=self.startdate,
            enddate=self.enddate,
            loglevel=self.loglevel,
        )

    def retrieve(self) -> None:
        variables = self.config.get("variables", [])
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

                data_ref = self._retrieve_single(self.reader_data_ref, retrieve_args, key, is_reference=True)
                data = self._retrieve_single(self.reader_data, retrieve_args, key, is_reference=False)

                if data_ref is None or data is None:
                    continue

                self.retrieved_data_ref[key] = data_ref
                self.retrieved_data[key] = data

        missing = set(self.retrieved_data_ref) ^ set(self.retrieved_data)
        if missing:
            for key in missing:
                self.retrieved_data_ref.pop(key, None)
                self.retrieved_data.pop(key, None)
            if missing:
                self.logger.warning("Dropped variables with incomplete data: %s", sorted(missing))

        if not self.retrieved_data:
            self.logger.warning("No variables retrieved successfully")

    def _retrieve_single(
        self,
        reader: Reader,
        retrieve_args: Dict[str, Any],
        key: str,
        is_reference: bool,
    ) -> Optional[xr.Dataset]:
        label = "reference" if is_reference else "experiment"
        try:
            dataset = reader.retrieve(**retrieve_args)
            level = retrieve_args.get("level")
            var = retrieve_args["var"]
            if level is not None and "plev" in dataset.coords:
                dataset = dataset.isel(plev=0, drop=True)
            tgt_grid = getattr(reader, "tgt_grid_name", None)
            if tgt_grid:
                if hasattr(reader, "regridder"):
                    self.logger.debug("Applying regridding to %s data for %s", label, key)
                    dataset = reader.regrid(dataset)
                else:
                    self.logger.debug(
                        "Skipping regridding for %s data for %s; reader has no regridder",
                        label,
                        key,
                    )
            if var not in dataset:
                self.logger.warning("Variable '%s' missing in retrieved %s dataset for key %s", var, label, key)
                return None
            return dataset
        except Exception as exc:
            self.logger.error("Failed to retrieve %s data for %s: %s", label, key, exc, exc_info=True)
            return None

    def compute(self, save_fig: bool = True, save_data: bool = False) -> Dict[str, xr.Dataset]:
        if not hasattr(self, "retrieved_data") or not hasattr(self, "retrieved_data_ref"):
            raise RuntimeError("Data not retrieved. Call 'retrieve' before compute().")

        results: Dict[str, xr.Dataset] = {}

        for key in sorted(self.retrieved_data):
            if key not in self.retrieved_data_ref:
                continue

            data = self.retrieved_data[key]
            data_ref = self.retrieved_data_ref[key]
            base_var, level = self._parse_processed_key(key)

            if base_var not in data or base_var not in data_ref:
                self.logger.warning("Variable '%s' missing for key %s; skipping", base_var, key)
                continue

            for region in self.regions:
                region_key = f"{key}__{region['name']}"
                try:
                    result = self._compute_region_cycle(
                        data[base_var],
                        data_ref[base_var],
                        base_var,
                        level,
                        region,
                        key,
                        save_fig,
                        save_data,
                    )
                except NotEnoughDataError as exc:
                    self.logger.warning("Skipping %s (%s): %s", key, region["name"], exc)
                    continue
                except Exception as exc:
                    self.logger.error("Failed seasonal cycle for %s (%s): %s", key, region["name"], exc, exc_info=True)
                    continue

                if result is not None:
                    results[region_key] = result

        return results

    def _compute_region_cycle(
        self,
        data: xr.DataArray,
        data_ref: xr.DataArray,
        base_var: str,
        level: Optional[int],
        region: Dict[str, Any],
        key: str,
        save_fig: bool,
        save_data: bool,
    ) -> Optional[xr.Dataset]:
        da_data = self._compute_region_timeseries(self.reader_data, data, region)
        da_ref = self._compute_region_timeseries(self.reader_data_ref, data_ref, region)

        monthly_data = self.reader_data.timmean(da_data, freq="MS", exclude_incomplete=True)
        monthly_ref = self.reader_data_ref.timmean(da_ref, freq="MS", exclude_incomplete=True)

        monthly_data = monthly_data.dropna("time", how="all")
        monthly_ref = monthly_ref.dropna("time", how="all")

        if monthly_data.sizes.get("time", 0) < 12:
            raise NotEnoughDataError("Experiment data shorter than one year of monthly means")
        if monthly_ref.sizes.get("time", 0) < 12:
            raise NotEnoughDataError("Reference data shorter than one year of monthly means")

        monthly_data, monthly_ref = xr.align(monthly_data, monthly_ref, join="inner")
        if monthly_data.sizes.get("time", 0) < 12:
            raise NotEnoughDataError("Not enough overlapping monthly means between experiment and reference")

        seasonal_data = monthly_data.groupby("time.month").mean("time")
        seasonal_ref = monthly_ref.groupby("time.month").mean("time")

        if seasonal_data.sizes.get("month", 0) < 12:
            raise NotEnoughDataError("Experiment seasonal cycle missing months")
        if seasonal_ref.sizes.get("month", 0) < 12:
            raise NotEnoughDataError("Reference seasonal cycle missing months")

        anomaly_data = seasonal_data - seasonal_data.mean("month")
        anomaly_ref = seasonal_ref - seasonal_ref.mean("month")

        result = xr.Dataset(
            {
                "data": seasonal_data,
                "data_ref": seasonal_ref,
                "data_anomaly": anomaly_data,
                "data_ref_anomaly": anomaly_ref,
            }
        )

        result.attrs["variable"] = base_var
        result.attrs["region"] = region["name"]
        if level is not None:
            result.attrs["level"] = level

        if save_fig:
            self._plot_seasonal_cycle(result, base_var, level, region, key)

        if save_data and self.outputdir_data:
            self._save_data(result, key, region)

        return result

    def _compute_region_timeseries(
        self,
        reader: Reader,
        data: xr.DataArray,
        region: Dict[str, Any],
    ) -> xr.DataArray:
        lat_limits = region.get("lat")
        lon_limits = region.get("lon")

        if lat_limits is not None or lon_limits is not None:
            data_selected = area_selection(
                data,
                lat=lat_limits,
                lon=lon_limits,
                drop=False,
                loglevel=self.loglevel,
            )
        else:
            data_selected = data

        averaged = reader.fldmean(data_selected)
        if isinstance(averaged, xr.Dataset):
            averaged = averaged[data.name]
        return averaged.squeeze()

    def _plot_seasonal_cycle(
        self,
        result: xr.Dataset,
        base_var: str,
        level: Optional[int],
        region: Dict[str, Any],
        key: str,
    ) -> None:
        months = result["data"]["month"].values
        month_labels = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]
        label_lookup = dict(zip(range(1, 13), month_labels))
        tick_labels = [label_lookup.get(int(m), str(int(m))) for m in months]

        fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

        axes[0].plot(months, result["data"].values, label=self.data_label, marker="o")
        axes[0].plot(months, result["data_ref"].values, label=self.data_ref_label, marker="o")
        axes[0].set_ylabel(self._build_ylabel(result["data"]))
        axes[0].legend()
        axes[0].grid(True)

        axes[1].plot(months, result["data_anomaly"].values, label=self.data_label, marker="o")
        axes[1].plot(months, result["data_ref_anomaly"].values, label=self.data_ref_label, marker="o")
        axes[1].set_ylabel(self._build_ylabel(result["data_anomaly"], default=f"{base_var} anomaly"))
        axes[1].set_xticks(months)
        axes[1].set_xticklabels(tick_labels)
        axes[1].legend()
        axes[1].grid(True)

        title = self._build_title(base_var, level, region)
        fig.suptitle(title)
        fig.tight_layout(rect=(0, 0, 1, 0.97))

        filename = self._generate_filename(key, region, output_type="figure")
        try:
            fig.savefig(filename)
            self.logger.info("Saved seasonal cycle figure to %s", filename)
        except Exception as exc:
            self.logger.error("Failed to save figure %s: %s", filename, exc, exc_info=True)
        finally:
            plt.close(fig)

    def _save_data(self, data: xr.Dataset, key: str, region: Dict[str, Any]) -> None:
        filename = self._generate_filename(key, region, output_type="netcdf")
        try:
            data.to_netcdf(filename)
            self.logger.info("Saved seasonal cycle data to %s", filename)
        except Exception as exc:
            self.logger.error("Failed to save NetCDF %s: %s", filename, exc, exc_info=True)

    def _generate_filename(self, key: str, region: Dict[str, Any], output_type: str) -> str:
        data_cfg = self.config.get("data", {})
        ref_cfg = self.config.get("data_ref", {})
        parts = [
            self._sanitize_filename_part(data_cfg.get("model", "model")),
            self._sanitize_filename_part(data_cfg.get("exp", "exp")),
            self._sanitize_filename_part(data_cfg.get("source", "src")),
            "vs",
            self._sanitize_filename_part(ref_cfg.get("model", "refmodel")),
            self._sanitize_filename_part(ref_cfg.get("exp", "refexp")),
            self._sanitize_filename_part(key),
            self._sanitize_filename_part(region["name"]),
            self._sanitize_filename_part(self.startdate),
            self._sanitize_filename_part(self.enddate),
            "seasonal_cycle",
        ]

        filename = "_".join(filter(None, parts))

        if output_type == "figure":
            extension = f".{self.figure_format}"
            directory = self.outputdir_fig
        elif output_type == "netcdf":
            extension = ".nc"
            directory = self.outputdir_data or "."
        else:
            raise ValueError(f"Unsupported output type '{output_type}'")

        return os.path.join(directory, f"{filename}{extension}")

    def _build_title(self, base_var: str, level: Optional[int], region: Dict[str, Any]) -> str:
        level_part = f", level {level}" if level is not None else ""
        region_part = region["name"]
        return f"Seasonal cycle for {base_var}{level_part} ({region_part})"

    def _build_ylabel(self, data: xr.DataArray, default: Optional[str] = None) -> str:
        units = data.attrs.get("units")
        name = default or data.name or "Value"
        if units:
            return f"{name} ({units})"
        return name

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
        ext = (extension or "").lower().lstrip(".")
        return ext or "pdf"

    @staticmethod
    def _sanitize_filename_part(value: Any) -> str:
        text = str(value) if value is not None else ""
        for char in [" ", "/", "\\", ":", "*", "?", '"', "<", ">", "|", "."]:
            text = text.replace(char, "_")
        return text

    def _infer_label(self, cfg: Dict[str, Any]) -> str:
        return cfg.get("label") or cfg.get("model") or cfg.get("exp") or "Dataset"

    def _parse_regions(self, regions_cfg: Any) -> List[Dict[str, Any]]:
        regions: List[Dict[str, Any]] = []
        if regions_cfg is None:
            return [{"name": "global", "lat": None, "lon": None}]

        if isinstance(regions_cfg, list):
            for idx, region in enumerate(regions_cfg):
                if not isinstance(region, dict):
                    continue
                name = region.get("name") or f"region_{idx+1}"
                regions.append(
                    {
                        "name": name,
                        "lat": self._validate_bounds(region.get("lat")),
                        "lon": self._validate_bounds(region.get("lon")),
                    }
                )
        elif isinstance(regions_cfg, dict):
            for name, region in regions_cfg.items():
                if not isinstance(region, dict):
                    continue
                regions.append(
                    {
                        "name": name,
                        "lat": self._validate_bounds(region.get("lat")),
                        "lon": self._validate_bounds(region.get("lon")),
                    }
                )

        if not regions:
            regions.append({"name": "global", "lat": None, "lon": None})
        return regions

    @staticmethod
    def _validate_bounds(bounds: Any) -> Optional[List[float]]:
        if bounds is None:
            return None
        if isinstance(bounds, (list, tuple)) and len(bounds) == 2:
            return [float(bounds[0]), float(bounds[1])]
        raise ValueError(f"Region bounds must be lists of two values, got {bounds}")


__all__ = ["SeasonalCycle"]

