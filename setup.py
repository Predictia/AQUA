#!/usr/bin/env python

from setuptools import setup

setup(name='aqua',
      version='0.0.1',
      description='AQUA; a model evaluation framework for high-resolution climate model simulations',
      author='The AQUA team',
      author_email='p.davini@isac.cnr.it',
      url='https://github.com/oloapinivad/AQUA',
      python_requires='>=3.9, <3.11',
      packages=['aqua'],
      install_requires=[
        'pyYAML',
        'xarray',
        'dask',  
        'numpy',
        'metpy',
        'intake-esm<=2021.8.17',
        'intake',
        'intake-xarray',
        'docker',
        'jinja2'
      ]
    )
