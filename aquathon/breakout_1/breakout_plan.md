# Breakout Session Plan: AQUA Analysis 

# Table of Contents

1. [Agenda Overview](#agenda-overview)
2. [Session Structure](#session-structure)
   - [1. Introduction and Overview (1 min)](#1-introduction-and-overview-1-min)
   - [2. AQUA Scientific Diagnostics (20 min)](#2-aqua-scientific-diagnostics-20-min)
   - [3. AQUA Analyses Wrapper (10 min)](#3-aqua-analyses-wrapper-10-min)
   - [4. Submitting AQUA Analyses (5 min)](#4-submitting-aqua-analyses-5-min)
   - [5. AQUA Analysis Output Review (5 min)](#5-aqua-analysis-output-review-5-min)
   - [6. Q&A Session (5 min)](#6-qa-session-5-min)
   - [7. Closing Remarks (Optional)](#7-closing-remarks-optional)
3. [Further Reading and Events](#further-reading-and-events)

## Agenda Overview
This session will focus on **Sailing with AQUA:**, which includes running the aqua-analysis tool, modifying configuration files, submitting jobs, and interpreting the outputs.


---

## Session Structure

### 1. **Introduction and Overview (1 min)**
- **Objective:** Introduce the session's objectives.
- **Steps:**
  - Briefly explain the session purpose and key activities.
  - Outline the tools that will be used during the session.

---


### 2. **AQUA Scientific Diagnostics (20 min)**

- **Objective:** Demonstrate how to use AQUA scientific diagnostics in a Jupyter notebook, showcasing key analytical workflows and outputs.

- **Steps:**
  - Walk through a comprehensive example of a scientific analysis (e.g., Ocean3D, Global Mean Time Series, Atmospheric Global Mean Biases Diagnostics).
  - Explain and highlight key functions, detailing their purpose and outputs.
  - Engage participants by encouraging them to follow along, explore the notebook, and ask questions in real-time.


> ⚠️ **Important Notice:**  
>  
> Currently, each scientific diagnostic has been implemented by one or multiple developers, leading to variations in how each diagnostic is used and structured. We are actively working to standardize the diagnostics by introducing specific requirements for implementation, documentation, and usage.  
>  
> In the next one to two months, the usage of diagnostics will change from the current approach.  
>  
> If you plan to attend the Climate DT Hackathon in Hamburg this October, you’ll have the opportunity to explore the updated AQUA package and the new, streamlined diagnostic workflows.



---


### 3. **AQUA Analyses Wrapper (10 min)**
- **Objective**: Demonstrate the aqua-analysis wrapper and how to modify the YAML configuration file.
- **Steps**:
  - Show how to run the aqua-analysis tool and its role in generating diagnostics.
  - Demonstrate how to modify the YAML file for custom analyses.
  - Discuss common troubleshooting techniques.

#### YAML Template

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

The `nworkers` key defines the number of parallel workers (or processes) used for running diagnostic analyses with Dask. More workers result in faster performance by distributing tasks across multiple CPU cores.

- **Tip**: Set `nworkers` based on the number of available cores on your machine (e.g., 4 or 8 workers for a multi-core system).

This ensures efficient utilization of your computing resources.

#### **`extra` Key**

The `extra` key allows passing additional command-line arguments to the diagnostic script, providing flexibility for customization.

For example, you can:
- Specify a custom configuration file (`--config`).
- Enable reference data analysis (`--ref`).
- Set parameters such as regridding or frequency (`--regrid=r100 --freq=M`).

Each diagnostic can have its own `extra` arguments tailored to specific needs, ensuring a flexible and detailed analysis process.

#### **`outname` Key**

The `outname` key specifies the directory name where the output results for a diagnostic will be stored. By default, it uses the diagnostic name, but you can customize it as needed.

For example:
- Setting `outname: global_time_series` will store results in a directory named `global_time_series`.

This ensures that output files are organized in clearly labeled directories, making it easier to manage and access results.


---

### 4. **Submitting AQUA Analyses (5 min)**
- **Objective:** Demonstrate how to submit aqua-analysis jobs.
- **Steps:**
  - Submit jobs using `./cli/aqua-web/submit-aqua-web.py` for parallel aqua-web SLURM jobs.

There is no need to write a custom bash or Python script for each individual user. You can use the pre-prepared scripts available in the `AQUA/cli/aqua-web` folder to simplify the process.

You can submit the wrapper using the following command:

```bash
python submit-aqua-web.py -p /users/jvonhar/aqua-web.experiment.list
```
---

### 5. **AQUA Analysis Output Review (5 min)**
- **Objective:** Review the output structure of aqua-analysis.
- **Steps:**
  - Show how the output folder is organized into model, experiment, and diagnostic levels.
  - Review the content of log files, PDF reports, and NetCDF files for detailed analysis.


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

The example of the output structure is:

```plaintext
output/
└── IFS-NEMO/
    └── historical-1990/
        ├── seasonal_cycles.log
        ├── ecmean.log
        ├── seasonal_cycles/
        │   ├── pdf/
        │   │   └── global_time_series_seasonalcycle_msshf_IFS-NEMO_historical-1990_ERA5.pdf
        │   │   └── global_time_series_seasonalcycle_mtpr_IFS-NEMO_historical-1990_ERA5.pdf
        │   └── netcdf/
        │       └── IFS-NEMO_historical-1990/
        │           └── seasonal_cycles_msshf.nc
        ├── ecmean/
        │   ├── PDF/
        │   │   └── PI4_EC23_historical-1990_ClimateDT_r1i1p1f1_1990_2002.pdf
        │   └── YAML/
        │       └── PI4_EC23_historical-1990_ClimateDT_r1i1p1f1_1990_2002.yml
```


---

### 6. **Q&A Session (5 min)**
- **Objective:** Address questions and clarify any doubts regarding the session content.
- **Steps:**
  - Open the floor for questions.
  - Encourage feedback and suggestions for improvement.

---

### 7. **Closing Remarks (Optional)**
- **Objective:** Summarize the key takeaways from the session and provide further learning resources.
- **Steps:**
  - Recap the session’s key points.
  - Offer additional resources and thank participants for their engagement.

---

## Further Reading and Events
- [AQUA Documentation](https://aqua-web-contbuild.2.rahtiapp.fi/documentation/index.html)
- [Hamburg Hackathon](https://climatehackathon.devpost.com)
