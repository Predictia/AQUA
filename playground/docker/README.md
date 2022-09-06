# Examples for running diagnostics using docker

These are a few examples on how we can prepare configuration files and then run diagnostics from docker containers.

Three examples are provided:
   - [ESMValTool](https://github.com/ESMValGroup/ESMValTool): the MiLES blocking recipe is run using the default public esmvaltool docker image.
   - [MiLES](https://github.com/oloapinivad/MiLES): the MiLES tool is used directly from a container to compute blocking statistics. Since no public official container exists we created one using the Docker file `miles/docker/Dockerfile`
   - [PCMDI Metrics Package (PMP)](https://github.com/PCMDI/pcmdi_metrics): the example runs the variability metric, computing DJF NAM EOFs. Since no public official container exists we created one using the Docker file `pmp/docker/Dockerfile`

All three examples share the same notebook `test_rundiagnostic.ipynb` which loads configuration info from two specific yaml files `machine.yaml` and `diagnostic.yaml`. The notebooks only differ in possible postprocessing of the docker output. 
All user configuration occurs in the two yaml files. The examples refer to test data available on our machine (mafalda.polito.it).

