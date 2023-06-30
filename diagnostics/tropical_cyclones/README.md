# Tropical Cyclones diagnostic for tracking and zoom in

## Description

A diagnostic to identify tropical cyclones (TCs) centres (mean sea level pressure minima) and compute their trajectories based 
on the tempest-extremes python library (https://climate.ucdavis.edu/tempestextremes.php). In addition to detection and tracking
it features the possibility to save selected variables in a box in the vicinity of TCs centres along trajectories.


## Table of Contents

* [Installation Instructions](#installation-instructions)

  - [Installation on Levante](#installation-on-levante)

  - [Installation on Lumi](#installation-on-lumi)

* [Data requirements](#data-requirements)

* [Examples](#examples)

* [Contributing](#contributing)

## Installation Instructions

### Installation on Levante

To install the tropical_cyclones diagnostic on `Levante` you can use conda; the yaml file
`AQUA/diagnostics/tropical_cyclones/env-TCs.yml` to create the dedicated conda environment includes the tempest-extremes package and
all the necessary dependencies to run the tropical cyclones diagnostic.

To install the diagnostic in a new conda environment run:

```bash
conda env create -f env-TCs.yml
```

To install the diagnostic in an existing conda environment run:

```bash
conda env update -f env-TCs.yml
```

To activate the environment run:

```bash
conda activate TCs
```

The diagnostic environment is compatible with python 3.9 and 3.10 and with the AQUA framework.
Different diagnostic environments may be not compatible with each other.
If you want to use multiple diagnostics at the same time, it is recommended to use the different environments for each of them.

### Installation on Lumi 

Not tested yet - To be updated

## Data requirements  

Variables needed to perform TCs detection and tracking through tempest-extremes are:


## Examples

The **notebook/** folder contains the following notebooks:

- **tropical_cyclones.ipynb**: 
  Notebook to explain and demonstrate the tropical cyclones diagnostic. It includes the main diagnostic feature which are the detection and tracking of tropical cyclones (usually performed on low resolution data) and the zoom in feature. The zoom in allows to save
  some selected variables in the vicinity of tropical cyclones centres along their trajectories using original resolution data.

## Contributing

The tempest-extremes library is available at: https://climate.ucdavis.edu/tempestextremes.php
Person responsible dor the development and mainteinance of the tropical cyclones diagnostic is Paolo Ghinassi (p.ghinass@isac.cnr.it)