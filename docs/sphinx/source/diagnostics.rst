Diagnostics
===========

Overview of Available Diagnostics
---------------------------------

AQUA provides a collection of built-in diagnostics to analyze climate model outputs. These diagnostics cover a wide range of climate variables and metrics. Some examples of the available diagnostics include:

- Mean state analysis: Calculates the mean state of climate variables over a specified region and time period.
- Extreme events analysis: Identifies and quantifies extreme events, such as heatwaves or heavy precipitation.
- Climate indices: Computes various climate indices, such as the North Atlantic Oscillation (NAO) or El Niño Southern Oscillation (ENSO).
- Trend analysis: Estimates trends and changes in climate variables over time.
- Model evaluation: Compares model outputs against observations or other reference datasets.

Creating Custom Diagnostics
---------------------------

AQUA allows users to create custom diagnostics to suit their specific needs. Custom diagnostics can be implemented as Python functions or classes and integrated into AQUA's diagnostic framework. To create a custom diagnostic, follow these general steps:

1. Define the diagnostic function or class, including its input arguments and expected outputs.
2. Ensure that the diagnostic function or class can handle xarray DataArrays or Datasets as inputs.
3. Register the custom diagnostic with AQUA, providing its name and a reference to the function or class.
4. Optionally, create a configuration file to specify default settings and parameters for the custom diagnostic.

Running Diagnostics in Parallel
-------------------------------

AQUA supports parallel execution of diagnostics to improve performance and reduce computational time. To run diagnostics in parallel, follow these steps:

1. Configure the parallel processing settings, such as the number of threads, processes, or nodes to use.
2. Create a list of diagnostics to execute, either from the built-in set or custom diagnostics.
3. Use AQUA's parallel execution functions to distribute the diagnostics across the available resources.
4. Collect and analyze the diagnostic results once the parallel execution is complete.

Note that not all diagnostics may be suitable for parallel execution. Some diagnostics may have specific requirements or limitations that prevent them from being run in parallel. Consult the documentation for each diagnostic to determine its compatibility with parallel processing.
