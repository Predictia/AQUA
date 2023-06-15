Tropical rainfall diagnostic
============================

The goal of tropical rainfall diagnostic is to provide fast and straightforward precipitation analysis in tropical or global areas. 

Overview of Available Diagnostics
---------------------------------

The current version of tropical rainfall diagnostic successfully achieves the minimal requirements: it can calculate the histograms 
in the form of xarrays.Dataset, which contains the counts, frequencies, and probability distribution functions (pdf) for specified bins.


The main attributes of `TR_PR_Diagnostic` Class
-----------------------------------------------


The most crucial attributes of the class are:

 - `trop_lat (int or float)`:            

    the latitude of the tropical zone.  
    The default value of the attribute is equal to 10. 
    The user can easily modify the value tropical latitude band. The first way to do that is to set a new default value during the initialization of the class. 
 
  .. code-block:: python

    from tropical_rainfall_class import TR_PR_Diagnostic as TR_PR_Diag
    diag = TR_PR_Diag(trop_lat=20)

  Another way is to modify the tropical latitude after the initialization of the class: 
  
  .. code-block:: python

    diag.trop_lat=15

  The user can modify the latitude band by parsing the argument `trop_lat` to the functions. In this case, not only will a function use a new value of `trop_lat`, 
  but it will also update the class's default value. For example:
  
  .. code-block:: python

    diag.histogram(ifs, trop_lat=90)
    diag.trop_lat
  
  While the user set `trop_lat=90`, the diagnostic will calculate the global precipitation, not tropical. 

  The user can update all class attributes in the way as the `trop_lat` attribute. 

 - `num_of_bins (int)`:            
 
    the number of bins,
 - `first_edge (int, float)`:    
 
    the first edge of the bin,
 - `width_of_bin (int, float)`:  
 
    the width of the bin. If the user initializes the `num_of_bins`, `first_edge`, and  `width_of_bin`,  
    the diagnostic will calculate the 
    histograms with continuous uniform binning, i.e., all bins in the histogram will have the same width.

 - `bins (np.ndarray, list)`:            
 
    the bins.  If the user wants to perform the calculation for non-uniform binning (for example, log-spaced), 
    use the `bins` attribute of the diagnostic instead of `num_of_bins`, `first_edge`, and `width_of_bin`.



- `s_time (int, str)`:          The start time of the time interval. 
- `f_time (int, str)`:          The end time of the time interval. 
- `s_year (int)`:               The start year of the time interval. 
- `f_year (int)`:               The end year of the time interval. 
- `s_month (int)`:              The start month of the time interval. 
- `f_month (int)`:               The end month of the time interval. 

You can specify `s_time` and `f_time` as integers. For example, 
There is the possibility of specifying only the year band or only the months' band. For example, we can select June, July, and August in a whole dataset as
Also, you can specify `s_time` and `f_time` as strings. For example, 

The histogram calculation
-------------------------

The simplest example of a histogram calculation is: 

.. code-block:: python

    diag = TR_PR_Diag(num_of_bins = 20, first_edge = 0, width_of_bin = 1*10**(-5))
    diag.histogram(ifs)

or with the log-spaced binning:

.. code-block:: python

    diag = TR_PR_Diag()

    bins = [1.00000000e-09, 1.63789371e-09, 2.68269580e-09, 4.39397056e-09,
       7.19685673e-09, 1.17876863e-08, 1.93069773e-08, 3.16227766e-08,
       5.17947468e-08, 8.48342898e-08, 1.38949549e-07, 2.27584593e-07,
       3.72759372e-07, 6.10540230e-07, 1.00000000e-06]
    diag.histogram(ifs)




The function provides the opportunity to calculate the histogram with weights. Compared to standard methods, such computations 
are `high-speed` because they are based on `boost_histogram` and `dask_histogram` packages (see `env-tropical-rainfall.yml` file).

.. code-block:: python

    diag.histogram(icon, weights=reader.grid_area)


The output of the histogram function is xarray.Dataset, which has two coordinates 
- `center_of_bin`:   the center of each bin
- `width`:           width of each bin
We used two coordinated instead of one to allow the user usage of not uniformal binning if needed. 
The array.Dataset  contains three variables:
- `counts`:       the number of observations that fall into each bin
- `frequency`:    the number of cases in each bin, normalized by the total number of counts. The sum of the frequencies equals 1.
- `pdf`:          the number of cases in each bin, normalized by the total number of counts and width of each bin. 

local and global attributes. Local attributes contain the information about the time and space grid for which diagnostic performed the calculations:
- `time_band`:    the value of time of the first and last element in the dataset and the frequency of the time grid
- `lat_band`:     the maximum and minimum values of the tropical latitude band and the frequency of the latitude grid
- `lon_band`:     the maximum and minimum values of the longitude and the frequency of the longitude grid

Global attribute `history` contains the information about when the histogram was calculated and values of `time_band`, `lat_band`, and `lon_band`.


The lazy mode 
--------------

Calculation of histogram of global or tropical precipitation can be done in the lazy (or delayed) mode. To perform calculations in the so-called lazy mode, 
use the flag `lazy` in the histogram function. 

  .. code-block:: python

    hist_icon_lazy=diag.histogram(icon, lazy=True)

In the case of lazy calculation, the function's output will be different:  the xarray.DataArray will contain only non-computed counts. If user want 
to add frequency and pdf variables to the histogram Dataset, apply the following function `histogram_to_xarray` (but only when you are actually 
ready to compute the histogram).
The function `data_with_global_atributes` argument is needed to populate Dataset with global attributes. 

  .. code-block:: python

    diag.histogram_to_xarray(hist_counts=hist_icon_lazy, data_with_global_atributes=icon)

The histogram plots 
-------------------

The diagnostic contains the simple in-the-use function to create the histogram plot. The user can create plots of the obtained data in 
different styles and scales. 



Output 
------

The diagnostic already provides unique names for the histograms. Namely, the name of the histogram includes the starting and final time 
steps for which the diagnostic performs the calculations in the following format: `year-month-day-hour`. The name of the file, which you 
specified, would be added at the beginning of the file name. 
For example, for one day of the icon data (freq=30m) the name of the histogram is `icon_2020-01-20T00_2020-01-20T23_histogram.pkl`.


List of histograms 
------------------

The diagnostic can merge any set of histograms into one, automatically recalculating the frequencies and pdf values and updating the 
attributes.


If you want to merge all histograms if the specified repository, set the following flag: `all=True.`

The function will merge all histograms into single histograms. In order to avoid possible mistakes, keep the histograms obtained for 
different models in different repositories. 


If you want to merge only a specific number of histograms, set the function `multi`-argument. 
The function will sort the files in the repository and take the first `multi` number of histograms in the repo.



Notebooks 
---------

The notebook folder contains the following notebooks:

 - `ICON histogram calculation <https://github.com/oloapinivad/AQUA/blob/devel/trop_rainfall_core/diagnostics/tropical-rainfall-diagnostic/notebooks/ICON_histogram_calculation.ipynb>`_: 

    The notebook demonstrates the major abilities of tropical rainfall diagnostic: 
    - initialization of an object of the diagnostic class, 
    - selection of the class attributes,  
    - calculation of the histograms in the form of xarray, 
    - saving the histograms in the storage,
    - and loading the histograms from storage.
 - `ICON histogram plotting <https://github.com/oloapinivad/AQUA/blob/devel/trop_rainfall_core/diagnostics/tropical-rainfall-diagnostic/notebooks/ICON_histogram_plotting.ipynb>`_:

    The notebook demonstrates the abilities of the histogram plotting functions:
    - selection of the plot style: step line style, 2D smooth line style, and different color maps,
    - selection of the plot size, axes scales, 
    - saving plot into storage, 
    - plotting the counts, frequencies, and Probability density function (pdf) from the obtained histograms.
 - `diagnostic during streaming <https://github.com/oloapinivad/AQUA/blob/devel/trop_rainfall_core/diagnostics/tropical-rainfall-diagnostic/notebooks/diagnostic_vs_streaming.ipynb>`_:

    The notebook demonstrates the usage of diagnostic during the streaming mode:
    - saving the obtained histogram with the histogram into storage per each chunk of any data during the stream, 
    - loading all or multiple histograms from storage and merging them into a single histogram. 

 - `histogram_comparison.ipynb`:

    The notebook demonstrates:
    - a simple comparison of obtained histograms for different climate models, 
    - ability to merge a few separate plots into a single one. 

