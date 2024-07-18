#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
AQUA basic tool for generating catalog entries based on jinja
'''

import jinja2
import os
import re
import sys
import argparse
import yaml
from aqua.util import load_yaml, dump_yaml, get_arg
from aqua.logger import log_configure


def parse_arguments(arguments):
    """
    Parse command line arguments 
    """

    parser = argparse.ArgumentParser(description='AQUA FDB entries generator')
    parser.add_argument("-p", "--portfolio", 
                        help="Type of Data Portfolio utilized (production/reduced)")
    parser.add_argument('-c', '--config', type=str,
                        help='yaml configuration file')
    parser.add_argument('-l', '--loglevel', type=str,
                        help='loglevel', default='INFO')

    return parser.parse_args(arguments)

def get_local_grids(portfolio, grids):
    local_grids = grids["common"]
    local_grids.update(grids[portfolio])
    return local_grids

def get_available_resolutions(local_grids, model):
    re_pattern = f"horizontal-{model.upper()}-(.+)"
    resolutions = []

    for key in local_grids:
        match = re.match(re_pattern, key)
        if match:
            resolutions.append(match.group(1))
    return resolutions


def get_levelist(profile, local_grids, levels):
    vertical = profile.get("vertical")
    if vertical is None:
        return None, None
    else:
        level_data = levels[local_grids[f"vertical-{vertical}"]]
        return level_data["levelist"], level_data["levels"]

def get_profile_content(template, profile, resolution, model, dp_version, local_grids, levels):
    grid = local_grids[f"horizontal-{model.upper()}-{resolution}"]
    
    #matching dp grid with aqua grid
    matching_grids = load_yaml("matching_grids.yaml")
    aqua_grid = matching_grids[grid]
    levelist, levels_values = get_levelist(profile, local_grids, levels)

    levtype_str = (
        'atm2d' if profile["levtype"] == 'sfc' else
        'atm3d' if profile["levtype"] == 'pl' else
        'oce2d' if profile["levtype"] == 'o2d' else
        'oce3d' if profile["levtype"] == 'o3d' else
        profile["levtype"]
    )
    
    grid_str = (
        aqua_grid + '-nested' if profile["levtype"] == 'sfc' else
        aqua_grid + '-nested' if profile["levtype"] == 'pl' else

        'nemo-eORCA12-' + aqua_grid + '-nested' if profile["levtype"] == 'o2d' and model == 'ifs-nemo' else
        'fesom-' + aqua_grid + '-nested' if profile["levtype"] == 'o2d' and model == 'ifs-fesom' else
        'icon-' + aqua_grid + '-nested' if profile["levtype"] == 'o2d' and model == 'icon' else

        'nemo-eORCA12-' + aqua_grid + '-nested-3d' if profile["levtype"] == 'o3d' and model == 'ifs-nemo' else
        'fesom-' + aqua_grid + '-nested-3d' if profile["levtype"] == 'o3d' and model == 'ifs-fesom' else
        'icon-' + aqua_grid + '-nested-3d' if profile["levtype"] == 'o3d' and model == 'icon' else

        aqua_grid
    )

    # Construct the source string
    source = f"{frequency}-{aqua_grid}-{levtype_str}"

    kwargs = {
        "dp_version": dp_version,
        "resolution": resolution,
        "grid": grid_str,
        "source": source,
        "levelist": levelist,
        "levels": levels_values,
        "levtype":  profile["levtype"],
        "variables": profile["variables"],
        "param": profile["variables"][0],
        "time": get_time(profile["frequency"])

    }
    return kwargs

def get_time(frequency):
    freq2time = {
        "hourly": '"0000/to/2300/by/0100"',
        "daily": '"0000"',
        "monthly": None
    }
    return freq2time[frequency]


def create_catalog_entry(config, catalog_dir_path, model, all_content):
    # Create output file in model folder
    output_dir = os.path.join(catalog_dir_path, 'catalogs', config['catalog_dir'], 'catalog', model)
    output_filename = f"{config['exp']}.yaml"
    output_path = os.path.join(output_dir, output_filename)

    if os.path.exists(output_path):
        os.remove(output_path)

    with open(output_path, "w", encoding='utf8') as f:
        f.write('sources:\n')
        for content in all_content:
            f.write(f'  {content}\n')

    logger.info("File %s has been created in %s", output_filename, output_dir)

    # Update main.yaml
    main_yaml_path = os.path.join(output_dir, 'main.yaml')

    main_yaml = load_yaml(main_yaml_path)
    main_yaml['sources'][config['exp']] = {
        'description': config['description'],
        'driver': 'yaml_file_cat',
        'args': {
            'path': f"{{{{CATALOG_DIR}}}}/{config['exp']}.yaml"
        }
    }
    dump_yaml(main_yaml_path, main_yaml)

    logger.info("%s entry in 'main.yaml' has been updated in %s", config['exp'], output_dir)


if __name__ == '__main__':

    # parsing
    args = parse_arguments(sys.argv[1:])

    dp_version = get_arg(args, 'portfolio', 'production')
    config_file = get_arg(args, 'config', 'config.yaml')
    loglevel = get_arg(args, 'loglevel', 'WARNING')

    logger = log_configure(loglevel, 'FDB catalog generator')
    logger.info("Running FDB catalog generator") 

    # reading config file
    with open("config.yaml", 'r') as config_file:
        config = yaml.safe_load(config_file)
    
    dp_dir_path = config["repos"]["data-portfolio_path"]
    catalog_dir_path = config["repos"]["Climate-DT-catalog_path"]
    model = config["model"].lower()
    
    # reading the portfolio file
    dp_file_path =  os.path.join(dp_dir_path, dp_version, 'portfolio.yaml')
    with open(dp_file_path, 'r') as dp_file:
        dp = yaml.safe_load(dp_file)

    # readig the grids file
    grids_file_path = os.path.join(dp_dir_path, dp_version, 'grids.yaml')
    with open(grids_file_path, 'r') as grids_file:
        grids = yaml.safe_load(grids_file)

    portfolio = config["portfolio"]   
    local_grids = get_local_grids(portfolio, grids)

    # readig the levels file
    levels_file_path = os.path.join(dp_dir_path, 'definitions', 'levels.yaml')
    with open(levels_file_path, 'r') as levels_file:
        levels = yaml.safe_load(levels_file)
 
    # jinja2 loading and replacing 
    templateLoader = jinja2.FileSystemLoader(searchpath='./')
    templateEnv = jinja2.Environment(loader=templateLoader, trim_blocks=True, lstrip_blocks=True)

    jinja_file = f"{dp_version}.j2"   
    template = templateEnv.get_template(jinja_file)

    all_content = []

    for profile in dp[model]:
        levtype = profile["levtype"]
        frequency = profile["frequency"]
        resolutions = get_available_resolutions(local_grids, model)
        for resolution in resolutions:
            content = get_profile_content(
                        template, profile, resolution, model, dp_version,
                        local_grids, levels)
            combined = {**config, **content}
            all_content.append(template.render(combined))


    create_catalog_entry(config, catalog_dir_path, model.upper(), all_content)
