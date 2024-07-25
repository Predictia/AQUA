#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
AQUA basic tool for generating catalog entries based on jinja
'''

import os
import re
import sys
import argparse
import jinja2
from aqua.util import load_yaml, dump_yaml, get_arg
from aqua.logger import log_configure
from aqua.lra_generator.lra_util import replace_intake_vars

class AquaFDBGenerator:
    def __init__(self, data_portfolio, config_path, loglevel='INFO'):
        self.dp_version = data_portfolio
        self.config = load_yaml(config_path)
        self.loglevel = loglevel
        self.logger = self.setup_logger()
        self.dp_dir_path = self.config["repos"]["data-portfolio_path"]
        self.catalog_dir_path = self.config["repos"]["Climate-DT-catalog_path"]
        self.model = self.config["model"].lower()
        self.portfolio = self.config["portfolio"]
        
        self.dp = load_yaml(os.path.join(self.dp_dir_path, data_portfolio, 'portfolio.yaml'))
        self.grids = load_yaml(os.path.join(self.dp_dir_path, data_portfolio, 'grids.yaml'))
        self.levels = load_yaml(os.path.join(self.dp_dir_path, 'definitions', 'levels.yaml'))
        
        self.local_grids = self.get_local_grids(self.portfolio, self.grids)
        self.template = self.load_jinja_template(f"{data_portfolio}.j2")

    def setup_logger(self):
        logger = log_configure(self.loglevel, 'FDB catalog generator')
        logger.info("Running FDB catalog generator for %s portfolio", self.dp_version)
        return logger

    @staticmethod
    def parse_arguments(arguments):
        parser = argparse.ArgumentParser(description='AQUA FDB entries generator')
        parser.add_argument("-p", "--portfolio", help="Type of Data Portfolio utilized (production/reduced): Default is production")
        parser.add_argument('-c', '--config', type=str, help='yaml configuration file')
        parser.add_argument('-l', '--loglevel', type=str, help='loglevel', default='INFO')
        return parser.parse_args(arguments)

    @staticmethod
    def get_local_grids(portfolio, grids):
        """
        Get local grids based on the portfolio.

        Args:
            portfolio (str): The portfolio type (production/reduced).
            grids (dict): The grids definition.

        Returns:
            dict: Local grids for the given portfolio.
        """
        local_grids = grids["common"]
        local_grids.update(grids[portfolio])
        return local_grids

    @staticmethod
    def get_available_resolutions(local_grids, model):
        """
        Get available resolutions from local grids.

        Args:
            local_grids (dict): Local grids definition.
            model (str): The model name.

        Returns:
            list: List of available resolutions.
        """
        re_pattern = f"horizontal-{model.upper()}-(.+)"
        resolutions = [match.group(1) for key in local_grids if (match := re.match(re_pattern, key))]
        return resolutions

    @staticmethod
    def get_levelist(profile, local_grids, levels):
        """
        Get the level list from local grids.

        Args:
            profile (dict): Profile definition.
            local_grids (dict): Local grids definition.
            levels (dict): Levels definition.

        Returns:
            tuple: Levelist and levels values.
        """

        vertical = profile.get("vertical")
        if vertical is None:
            return None, None
        level_data = levels[local_grids[f"vertical-{vertical}"]]
        return level_data["levelist"], level_data["levels"]

    @staticmethod
    def get_time(frequency):
        """
        Get time string based on the frequency.

        Args:
            frequency (str): The frequency type (hourly/daily/monthly).

        Returns:
            str: Corresponding time string.
        """

        freq2time = {
            "hourly": '"0000/to/2300/by/0100"',
            "daily": '"0000"',
            "monthly": None
        }
        return freq2time[frequency]

    def load_jinja_template(self, template_file):
        """
        Load a Jinja2 template.

        Args:
            template_file (str): Template file name.

        Returns:
            jinja2.Template: Loaded Jinja2 template.
        """

        templateLoader = jinja2.FileSystemLoader(searchpath='./')
        templateEnv = jinja2.Environment(loader=templateLoader, trim_blocks=True, lstrip_blocks=True)
        return templateEnv.get_template(template_file)

    def get_profile_content(self, profile, resolution):
        """
        Generate profile content based on the given parameters.

        Args:
            profile (dict): Profile definition.
            resolution (str): Resolution value.

        Returns:
            dict: Generated profile content.
        """

        grid = self.local_grids[f"horizontal-{self.model.upper()}-{resolution}"]
        matching_grids = load_yaml("matching_grids.yaml")
        aqua_grid = matching_grids[grid]
        levelist, levels_values = self.get_levelist(profile, self.local_grids, self.levels)

        levtype_str = (
            'atm2d' if profile["levtype"] == 'sfc' else
            'atm3d' if profile["levtype"] == 'pl' else
            'oce2d' if profile["levtype"] == 'o2d' else
            'oce3d' if profile["levtype"] == 'o3d' else
            profile["levtype"]
        )

        grid_mappings = matching_grids['grid_mappings']
        levtype = profile["levtype"]

        if levtype in grid_mappings:
            grid_str = grid_mappings[levtype].get(
                self.model, grid_mappings[levtype].get('default')).format(aqua_grid=aqua_grid)
        else:
            grid_str = grid_mappings['default'].format(aqua_grid=aqua_grid)

        source = f"{profile['frequency']}-{aqua_grid}-{levtype_str}"

        kwargs = {
            "dp_version": self.dp_version,
            "resolution": resolution,
            "grid": grid_str,
            "source": source,
            "levelist": levelist,
            "levels": levels_values,
            "levtype": profile["levtype"],
            "variables": profile["variables"],
            "param": profile["variables"][0],
            "time": self.get_time(profile["frequency"])
        }
        return kwargs

    def create_catalog_entry(self, all_content):
        """
        Create catalog entry file and update main YAML.

        Args:
            all_content (list): List of all generated content strings.
        """
        output_dir = os.path.join(self.catalog_dir_path, 'catalogs', 
                                  self.config['catalog_dir'], 'catalog', self.model.upper())
        output_filename = f"{self.config['exp']}.yaml"
        output_path = os.path.join(output_dir, output_filename)

        if os.path.exists(output_path):
            os.remove(output_path)

        with open(output_path, "w", encoding='utf8') as f:
            f.write('sources:\n')
            for content in all_content:
                f.write(f'  {content}\n')

        self.logger.info("File %s has been created in %s", output_filename, output_dir)

        main_yaml_path = os.path.join(output_dir, 'main.yaml')
        main_yaml = load_yaml(main_yaml_path)
        main_yaml['sources'][self.config['exp']] = {
            'description': self.config['description'],
            'driver': 'yaml_file_cat',
            'args': {
                'path': f"{{{{CATALOG_DIR}}}}/{self.config['exp']}.yaml"
            }
        }
        dump_yaml(main_yaml_path, main_yaml)
        self.logger.info("%s entry in 'main.yaml' has been updated in %s", self.config['exp'], output_dir)

    def generate_catalog(self):
        """
        Generate the entire catalog by processing profiles and resolutions.
        """

        all_content = []

        for profile in self.dp[self.model]:
            resolutions = self.get_available_resolutions(self.local_grids, self.model)
            for resolution in resolutions:
                content = self.get_profile_content(profile, resolution)
                combined = {**self.config, **content}
                self.logger.info('Creating catalog entry for %s', combined['source'])
                for replacepath in ['fdb_home', 'eccodes_path']:
                    combined[replacepath] = '"' + replace_intake_vars(combined[replacepath], catalog=combined['catalog_dir']) + '"'
                all_content.append(self.template.render(combined))

        self.create_catalog_entry(all_content)

if __name__ == '__main__':
    args = AquaFDBGenerator.parse_arguments(sys.argv[1:])
    dp_version = get_arg(args, 'portfolio', 'production')
    config_file = get_arg(args, 'config', 'config.yaml')
    loglevel = get_arg(args, 'loglevel', 'INFO')

    generator = AquaFDBGenerator(dp_version, config_file, loglevel)
    generator.generate_catalog()
