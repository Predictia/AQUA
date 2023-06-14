Tropical rainfall diagnostic
============================

The goal of tropical rainfall diagnostic is to provide fast and straightforward precipitation analysis in tropical or global areas. 

Overview of Available Diagnostics
---------------------------------

The current version of tropical rainfall diagnostic successfully achieves the minimal requirements: it can calculate the histograms 
in the form of xarrays.Dataset, which contains the counts, frequencies, and probability distribution functions (pdf) for specified bins.

Counts, frequencies, and probability are stored in the histograms as a variables and have their local attributes. The essential 
attributes of each variables contain the information about space and time grids for which the user performed the diagnostic. Namely, 
these attributes are information about the time (`time_band`), longitude (`lon_band`), and latitude (`lat_band`) bands, including frequencies.
Also, the time and space grid information is automatically added to the global attribute `history`.


The histograms contain the two coordinates: center (`center_of_bin`) and width (`width`) of each bin. We used two coordinated instead 
of one to allow the user usage of not uniformal binning if needed. 

The diagnostic can merge any set of histograms into one, automatically recalculating the frequencies and pdf values and updating the 
attributes.

The diagnostic contains the simple in-the-use function to create the histogram plot. The user can create plots of the obtained data in 
different styles and scales. 


Main functions of the diagnostic
--------------------------------

