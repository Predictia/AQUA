# Breakout Session Plan: AQUA Analysis 


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


> **:warning: Important Notice:**  
> Currently, each scientific diagnostic has been implemented by one or multiple developers, leading to variations in how each diagnostic is used and structured. We are actively working to standardize the diagnostics by introducing specific requirements for implementation, documentation, and usage.  
> In the next one to two months, the usage of diagnostics will change from the current approach.  
> If you plan to attend the Climate DT Hackathon in Hamburg this October, you’ll have the opportunity to explore the updated AQUA package and the new, streamlined diagnostic workflows.



---

### 3. **AQUA Analyses Wrapper (10 min)**
- **Objective:** Demonstrate the aqua-analysis wrapper, modify the YAML file, and submit analyses.
- **Steps:**
  - Show how to run the aqua-analysis tool and its role in diagnostics.
  - Demonstrate how to modify YAML files for custom analyses. 
  - Explain common troubleshooting techniques.

#### YAML Template
```yaml
# Configuration file for aqua-analysis.sh

job:
    max_threads: {{ max_threads, int }}  # Maximum number of threads or 0 for no limit
    loglevel: {{ loglevel, str }}  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    run_dummy: {{ run_dummy, bool }}  # Test configuration with dummy analysis
    outputdir: {{ /path/to/output, str }}  # Output directory path
    model: {{ model_name, str }}  # Model name for analysis
    exp: {{ experiment_name, str }}  # Experiment identifier
    source: {{ source_name, str }}  # Data source identifier

diagnostics:
  run: {{ diagnostics_to_analyze, list }}
  diagnostic_name:
    nworkers: {{ nworkers, int }}  # Number of workers
    script_path: {{ script_path, str }}  # Diagnostic script path
    extra: {{ extra_arguments, str }}  # Additional command-line arguments
    outname: {{ outname, str }}  # Output directory name
```

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
