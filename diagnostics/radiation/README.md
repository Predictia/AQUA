# Radiation Budget Diagnostic

## Description

This diagnostic computes and plots biases of radiation variables and uses the nextGEMS Cycle 3 data as input.


## Installation Instructions

This diagnostic does not rely on any additional dependencies. You can use the
common python environment provided by the AQUA framework.

## Data requirements

The diagnostic reads various model runs (NextGEMS Cycle 3 at the moment) to
compute and plot the results. In addition, the time series has to be
extended to inclued ERA5 reanalysis data and CERES EBAF as reference.

## Examples

The **notebook/** folder contains the following notebooks:

- time_series.ipynb: a notebook that show how the output of the plot_model_comparison_timeseries: URL
- The gregory.ipynb notebook demonstrates how to produce gregory plots of desired models: URL
- bar_plot.ipynb: a simple demonstration on how to create bar plots 
- bias_maps.ipynb: Creation of bias maps to localise signifikant biases in comparison to CERES data. This is possible for the variables ttr, tsr and tnr and for a desired model year. The notebook produces monthly maps.
   
