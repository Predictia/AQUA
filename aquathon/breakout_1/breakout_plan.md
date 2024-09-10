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
  - **1.2** Outline the tools that will be used during the session

---


### 2. **AQUA Scientific Diagnostics (20 min)**
---
- **Objective:** Demonstrate how to use AQUA scientific diagnostics in a Jupyter notebook, showcasing key analytical workflows and outputs.

- **Steps:**
  - **2.1**  [Important Notice](#21-important-notice) 
    Discuss common issues users may encounter, along with tips for resolving them.
  
  - **2.2** [Comprehensive Example](#22-access-the-notebook-here)  
    Walk through an example analysis (e.g., Ocean3D, Global Mean Time Series, Atmospheric Global Mean Biases Diagnostics). Explain key functions, their purpose, and outputs.

- **Engagement:**  
  Encourage participants to follow along in real-time, explore the notebook, and ask questions.

#### 2.1 Important Notice

<details>
  <summary>A major refactoring of diagnostics is underway, so be aware that this information may change.</summary>

> ⚠️  
>  
> Each scientific diagnostic has been developed by different contributors, leading to variations in usage and structure. We are currently standardizing the diagnostics with clear requirements for implementation, documentation, and usage.  
>  
> Within the next month, there will be changes to how diagnostics are used.  
>  
> Attendees of the Climate DT Hackathon in Hamburg, Germany 11-15 November will have the opportunity to explore the updated AQUA package and experience new diagnostic workflows.
>  
</details>


#### 2.2 Access the notebook [here](https://github.com/DestinE-Climate-DT/AQUA/blob/aquathon/aquathon/breakout_1/aqua_analysis.ipynb)



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


#### 3.2 [YAML Template](https://github.com/DestinE-Climate-DT/AQUA/blob/aquathon/cli/aqua-analysis/config.aqua-analysis.tmpl)

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
</details>

#### **`nworkers` Key** 
<details>
  <summary> Click to expand </summary>

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

---
### 4. **Running AQUA Analyses (5 min)**
---
- **Objective:** 

- **Steps:**

  - **4.1** [Running the Python Script](#41-running-the-python-script)
  - **4.2** [Running the Bash Script](#42-running-the-bash-script)
  - **4.3** [Submitting AQUA Analyses to the SLURM Queue](#43-submitting-aqua-analyses-to-the-slurm-queue)
---
#### 4.1 Running the Python Script

To run the Python script with command-line arguments:

```bash
python your_python_script.py --catalog climatedt-phase1 --model IFS-NEMO --exp historical --source lra-r100-monthly --config config.aqua-web.yaml --loglevel INFO 
```
- Pass the required arguments (`--catalog`, `--model`, etc.) as needed.


#### 4.2 Running the Bash Script

To run the bash script with command-line arguments that includes multiple Python scripts:

```bash
./your_bash_script.sh --model IFS-NEMO --exp historical --source lra-r100-monthly --catalog climatedt-phase1 --outputdir /path/to/output --config config.aqua-web.yaml --threads 4 --loglevel INFO
```
- `--model`, `--exp`, `--source`, etc., are the required arguments.
- Ensure the script is executable with `chmod +x your_bash_script.sh`.


#### 4.3 Submitting AQUA Analyses to the SLURM Queue

- **Objective:** Demonstrate how to submit aqua-analysis jobs to the SLURM queue.
- **Steps:**
  - Submit jobs using `./cli/aqua-web/submit-aqua-web.py` for parallel aqua-web SLURM jobs.
  
Use the pre-prepared scripts in the `AQUA/cli/aqua-web` folder to simplify the process.

Submit the wrapper with this command:

```bash
python submit-aqua-web.py -p /users/jvonhar/aqua-web.experiment.list
```

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
