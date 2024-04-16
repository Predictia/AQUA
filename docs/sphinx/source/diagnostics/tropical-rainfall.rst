Tropical rainfall diagnostic
============================

The precipitation variability is an excellent indicator of the accuracy of climatological simulations.
The goal of tropical rainfall diagnostic is to provide fast and straightforward precipitation analysis in tropical or global areas. 


Description
-----------

The current version of tropical rainfall diagnostic successfully achieves the minimal requirements: 

* calculation of histograms for selected tropical area band,
* calculation of the seasonal mean of precipitation along the latitude or longitude coordinate,
* calculation of the bias between the climatological model and observations, and
* diurnal, i.e., daily variability of precipitation data.
The diagnostic also provides us with simple in-the-use plotting functions to create a graphical representation of obtained results. 


Structure
---------

The Tropical-Rainfall Diagnostic is structured around a main class and associated utility classes, organized across several files to facilitate ease of use and modularity:

#. Core Files:
    - `tropical_rainfall_class.py`: Contains the Tropical_Rainfall class, which includes the constructor and method definitions essential for the diagnostic operations.
    - `pyproject.toml`: Configuration file used to install the diagnostic package.
#. Documentation and Examples:
    - `README.md`: Provides technical installation guidelines and general information about the tropical-rainfall diagnostic.
    - `notebooks/*.ipynb`: A collection of iPython notebooks demonstrating the use of the dummy class and its methods.
#. Configuration:
   - `config-tropical-rainfall.yaml`: A YAML file specifying necessary settings for the physical quantities required for proper diagnostic initialization.
#. Command Line Interface (CLI):
    - `cli_tropical_rainfall.py`: Python script that initializes the **Tropical_Rainfall_CLI** class and contains the actual list of functions to run.
    - `src/tropical_rainfall_cli_class.py` and `src/tropical_rainfall_utils.py`: These files include the CLI class and utility functions that are necessary to utilize the CLI efficiently.
    - `cli_config_trop_rainfall.yml`: A YAML file specifying settings necessary for the CLI execution and physical quantities required for proper diagnostic initialization.
    - `run_cli_tropical_rainfall.sh`: A Bash script that submits the CLI script to the Slurm queue.


Detailed Class Descriptions:

#. `src/tropical_rainfall_main`:
    * Purpose: Serves as the main functional class for the diagnostic, encapsulating key functionalities such as histogram generation and plotting.
    * Key Methods: Includes histogram, histogram_plot, etc.
    * Attributes: Handles major physical quantities such as tropical latitude band (trop_lat), number of histogram bins (num_of_bins), bin width (width_of_bin), and model variables.
#. `src/tropical_rainfall_plots`:
    * Purpose: Manages all plotting functions specific to the diagnostics.
    * Key Methods: Features methods like histogram_plot, plot_of_average, and daily_variability_plot.
    * Attributes: Plotting-specific settings such as PDF format (pdf_format), figure size (figsize), font size (fontsize), line style (linestyle), line width (linewidth), and others. 
      Incorporating these directly into the class allows for uniform styling across plots through initial class setup rather than manual specification for each function.
#. `src/tropical_rainfall_tools`:
    * Purpose: Contains utility functions that support the diagnostic processes but are not directly involved in scientific calculations or plotting.
    * Key Functions: Includes open_dataset, find_files_with_keys, remove_file_if_exists_with_keys, and check_need_for_regridding.
    * Attributes: None
#. `src/tropical_rainfall_meta`:
    * Purpose: Facilitates the importation of methods from nested classes into the main class file for streamlined access and use.
    * Functionality: Allows specific or all methods from nested classes to be treated as methods of the main tropical_rainfall_class.py, simplifying the structure and enhancing the compactness of the diagnostic by segmenting the class into smaller, more manageable units.
    * Attributes: None

This structure and documentation aim to provide clear guidance on the functionality and organization of the Tropical-Rainfall Diagnostic package, making it accessible and easy to use for its intended purposes.



Input variables
---------------
* `mtpr` (total precipitation rate, GRIB paramid 235055)

Output
------
All output of the diagnostic is in the format of NetCDF to be further analysed, or in PDF for rapid visualization. 

Examples
--------

The histogram calculation
^^^^^^^^^^^^^^^^^^^^^^^^^

The most straightforward illustration of a histogram calculation with continuous uniform binning:

.. code-block:: python

      diag = Tropical_Rainfall(num_of_bins = 20, first_edge = 0, width_of_bin = 0.5)
      diag.histogram(ifs)

The default unit of precipitation is set to mm/day. Users can set a new unit either by assigning a new value to the class attribute as shown below
.. code-block:: python

      diag.new_units = 'mm/hr' 
Alternatively, users can pass the **new_units** argument directly to the histogram function.

The output from the histogram function is an xarray.Dataset, which includes two coordinates:

* `center_of_bin`:   the center of each bin
* `width`:           width of each bin

The xarray.Dataset contains three variables: 
* `counts`: the raw number of cases in each bin
* `frequency`: the proportion of cases in each bin, normalized by the total number of cases
* `pdf`: the probability distribution function
* `pdfP`: the probability distribution function multiplied by probability.

The resulting xarray.Dataset features both local and global attributes. The global attribute `history` and local attributes provide details about the temporal and spatial grid used for the diagnostic calculations: `time_band`, `lat_band`, and `lon_band`.

For more detailed information about these attributes, refer to the notebook located at `$AQUA/diagnostics/tropical_rainfall/notebooks/functions_demo/data_attributes.ipynb`.


List of histograms 
^^^^^^^^^^^^^^^^^^

The diagnostic can combine any number of histograms into a single histogram, recalculating 
the frequencies and pdf values and modifying the attributes automatically.

For example, if you want to merge all histograms if the specified repository, set the following flag: **all=True**.

.. code-block:: python

  path_to_histograms="/work/bb1153/b382267/tropical_rainfall_cicle3/NetCDF/histograms/"

  merged_histograms = diag.merge_list_of_histograms(path_to_histograms=path_to_histograms, all=True)

**Reminder**: Store the obtained histograms for distinct models in separate repositories to avoid possible errors. 


The histogram plots 
^^^^^^^^^^^^^^^^^^^

The diagnostic contains the simple in-the-use function to create the histogram plot. 
The user can create plots of the obtained data in  different styles and scales. 
The example of a histogram plot is:

.. code-block:: python

  diag.histogram_plot(histogram, smooth = False, color_map = 'gist_heat', figsize=0.7, 
               xlogscale = True, ylogscale=True)


You can find an example of the histogram obtained with the tropical-rainfall diagnostic below. 

.. figure:: figures/trop_rainfall_icon_ngc3028_ifs_tco2559_ng5_ifs_tco1279_orca025_mswep_lra_r100_monthly_comparison_histogram.png
    :width: 12cm

Seasonal Mean Values
^^^^^^^^^^^^^^^^^^^^

The diagnostic can provide us with a graphical comparison of the mean value along different coordinates. 
For example, the function 

.. code-block:: python

  diag.trop_lat = 90
  diag.mean_and_median_plot(icon_ngc3028, coord='lon',  
                                  legend='icon, ngc3028', new_unit = 'mm/day' )

calculates the mean value of precipitation along the longitude during 

- December-January-February (`DJF`), 
- March-April-May (`MAM`), 
- June-July-August (`JJA`), 
- September-October-November (`SON`), and 
- for the total period of time. 

Bias between model and observations 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Tropical-rainfall diagnostic provides the graphical representation of the bias between the mean value of precipitation of the 
climatological model and the mean value of observations. 
The function 

.. code-block:: python

  diag.plot_bias(icon_ngc3028, dataset_2 = mswep_mon, seasons=True, new_unit='mm/day',  trop_lat=90,  vmin=-10, vmax=10,
                    plot_title='The bias between icon, ngc3028 ans mswep, monthly, 1 degree res (100km)',
                    path_to_pdf=path_to_pdf, name_of_file='icon_ngc3028_mswep_lra_r100_monthly_bias')

calculates the mean value of precipitation for each season  `DJF`, `MAM`, `JJA`, `SON` and  for the total period of time.

Available demo notebooks
------------------------

The notebook folder contains the demonstration of:

#. `Diagnostic Demonstartion on Low_resolution data  <https://github.com/DestinE-Climate-DT/AQUA/blob/main/diagnostics/tropical_rainfall/notebooks/demo_for_lowres_data.ipynb>`_: 
The notebook demonstrates:
    - histogram comparison for different climate models,
    - the ability to merge a few separate plots into a single one, 
    - mean of tropical and global precipitation calculations for different climate models,
    - bias between climatological model and observations. 

#. `Histogram Calculation <https://github.com/DestinE-Climate-DT/AQUA/blob/main/diagnostics/tropical_rainfall/notebooks/functions_demo/histogram_calculation.ipynb>`_: 
   
   The notebook demonstrates the major abilities of tropical rainfall diagnostic: 
    - initialization of an object of the diagnostic class, 
    - selection of the class attributes,  
    - calculation of the histograms in the form of xarray, 
    - saving the histograms in the storage,
    - and loading the histograms from storage.

#. `Histogram Plotting <https://github.com/DestinE-Climate-DT/AQUA/blob/main/diagnostics/tropical_rainfall/notebooks/functions_demo/histogram_plotting.ipynb>`_:

   The notebook demonstrates the abilities of the histogram plotting functions:
    - selection of the plot style: step line style, 2D smooth line style, and different color maps,
    - selection of the plot size, axes scales, 
    - saving plot into storage, 
    - plotting the counts, frequencies, and Probability density function (pdf) from the obtained histograms.

#. `Diagnostic During Streaming <https://github.com/DestinE-Climate-DT/AQUA/blob/main/diagnostics/tropical_rainfall/notebooks/functions_demo/diagnostic_vs_streaming.ipynb>`_:

   The notebook demonstrates the usage of diagnostic during the streaming mode:
    - saving the obtained histogram with the histogram into storage per each chunk of any data during the stream, 
    - loading all or multiple histograms from storage and merging them into a single histogram. 

#. `Data attributes of produced output <https://github.com/DestinE-Climate-DT/AQUA/blob/main/diagnostics/tropical_rainfall/notebooks/functions_demo/data_attributes.ipynb>`_:
....

Detailed API
------------

This section provides a detailed reference for the Application Programming Interface (API) of the "tropical_rainfall" diagnostic,
produced from the diagnostic function docstrings.

.. automodule:: tropical_rainfall
    :members:
    :undoc-members:
    :show-inheritance: