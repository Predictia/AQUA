# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)

## [Unreleased]

Unreleased in the current development version (target v0.18.0):
Removed:
-  removed old OutputSaver (#2146) 

Workflow modifications:
- `aqua-analysis.py` is now an entry point `aqua analysis` in the AQUA console, with the same syntax as before.

AQUA core complete list:
- Data extraction (LRA) can be done without regrid option and LRA log history is more accurate (#2142)
- Split out plotting function for vertical profile and add contour option (#2190)
- GSV update to v2.13.1, support for Polytope access to MN5 DataBridge (#2202)
- Separation of concerns in LRA between dask-based computation and serial netcdf writing (#2212)
- Refactor `grids-downloader.sh` script, now outputdir is a cli argument (#2209)
- Refactor of some `aqua.util.time` function, improving name and pandas integration (#2205,#2218)
- Refactor of the `dump_yaml` utility function, now correctly handling `None` values as `null` (#2198)
- `Reader` will now turn off areas and grids capabilities when `src_grid_name` is `False` (#2198)
- LRA and `OutputSaver` jinja-related duplicated methods are now merged (#2198)
- LatLonProfiles: refinement of the graphical functions (#2201)
- Minor EC-Earth4 adjustments (#2196)
- Hotfix in catgen for monthly chunking (#2184)
- Fix loaded areas as dataset (#2174)
- Show error message if empty data are retrieved by in `reader` (#2170)
- Few graphical adjustments in multiple_maps (#2159)
- Add description for ECmean diagnostic (#2158)
- Fix fldstat coordinate treatment (#2147)
- Fixer applied when units name changes is required and no factor is found (#2128)
- Update aqua-analysis config for refactored diagnostics (#2144)
- Fixed incompatible coordinate transformatiosn (#2137)
- Added Nord4 support in the `load-aqua-container.sh` script (#2130)
- Add `aqua analysis` to replace the `aqua-analysis.py` script, with a more flexible CLI interface (#2065)
- Bugfix in `plot_seasonalcycles()` trying to use a non-existing `time` coordinate (#2114)
- Add `norm` keyword argument to the `plot_single_map` to allow non-linear colorbar normalisation (#2107)
- `draw_manual_gridlines()` utility function to draw gridlines on cartopy maps (#2105)
- `apply_circular_window()` utility function to apply a circular window to cartopy maps (#2100)

AQUA diagnostics complete list:
- Add `source_oce` option for ECmean to aqua anlysis (#2246)
- Add missing center time option to seasonalcycles (#2247)
- Teleconnections: adapted MJO to the new Hovmoller graphical function (#1969)
- Ocean Drift: Hovmoller multiplot class and complete diagnostic cli (#1969)
- Diagnostic core: Locking of catalog yaml when modified (#2238)
- Timeseries: fix output figure to use diagnostic name (#2240)
- Diagnostic core: bugfix in Diagnostic class related to parsing realization (#2226)
- Updated grouping file for dashboard (#2241)
- Dummy: removed old diagnostic (#2210)
- Diagnostic core: `retrieve` and `_retrieve` methods can take a `months_required` argument so that diagnostics can raise an error if insufficient months of data are available. (#2205)
- Timeseries: introduction of the catalog entry capability, default in CLI (#2198)
- Diagnostic core: introduction of the catalog entry capability and `self.realization` attribute (#2198)
- Ensemble: Updating the ensemble module according the the issue #1925 (#2004)
- Timeseries: refined title and description, more attributes used (#2193)
- New LatLonProfiles diagnostic tool (#1934 and #2207)
- Boxplots: add support for reader_kwargs (#2149)
- Global Biases: add the `diagnostic_name` option in config file (#2159)
- Gregory: refined the reference label generation (#2157)
- Seaice: add support for `reader_kwargs` (#2153)
- Remove old seaice diagnostic scripts (#2152)
- Timeseries: fix lazy calculation of seasonal cycles (#2143)
- Boxplots: fix output dir (#2136) 
- Boxplots: add tests and update docs (#2129)
- Seaice: refactored diagnostic with cli and added bias plot with custom projections (#1684, #2140, #2165, #2171, #2178, #2185, #2221)
- Stratification: Stratification class to create density and mixed layer depth data, notebook and tests added. (#2093)
- Radiation: complete refactor of the diagnostic, now based on the `Boxplots` diagnostic and the  `boxplot ` function in graphics (#2007)
- SeasonalCycles: fix a bug which was preventing to plot when no reference data is provided (#2114)

## [v0.17.0]

Main changes are:
1. Support for realizations for `aqua-analysis`, `aqua-push` and a set of diagnostics (Timeseries, Global Biases, Teleconnections, Ecmean)
2. Support for data-portfolio v2.0.0
3. LRA output tree refactored accomodating for realization, statistic and frequency

Removed:
-  removed Reader.info() method (#2076) 

Workflow modifications:
- `machine` and `author` are mandatory fields in the catalog generator config file.
- Data portfolio required is v2.0.0, no API changes are involved in this change.
- Add possibility to change the 'default' realization in Catalog Generator config file.
- AQUA analysis can take a `--realization` option to enable the analysis of a specific realization.

AQUA core complete list:
- Introduce a tentative command to generate grids from sources, `aqua grids build` based on `GridBuilder` class (#2066)
- Support for data-portfolio v2.0.0: updated catalog generator, pinned gsv to v2.12.0. Machine now required in config. (#2092)
- Add possibility to change the 'default' realization in Catalog Generator config file (#2058) 
- `aqua add <catalog>` option in the AQUA console can use GITHUB_TOKEN and GITHUB_USER environment variables to authenticate with GitHub API (#2081)
- Added a `aqua update -c all` option in the AQUA console to update all the catalogs intalled from the Climate-DT repository (#2081)
- `Reader` can filter kwargs so that a parameter not available in the intake source is removed and not passed to the intake driver (#2074)
- Adapt catgen to changes in data-portfolio v1.3.2 (#2076)
- Add `get_projection()` utility function for selection of Cartopy map projections (#2068)
- Tools to push to dashboard support ensemble realizations (#2070)
- `aqua-analysis.py` now supports a `--realization` option to enable the analysis of a specific realization (#2041, #2090)
- Separate new histogram function in the framework (#2061)
- Introducing `timsum()` method to compute cumulative sum (#2059)
- `EvaluateFormula` class to replace the `eval_formula` function with extra provenance features (#2042)
- Solve fixer issue leading to wrong target variable names (#2057)
- Upgrade to `smmregrid=0.1.2`, which fixes coastal erosion in conservative regridding (#1963)
- Refactor LRA of output and catalog entry creatro with `OutputPathBuilder` and `CatalogEntryBuilder` classes (#1932)
- LRA cli support realization, stat and frequency (#1932)
- Update to the new STACv2 API for Lumi (#2039)
- `aqua add` and `aqua avail` commands now support a `--repository` option to specify a different repository to explore (#2037)
- `AQUA_CONFIG` environment variable can be set to customize the path of the configuration files in `aqua-analysis.py` (#2027)
- Development base container updated to stack 7.0.2.8 (#2022, #2025)
- `Trender()` class provide also coefficients and normalize them (#1991)
- Catalog entry builder functionality for diagnostics included in OutputSaver Class (#2086)

AQUA diagnostics complete list:
- Sea-ice extent and volume: bugs related to use of legacy reader functionality (#2111)
- Ocean Trends: Trends class to create trend data along with zonal trend, notebook and tests added. (#1990)
- Global Biases: allow GlobalBias to take projection as argument (#2036)
- ECmean: diagnostics refactored to use `OutputSaver` and new common configuration file (#2012)
- ECmean: dependency to 0.1.15 (#2012)
- Timeseries, Global Biases, Teleconnections, Ecmean: `--realization` option to select a specific realization in the CLI (#2041)
- Global Biases: add try-except block in cli (#2069)
- Global Biases: handling of formulae and Cloud Radiative Forcing Computation (#2031)
- Global Biases: pressure levels plot works correctly with the CLI (#2027)
- Timeseries: `diagnostic_name` option to override the default name in the CLI (#2027)
- Global Biases: output directory is now correctly set in the cli (#2027)
- Timeseries: `center_time` option to center the time axis is exposed in the CLI (#2028)
- Timeseries: fix the missing variable name in some netcdf output (#2023)
- Diagnostic core: new `_select_region` method in `Diagnostic`, wrapped by `select_region` to select a region also on custom datasets (#2020, #2032)

## [v0.16.0]

Removed:
- Removed source or experiment specific fixes; only the `fixer_name` is now supported.

Workflow modifications:
- Due to a bug in Singularity, `--no-mount /etc/localtime` has to be implemented into the AQUA container call 
- `push_analysis.sh` now updates and pushes to LUMI-O the file `experiments.yaml`, which is used by the 
  dashboard to know which experiments to list. The file is downloaded from the object store, updated and 
  pushed back. Additionally it exit with different error codes if the bucket is missing or the S3 credential
  are not correct.

AQUA core complete list:
- Update to the new STAC API for Lumi (#2017)
- Added the `aqua grids set` command to set the paths block in the `aqua-config.yaml` file, overwriting the default values (#2003)
- Derivation of metadata from eccodes is done with a builtin python method instead of definiton file inspection (#2009, #2014)
- `h5py` installed from pypi. Hard pin to version 3.12.1 removed in favor of a lower limit to the version (#2002)
- `aqua-analysis` can accept a `--regrid` argument in order to activate the regrid on each diagnostics supporting it (#1947)
- `--no-mount /etc/localtime` option added to the `load_aqua_container.sh` script for all HPC (#1975)
- Upgrade to eccodes==2.41.0 (#1890)
- Fix HPC2020 (ECMWF) installation (#1994)
- `plot_timeseries` can handle multiple references and ensemble mean and std (#1988, #1999)
- Support for CDO 2.5.0, modified test files accordingly (v6) (#1987)
- Remove DOCKER secrets and prepare ground for dependabot action e.g introduce AQUA_GITHUB_PAT (#1983)
- `Trender()` class to include both `trend()` and `detrend()` method (#1980)
- `cartopy_offlinedata` is added on container and path is set in cli call, to support MN5 no internet for coastlines download (#1960)
- plot_single_map() can now handle high nlevels with a decreased cbar ticks density (#1940)
- plot_single_map() now can avoid coastlines to support paleoclimate maps (#1940)
- Fixes to support EC-EARTH4 conversion to GRIB2 (#1940)
- Added support for TL63, TL255, eORCA1, ORCA2 grids for EC-EARTH4 model (#1940)
- `FldStat()` as independent module for area-weighted operations (#1835)
- Refactor of `Fixer()`, now independent from the `Reader()` and supported by classes `FixerDataModel` and `FixerOperator` (#1929) 
- Update and push to lumi-o the a file listing experiments needed by the dashboard (#1950)
- Integration of HEALPix data with `plot_single_map()` (#1897)
- Use scientific notation in multiple maps plotting to avoid label overlapping (#1953)

AQUA diagnostics complete list:
- Diagnostic core: a `diagnostic_name` is now available in the configuration file to override the default name (#2000)
- Ecmean, GlobalBiases, Teleconnections: regrid functionality correctly working in cli (#2006)
- Diagnostic core: updated docs for `OutputSaver` (#2010)
- Diagnostic core: save_netcdf() is now based on the new OutputSaver (#1965)
- Diagnostic core: raise an error if retrieve() returns an empty dataset (#1997)
- GlobalBiases: major refactor (#1803, #1993)
- Ocean Drift: using the `_set_region` method from the `Diagnostic` class (#1981)
- Diagnostic core: new `_set_region` method in `Diagnostic` class to find region name, lon and lat limits (#1979)
- Timeseries: regions are now in the `definitions` folder (not `interface` anymore) (#1884)
- Teleconnections: complete refactor according to the Diagnostic, PlotDiagnostic schema (#1884)
- Radiations: timeseries correctly working for exps with enddate before 2000 (#1940)
- Diagnostic core: new `round_startdate` and `round_enddate` functions for time management (#1940)
- Timeseries: fix in the new cli wich was ignoring the regrid option and had bad time handling (#1940)
- Timeseries: Use new OutputSaver in Timeseries diagnostics (#1948, #2000)
- Diagnostic core: new `select_region` to crop a region based on `_set_region` and `area_selection` method (#1984)

## [v0.15.0]

Main changes are:
- Polytope support 
- Plotting routines support cartopy projections and matplotlib styles
- Major refactor of AQUA core functionalities: Regridder, Datamodel, OutputSaver, Timstat  
- Major refactor of Timeseries, SeasonalCycle, GregoryPlot diagnostics

Removed:
- `aqua.slurm` has been removed.

Workflow modifications:
- `push_analysis.sh` (and the tool `push_s3.py` which it calls) now both return proper error codes if the transfer fails. 0 = ok, 1 = credentials not valid, 2 = bucket not found. This would allow the workflow to check return codes. As an alternative, connectivity could be tested before attempting to run push_analysis by pushing a small file (e.g. with `python push_s3.py aqua-web ping.txt`))

AQUA core complete list:
- Add FDB_HOME to debug logs (#1914)
- Enabling support for DestinE STAC API to detect `bridge_start_date`and `bridge_end_date` (#1895)
- Return codes for push_s3 and push_analysis utilities (#1903)
- Polytope support (#1893)
- Additional stats for LRA and other refinements (#1886) 
- New OutputSaver class (#1837)
- Introduce a `Timstat()` module independent from the `Reader()` (#1832)
- Adapt Catalog Generator to Data-Portfolio v1.3.0 (#1848)
- Introduction of a internal AQUA data model able to guess coordinates and convert toward required target data convention definition (#1862, #1877, #1883)
- Custom `paths` in the `config-aqua.yaml` can now be defined and will take priority over the catalog paths (#1809)
- Remove deprecated `aqua.slurm` module (#1860)
- Refactor of `plot_maps()` and `plot_maps_diff()` functions with projection support and use their single map version internally (#1865)
- Refactor of `plot_single_map()` and `plot_single_map_diff()` functions with projection support (#1854)
- Refactor time handling: replacement of `datetime` objects and of `pd.Timestamp` lists (#1828)
- Fix the `regrid_method` option in the Reader (#1859)
- Add a GitHub Token for downloading ClimateDT catalogs (#1855)
- Ignore `nonlocal` complaints by flake8 (#1855)
- WOCE-ARGO ocean dataset grids and fixes added (#1846)
- Upgrade of base container to FDB 5.15.11 (#1845)
- Matplotlib styles can be set in the configuration file (#1729)
- Graphics refactoring for timeseries plot functions (#1729, #1841)
- Major refactor of the regrid options, with new modular `Regridder()` class replacing `Regrid()` mixin (#1768)
- Refactor of the `retrieve_plain()` function with contextmanager and smmregrid GridInspector (#1768)

AQUA diagnostics complete list:
- Diagnostic core: refinement of OutputSaver metadata and name handling (#1901)
- Diagnostic core: refactor of the documentation folder structure (#1891)
- Timeseries: complete refactor of the timeseries diagnostic according to the Diagnostic, PlotDiagnostic schema (#1712, #1896)

## [v0.14.0]

Main changes are:
- AQUA is now open source
- Documentation is now available on ReadTheDocs
- Attributes added by AQUA are now "AQUA_" prefixed
- A core diagnostic class has been introduced

Removed:
- Support for python==3.9 has been dropped.
- Generators option from the Reader has been removed.

Workflow modifications:
- `aqua_analysis.py`: all the config files are used from the `AQUA_CONFIG` folder. This allows individual run modification kept in the `AQUA_CONFIG` folder for reproducibility.
- `makes_contents.py`: can now take a config file as an argument to generate the `content.yaml` file.
- `push_analysis.sh`: now has an option to rsync the figures to a specified location. Extra flags have been added (see Dashboard section in the documentation).

AQUA core complete list:
- Updated AQUA development container to micromamba 2.0.7 (#1834)
- Updated base container to eccodes 2.40 (#1833)
- Added Healpix zoom 7 grid for ICON R02B08 native oceanic grid (#1823)
- Remove generators from Reader (#1791)
- Fix tcc grib code and add some cmor codes in the convention file (#1800)
- Add a regrid option to cli of relevant diagnostics (#1792)
- Limit estimation of time for weight generation only to regular lon/lat grids (#1786)
- LRA generation can operate spatial subsection (#1711)
- Attributes added by AQUA are now "AQUA_" prefixed (#1790)
- Remove zarr pin (#1794)
- Dropping support for python==3.9 (#1778, #1797)
- Reader intake-xarray sources can select a coder for time decoding (#1778)
- Document use of AQUA on ECMWF HPC2020 (#1782)
- Added history logging for lat-lon in area selection (#1479)
- Cleaner workflow and pytest/coverage configuration (#1755, #1758)
- catalog, model, exp, source info are now stored in the DataArray attributes (#1753)
- Avoid infinite hanging during bridge access (#1733, #1738)
- Enable dependabot to monitor dependencies every month (#1748)
- `eccodes` bump to 2.40.0 (#1747)
- Integrate codecov to monitor coverage and test analytics and remove old bot (#1736, #1737, #1755, #1819)
- Reinitialize `GSVRetriever` instance only when needed (#1733)
- Enable the option to read FDB data info from file, and refactor start/end hpc/bridge dates handling (#1732, #1743, #1762)
- Fix `push_analysis.sh` options and `aqua_analysis.py` config paths (#1723, #1754)
- Enable zip compression for LRA yearly files (#1726)
- Enable publication of documentation on ReadTheDocs (#1699, #1716)
- Adapt Catgen test to the new number of sources for ICON (#1708)
- Added tests for the Hovmoller plot routine (#1532)
- `push_s3` compatibility with `boto3>=1.36.0` (#1704)
- Rsync option for push_analysis.sh (#1689)
- Multiple updates to allow for AQUA open source, including Dockerfiles, actions, dependencies and containers (#1574)

AQUA diagnostics complete list:
- Ensemble: config file structure and tests (#1630)
- Ocean3d: Tests for the Ocean3d diagnostic (#1780)
- Diagnostic core: A common function to check and convert variable units is provided as `convert_data_units()` (#1806)
- Ocean3d: Bug fix to regridding of observations in cli (#1811)
- Diagnostic core: the `retrieve()` method uses internally a `_retrieve()` method that returns instead of updating attributes (#1763)
- Diagnostic core: documentation about class and config file structure (#1790)
- Diagnostic core: A common function to load the diagnostic config file is provided (#1750)
- Global bias: add test (#1675)
- Diagnostic core: Add additional command-line arguments for configuration and processing options (#1745)
- Global bias: Handling plev and using scientific notation in contour plots (#1649)
- Ecmean: Fix net surface radiative flux and wind stresses in ecmean (#1696)
- Diagnostic core: A common parser and fuctions to open/close the dask cluster are provided (#1703)

## [v0.13.1]

Main changes are:
1. Ocean3d major refactoring

AQUA core complete list:
- Fixer delete option accepts non-lists (#1687)
- Ansi color 8-bit fix for logger (#1671)
- Hotfix for unmatched string in catgen (#1672)
- Test for aqua-analysis.py (#1664)
- Fix in the catgen now correctly generating an automatic description if not provided (#1662)

AQUA diagnostics complete list:
- Diagnostic core: added a Diagnostic class to be inherited by all diagnostics (#1681)
- Timeseries: hotfix of problems with the catalog usage in output saving (#1669)
- Tropical Rainfall: Update of the precomputed histograms paths for lumi and MN5 (#1661)
- Ocean3d: Trend is calculating using polyfit. Restructed the mixed layer depth function. (#1651)
- Global bias: hotfix for regrid option (#1670)

## [v0.13.0]

Main changes are:
1. Grids updated to work with operational O-25.1
2. Compliance of the catalog generator to the O-25.1 data portfolio
3. New 'Biases and Radiation' diagnostics replace the old 'AtmGlobalMean and Radiation'
4. Push of figures to LUMI-O and improvements for aqua-web

Deprecated:
- `aqua-analysis.sh` script is deprecated and has been removed. Use `aqua-analysis.py` instead.
- `cli_dummy.py` script is deprecated and will be removed in the next release. Use the `cli_checker.py` instead.
 
AQUA core complete list:
- More general checksum checker for grids and observations ( #1550)
- Output dir including catalogue for aqua-analysis.py (#1640)
- Grids for O-25.1 cycle are added in the grids folder (they are v3) (#1647)
- `deltat` for fixer can now be specified in source metadata and not only in fixes (#1626)
- LRA generator integrates ``--rebuild`` flag to regenerate areas and weights. The `--autosubmit` option is removed (#1623)
- Hotfix for catgen tests (#1648)
- Experiment and dashboard metadata are now created with the catalog generator (#1637)
- Safety checks according to data frequency for HPC, bridge and request start/end dates in intake GSV (#1636, #1655)
- Experiment metadata for aqua-web and dashboard from catalog entry (#1633)
- Automatic identification of ocean grid in the catalog generator (#1621)
- `OutputSaver` can deduce the catalog name from the model, exp (#1627)
- Pin zarr<3.0.0 to avoid breaking changes (#1625)
- Units utility are now functions and not methods of FixerMixin (#1558)
- New `cli_checker.py` tool to check the existance of the required model in the catalog and rebuild the area files (#1619)
- Update the catalog generator to align with changes in the data portfolio (#1593)
- Adding ICON phase2 hpx6 and hpz9 grids (#1596)
- Push figures to LUMI-O for dashboard (#1582, #1607)
- Bridge_start_date and expver switching (#1597)
- Include all available figure metadata in content.json for dashboard/aqua-web (#1573)
- Upgrade LUMI module to 24.03 and to eccodes 2.39.0

AQUA diagnostics complete list:
- Old AtmoGlobalMean and Radiation diagnostics removed (#1622)
- `--catalog` is accepted by all the diagnostics altough it is not used by all of them yet (#1619)
- Timeseries: enabled region selection in the CLI (#1564)
- Ocean3d: Bugfix of values for Ocean trend function (#1583)
- Biases and Radiation: Refactoring of Bias and Radiation Diagnostics (#1243)
- Biases and Radiation: Fix Seasonal Bias Output in global_biases for NetCDF Saving Compatibility and other fixes (#1585, #1604, #1628)
- Biases and Radiation: Adding `save_netcdf` flag and function (#1510)
- Biases and Radiation: Integrating Updated OutputSaver (#1487)

## [v0.13-beta]

Main changes are:
1. All the diagnostics are now compatible with the new fixes and eccodes version.
2. Full compatibility with HealPix grids and the new CDO version.
3. Major improvements in the Ocean3D diagnostic.

AQUA core complete list:
- Safety checks and error messages on FDB folders (#1512)
- Refreshed internal `to_list` function (#1512)
- Reorganizing and extending CI/CD catalog with 5 years of hpz3 data from ERA5 (atm) and FESOM (oce) (#1552)
- Version info in a separate module (#1546) 
- Corrected `tcc` units to % (#1551)
- Fix pdf attributes (#1547)
- Catgen fixes (#1536)
- Introduced fixer for ClimateDT phase 2 (#1536)
- `aqua_analysis.py` using a common central dask cluster (#1525)
- Added the `cdo_options: "--force"` to the definitions of the oceanic HealPix grids (#1539)

AQUA diagnostic complete list:
- ECmean: Integrating the performance indices and global mean within the `aqua_diagnostics` module (#1556)
- Teleconnections: The `teleconnections` diagnostic is now integrated in the `aqua_diagnostics` module (#1352)
- Teleconnections: OutputSaver for the teleconnections diagnostic (#1567, #1570)
- Ocean3d: Fix to improve memory usage and cli (#1490)
- Seaice: Fix to read sithick as fallback instead of sivol (#1543)
- Ocean3d: Minor fix to allow to read new variable names (#1540)
- Timeseries: The `timeseries` diagnostic is now integrated in the `aqua_diagnostics` module (#1340)
- Timeseries: Integrating Updated OutputSaver (#1492)

## [v0.13-alpha]

Main changes are:
1. A refactor of the fixes, with a new common main convention table is available, based on eccodes.
2. Diagnostics are updated to work with the new fixes and the new eccodes version. This is not yet complete and will be finalized in the next release.
3. The FDB reader always rely on paramids, so that support for eccodes 2.39.0 and backward compatibility is ensured.

AQUA core complete list:
- push-analysis.sh maintenance (#1555)
- Added the `cdo_options: "--force"` to the definitions of the HealPix grids (#1527)
- Removing default fixes (#1519)
- Support for eccodes=2.39.0 with full fixes refactoring (#1519)
- Dashboard: Moved making of contents yaml to local hpc (#1470)
- Support for new smmregrid==0.1.0 including simpler weights and area generation (#1395)
- Removing cdo pin for more recent versions (#1395)
- Change `bridge_end_date` convention (#1498)
- `catgen` to support data bridge options (#1499)
- Enhance OutputSaver with Improved File Handling, Logging, and NetCDF Write Modes (#1495)
- Introduction a specific pipeline and tests for `catgen` utiliy (#1505)
- Remove pin on xarray (#1507)
- FDB reader internally always asks for paramids (#1491, #1508, #1529)
- Introduction of a convention table for the fixer, in order to create a more general fixer (#1488, #1506)
- Refactor of `cli_lra_parallel_slurm.py` to work with container via jinja (#1497) 
- Convert `aqua-analysis.sh` to Python with Subprocess and Multiprocessing Support (#1354, #1521)
- New base container for aqua-container (#1441)
- Autodetection of latest AQUA in `load-aqua-container.sh` script (#1437)
- Update Metadata Handling for NetCDF, PDF, and PNG Outputs (#1430)
- Add instructions to install AQUA on MN5 (#1468)
- Introduce `grids-checker.py` tool to verify presence and checksum of the grid files (#1486)

AQUA diagnostic complete list:
- Tropical Cyclones: Adaptation to IFS-FESOM and tool to compute orography from data (#1393)
- Seaice: Hotfix for sea ice plots (#1432)

## [v0.12.2]

Main changes are: 
1. Single container script to be used on Lumi, MN5 and Levante

AQUA core complete list:
- Introduce `timeshift` option for the fixer to roll forward/back the time axis (#1411)
- Centralize and refactor in single script the tool to load AQUA container (#1413)
- Add extra maintenance options to submit-aqua-web (#1415)
- Update push-analysis.sh removing dependency on full AQUA and option not to convert to png (#1419)
- Pin to xarray<2024.09 to prevent bug in polyfit requires temporary (#1420)
- Remove spurious dimensions when running `fldmean()` (#1423)

AQUA diagnostic complete list:
- Refactor of plotThickness method in the sea ice diagnostic (#1427)


## [v0.12.1]

AQUA core complete list:
- Allow multiple realizations in fdb-catalog-generator (#1335)
- Fix the container loading script in order to avoid load of local libraries (#1399)
- Fix using AQUA container for submit-aqua-web, do not wipe old figures by default (#1387)
- New `timstat` module which opens complement `timmean()` with `timmax()`, `timmin()` and `timstd()` methods (#1391)
- Fix installation to avoid mismatch between `hdf5` and `h5py` libraries (#1408)

## [v0.12]

Main changes are:
1. AQUA installation now requires a mandatory machine name.
2. The `aqua` source code has been moved to the `src` folder. The change is transparent to the user.
3. A diagnostic module, called `aqua.diagnostics`, is under development. The module is not yet active, diagnostics are still available with the previous structure.

AQUA core complete list:
- Mixed updates to support data for NextGEMS cycle4 hackathon (#1375)
- Preprocess functionality added to the `Reader` class (#1298)
- The AQUAthon material has been moved under the `notebooks` folder (#1342)
- `aqua` source code has been moved to the `src` folder (#1332)
- A diagnostic module, called `aqua.diagnostics`, has been created under the `src` folder (#1332, #1341)
- LRA generator tool support for multiple relizations (#1357, #1375)
- LRA generator requires `catalog` as a mandatory argument (#1357)
- AQUA console revisiting, adding `avail` method and `update` method (#1346)
- AQUA install now requires mandatory machine name (#1346)
- Fix to make keyword step optional in request (#1360)

## [v0.11.3]

AQUA core complete list:
- LRA, both from CLI and worklow, is part of the AQUA console and can be run with `aqua lra $options` (#1294)
- FDB catalog generator is part of the AQUA console and can be run with `aqua catgen $options` (#1294)
- Coordinate unit overriding is now possible via the `tgt_units` argument (#1320)
- Full support for python>=3.9 (#1325)
- Pin of (python) eccodes<2.37.0 in pyproject due to recent changes in binary/python structure (#1325)

AQUA diagnostic complete list:
- Radiation: Bugfix in the CLI for the radiation diagnostic (#1319)

## [v0.11.2]

AQUA core complete list:
- Renaming of FESOM grids to include original resolution name (#1312)
- Bugfix of the fdb-catalog-generator tool that was not correctly assigning NEMO grids (#1309)
- Bugfix of the GSV intake driver that was not handling correctly metadata jinja replacement (#1304) 
- Bugfix of _merge_fixes() method when the parent fix has no vars specified (#1310)
- Safety check for the netcdf driver providing more informative error when files are not found (#1307, #1313)

AQUA diagnostic complete list:
- Tropical Rainfall: Fix Minor Issues in Tropical Precipitation CLI Metadata and Formatting (#1266)

## [v0.11.1]

Attention: If you are accessing FDB experiments, we suggest to not use versions older than this release.

Main changes are:
1. AQUA works with FDB written with ecCodes versions > 2.35 as well as lower.
2. Timeseries and Seasonal cyle can now be evaluated also on a specific region 

AQUA core complete list:
- ecCodes now pinned to >=2.36.0 and tool for fixing older definition files (#1302)

AQUA diagnostic complete list:
- Timeseries: a region can be selected for Timeseries and Seasonal Cycle with the `lon_limits` and `lat_limits` arguments (#1299)
- Timeseries: the cli argument for extending the time range is now extend (previously expand) (#1299)
- Timeseries: all the available diagnostics support the catalog argument (#1299)

## [v0.11]

Attention: this version is not compatible with catalog entries with ecCodes >= 2.35.0.

1. LRA supports multi-catalog structure
2. ecCodes temporarily restricted to < 2.34

AQUA core complete list:
- Refactor the fdb-catalog-generator tool to work with data-portfolio repository (#1275)
- Introduce a function to convert NetCDF to Zarr and zarr catalog entry for LRA (#1068)
- Suppress the warning of missing catalogs in the AQUA console `add` command (#1288)
- Lumi installation is completely updated to LUMI/23.09 modules (#1290)
- gsv_intake switches eccodes also for shortname definitions (#1279)
- Increase compatibility between LRA generator and multi-catalog (#1278)
- Allow for intake string replacement within LRA-generated catalogs (#1278)
- Avoid warning for missing intake variable default when calling the `Reader()` (#1287)

AQUA diagnostic complete list:
- Teleconnections: catalog feature bugfix (#1276)

## [v0.10.3]

Attention: this version is not compatible with catalog entries with ecCodes < 2.35.0.

Main changes are:
1. support for ecCodes >= 2.35.0 (to be used with caution, not working with exps with eccodes < 2.35.0)
2. fdb_path is deprecated in favour of fdb_home

AQUA core complete list:
- Restructure fixes folder and files (#1271)
- Removed eccodes pin, better handling of tables in get_eccodes_attr (#1269)
- Added test for diagnostics integration to AQUA installation process (#1244)
- Bugfix for the monthly frequency data with monthly cumulated fluxes (#1255)
- fdb_path becomes optional and deprecated in favour of fdb_home (#1262)
- Branch support for tool to push analysis to explorer (#1273)

AQUA diagnostic complete list:
- ECmean documentation updates (#1264)

## [v0.10.2]

Main changes are:
1. aqua-analysis script can be configured with an external yaml file
2. AQUA installation process now includes diagnostics integration

AQUA core complete list:
- Rename OutputNamer to OutputSaver and add catalog name (#1259)
- Hotfix for rare situation with 3D data but no vertical chunking defined (#1252)
- External yaml file to configure aqua-analysis (#1246)
- Adding diagnostics integration to AQUA installation process (#1229)

AQUA diagnostic complete list:
- Teleconnections: adding the catalog feature to the diagnostic (#1247)
- ECmean upgrades for the CLI (#1241)
- ECmean enables the computation of global mean diagostic (#1241)

## [v0.10.1]

AQUA core complete list:
- Fixer for monthly frequency data with monthly cumulated fluxes (#1201)
- Catalogs can be installed from the external repository (#1182)
- Added grid for NEMO multiIO r100 (#1227)
- Reorganized analysis output in catalog/model/exp structure (#1218)

## [v0.10]

Main changes are:
1. The catalog is externalized and AQUA supports multiple catalogs. It is now mandatory to use the aqua console to add a new catalog to the AQUA installation.

AQUA core complete list:
- Catalog is externalized to a separate repository (#1200)
- AQUA is now capable of accessing multiple catalogs at the same time (#1205)
- MN5 container for AQUA (#1213)

## [v0.9.2]

Main changes are:
1. The `aqua-config.yaml` file is replaced by a template to be installed. The aqua console is now mandatory to use aqua.
2. `$AQUA` removed from the `Configdir()` autosearch, an installation with the aqua console is mandatory to use aqua.
3. AQUA cli command to provide the installation path with `--path` option. This can substitute the `$AQUA` variable in scripts.
4. The catalog file is now split into `machine.yaml` and `catalog.yaml` to support machine dependency of data path and intake variables as kwargs into each catalog.

AQUA core complete list:
- More detailed documentation for Levante and Lumi installation (#1210)
- `aqua-config.yaml` replaced by a template to be installed on each machine (#1203)
- `$AQUA` removed from the `Configdir()` autosearch (#1208)
- AQUA cli command to provide the installation path with `--path` option (#1193)
- Restructure of the `machine` and `catalog` instances to support a catalog based development (#1186)
- AQUA installation via command line support a machine specification `aqua install lumi` (#1186)
- Introduction of `machine.yaml` file to support machine dependency of data path and intake variables as kwargs into each catalog (#1186)
- Removing all the AQUA catalogs from the repo, now using https://github.com/DestinE-Climate-DT/Climate-DT-catalog (#1200)

## [v0.9.1]

Main changes are:
1. Update of fdb libraries to be compatible with the FDB data bridge

AQUA core complete list:
- OutputNamer Class: Comprehensive Naming Scheme and Metadata Support (#998)
- Creation of png figures for AQUA explorer is local (#1189)

## [v0.9]

Main changes are:
1. AQUA has an `aqua` CLI entry point, that allow for installation/uninstallation, catalog add/remova/update, fixes and grids handling
2. Experiments placed half on HPC and half on DataBridge data can be accessed in continuous manner.

AQUA core complete list:
- AQUA entry point for installation and catalog maintanance and fixes/grids handling (#1131, #1134, #1146, #1168, #1169)
- Automatic switching between HPC and databridge FDB (#1054, #1190)
- CLI script for automatic multiple experiment analysis submission (#1160, #1175)

## [v0.8.2]

Main changes are: 
1. `aqua-grids.yaml` file split in multiple files into `grids` folder
2. Container for Levante

AQUA core complete list:
- Removing any machine name depencency from slurm files (#1135)
- Jinja replacement is added to the aqua-config.yaml (#1154)
- grid definitions split in multiple files (#1152)
- Add script to access the container on Levante HPC (#1151)
- Add support for IFS TL63 and TL159 grids (#1150)
- Swift links for tests and grids renewed (#1142)
- Removing the docker folder (#1137)
- Introducing a tool for benchmarking AQUA code (#1057)
- Define AQUA NEMO healpix grids as a function of their ORCA source (#1113)

AQUA diagnostics complete list:
- Tropical Rainfall: Improve Paths in Live Demonstration Notebook  (#1157)
- Atm global mean: produce seasonal bias plots by default (#1140)
- Tropical Rainfall: Notebook for the Live Demonstration (#1112)
- Teleconnections: MJO Hovmoller plot introduced as notebook (#247)
- Tropical Rainfall: Reduce Redundancy in Conversion Functions (#1096)

## [v0.8.1]

Main changes are: 
1. Fixes following internal D340.7.3.3 and D340.7.1.4 review 

AQUA core complete list:
- Tco399-eORCA025 control, historical and scenario runs added to Lumi catalog (#1070)
- ESA-CCI-L4 dataset added for Lumi and Levante catalogs (#1090)
- Various fixes to the documentation (#1106)
- Fixer for dimensions is now available (#1050)

AQUA diagnostics complete list:
- Timeseries: units can be overridden in the configuration file (#1098)
- Tropical Rainfall: Fixing the Bug in the CLI (#1100)

## [v0.8]

Main changes are:
1. Support for Python 3.12
2. Update in the catalog for Levante and introduction of Leonardo
3. Multiple diagnostics improvement to fullfil D340.7.3.3 and D340.7.1.4

AQUA core complete list:
- LRA for ICON avg_sos and avg_tos (#1076)
- LRA for IFS-NEMO, IFS-FESOM, ICON added to Levante catalog (#1072)
- IFS-FESOM storyline +2K added to the Lumi catalog (#1059)
- Allowing for jinja-based replacemente in load_yaml (#1045) 
- Support for Python 3.12 (#1052)
- Extending pytests (#1053)
- More efficient use of `_retrieve_plain` for acessing sample data (#1048)
- Introducing the catalog structure for Leonardo HPC (#1049)
- Introducing an rsync script between LUMI and levante for grids (#1044)
- Introducing a basic jinja-based catalog entry generator (#853)
- Adapt NextGEMS sources and fixes to the final DestinE governance (#1008, #1035)
- Remove  NextGEMS cycle2 sources (#1008)
- Avoid GSVSource multiple class instantiation in dask mode (#1051)

AQUA diagnostics complete list:
- Teleconnections: refactor of the documentation (#1061)
- Tropical rainfall: Updating the Documentation and Notebooks (#1083)
- Performance indices: minor improvements with the inclusion of mask and area files (#1076)
- Timeseries: Seasonal Cycle and Gregory plots save netcdf files (#1079)
- Tropical rainfall: minor modifications to the CLI and fixes to changes in the wrapper introduced in PR #1063 (#1074)
- Tropical rainfall: adding daily variability and precipitation profiles to the cli (#1063)
- Teleconnections: bootstrap evaluation of concordance with reference dataset (#1026)
- SSH: Improvement of the CLI (#1024) 
- Tropical rainfall: adding metadata and comparison with era5 and imerg to the plots, re-binning of the histograms and buffering of the data (#1014)
- Timeseries: refactor of the documentation (#1031)
- Radiation: boxplot can accomodate custom variables (#933)
- Seaice: convert to module, add Extent maps (#803)
- Seaice: Implement seaice Volume timeseries and thickness maps (#1043)

## [v0.7.3]

Main changes are:
1. IFS-FESOM NextGEMS4 and storylines simulations available in the catalog
2. Vertical chunking for GSV intake access
3. FDB monthly average data access is available
4. kwargs parsing of reader arguments (e.g. allowing for zoom and ensemble support)

AQUA core complete list:
- Add kwargs parsing of reader arguments, passing them to intake to substitute parameters (#757)
- Remove `zoom` and use kwargs instead (#757)
- Enabling the memory monitoring and (optional) full performance monitoring in LRA (#1010)
- Adding IFS_9-FESOM_5 NextGEMS4 simulation on levante (#1009)
- Function to plot multiple maps is introduced as `plot_maps()` and documented (#866)
- Adding the IFS-FESOM storylines simulation (#848)
- `file_is_complete()` accounts also for the mindate attribute (#1007)
- Introducing a `yearmonth` timestyle to access FDB data on monthly average (#1001)
- Adding expected time calculation for weight generation (#701)
- Vertical chunking for GSV intake access (#1003)

AQUA diagnostics complete list:
- Timeseries: Various bugfix and improvements for cli and formula (#1013, #1016, #1022)

## [v0.7.2]

Main changes are:
1. `mtpr` is used for precipitation in all the catalog entries
2. LRA CLI support for parallel SLURM submission and other improvements
3. ICON production simulations available in the catalog
4. `detrend()` method is available in the `Reader` class
5. All the diagnostics have dask support in their CLI

AQUA core complete list:
- Fix LRA sources to allow incomplete times for different vars (#994)
- Distributed dask option for diagnostic CLIs and wrapper (#981)
- Added documentation for `plot_timeseries`, `plot_seasonalcycle` and `plot_single_map_diff` (#975)
- Minimum date fixer feature / ICON net fluxes fix (#958)
- Unified logging for all diagnostics (#931)
- A `detrend()` method is added to the Reader class (#919)
- LRA file handling improvements (#849, #972)
- Updating fixer for ERA5 monthly and hourly data on Levante (#937)
- GSV pin to 1.0.0 (#950)
- Adding ICON production simulations (#925)
- LRA CLI for parallel SLURM submission support a max number of concurrent jobs and avoid same job to run (#955, #990)
- Renaming of EC-mean output figures in cli push tool for aqua-web (#930)
- Renaming the `tprate` variable into `mtpr` in all fixes (#944)

AQUA diagnostic complete list:
- Tropical rainfall: enhancements of plotting and performance, files path correction (#997)
- Timeseries: seasonal cycle runs as a separate cli in aqua-analysis for performance speed-up (#982)
- Timeseries: seasonal cycle is added if reference data are not available in some timespan (#974)
- Tropical rainfall: Removing unnecessary printing during the CLI, optimazing the CLi for low and high-resolution data (#963)
- Timeseries: Grergory plot TOA limits are dynamically chosen (#959)
- SSH: technical improvements including removal of hardcoded loglevel and timespan definition. (#677)
- SSH: ready with new data governance and option to plot difference plots added. (#677)
- Atmosferic Global Mean: added mean bias for the entire year in seasonal bias function (#947)
- Tropical Cyclones: working with IFS-NEMO and ICON, includes retrieval of orography from file (#1071).

## [v0.7.1]

Main changes are:
1. Complete update of the timeseries diagnostic
2. LRA CLI for parallel SLURM submission
3. SSP370 production scenario for IFS-NEMO available in the catalog

AQUA core complete list:
- Plot timeseries is now a framework function (#907)
- Improve the automatic parsing of date range according to schema from fdb (#928)
- LRA CLI for parallel SLURM submission (#909)
- Added graphics function to plot data and difference between two datasets on the same map (#892)
- Add IFS-NEMO ssp370 scenario (#906)

AQUA diagnostics complete list:
- Teleconnections: comparison with obs is done automatically in diagnostic CLI (#924)
- Teleconnections: capability to find index file if already present (#926)
- Timeseries: save flag introduced to save to enable/disable saving of the timeseries (#934)
- Improve the automatic parsing of date range according to schema from fdb (#928)
- Updated output filenames for atmglobalmean diagnostic (#921)
- Added graphics function to plot data and difference between two datasets on the same map (#892)
- Implemented `pyproject.toml` for global_time_series diagnostic (#920).
- Implemented `pyproject.toml` for tropical_rainfall diagnostic (#850).
- Updating CLi for tropical_rainfall diagnostic (#815)
- LRA cli for parallel SLURM submission (#909)
- Timeseries: seasonal cycle is available for the global timeseries (#912)
- Timeseries: refactory of Gregory plot as a class, comparison with multiple models and observations (#910)
- Add IFS-NEMO ssp370 scenario (#906)
- Timeseries: complete refactory of the timeseries as a class, comparison with multiple models and observations (#907)
- Plot timeseries is now a framework function (#907)

## [v0.7]

Main changes are:
1. Multiple updates to the diagnostics, both scientific and graphical, to work with more recent GSV data
2. `mtpr` is now used instead of `tprate` for precipitation
2. Documentation has been reorganized and integrated

Complete list:
- New utility `add_pdf_metadata` to add metadata to a pdf file (#898)
- Experiments `a0gg` and `a0jp` added to the IFS-NEMO catalog, and removal of `historical-1990-dev-lowres` (#889)
- Updated notebooks to ensure consistency across different machines by using observational datasets, and included a demo of aqua components for Lumi (#868)
- Scripts for pushing figures and docs to aqua-web (#880)
- Fixed catalog for historical-1990-dev-lowres source (#888, #895)
- data_models src files are now in the aqua/data_models folder, with minor modifications (#884)
- Warning options based on the `loglevel` (#852)
- Timeseries: formula bugfix and annual plot only for complete years (#876)
- mtpr instead of tprate derived from tp (#828)
- eccodes 2.34.0 does not accomodate for AQUA step approach, pin to <2.34.0 (#873)
- Bugfix of the `aqua-analysis` wrapper, now can work teleconnections on atmospheric and oceanic variables 
and the default path is an absolute one (#859, #862)
- Ocean3D: many fixes and adaptations to new data governance (#776)
- Bugfix of the `aqua-analysis` wrapper, now can work teleconnections on atmospheric and oceanic variables (#859)
- Radiation: adaptation to new data governance and many improvements (#727)
- Seaice: Sea ice extent has now seasonal cycle (#797)
- Fixing the paths in `cli/lumi-install/lumi_install.sh` (#856).
- Refactor of the documentation (#842, #871)
- The drop warning in `aqua/gsv/intake_gsv.py` (#844)
- Tropical cyclones diagnostic: working with new data governance (includes possibility to retrieve orography from file (#816)

## [v0.6.3]

Complete list:
- Setting last date for NaN fix for IFS-NEMO/IFS-FESOM to 1999-10-01 and cleaner merge of parent fixes (#819)
- Hotfix to set `intake==0.7.0` as default (#841)
- Timeseries: can add annual std and now default uncertainty is 2 std (#830)
- `retrieve_plain()` method now set off startdate and enddate (#829)
- Complete restructure of fixer to make use of `fixer_name`: set a default for each model and a `False` to disable it (#746)
- Added `center_time` option in the `timmean()` method to save the time coordinate in the middle of the time interval and create a Timmean module and related TimmeanMixin class (#811)
- Fixer to rename coordinates available (#822)
- Fixing new pandas timedelta definition: replacing H with h in all FDB catalog (#786)
- Change environment name from `aqua_common` to `aqua`(#805)
- Adding a run test label to trigger CI (#826)
- Tropical_rainfall: improve organization and maintainability, introducing nested classes (#814)
- Revisiting CERES fixes (#833)
- Timeseries: add bands for observation in Gregory plots (#837)

## [v0.6.2]

Complete list:
- Global time series plot annual and monthly timeseries together, improved Gregory plot (#809)
- Teleconnection can now take a time range as input and ylim in the index plot function (#799)
- LRA to use `auto` final time and `exclude_incomplete` (#791)
- Hotfix for v0.12.0 of the GSV_interface related to valid_time (#788)
- Global time series adapted to new data governance (#785)
- AtmoGlobalMean diagnostic improvements and adaptation to new data governance (#745 #789 #807 #812)
- Sea-ice diagnostic adapted to new data governance (#790)
- Implement a fix setting to NaN the data of the first step in each month (for IFS historical-1990) (#776)

## [v0.6.1]

Complete list:
- Teleconnection improvement to accept different variable names for ENSO (avg_tos instead of sst) (#778)
- ERA5 fixes compatible with new data governance (#772)
- Update the LRA generator (removing aggregation and improving) filecheck and fix entries for historical-1990-dev-lowres (#772)
- Updates of ECmean to work with production experiments (#773, #780)
- Automatic data start and end dates for FDB sources (#762)

## [v0.6]

Main changes are:
1. Inclusion in the catalog of the historical-1990 production simulations from IFS-NEMO and IFS-FESOM.
2. New fixes that targets the DestinE updated Data Governance

Complete list:
- IFS-FESOM historical-1990-dev-lowres with new data governance added to the catalog (#770)
- AtmoGlobalMean diagnostic improvements (#722)
- Teleconnections diagnostic improvements (#722)
- Read only one level for retrieving 3D array metadata, select single level for retrieve (#713)
- IFS-FESOM historical-1990-dev-lowres with new data governance added to the catalog
- Fix mismatch between var argument and variables specified in catalog for FDB (#761)
- Compact catalogs using yaml override syntax (#752)
- Fix loading source grid file before smmregrid weight generation (#756)

## [v0.5.2-beta]

Complete list:
-  A new fdb container is used to generate the correct AQUA container

## [v0.5.2-alpha]

Main changes are:
1. Coupled models IFS-NEMO and IFS-FESOM are now supported
2. Accessor to use functions and reader methods as if they were methods of xarray objects, see [notebook](https://github.com/DestinE-Climate-DT/AQUA/blob/main/notebooks/reader/accessor.ipynb)
3. Preliminary provenance information is now available in the history attribute of the output files
4. AQUA analysis wrapper is parallelized
5. A levelist can be provided in FDB sources, this will greatly speed up the data retrieve

Complete list:
- Fix reading only one sample variable and avoid _bnds variables (#743)
- Allow correct masked regridding after level selection. Add level selection also for not-FDB sources (#741)
- Read only one level for retrieving 3D array metadata, select specific levels for FDB retrieve (#713)
- Defining catalog entry for coupled models IFS-NEMO and IFS-FESOM (#720)
- Change fixer_name to fixer_name (#703)
- Reorganization of logging calls (#700)
- Accessor to use functions and reader methods as if they were methods of xarray objects (#716)
- Suggestions are printed if a model/exp/source is not found while inspecting the catalog (#721)
- Improvements in the single map plot function (#717)
- Minor metadata fixes (logger newline and keep "GRIB_" in attrs) (#715)
- LRA fix now correctly aggregating monthly data to yearly when a full year is available (#696)
- History update and refinement creating preliminary provenance information (plus AQUA emoji!) (#676)
- OPA lra compatible with no regrid.yaml (#692)
- Introducing fixer definitions not model/exp/source dependents to be specified at the metadata level (#681)
- AQUA analysis wrapper is parallelized and output folder is restructured (#684, #725)

## [v0.5.1]

Main changes are:
1. A new `Reader` method `info()` is available to print the catalog information
2. Grids are now stored online and a tool to deploy them on the `cli` folder is available

Complete list:
- Fix attributes of DataArrays read from FDB (#686)
- Reader.info() method to print the catalog information (#683)
- Simpler reader init() by reorganizing the calls to areas and regrid weights configuration and loading (#682)
- Optional autosearch for vert_coord (#682)
- plot_single_map adapted to different coordinate names and bugfixes (#680)
- Sea ice volume datasets for the Northern Hemisphere (PIOMAS) and the Southern Hemisphere (GIOMAS) (#598)
- Possibility of defining the regrid method from the grid definition (#678)
- Grids stored online and tool to deploy them on cli folder (#675)
- Global time series diagnostic improvements (#637)
- Teleconnections diagnostic improvements (#672)

## [v0.5]

Main changes are:
1. Refactor of the Reader() interface with less options at the init() level
2. Grids are now defined with the source metadata and not in a machine-dependent file
3. CLI wrapper is available to run all diagnostics in a single call
4. Refactoring of the streaming emulator with equal treatment for FDB or file sources

Complete list:
- Controlling the loglevel of the GSV interface (#665)
- Fix wrong fdb source (#657)
- Adding sample files and tests for NEMO 2D and 3D grids (#652)
- tprate not derived from tp for GSV sources (#653)
- Simplify reader init and retrieve providing less argument in initialization (#620)
- var='paramid' can be used to select variables in the retrieve method (#648)
- configdir is not searched based on util file position in the repo (#636)
- Cleaner mask treatment (Revision of mask structure in the reader #617)
- Fldmean fix if only one dimension is present for area selection (#640)
- Adding higher frequency ERA5 data on Levante and Lumi (#628)
- regrid.yaml files are removed, grid infos are now in the catalog metadata (#520, #622, #643)
- Load all available variables in FDB xarray/dask access (#619)
- Lint standard and enforced in CI (#616)
- Reader init split with methods (#523)
- Single map plot utility to be used by all diagnostics (#594)
- Script for automatic generation of Fdb catalog entries (IFS only) (#572)
- Fix loading of singularity mounting /projappl (#612)
- CLI wrapper parser (#599)
- Refactoring of streaming emulator (#593)
- Radiation CLI and diagnostic refinement (#537)
- Ocean3D CLI and diagnostic refinement (#578)
- AtmGlobalMean CLI and diagnostic refinement (#587)
- Tropical cyclones CLI refinements and TC module (#568, #645)
- Removing OPA, OPAgenerator and related tests from the AQUA (Remove OPA from AQUA #586)
- Renaming the experiments according to the DE340 AQUA syntax (Including dev-control-1990 in the source and rename the experiment according to DE340 scheme #556, #614, #618)
- Teleconnections diagnostic improvements (#571, #574, #576, #581, #592, #623)

## [v0.4]

Main changes are:
1. Update to all the diagnostics CLI
2. Refactor of the regridder so that `regrid.yaml`` is grid-based and not experiment-based
3. Xarray access to FDB sources
4. Refactor of the fixer so that merge/replace/default options are available
5. Remove of the `aqua` environment in favour of the `aqua_common` one. 

Complete list:
- Introduced color scheme for aqua logging (#567)
- CLI for sea diagnostic (#549)
- Add CLI for SSH diagnostic and some bug fixes (#540)
- Fix SSH diagnostic to be compatible with lates AQUA version (#538) 
- Helper function to identify vertical coordinates in a dataset (#552)
- Orography for tempest extremes TCs detection and update TCs CLI (Orography threshold included and CLI update #404)
- Improvement of performance indices CLI (Update of ECmean CLI #528)
- Fix to allow reading a list of multiple variables from FDB (#545)
- Further improvement of function to inspect the catalog (#533)
- Custom exceptions for AQUA (#518)
- Speed up of the `retrieve_plain` method (#524)
- Update documention for adding new data and setting up the container (Increase documentation coverage #519)
- CLI wrapper for the state-of-the-art diagnostics analysis (#517, #527, #525, #530, #534, #536, #539, #548, #549, #559)
- Refactor the regrid.yaml as grid-based instead of experiment-based (#291)
- aqua_common environment simplified and updated (#498)
- Update available variables in FDB catalogs on lumi (#514)
- Solve reversed latitudes bug for fixed data (#510)
- Switch to legacy eccodes tables based on intake source metadata (#493)
- Add GPM IMERG precipitation data to the catalog on levante (#505)
- Fix ocean3d diagnostic colorbars not being symmetric when missing values are present (#504) 
- FDB NEMO test access to data (#488)
- Xarray dask access to FDB (#476)
- Issue a warning when multiple gribcodes are associated to the same shortname (Cases for multiple eccodes grib codes #483)
- Allowing fixer to overwrite or merge default configuration (Increasing flexibiity of the fixer allowing for merge, replace and default options #480)
- Add new tests (Increase testing #250)
- Global time series diagnostic setup for multiple variables CLI (#474)
- Option to avoid incomplete chunk when averagin with timmean (Introduce check for chunk completeness in timmean() #466)
- Simplification of Fixer() workflow, more methods and less redundancy (Functionize fixer #478)
- Remove the `aqua` environment file, only `aqua_common` is left (#482)

## [v0.3]

Main changes are:
1. Fixer moved at `Reader()` level
2. Area selection available in `fldmean()` method
3. FDB/GSV access for IFS-NEMO development simulations
4. Configuration file `config-aqua.yaml` replaces `config.yaml`

Complete list:
- Templates in configuration yaml files (#469)
- Bug fixes for FDB access options (#463, #462)
- Add observational catalogs on Lumi (Update Lumi catalog #454)
- Automatic finding of cdo (#456)
- Area is fixed if data are fixed (Fixer applied to grid areas #442)
- Tests missing failure fix (Fix #436 CI workflow passes even if some tests fail #452)
- FDB/GSV access to IFS control and historical simulations (#434, #458)
- Climatology support restored in the Reader (Fix for climatology #445)
- Improvement function to inspect the catalog (Inspect_catalog improvement #446)
- Minor improvements of the gribber (Fix gribber fdb #427)
- Allow the LRA generator to work with generators and so with FDB (LRA from fdb on mafalda #430)
- Fixes only on selected variables (Fixer updates #428)
- Complete revision of the FDB/GSV access, allowing to access also recent experiments using variable step (#343)
- Teleconnections diagnostic adapted to new code improvements (Teleconnections Dev branch update #424, #465)
- Add support for area selection with fldmean (Fldmean box selection #409)
- Environment simplified, dependencies are now mostly on the pyproject file (A simpler environment.yml #286)
- Intake esm functionality added back (Fix intake-esm #287)
- Intake esm tests (Test also intake-esm #335)
- Yaml dependencies removed (Logger and yaml issues in util.py #334)
- Log history working for iterators as well (Logger and yaml issues in util.py #334)
- Util refactor (Utility refactor #405)
- Fixer at reader level (Fixes at Reader level #244)
- Uniform timmean (Uniform time after timmean and add option for time_bnds #419)
- FDB tests added (Add FDB 5.11, a local FDB with some test data #280, #432)
- Refactor of unit conversion and non-metpy cases (Flexible unit fix from YAML file #416)
- Refactor of the config file definition (Refactor of the configuration search #417)

## [v0.2.1]

- Add development control-1950 and historical-1990 experiments to the LRA (LRA for control-1950 and historical-1990 on Levante from v0.2 #455)

## [v0.2]

- Improve the LRA generator and worklow CLI (Streaming for the LRA #289)
- AQUA new common environment installation tool for LUMI added (#413)
- Added a bash script "load_aqua_lumi.sh" to load aqua environment in LUMI with containers (Adding an AQUA singularity container for LUMI #418)

## [v0.2-beta]

This is the `AQUA` version part of the Deliverable D340.7.1.2. 

- SSH diagnostic improvements (Linting SSH diagnostics #377, SSH diag: PDF file name changed #388)
- Timmean fix to uniform time axis (Fix for timmean() to uniform output time axis #381)
- New tests trigger routine (Tests trigger with label #385)
- Fix for tco1279 and FESOM (fix for masked tco1279 #390, psu fix for salinity #383)
- ECmean improvements (various improvement for ecmean #392)
- Seaice diagnostic improvements (Deliverable340.7.1.2 fix seaice #389, Linting Seaice diagnostics #376)
- Teleconnections diagnostic graphics module enhanced and various improvements (Teleconnections corrections for D340.7.1.2 #379, Fix import in teleconnections notebooks #395, Teleconnections fix docs #408)
- Tropical cyclones linting of the diagnostic (Linting tropical cyclones diagnostics #380, Improved plotting functions for tropical cyclones #391)
- Ocean diagnostics restructured in a single folder, sharing common functions and other improvements (Linting+Fixes Ocean diagnostics #374, Adding units for MLD plot in ocean3d package #406)
- Documentation fixes (Documentation fixes after review #403)
- Atmglobalmean and radiation diagnostic improvements (Atmglobalmean fix #371)
- MSWEP fixer bugfix (Change MSWEP datamodel #397, fixing of mswep #401)

## [v0.2-alpha]

This is the `AQUA` version that will be part of the Deliverable D340.7.1.2, sent to internal review. This is mostly done by the inclusion of twelve diagnostics within the AQUA framework

- Added teleconnections diagnostic (#308, #309, #318, #333, #352)
- Added tropical cyclones diagnostic (#310, #345)
- Added performance indices diagnostic based on ECmean tool (#57, #327) 
- Added sea ice diagnostic (#353, #368)
- Added global timeseries diagnostic (#358, #359)
- Added radiation analysis diagnostic (#301, #360)
- Added global mean bias diagnostic (#285, #371)
- Added SSH variability diagnostic (#367, #369)
- Added tropical rainfall diagnostic (#314)
- Added Ocean circulation diagnostic (#295)
- Added global ocean diagnosc (#164)
- Added global mean timeseries (#268)
- Multiple fixes in the Reader (#316, #324, #334)
- Avoid time duplicated in the Reader (#357)
- Enabling autodoc for diagnostics (#330)
- Data access improvement on Levante, including new datasets (#332, #355, #321)
- Added a common environment file (#363)
- Support for Lumi installation (#315)
- Added the `changelog` file

### Changed

- Dummy diagnostic is now in the `dummy` folder (previously was `dummy-diagnostic`)
- Tests and code is now working with python>=3.9 (previously python 3.11 was excluded)

## [v0.1-beta]

This is the `AQUA` version that will be part of the Deliverable D340.7.1.1.
This is mostly built on the `AQUA` `Reader` class which support for climate model data interpolation, spatial and temporal aggregation and conversion for a common GRIB-like data format.


- Low resolution archive documentation
- Fixed a bug in the `Gribber` class that was not reading the correct yaml catalog file

## v0.1-alpha

This is the AQUA pre-release to be sent to internal reviewers. 
Documentations is completed and notebooks are working.

[unreleased]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.17.0...HEAD
[v0.17.0]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.16.0...v0.17.0
[v0.16.0]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.15.0...v0.16.0
[v0.15.0]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.14.0...v0.15.0
[v0.14.0]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.13.1...v0.14.0
[v0.13.1]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.13.0...v0.13.1
[v0.13.0]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.13-beta...v0.13.0
[v0.13-beta]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.13-alpha...v0.13-beta
[v0.13-alpha]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.12.2...v0.13-alpha
[v0.12.2]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.12.1...v0.12.2
[v0.12.1]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.12...v0.12.1
[v0.12]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.11.3...v0.12
[v0.11.3]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.11.2...v0.11.3
[v0.11.2]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.11.1...v0.11.2
[v0.11.1]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.11...v0.11.1
[v0.11]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.10.3...v0.11
[v0.10.3]:https://github.com/DestinE-Climate-DT/AQUA/compare/v0.10.2...v0.10.3
[v0.10.2]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.10.1...v0.10.2
[v0.10.1]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.10...v0.10.1
[v0.10]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.9.2...v0.10
[v0.9.2]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.9.1...v0.9.2
[v0.9.1]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.9...v0.9.1
[v0.9]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.8.2...v0.9
[v0.8.2]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.8.1...v0.8.2
[v0.8.1]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.8...v0.8.1
[v0.8]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.7.3...v0.8
[v0.7.3]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.7.2...v0.7.3
[v0.7.2]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.7.1...v0.7.2
[v0.7.1]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.7...v0.7.1
[v0.7]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.6.3...v0.7
[v0.6.3]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.6.2...v0.6.3
[v0.6.2]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.6.1...v0.6.2
[v0.6.1]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.6...v0.6.1
[v0.6]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.5.2-beta...v0.6
[v0.5.2-beta]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.5.2-alpha...v0.5.2-beta
[v0.5.2-alpha]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.5.1...v0.5.2-alpha
[v0.5.1]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.5...v0.5.1
[v0.5]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.4...v0.5
[v0.4]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.3...v0.4
[v0.3]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.2.1...v0.3
[v0.2.1]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.2...v0.2.1
[v0.2]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.2-beta...v0.2
[v0.2-beta]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.2-alpha...v0.2-beta
[v0.2-alpha]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.1-beta...v0.2-alpha
[v0.1-beta]: https://github.com/DestinE-Climate-DT/AQUA/compare/v0.1-alpha...v0.1-beta
