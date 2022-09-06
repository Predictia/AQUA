# AQUA
AQUA model evaluation framework

This repo is thought to host the code development as well as the the discussion for the DE_340 AQUA model evaluation framework. In the first phase, please use it as a playground, including code examples or notebook if you want to show some specific configuration. Please use specific branches to host your development.  

AQUA framework will be based on a series of python3 libraries, mainly `Aqua.preprocess` and `Aqua.postprocess`, that will be coupled with a series of independently running diagnostics. Those pre- and post-processing libraries will be based on the `xarray+dask` framework so that they will be able to exploit out-of-core computation, fundamental to operate on the large volume of expected DE_340 data. 

Diagnostics can be introduced within the AQUA framework making use of a specific python3 subpackage (e.g. `aqua.diagnosticname`) or being accessed via containerized diagnostic (if pre-existing and written in non-python3 language): 

- The first approach requires the rewriting of the tool in modern python3 standard, but might guarantee much longer longevity and more efficient data access, especially for big data. 
- The second approach is less efficient and might incur some technical limitations, but as long as the diagnostic is not modified within the project and treated as a black box guarantees longevity as well. Of course, the biggest advantage of containerization is that it allows for a faster development phase since it reuses available diagnostics. 
