import os
import subprocess
import xarray as xr
import pandas as pd
from util import clean_files, write_fullres_field

class DetectNodes():
    """Class Mixin to take care of detect nodes"""

    def detect_nodes_zoomin(self):
        """
        Detect nodes for the zoomed-in time range.

        Parameters:
        - self: Reference to the current instance of the class.

        Returns:
        None
        """
        if self.streaming:
            timerange = pd.date_range(start=self.stream_startdate, end=self.stream_enddate, freq=self.frequency)
        else:
            timerange = pd.date_range(start=self.startdate, end=self.enddate, freq=self.frequency)
        
        for tstep in timerange.strftime('%Y%m%dT%H'):
            self.logger.warning(f"processing time step {tstep}")
            self.readwrite_from_intake(tstep)
            self.run_detect_nodes(tstep)
            clean_files([self.tempest_filein])
            self.read_lonlat_nodes()
            self.store_detect_nodes(tstep)

    
    def readwrite_from_intake(self, timestep):
        """
        Read and write data from intake reader for the specified timestep.

        Argss:
        - self: Reference to the current instance of the class.
        - timestep: Timestep for which to read and write the data.

        Returns:
            None
        """

        self.logger.info(f'Running readwrite_from_intake() for {timestep}')

        outfield = 0
        fileout = os.path.join(self.paths['regdir'], f'regrid_{timestep}.nc')

        for var in self.varlist2d:
            self.logger.info(f'Regridding 2D data for {var}')
            lowres = self.reader2d.regrid(self.data2d[var].sel(time=timestep))
            if isinstance(outfield, xr.Dataset):
                if var in '10u':
                    varout = 'u10m'
                elif var in '10v':
                    varout = 'v10m'
                else: 
                    varout = var
                outfield = xr.merge([outfield, lowres.to_dataset(name=varout)])
            else:
                outfield = lowres.to_dataset(name=var)
        
        if self.exp=="tco2559-ng5":
            for var in self.varlist3d:
                self.logger.info(f'Regridding 3D data for {var}')
                lowres = self.reader3d.regrid(self.data3d[var].sel(time=timestep, plev=[30000,50000]))
                outfield = xr.merge([outfield, lowres.to_dataset(name=var)])

            outfield['plev'] = outfield['plev'].astype(float)
            outfield['plev'].attrs['units'] = 'Pa'
            
        elif self.exp=="tco2559-ng5-cycle3":
            for var in self.varlist3d:
                self.logger.info(f'Regridding 3D data for {var}')
                lowres = self.reader3d.regrid(self.data3d[var].sel(time=timestep, plev=[30000,50000]))
                outfield = xr.merge([outfield, lowres.to_dataset(name=var)])

            outfield['plev'] = outfield['plev'].astype(float)
            outfield['plev'].attrs['units'] = 'Pa'
            
        # check if output file exists
        if os.path.exists(fileout):
            os.remove(fileout)
            
        #then write netcdf file for tempest
        self.logger.info('Writing low res to disk..')
        outfield.to_netcdf(fileout)
        outfield.close()
        
        self.tempest_dictionary = {'lon': 'lon', 'lat': 'lat', 
                    'psl': 'msl', 'zg': 'z',
                    'uas': 'u10m', 'vas': 'v10m'}
        self.tempest_filein=fileout

    def read_lonlat_nodes(self):

        """
        Read from txt files output of DetectNodes the position of the centers of the TCs

        Args:

            tempest_fileout: output file from tempest DetectNodes

        Returns: 
        out: dictionary with 'date', 'lon' and 'lat' of the TCs centers
        """

        with open(self.tempest_fileout) as f:
            lines = f.readlines()
        first = lines[0].split('\t')
        date = first[0] + first[1].zfill(2) + first[2].zfill(2) + first[4].rstrip().zfill(2)
        lon_lat = [line.split('\t')[3:] for line in lines[1:]]
        self.tempest_nodes = {'date': date, 'lon': [val[0] for val in lon_lat], 'lat': [val[1] for val in lon_lat]}

    
    def run_detect_nodes(self, timestep) : 

        """"
        Basic function to call from command line tempest extremes DetectNodes
        Args:
            tempest_dictionary: python dictionary with variable names for tempest commands
            tempest_filein: file (netcdf) with low res data
            tempest_fileout: output file (.txt) from DetectNodes command
        Returns: 
            detect_string: output file from DetectNodes in string format 
        """
        
        self.logger.info(f'Running run_detect_nodes() for timestep {timestep}')
        
        tempest_filein = self.tempest_filein
        tempest_dictionary = self.tempest_dictionary
        tempest_fileout = os.path.join(self.paths['tmpdir'], 'tempest_output_' + timestep + '.txt')
        self.tempest_fileout = tempest_fileout

        
        detect_string= f'DetectNodes --in_data {tempest_filein} --timefilter 6hr --out {tempest_fileout} --searchbymin {tempest_dictionary["psl"]} ' \
        f'--closedcontourcmd {tempest_dictionary["psl"]},200.0,5.5,0;_DIFF({tempest_dictionary["zg"]}(30000Pa),{tempest_dictionary["zg"]}(50000Pa)),-58.8,6.5,1.0 --mergedist 6.0 ' \
        f'--outputcmd {tempest_dictionary["psl"]},min,0;_VECMAG({tempest_dictionary["uas"]},{tempest_dictionary["vas"]}),max,2 --latname {tempest_dictionary["lat"]} --lonname {tempest_dictionary["lon"]}'

        subprocess.run(detect_string.split(), stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    def store_detect_nodes(self, timestep, write_fullres=True):

        self.logger.info(f'Running store_detect_nodes() for timestep {timestep}')
        
        # in case you want to write netcdf file with ullres field after Detect Nodes
        if write_fullres:
          # loop on variables to write to disk only the subset of high res files
            for var in self.var2store:

                subselect = self.fullres[var].sel(time=timestep)
                data = self.reader_fullres.regrid(subselect)
                data.name = var
                xfield = self.store_fullres_field(0, data, self.tempest_nodes)
                self.logger.info(f'store_fullres_field for timestep {timestep}')
                store_file = os.path.join(self.paths['fulldir'], f'TC_{var}_{timestep}.nc')
                write_fullres_field(xfield, store_file)
    
