from aqua import Reader
import ocean_circulation_func as GlobalOcean
from aqua.util import load_yaml


class Global_OceanDiagnostic:
    def __init__(self, model, exp, source, config_filename="config.yaml"):
        self.config = load_yaml(config_filename)
        self.reader = Reader(model=model, exp=exp, source=source)
        self.data = self.reader.retrieve()[["ocpt", "so"]]
        self.data = self.data.rename({"nz1": "lev"})

        self.hovmoller_config = self.config.get("hovmoller_plot", {})
        self.time_series_config = self.config.get("time_series", {})
        self.multilevel_trend_config = self.config.get("multilevel_trend", {})
        self.zonal_mean_trend_config = self.config.get("zonal_mean_trend", {})

    def process_data(self):
        self.data = self.data.resample(time="Y").mean()

    def plot_profile(self):
        fn.hovmoller_plot(
            self.data,
            region=self.hovmoller_config.get("region"),
            latS=self.hovmoller_config.get("latS"),
            latN=self.hovmoller_config.get("latN"),
            lonE=self.hovmoller_config.get("lonE"),
            lonW=self.hovmoller_config.get("lonW"),
            type=self.hovmoller_config.get("type"),
            output=self.hovmoller_config.get("output", False),
            output_dir=self.hovmoller_config.get("output_dir", "output")
        )

        fn.time_series(
            self.data,
            region=self.time_series_config.get("region"),
            latS=self.time_series_config.get("latS"),
            latN=self.time_series_config.get("latN"),
            lonE=self.time_series_config.get("lonE"),
            lonW=self.time_series_config.get("lonW"),
            type=self.time_series_config.get("type"),
            customise_level=self.time_series_config.get("customise_level", False),
            levels=self.time_series_config.get("levels"),
            output=self.time_series_config.get("output", False),
            output_dir=self.time_series_config.get("output_dir", "output")
        )

        fn.multilevel_t_s_trend_plot(
            self.data,
            region=self.multilevel_trend_config.get("region"),
            latS=self.multilevel_trend_config.get("latS"),
            latN=self.multilevel_trend_config.get("latN"),
            lonE=self.multilevel_trend_config.get("lonE"),
            lonW=self.multilevel_trend_config.get("lonW"),
            type=self.multilevel_trend_config.get("type"),
            customise_level=self.multilevel_trend_config.get("customise_level", False),
            levels=self.multilevel_trend_config.get("levels"),
            output=self.multilevel_trend_config.get("output", False),
            output_dir=self.multilevel_trend_config.get("output_dir", "output")
        )

        fn.zonal_mean_trend_plot(
            self.data,
            region=self.zonal_mean_trend_config.get("region"),
            latS=self.zonal_mean_trend_config.get("latS"),
            latN=self.zonal_mean_trend_config.get("latN"),
            lonE=self.zonal_mean_trend_config.get("lonE"),
            lonW=self.zonal_mean_trend_config.get("lonW"),
            output=self.zonal_mean_trend_config.get("output", False),
            output_dir=self.zonal_mean_trend_config.get("output_dir", "output")
        )

    def run(self):
        self.process_data()
        self.plot_profile()
