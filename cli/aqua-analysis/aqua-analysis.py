#!/usr/bin/env python3

import os
import sys
import subprocess
import argparse
from aqua.logger import log_configure
from aqua.util import load_yaml
# Set up logger
#logger = log_configure('debug', 'AQUA Analysis')

def run_command(cmd, log_file=None):
    """Run a system command and capture the exit code, redirecting output to the specified log file."""
    try:
        # Ensure the log file path is expanded properly
        log_file = os.path.expandvars(log_file)
        
        # Ensure the directory for the log file exists
        log_dir = os.path.dirname(log_file)
        os.makedirs(log_dir, exist_ok=True)
        
        # Open the log file and redirect stdout and stderr
        with open(log_file, 'w') as log:
            process = subprocess.run(cmd, shell=True, stdout=log, stderr=log, text=True)
            return process.returncode
    except Exception as e:
        print(f"Error running command {cmd}: {e}")
        raise

def run_diagnostic(diagnostic, *, script_path, extra_args, loglevel, logger, logfile):
    """Run the diagnostic script with specified arguments."""
    try:
        # Construct the command
        cmd = f"python {script_path} {extra_args} -l {loglevel} > {logfile} 2>&1"
        
        # Log the command for debugging
        logger.info(f"Running diagnostic {diagnostic} with command: {cmd}")
        
        # Execute the command
        process = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Capture stdout and stderr
        stdout, stderr = process.stdout, process.stderr

        if process.returncode != 0:
            logger.error(f"Error running diagnostic {diagnostic}: {stderr}")
        else:
            logger.info(f"Diagnostic {diagnostic} completed successfully.")
            logger.debug(f"Diagnostic output: {stdout}")

    except Exception as e:
        logger.error(f"Failed to run diagnostic {diagnostic}: {e}")

# Argument parser setup
def get_args():
    parser = argparse.ArgumentParser(description="Run diagnostics for the AQUA project.")
    
    parser.add_argument("-a", "--model_atm", type=str, help="Atmospheric model")
    parser.add_argument("-o", "--model_oce", type=str, help="Oceanic model")
    parser.add_argument("-m", "--model", type=str, help="Model (atmospheric and oceanic)")
    parser.add_argument("-e", "--exp", type=str, help="Experiment")
    parser.add_argument("-s", "--source", type=str, help="Source")
    parser.add_argument("-f", "--config", type=str, default="$AQUA/cli/aqua-analysis/config.aqua-analysis.yaml", help="Configuration file")
    parser.add_argument("-d", "--outputdir", type=str, help="Output directory")
    parser.add_argument("-c", "--catalog", type=str, help="Catalog")
    parser.add_argument("-p", "--parallel", action="store_true", help="Run diagnostics in parallel")
    parser.add_argument("-t", "--threads", type=int, default=-1, help="Maximum number of threads")
    parser.add_argument("-l", "--loglevel", type=str, choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="Log level")
    
    return parser.parse_args()

def get_aqua_paths(args, logger):
    """Get both the AQUA path and the AQUA config path."""
    try:
        # Get the AQUA path from the 'aqua --path' command
        aqua_path = subprocess.run(["aqua", "--path"], stdout=subprocess.PIPE, text=True).stdout.strip()
        if not aqua_path:
            raise ValueError("AQUA path is empty.")
        aqua_path = os.path.abspath(os.path.join(aqua_path, ".."))
        logger.info(f"AQUA path: {aqua_path}")

        # Determine the config path, either from args or fallback to the default path
        if args.config and args.config.strip():  # If config is provided and not empty
            aqua_config = os.path.expandvars(args.config)
        else:
            aqua_config = os.path.join(aqua_path, "cli/aqua-analysis/config.aqua-analysis.yaml")
        
        # Check if the config file exists
        if not os.path.exists(aqua_config):
            logger.error(f"Config file {aqua_config} not found.")
            sys.exit(1)

        logger.info(f"AQUA config path: {aqua_config}")
        return aqua_path, aqua_config
    
    except Exception as e:
        logger.error(f"Error getting AQUA path or config: {e}")
        sys.exit(1)


def main():
    args = get_args()

    # Temporarily use 'WARNING' log level until we can read from the config file
    logger = log_configure('warning', 'AQUA Analysis')

    # Get AQUA path and load the config file
    AQUA, aqua_config_path = get_aqua_paths(args, logger)

    # Load the entire config file using load_yaml
    config = load_yaml(aqua_config_path)

    # Now extract loglevel from the config or fallback to command-line argument
    loglevel = config.get('job', {}).get('loglevel', args.loglevel or "WARNING")

    # Reconfigure the logger with the correct loglevel
    logger = log_configure(loglevel.lower(), 'AQUA Analysis')

    # Continue extracting other variables from the config as needed
    model = args.model or config.get('job', {}).get('model')
    exp = args.exp or config.get('job', {}).get('exp')
    source = args.source or config.get('job', {}).get('source')

    outputdir = args.outputdir or config.get('job', {}).get('outputdir', './output')
    max_threads = args.threads
    catalog = args.catalog or config.get('job', {}).get('catalog')

    logger.debug(f"outputdir: {outputdir}")
    logger.debug(f"max_threads: {max_threads}")
    logger.debug(f"catalog: {catalog}")
    logger.debug(f"loglevel: {loglevel}")

    diagnostics = config.get('diagnostics', {}).get('run')
    if not diagnostics:
        logger.error("No diagnostics found in configuration.")
        sys.exit(1)

    # Validations
    if not all([model, exp, source]):
        logger.error("Model, experiment, and source must be specified either in config or as command-line arguments.")
        sys.exit(1)
    else:
        logger.info(f"Successfully validated inputs: Model = {model}, Experiment = {exp}, Source = {source}.")

    output_dir = f"{outputdir}/{model}/{exp}"
    os.environ["OUTPUT"] = output_dir
    source_args = f"--model {model} --exp {exp} --source {source}"

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Run setup checker if needed
    run_dummy = config.get('job', {}).get('run_dummy')
    logger.info(f"run_dummy  {run_dummy}")
    if run_dummy:
        dummy_script = os.path.join(AQUA, "diagnostics/dummy/cli/cli_dummy.py")
        
        # Expand environment variables and construct the correct log file path
        output_log_path = os.path.expandvars(f"{output_dir}/setup_checker.log")
        
        # Construct the command
        command = f"python {dummy_script} --model_atm {model} --model_oce {model} --exp {exp} --source {source} -l {loglevel}"
        
        # Log the command being run
        logger.info(f"Running setup checker: {command}")
        
        # Run the command and store its exit code
        result = run_command(command, log_file=output_log_path)

        # Check the exit code just like in your bash script
        if result == 1:
            logger.critical("Setup checker failed, exiting.")
            sys.exit(1)
        elif result == 2:
            logger.error("Atmospheric model not found, it will be skipped.")
        elif result == 3:
            logger.error("Oceanic model not found, it will be skipped.")
        else:
            logger.info("Setup checker completed successfully.")


    logger.info("Finished setup checker.")

    thread_count = 0
    for diagnostic in diagnostics:
        script_path = os.path.join(AQUA, "diagnostics", config.get('diagnostics', {}).get(diagnostic).get('script_path') \
            or f"{diagnostic}/cli/cli_{diagnostic}.py")
        logfile = f"{output_dir}/{diagnostic}.log"
        # Safely concatenate extra_args with 'extra' from the config, defaulting to an empty string if None
        extra_args = " " + (config.get('diagnostics', {}).get(diagnostic).get('extra') or "")
        
        # Generate the output name, defaulting to diagnostic if outname is None
        outname = f"{output_dir}/{config.get('diagnostics', {}).get(diagnostic).get('outname') or diagnostic}"
        logger.debug(f"outname: {outname}")
        
        args = source_args + " --outputdir " + outname + extra_args
        # Concatenate extra_args with the number of workers, defaulting to 1 if None
        args = args + f" --nworkers {config.get('diagnostics', {}).get(diagnostic).get('nworkers')}"
        if max_threads > 0:
            thread_count += 1
            if thread_count >= max_threads:
                logger.info(f"Reached max threads ({max_threads}), waiting for processes to finish.")
                os.system("wait")
                thread_count = 0
                
        # Run the diagnostic with keyword arguments
        run_diagnostic(
            diagnostic=diagnostic,
            script_path=script_path,
            extra_args=args,
            loglevel=loglevel,
            logger=logger,
            logfile=logfile
        )
    logger.info("All diagnostics finished successfully.")

if __name__ == "__main__":
    main()