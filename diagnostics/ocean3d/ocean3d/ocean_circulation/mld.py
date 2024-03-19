from .ocean_circulation import *
from ocean3d import split_ocean3d_req

class MLD:
    def __init__(self, o3d_request):
        split_ocean3d_req(self, o3d_request)
        self.logger = log_configure(self.loglevel, 'stratification')


    def data_for_plot_spatial_mld_clim(self, data):
        data = area_selection(data, self.region, self.lat_s, self.lat_n, self.lon_w, self.lon_e)
        data = convert_variables(data)
        data = compute_mld_cont(data)
        data, self.time = data_time_selection(data, self.time)
        return data.mean("time")


    def plot(self):
        if self.overlap:
            self.obs_data = crop_obs_overlap_time(self.data, self.obs_data)
            self.data = crop_obs_overlap_time(self.obs_data, self.data)

        mod_clim  = self.data_for_plot_spatial_mld_clim(self.data)  # To select the month and compute its climatology
        obs_clim = self.data_for_plot_spatial_mld_clim(self.obs_data)  # To select the month and compute its climatology
        myr1 = self.data.time.dt.year[0].values
        myr2 = self.data.time.dt.year[-1].values

        oyr1 = self.obs_data.time.dt.year[0].values
        oyr2 = self.obs_data.time.dt.year[-1].values

        mod_clim = mod_clim["rho"].load()
        obs_clim = obs_clim["rho"].load()
    

        self.logger.info("Spatial MLD plot is in process")
        fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(20, 6.5))

        region_title = custom_region(region= self.region, lat_s= self.lat_s, lat_n= self.lat_n, lon_w= self.lon_w, lon_e= self.lon_e)
        title = f'Climatology of {self.time.upper()} mixed layer depth in {region_title}'
        fig.suptitle(title, fontsize=20)
        fig.set_figwidth(18)

        clev1 = 0.0
        clev2 = np.max(obs_clim)
        
        if clev2 < 200:
            inc = 10
            clev2 = round(int(clev2), -1)
        elif clev2 > 1500:
            inc = 100
            clev2 = round(int(clev2),-2)
        else:
            inc = 50
            clev2 = round(int(clev2), -2)

        nclev = int(clev2/inc)+1
        clev2 = float(clev2)

        cs1 = axs[0].contourf(mod_clim.lon, mod_clim.lat, mod_clim,
                            levels=np.linspace(clev1, clev2, nclev), cmap='jet')
        fig.colorbar(cs1, location="bottom", label='Mixed layer depth (in m)')

        cs1 = axs[1].contourf(obs_clim.lon, obs_clim.lat, obs_clim,
                            levels=np.linspace(clev1, clev2, nclev), cmap='jet')

        fig.colorbar(cs1, location="bottom", label='Mixed layer depth (in m)')


        axs[0].set_title(f"Model climatology {myr1}-{myr2}", fontsize=18)
        axs[0].set_ylabel("Latitude", fontsize=14)
        axs[0].set_xlabel("Longitude", fontsize=14)
        axs[0].set_facecolor('grey')

        axs[1].set_title(f"EN4 OBS climatology {oyr1}-{oyr2}", fontsize=18)
        axs[1].set_xlabel("Longitude", fontsize=14)
        axs[1].set_yticklabels([])
        axs[1].set_facecolor('grey')

        plt.subplots_adjust(top=0.85, wspace=0.1)

        if self.output:
            filename = file_naming(self.region, self.lat_s, self.lat_n, self.lon_w, self.lon_e, plot_name=f"{self.model}-{self.exp}-{self.source}_spatial_MLD_{self.time}")
            write_data(self.output_dir,f"{filename}_mod_clim", mod_clim)
            write_data(self.output_dir,f"{filename}_obs_clim", obs_clim)
            export_fig(self.output_dir, filename , "pdf", metadata_value = title, loglevel= self.loglevel)

        plt.show()
        return
