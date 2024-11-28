"""Testing for the catalog generator"""

import subprocess
import os
import pytest
import logging
from aqua.util import load_yaml, dump_yaml

loglevel = "DEBUG"

def load_and_prepare(tmp_path, model, kind, reso):

    config_file = 'tests/catgen/config-test-catgen.j2'

    # to parametriza on models, load the file, do jinja replacement and save it
    definitions = {'model': model, 'kind': kind, 'resolution': reso}
    config = load_yaml(config_file, definitions)
    model_config = f'{tmp_path}/test.yaml'
    
    dump_yaml(model_config, config)

    # Command to run
    command = ["aqua", "catgen", '-p', kind, '-c', model_config, '-l', loglevel]

    # Run the command
    try:
        # Run the command and capture stdout and stderr
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        # Log the output on success
        logging.info(f"Command succeeded with output: {result.stdout}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        # Handle the error and log the details
        logging.error(f"Command failed with error: {e}")
        logging.error(f"Return code: {e.returncode}")
        logging.error(f"stderr: {e.stderr}")
        raise  # Re-raise the exception to allow for higher-level handling if necessary
    except subprocess.SubprocessError as e:
        # Catch any other subprocess-related errors
        logging.error(f"Subprocess error: {e}")
        raise
    except Exception as e:
        # Catch other unforeseen exceptions
        logging.error(f"Unexpected error: {e}")
        raise

    model = config['model']
    exp = config['exp']
    catalog_dir = config['catalog_dir']
    expected_path = os.path.join(config['repos']['Climate-DT-catalog_path'],
                                 'catalogs', catalog_dir, 'catalog', model)

    entry = os.path.join(expected_path, f'{exp}.yaml')
    assert os.path.exists(os.path.join(expected_path, 'main.yaml'))
    assert os.path.exists(entry)

    sources =  load_yaml(entry)
    #os.remove(os.path.join(expected_path, 'main.yaml'))
    #os.remove(entry)

    return sources

@pytest.mark.parametrize(('model,nsources,nocelevels'),
                        [('IFS-NEMO', 4, 75),
                         ('IFS-FESOM', 5, 47)])
@pytest.mark.catgen
def test_catgen_reduced(tmp_path, model, nsources, nocelevels):
    """test for production portfolio"""

    sources = load_and_prepare(tmp_path=tmp_path, model=model, kind='reduced', reso='intermediate')

    # check how many sources
    assert len(sources['sources']) == nsources

    # check number of vertical levels in the atmosphere
    if model == 'IFS-NEMO':
        grid, freq = 'lon-lat', 'monthly'
    elif model == 'IFS-FESOM':
        grid, freq = 'hpz7', 'daily'
    else:
        raise ValueError(f'{model} not supported!')
    assert len(sources['sources'][f'monthly-{grid}-atm3d']['metadata']['levels']) == 19

    # check number of vertical levels in the atmosphere
    assert len(sources['sources'][f'{freq}-{grid}-oce3d']['metadata']['levels']) == nocelevels

@pytest.mark.parametrize(('model,nsources,nocelevels'),
                        [('IFS-NEMO', 30, 75),
                         ('IFS-FESOM', 34, 69),
                         ('ICON', 17, 72)])
@pytest.mark.catgen
def test_catgen_production(tmp_path, model, nsources, nocelevels):
    """test for production portfolio"""

    sources = load_and_prepare(tmp_path, model, 'production', 'production')

    # check how many sources
    assert len(sources['sources']) == nsources

    # check number of vertical levels in the atmosphere
    assert len(sources['sources']['hourly-hpz10-atm3d']['metadata']['levels']) == 19

    # check number of vertical levels in the atmosphere
    assert len(sources['sources']['daily-hpz10-oce3d']['metadata']['levels']) == nocelevels


