Getting Started
===============

Basic Concepts
--------------

AQUA is designed to simplify the process of running diagnostics on high-resolution climate models. The package is built around a few core concepts:

- Data reading and preprocessing: AQUA supports various climate data formats and provides tools to preprocess the data for further analysis.
- Interpolation and regridding: AQUA offers robust interpolation and regridding functionality to align datasets with different spatial resolutions.
- Averaging and aggregation: AQUA provides tools to perform temporal and spatial averaging and aggregation of climate data.
- Diagnostics: AQUA includes a set of built-in diagnostic tools, and it allows users to create custom diagnostics as well.
- Parallel processing: AQUA supports parallel processing to speed up the execution of diagnostics.

Workflow Overview
-----------------

The typical workflow when using AQUA consists of the following steps:

1. Data preparation: Read and preprocess the input data (e.g., climate model outputs, observations) using AQUA's data handling functions.
2. Interpolation and regridding: Align datasets with different spatial resolutions using AQUA's interpolation and regridding tools.
3. Averaging and aggregation: Perform necessary temporal and spatial averaging or aggregation using AQUA's built-in tools.
4. Diagnostics: Choose and configure the desired diagnostics, either from the built-in set or by creating custom diagnostics.
5. Execution: Run the diagnostics in parallel, if applicable, and collect the results.
6. Analysis and visualization: Analyze the diagnostic results and create visualizations using AQUA's utilities or other Python libraries.

Example Use Case
----------------

To demonstrate a simple use case, we will walk you through an example of using AQUA to calculate the mean temperature for a specific region and period. The following Python code snippet demonstrates this process:

.. code-block:: python

   import AQUA as aqua

   # Read and preprocess data
   data = aqua.read_data("path/to/climate_data.nc")

   # Interpolate and regrid data
   data_regridded = aqua.interpolate_and_regrid(data, target_resolution=1.0)

   # Perform spatial averaging
   region = {"lat_min": -10, "lat_max": 10, "lon_min": -60, "lon_max": -40}
   mean_temperature = aqua.spatial_average(data_regridded, region=region)

   # Print the result
   print(f"Mean temperature for the specified region: {mean_temperature:.2f}°C")

For more detailed examples and tutorials, refer to the Examples and Tutorials section of this documentation or explore the Jupyter notebooks provided with AQUA.
