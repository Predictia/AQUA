#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
AQUA tool to evalute speedo of some methods
'''

import argparse
import sys
import dask
from dask.distributed import Client, LocalCluster
import pandas as pd
from timeit import timeit
from aqua import Reader
from aqua import __version__ as version
from aqua.logger import log_configure

print('AQUA version is: ' + version)

def parse_arguments(arguments):
    """
    Parse command line arguments for the LRA CLI
    """

    parser = argparse.ArgumentParser(description='AQUA Benchmarker')
    parser.add_argument('-w', '--workers', type=str, default='1',
                        help='number of dask workers')
    parser.add_argument('-l', '--loglevel', type=str, default='WARNING',
                        help='log level [default: WARNING]')


    return parser.parse_args(arguments)


class DaskBenchmarker(): 

    @property
    def dask(self):
        """Check if dask is needed"""
        return self.nproc > 1

    def __init__(self, nproc=1, loglevel='WARNING'):

        self.logger = log_configure(loglevel, 'daske')
        self.loglevel = loglevel
        self.nproc = nproc
        self.cluster = None
        self.client = None

    def set_dask(self):
        """
        Set up dask cluster
        """
        if self.dask:  # self.nproc > 1
            self.logger.info('Setting up dask cluster with %s workers', self.nproc)
            #dask.config.set({'temporary_directory': self.tmpdir})
            #self.logger.info('Temporary directory: %s', self.tmpdir)
            self.cluster = LocalCluster(n_workers=self.nproc,
                                        threads_per_worker=1)
            self.client = Client(self.cluster)
        else:
            self.client = None
            dask.config.set(scheduler='synchronous')

    def close_dask(self):
        """
        Close dask cluster
        """
        if self.dask:  # self.nproc > 1
            self.client.shutdown()
            self.cluster.close()
            self.logger.info('Dask cluster closed')



if __name__ == '__main__':

    args = parse_arguments(sys.argv[1:])
    logger = log_configure(args.loglevel, 'benchmarker')
    nrepeat = 5

    bench = DaskBenchmarker(int(args.workers), args.loglevel)
    bench.set_dask()
    single = timeit(lambda: Reader('ICON', 'historical-1990', 'hourly-hpz10-atm2d'),
                           number=nrepeat)
    out = round(single / nrepeat, 1)
    bench.close_dask()
    print(f'Reader initialization took on average {out} seconds over {nrepeat} runs')


    bench.set_dask()
    reader = Reader('ICON', 'historical-1990', 'hourly-hpz10-atm2d')
    tsteps = 200
    single = timeit(lambda: reader.retrieve(var='2t').isel(time=slice(0,tsteps)).aqua.fldmean().compute(),
                           number=nrepeat)
    out = round(single / nrepeat, 1)
    bench.close_dask()
    print(f'Retrieving {tsteps} timestep of 2d var + fldmean took on average {out} seconds over {nrepeat} runs')
