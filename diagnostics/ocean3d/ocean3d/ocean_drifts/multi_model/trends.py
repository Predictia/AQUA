from ocean3d.ocean_drifts.tools import *
from ocean3d.ocean_drifts.trends import TrendCalculator 



class surface_trend:
    def __init__(self, o3d_request):
        self.data_dict = o3d_request.get('data_dict')
        # self.model = o3d_request.get('model')
        # self.exp = o3d_request.get('exp')
        # self.source = o3d_request.get('source')
        # self.obs_data = o3d_request.get('obs_data', None)
        self.time = o3d_request.get('time', None)
        self.region = o3d_request.get('region', None)
        self.lat_s = o3d_request.get('lat_s', None)
        self.lat_n = o3d_request.get('lat_n', None)
        self.lon_w = o3d_request.get('lon_w', None)
        self.lon_e = o3d_request.get('lon_e', None)
        self.customise_level = o3d_request.get('customise_level', None)
        self.level = o3d_request.get('level', None)
        self.overlap = o3d_request.get('overlap', None)
        self.output = o3d_request.get('output')
        self.output_dir = o3d_request.get('output_dir', None)
        self.loglevel = o3d_request.get('loglevel',"WARNING")

    def plot(self):
        self.TS_trend_dict = {}
        for i, data_name in enumerate(self.data_dict):
            data = self.data_dict[data_name]
            trend_data_name = f"{data_name}"
            data = area_selection(data, self.region, self.lat_s, self.lat_n, self.lon_w, self.lon_e)
            TS_trend_data = self._calculate_trend_data(data)
            TS_trend_data = TS_trend_data[["avg_thetao","avg_so"]]
            TS_trend_data = TS_trend_data.interp(lev=self.level).squeeze()
            self.TS_trend_dict[trend_data_name] = TS_trend_data.load()
    
        self._plot_multilevel_trend(TS_trend_data)
        return


    def _calculate_trend_data(self, data):
        """
        Calculates the trend data for temperature and salinity.
        """
        TS_trend_data = TrendCalculator.TS_3dtrend(data, loglevel=self.loglevel)
        TS_trend_data.attrs = data.attrs
        return TS_trend_data

    def _plot_multilevel_trend(self, data):
        """
        Plots the multilevel trend for temperature and salinity.
        """  
        cbar_value = {'max_values': {"avg_thetao": [],
                                     "avg_so": []},
                      'min_values': {"avg_thetao": [],
                                     "avg_so": []}}

        for data_name in self.TS_trend_dict:
            data = self.TS_trend_dict[data_name]
            for variable in list(data.data_vars):
                max_value = np.max(data[variable])
                min_value = np.min(data[variable])
                cbar_value['max_values'][variable].append(max_value)
                cbar_value['min_values'][variable].append(min_value)

        self.max_values = {}
        self.min_values = {}

        for variable, values_list in cbar_value['max_values'].items():
            self.max_values[variable] = np.max(values_list)

        for variable, values_list in cbar_value['min_values'].items():
            self.min_values[variable] = np.min(values_list)

            # for variable in [cbar_value['max_values'], cbar_value['min_values']]:
            #     max(max_values_list)
                    
                    

        dim1 = 16
        dim2 = 6 * 5
        fig, axs = plt.subplots(nrows= 5, ncols=2, figsize=(dim1, dim2))
        fig.subplots_adjust(hspace=0.18, wspace=0.15, top=0.95)
        
        avg_thetao_levels = np.linspace(self.min_values["avg_thetao"], self.max_values["avg_thetao"], num=18)
        avg_so_levels = np.linspace(self.min_values["avg_so"], self.max_values["avg_so"], num=18)

        for num, data_name in enumerate(self.TS_trend_dict):
            data = self.TS_trend_dict[data_name]
            cs1 = axs[num,0].contourf(data.lon, data.lat, data["avg_thetao"], cmap="coolwarm", levels=avg_thetao_levels)
            cs2 = axs[num,1].contourf(data.lon, data.lat, data["avg_so"], cmap="coolwarm", levels=avg_so_levels)
            axs[num, 0].set_facecolor('grey')
            axs[num, 1].set_facecolor('grey')
            # axs[num, 0].set_ylabel("Latitude (in deg North)", fontsize=9)
            axs[num, 1].set_yticklabels([])
            # axs[num, 0].set_xlabel("Longitude (in de East)", fontsize=12)
            # axs[num, 0].set_ylabel("Latitude (in deg North)", fontsize=12)
            if num != len(self.TS_trend_dict)-1:
                axs[num, 0].set_xticklabels([])
                axs[num, 1].set_xticklabels([])
            axs[num, 0].text(-0.13, 0.33, data_name, fontsize=18, color='black', rotation=90, transform=axs[num, 0].transAxes, ha='center')
           
        # cb = fig.colorbar(cs1, ax=axs, location="bottom", pad=0.05, aspect=40, label='Mixed layer depth (in m)')
        # plt.subplots_adjust(bottom=0.30)

        cb = fig.colorbar(cs1, ax=axs[num,0], location="bottom", pad=0.1, aspect=40, label=f'Pot Temp trend in {data.avg_thetao.attrs["units"]}')
        cb2 = fig.colorbar(cs2, ax=axs[num,1], location="bottom", pad=0.1, aspect=40, label=f'Salinity trend in {data.avg_thetao.attrs["units"]}')

        region_title = custom_region(region=self.region, lat_s=self.lat_s, lat_n=self.lat_n, lon_w=self.lon_w, lon_e=self.lon_e)
        self.title = f'Linear Trends of T,S at {self.level}m in the {region_title}'
        plt.suptitle(self.title, fontsize=24)
        # if self.output:
        #     self._save_plot_data(data)


    def _save_plot_data(self, data):
        """
        Saves plot data.
        """
        filename = file_naming(self.region, self.lat_s, self.lat_n, self.lon_w, self.lon_e, plot_name=f"{self.model}-{self.exp}-{self.source}_multilevel_t_s_trend")
        write_data(self.output_dir, filename, data.interp(lev=self.levels[-1]))
        export_fig(self.output_dir, filename, "pdf", metadata_value=self.title, loglevel=self.loglevel)
        return