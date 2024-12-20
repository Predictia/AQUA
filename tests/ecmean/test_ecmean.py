"""Test for full pipeline of ecmean"""

import os
import pytest
from aqua import Reader
from aqua.util import load_yaml, ConfigPath
from aqua.diagnostics import performance_indices, global_mean

@pytest.mark.ecmean
def test_ecmean_generic(tmp_path):

    Configurer = ConfigPath()
    loglevel = 'warning'
    ecmeandir = os.path.join(Configurer.configdir, 'diagnostics', 'ecmean')
    interface = os.path.join(ecmeandir, 'interface_AQUA_climatedt.yaml')
    config = os.path.join(ecmeandir, 'ecmean_config_climatedt.yaml')
    config = load_yaml(config)
    config['dirs']['exp'] = ecmeandir

    exp = 'era5-hpz3'
    reader = Reader(model='ERA5', exp=exp, source='monthly', catalog='ci', 
                    regrid='r100')
    data = reader.retrieve()
    data = reader.regrid(data)

    performance_indices(exp, 1990, 1994, numproc=2, config=config,
                            interface=interface, loglevel=loglevel,
                            outputdir=tmp_path, xdataset=data)
    
    global_mean(exp, 1990, 1994, numproc=2, config=config,
                            interface=interface, loglevel=loglevel,
                            outputdir=tmp_path, xdataset=data)