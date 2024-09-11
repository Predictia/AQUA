# Breakout Session Plan: AQUA Analysis 

# Table of Contents

- [Agenda Overview](#agenda-overview)
- [Session Structure](#session-structure)
   1. [Introduction and Overview (1 min)](#1-introduction-and-overview-1-min)
   2. [AQUA Scientific Diagnostics (20 min)](#2-aqua-scientific-diagnostics-20-min)
   3. [AQUA Analyses Wrapper (10 min)](#3-aqua-analyses-wrapper-10-min)
   4. [Running AQUA Analyses (5 min)](#4-running-aqua-analyses-5-min)
   5. [AQUA Analysis Output Review (5 min)](#5-aqua-analysis-output-review-5-min)
   6. [Q&A Session (5 min)](#6-qa-session-5-min)
- [Further Reading and Events](#further-reading-and-events)

---
## Agenda Overview
This session will focus on **Sailing with AQUA:**, which includes running the aqua-analysis tool, modifying configuration files, submitting jobs, and interpreting the outputs.


---

## Session Structure

### 1. **Introduction and Overview (1 min)**
---
- **Objective:** Introduce the session's objectives.
- **Steps:**
  - **1.1** Briefly explain the session purpose and key activities
  - **1.2** Outline the tools that will be used during the session</summary> </details>

<details>
  <summary> 1.1 Briefly explain the session purpose and key activities </summary>
  
  - To demonstrate examples of diagnostics using the AQUA package.
  - To highlight troubleshooting techniques.
  - To show how to run and adjust scientific analyses with AQUA.
  
</details>


<details>
  <summary> 1.2 The tools that will be used during the session </summary>
  
  - **Notes**: Key takeaways and explanations will be provided in markdown notes.
  - **Python Scripts**: Scripts for running the diagnostics and analyses.
  - **Bash Scripts**: Shell scripts for automating tasks and submitting jobs.
  - **YAML Files**: Configuration files to set parameters for the diagnostics.
  - **Jupyter Notebooks**: Interactive notebooks for demonstrating and running analyses.

</details>

---


### 2. **AQUA Scientific Diagnostics (20 min)**
---
- **Objective:** Demonstrate how to use AQUA scientific diagnostics in a Jupyter notebook, showcasing key analytical workflows and outputs.

- **Steps:**


  - **2.1**  [Availibale Diagnostics](#21-availibale-diagnostics)

  - **2.2**  [General Folder Contents](#22-general-folder-contents)
  
  - **2.3** [Comprehensive Example](#24-access-the--notebook-with-comprehensive-example-here)  
    Walk through an example analysis (e.g., Ocean3D, Global Mean Time Series, Atmospheric Global Mean Biases Diagnostics). Explain key functions, their purpose, and outputs.

- **Engagement:**  
  Encourage participants to follow along in real-time, explore the notebook, and ask questions.

#### 2.1 Availibale Diagnostics



<details>
  <summary> Frontier Diagnostics</summary>
These diagnostics offer new insights into climate phenomena that can't be studied with standard-resolution models. Their goal is to showcase the scientific and technical capabilities of high-resolution data from the Digital Twin, working directly with the full temporal and spatial resolution of climate models.
</details>

- [SSH variability](https://github.com/DestinE-Climate-DT/AQUA/tree/aquathon/diagnostics/ssh)
- [Tropical Cyclones detection, tracking, and zoom-in diagnostic](https://github.com/DestinE-Climate-DT/AQUA/tree/aquathon/diagnostics/tropical_cyclones)
- [Tropical rainfall diagnostic](https://github.com/DestinE-Climate-DT/AQUA/tree/aquathon/diagnostics/tropical_rainfall)

<details>
  <summary> State-of-the-art Diagnostics</summary>

These diagnostics aim to monitor and diagnose model drifts, imbalances, and biases. Unlike the "frontier" diagnostics, they use aggregated coarse-resolution data from the Low Resolution Archive (LRA).
temporal and spatial resolution of climate models.
</details>

- [Atmospheric Global Mean Biases Diagnostic](https://github.com/DestinE-Climate-DT/AQUA/tree/aquathon/diagnostics/atmglobalmean)
- [Performance Indices](https://github.com/DestinE-Climate-DT/AQUA/tree/aquathon/diagnostics/ecmean)
- [Global time series](https://github.com/DestinE-Climate-DT/AQUA/tree/aquathon/diagnostics/global_time_series)
- [Ocean3D](https://github.com/DestinE-Climate-DT/AQUA/tree/aquathon/diagnostics/ocean3d)
- [Radiation Budget Diagnostic](https://github.com/DestinE-Climate-DT/AQUA/tree/aquathon/diagnostics/radiation)
- [Sea ice extent](https://github.com/DestinE-Climate-DT/AQUA/tree/aquathon/diagnostics/seaice)
- [Teleconnections diagnostic](https://github.com/DestinE-Climate-DT/AQUA/tree/aquathon/diagnostics/teleconnections)

#### 2.2 General Folder Contents:

- **`cli/`**: 
  - Contains command-line interface (CLI) tools or Python scripts used to run the diagnostics.
  - **Example**: `nworkers` and `memory` update scripts for adjusting parallel processing settings.

- **`config/`**:
  - Stores YAML configuration files or templates required for setting up and running diagnostics.
  - **Example**: `config.yaml` includes default settings for quick runs, while `config.tmpl` provides templates for configuration files.

- **`notebooks/`**:
  - Jupyter Notebooks used for demonstrating and testing the diagnostics.
  - **Example**: Contains examples, unit changes, or other updates in diagnostic workflows.

- **`README.md`**:
  - The README file provides an overview of the diagnostic package, instructions on usage, and important updates.
  - **Example**: Recent updates about YAML configurations or specific instructions on running the diagnostics.

- **`pyproject.toml`**:
  - Defines the project’s dependencies, environment settings, and packaging configurations.
  - **Example**: Includes settings for versioning and dependencies required for running diagnostics.

- **Python Scripts (`*.py`)**:
  - Core Python scripts that define the logic of the diagnostics.
  - **Example**: `ssh_class.py` contains logic for SSH variability diagnostics, while `__init__.py` initializes the module and removes outdated hacks.

- **Extra files**:
  - Diagnostics may contain precomputed data, directories for storing results, and additional scientific analysis outputs.
  - **Example**: Data or result folders specific to each diagnostic.


<details>
  <summary>⚠️ <span style="color: red;">Disclaimer:</span></summary>

> A major refactoring of diagnostics is underway, so be aware that this information may change. 
>  
> Each scientific diagnostic has been developed by different contributors, leading to variations in usage and structure. We are currently standardizing the diagnostics with clear requirements for implementation, documentation, and usage.  
>  
> Within the next month, there will be changes to how diagnostics are used.  
>  
> Attendees of the Climate DT Hackathon in Hamburg, Germany 11-15 November will have the opportunity to explore the updated AQUA package and experience new diagnostic workflows.
  
</details>



#### 2.4 Access the  notebook with comprehensive example [here](https://github.com/DestinE-Climate-DT/AQUA/blob/aquathon/aquathon/breakout_1/aqua_analysis.ipynb)

If you would like to see a detailed example of how each diagnostic is used, please check the $AQUA/diagnostics/diagnostic_name/notebooks folder.

---
### 3. **AQUA Analyses Wrapper (10 min)**
---
- **Objective**: Demonstrate the aqua-analysis wrapper and how to modify the YAML configuration file.

- **Steps:**

  - **3.1** [Show and discuss the aqua-analysis Wrapper.](#31-purpose-of-the-wrapper)
  - **3.2** [Demonstrate how to modify the YAML file for custom analyses.](#32-yaml-template)

#### 3.1 Purpose of the Wrapper

- Automates the running of multiple diagnostics for the AQUA project.
- Allows parallel execution to speed up analyses.
- Provides flexibility through command-line arguments and YAML configuration.

##### **Key Features**:
- **Command-line & YAML Configuration**:
  - Accepts options like model, experiment, source, output directory, and log level.
  - Missing options are retrieved from a YAML configuration file [`config.aqua-analysis.yaml`](https://github.com/DestinE-Climate-DT/AQUA/blob/aquathon/cli/aqua-analysis/config.aqua-analysis.yaml).

- **Parallel Execution**:
  - Diagnostics can be run in parallel using background processes.
  - Supports control over the number of threads with `max_threads`.

- **Logging**:
  - Logs are managed at different levels (`DEBUG`, `INFO`, `ERROR`) and written to individual log files for each diagnostic.

- **Error Handling**:
  - Detects missing configurations or failed diagnostics and provides informative error messages.


##### Logic of Storing YAML Files

In your AQUA diagnostics setup, the configuration files are stored in a consistent hierarchical structure under the `$HOME/.aqua/diagnostics` directory. The storage pattern for YAML files is as follows:

 - **Top-Level Directory**:
   Each diagnostic type (e.g., `tropical_rainfall`, `ocean3d`) has its own directory under `$HOME/.aqua/diagnostics/`. Inside each diagnostic folder, there are two main subdirectories:
   - `cli`: Contains YAML configuration files specific to command-line interfaces for diagnostics.
   - `config`: Contains YAML files that define the general configuration for that diagnostic.


<details>
  <summary>⚠️ <span style="color: red;">Disclaimer:</span></summary>

  The configuration files stored under `$HOME/.aqua/diagnostics/` are only kept there when the AQUA package is installed in non-development mode. If the package is installed in development mode, symbolic links (lines) may be used instead of actual files, pointing to the source files in the development environment.

</details>

#### 3.2 [YAML Template](https://github.com/DestinE-Climate-DT/AQUA/blob/aquathon/cli/aqua-analysis/config.aqua-analysis.tmpl)

The YAML file used to configure the wrapper is located at [`$AQUA/cli/aqua-analysis/config.aqua-analysis.yaml`](https://github.com/DestinE-Climate-DT/AQUA/blob/aquathon/cli/aqua-analysis/config.aqua-analysis.yaml). If you want to customize the settings (different from the default) and run AQUA analyses, you will need to modify this YAML file accordingly.



<details>
  <summary>Click to expand YAML Template</summary>

```yaml
# Configuration file for aqua-analysis.sh

job:
    max_threads: {{ max_threads, int }}  # Max threads (0 for no limit)
    loglevel: {{ loglevel, str }}  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    run_dummy: {{ run_dummy, bool }}  # Test run with dummy analysis
    outputdir: {{ /path/to/output, str }}  # Output directory path
    model: {{ model_name, str }}  # Model name for analysis
    exp: {{ experiment_name, str }}  # Experiment identifier
    source: {{ source_name, str }}  # Data source identifier

diagnostics:
  run: {{ diagnostics_to_analyze, list }}  # List of diagnostics to run
  diagnostic_name:
    nworkers: {{ nworkers, int }}  # Number of workers
    script_path: {{ script_path, str }}  # Path to diagnostic script
    extra: {{ extra_arguments, str }}  # Additional command-line arguments
    outname: {{ outname, str }}  # Name of output directory
```

#### **`nworkers` Key** 
<details>
  <summary>Click to expand</summary>

The `nworkers` key defines the number of parallel workers (or processes) used for running diagnostic analyses with Dask. More workers result in faster performance by distributing tasks across multiple CPU cores.

- **Tip**: Set `nworkers` based on the number of available cores on your machine (e.g., 4 or 8 workers for a multi-core system).

This ensures efficient utilization of your computing resources.

</details>

#### **`extra` Key**

<details>
  <summary>Click to expand</summary>

The `extra` key allows passing additional command-line arguments to the diagnostic script, providing flexibility for customization.

For example, you can:
- Specify a custom configuration file (`--config`).
- Enable reference data analysis (`--ref`).
- Set parameters such as regridding or frequency (`--regrid=r100 --freq=M`).

</details>

<details>
  <summary>⚠️ <span style="color: red;">Disclaimer:</span></summary>

  Each diagnostic can have its own `extra` arguments tailored to specific needs, ensuring a flexible and detailed analysis process.

</details>

#### **`outname` Key**

<details>
  <summary>Click to expand</summary>

The `outname` key specifies the directory name where the output results for a diagnostic will be stored. By default, it uses the diagnostic name, but you can customize it as needed.

For example:
- Setting `outname: global_time_series` will store results in a directory named `global_time_series`.

This ensures that output files are organized in clearly labeled directories, making it easier to manage and access results.

</details>

</details>

---
### 4. **Running AQUA Analyses (5 min)**
---
- **Objective:** Guide participants through the process of executing AQUA analyses using Python and Bash scripts, and submitting the jobs to the SLURM queue for parallel processing. 

- **Steps:**

  - **4.1** [Running the AQUA Analyses CLI for a Specific Diagnostic](#41-running-the-aqua-analyses-cli-for-a-specific-diagnostic)
  - **4.2** [Running AQUA Analyses for a Set of Diagnostics](#42-running-aqua-analyses-for-a-set-of-diagnostics)
  - **4.3** [Submitting AQUA Analyses to the SLURM Queue](#43-submitting-aqua-analyses-to-the-slurm-queue)
---
#### 4.1 Running the AQUA Analyses CLI for a Specific Diagnostic

To execute the AQUA Analyses CLI for a specific diagnostic using command-line arguments, for example, the `tropical_rainfall` diagnostic:


```bash
 python diagnostics/tropical_rainfall/cli/cli_tropical_rainfall.py 
```

##### Required arguments for CLI:

- `-c`, `--config` (str): Specifies the YAML configuration file to be used. This file contains settings for the diagnostics.
- `-l`, `--loglevel` (str): Defines the logging level (e.g., `DEBUG`, `INFO`, `WARNING`). Default is `WARNING`.
- `-n`, `--nworkers` (int): Specifies the number of Dask distributed workers for parallel processing.
- `--model` (str): Overrides the model name from the configuration file if provided. This is optional.
- `--exp` (str): Overrides the experiment name from the configuration file if provided. This is optional.
- `--source` (str): Overrides the source name from the configuration file if provided. This is optional.
- `--outputdir` (str): Specifies the output directory for the analysis results. Overrides the configuration file if provided.



<details>
  <summary>⚠️ <span style="color: red;">Disclaimer:</span></summary>
  
  Each diagnostic has a configuration file. If the command-line arguments (such as `model`, `exp`, `source`, etc.) are not provided, the values from the configuration file will be used. However, if these arguments are supplied via the command line, they will override the values in the configuration file and will be considered the main ones for the analysis.
  
</details>


```bash
python diagnostics/tropical_rainfall/cli/cli_tropical_rainfall.py  --model IFS-NEMO --exp historical --source lra-r100-monthly \
 --config config.aqua-web.yaml --loglevel INFO 
```
#### 4.2 Running AQUA Analyses for a Set of Diagnostics

To run AQUA Analyses for multiple diagnostics using command-line arguments:

```bash
./cli/aqua-analysis/aqua-analysis.sh
```
or 
```bash
./cli/aqua-analysis/aqua-analysis.sh --model IFS-NEMO --exp historical --source lra-r100-monthly --catalog climatedt-phase1 \
 --outputdir /path/to/output --config config.aqua-web.yaml --threads 4 --loglevel INFO
```
Ensure the script is executable with 

```bash
chmod +x your_bash_script.sh
```


#### 4.3 Submitting AQUA Analyses to the SLURM Queue
  
Use the pre-prepared scripts in the `AQUA/cli/aqua-web` folder to simplify the process.

Submit the wrapper with this command:

```bash
python cli/aqua-web/submit-aqua-web.py -p /users/jvonhar/aqua-web.experiment.list
```

<details>
  <summary>⚠️ <span style="color: red;">Disclaimer:</span></summary>
  
  This script is being updated and will soon handle not only the submission to SLURM but also the submission of results to [AQUA Web](https://aqua-web-contbuild.2.rahtiapp.fi/). Users may choose to avoid using this script directly and instead use it as inspiration for creating their own scripts to submit bash jobs to the queue.
  
</details>

---
### 5. **AQUA Analysis Output Review (5 min)**
---
- **Objective:** Review the output structure of aqua-analysis.
- **Steps:**
  - 5.1 [The output structure](#51-the-output-structure)
  - 5.2 Review the content of log files, PDF and NetCDF files including the metadata.

#### 5.1 The output structure

The output folder is organized in a clear hierarchical structure to help users easily navigate the analysis results. Below is a breakdown of the structure:

- **Model Level:**  
  The top-level directories represent different models or simulations used in the analysis.

- **Experiment Level:**  
  Inside each model directory, subdirectories correspond to different experiments or simulation periods.

- **Diagnostic Level:**  
  Each experiment folder contains diagnostics, which are categorized by types (e.g., time series, seasonal cycles).

- **Output Files:**  
  The diagnostic folders contain various output files, including:
  - **Log files:** Track the progress and details of the analysis process.
  - **PDF reports:** Provide visual summaries of the diagnostics.
  - **NetCDF files:** Contain detailed data for further in-depth analysis.


<details>
  <summary>Click to expand the example of the output structure</summary>

```plaintext
output/
└── IFS-NEMO/
    └── historical-1990/
        ├── seasonal_cycles.log
        ├── ecmean.log
        ├── seasonal_cycles/
        │   ├── pdf/
        │   │   └── global_time_series_seasonalcycle_msshf_IFS-NEMO_historical-1990_ERA5.pdf
        │   └── netcdf/
        │       └── seasonal_cycles_msshf.nc
        ├── ecmean/
        │   ├── pdf/
        │   │   └── PI4_EC23_historical-1990_ClimateDT_r1i1p1f1_1990_2002.pdf
        │   └── yaml/
        │       └── PI4_EC23_historical-1990_ClimateDT_r1i1p1f1_1990_2002.yml
```
</details>

---
### 6. **Q&A Session (5 min)**
---
- **Objective:** Address questions and clarify any doubts regarding the session content.
- **Steps:**
  - Open the floor for questions.
  - Encourage feedback and suggestions for improvement.


---
## Further Reading and Events
- [AQUA Documentation](https://aqua-web-contbuild.2.rahtiapp.fi/documentation/index.html)
- [Hackathon Hamburg, Germany 11-15 November]()
