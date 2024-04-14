from ocean3d.ocean_drifts.tools import *
from ocean3d.ocean_drifts.hovmoller_plot import hovmoller_plot


class time_series:
    def __init__(self, o3d_request):
        self.data_dict = o3d_request.get('data_dict')
        self.region = o3d_request.get('region', None)
        self.lat_s = o3d_request.get('lat_s', None)
        self.lat_n = o3d_request.get('lat_n', None)
        self.lon_w = o3d_request.get('lon_w', None)
        self.lon_e = o3d_request.get('lon_e', None)
        self.level = o3d_request.get('level', None)
        self.output = o3d_request.get('output')
        self.output_dir = o3d_request.get('output_dir', None)
        self.loglevel = o3d_request.get('loglevel',"WARNING")

    def _calculate_time_series(self):
        self.data_time_series = {}
        for data_name in self.data_dict:
            processed_data, self.type, cmap  = data_process_by_type(
                data=self.data_dict[data_name], anomaly=True, standardise=True, anomaly_ref='t0', loglevel=self.loglevel)
            
            self.data_time_series[data_name] = processed_data.mean("lat").mean("lon")
            # self.data_time_series[data_name] = self.data_time_series[data_name].load()
            
        return 

    def plot(self):
        self._calculate_time_series()

        dim1 = 16
        dim2 = 6 * 5
        fig, axs = plt.subplots(nrows= 5, ncols=2, figsize=(dim1, dim2))
        fig.subplots_adjust(hspace=0.18, wspace=0.15, top=0.95)
        
        # avg_thetao_levels = np.linspace(self.min_values["avg_thetao"], self.max_values["avg_thetao"], num=18)
        # avg_so_levels = np.linspace(self.min_values["avg_so"], self.max_values["avg_so"], num=18)
        levels = [0, 100, 500, 1000, 2000, 3000, 4000, 5000]
        
        for num, data_name in enumerate(self.data_time_series):
            data = self.data_time_series[data_name].load()
            start_year = self.data_time_series[data_name].time.dt.year[0].values
            end_year = self.data_time_series[data_name].time.dt.year[-1].values
            
            for level in levels:
                if level != 0:
                    # Select the data at the specified level
                    data_level = data.sel(lev=slice(None, level)).isel(lev=-1)
                else:
                    # Select the data at the surface level (0)
                    data_level = data.isel(lev=0)
            
                # Plot the temperature time series
                data_level.avg_thetao.plot.line(
                    ax=axs[num,0], label=f"{round(int(data_level.lev.data), -2)}")

                # Plot the salinity time series
                data_level.avg_so.plot.line(
                    ax=axs[num,1], label=f"{round(int(data_level.lev.data), -2)}")

            # cs1 = axs[num,0].contourf(data.lon, data.lat, data["avg_thetao"], cmap="coolwarm", levels=avg_thetao_levels)
            # cs2 = axs[num,1].contourf(data.lon, data.lat, data["avg_so"], cmap="coolwarm", levels=avg_so_levels)
            # axs[num, 0].set_facecolor('grey')
            # axs[num, 1].set_facecolor('grey')
            # axs[num, 0].set_ylabel("Latitude (in deg North)", fontsize=9)
            axs[num,0].set_ylabel(f"Pot. Temperature ", fontsize=12)
            axs[num,1].set_ylabel(f"Salinity", fontsize=12)
            axs[num, 1].set_yticklabels([])
            # axs[num, 0].set_xlabel("Longitude (in de East)", fontsize=12)
            # axs[num, 0].set_ylabel("Latitude (in deg North)", fontsize=12)
            if num != len(self.data_time_series)-1:
                axs[num, 0].set_xticklabels([])
                axs[num, 1].set_xticklabels([])
            axs[0,0].set_title(f"Pot. Temperature", fontsize=18)
            axs[0,1].set_title(f"Salinity", fontsize=18)
            axs[num, 0].text(-0.22, 0.33, f"{data_name} \n ({start_year}-{end_year}) " , fontsize=18, color='black', rotation=90, transform=axs[num, 0].transAxes, ha='center')
           
        axs[0,1].legend(loc='right')
           
        # cb = fig.colorbar(cs1, ax=axs, location="bottom", pad=0.05, aspect=40, label='Mixed layer depth (in m)')
        # plt.subplots_adjust(bottom=0.30)

        # cb1 = fig.colorbar(cs1, ax=axs[num,0], location="bottom", pad=0.2, aspect=40, label=f'Pot Temp trend in {data.avg_thetao.attrs["units"]}')
        # cb_pos = cb1.ax.get_position()
        # cb1.ax.set_position([cb_pos.x0, -0.05, cb_pos.width, cb_pos.height])
        
        # cb2 = fig.colorbar(cs2, ax=axs[num,1], location="bottom", pad=0.2, aspect=40, label=f'Salinity trend in {data.avg_thetao.attrs["units"]}')
        # cb_pos = cb2.ax.get_position()
        # cb2.ax.set_position([cb_pos.x0, -0.02, cb_pos.width, cb_pos.height])
        
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