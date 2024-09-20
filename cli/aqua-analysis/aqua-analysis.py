#!/usr/bin/env python3

import os
import sys
import subprocess
import argparse
from concurrent.futures import ThreadPoolExecutor
from aqua.logger import log_configure
from aqua.util import load_yaml

def run_command(cmd, log_file=None):
    """Run a system command and capture the exit code, redirecting output to the specified log file."""
    try:
        log_file = os.path.expandvars(log_file)
        log_dir = os.path.dirname(log_file)
        os.makedirs(log_dir, exist_ok=True)

        with open(log_file, 'w') as log:
            process = subprocess.run(cmd, shell=True, stdout=log, stderr=log, text=True)
            return process.returncode
    except Exception as e:
        print(f"Error running command {cmd}: {e}")
        raise

def run_diagnostic(diagnostic, *, script_path, extra_args, loglevel, logger, logfile):
    """Run the diagnostic script with specified arguments."""
    try:
        cmd = f"python {script_path} {extra_args} -l {loglevel} > {logfile} 2>&1"
        logger.info(f"Running diagnostic {diagnostic}")
        logger.debug(f"Command: {cmd}")

        process = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.stdout, process.stderr

        if process.returncode != 0:
            logger.error(f"Error running diagnostic {diagnostic}: {stderr}")
        else:
            logger.info(f"Diagnostic {diagnostic} completed successfully.")
    except Exception as e:
        logger.error(f"Failed to run diagnostic {diagnostic}: {e}")

def get_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run diagnostics for the AQUA project.")
    
    parser.add_argument("-a", "--model_atm", type=str, help="Atmospheric model")
    parser.add_argument("-o", "--model_oce", type=str, help="Oceanic model")
    parser.add_argument("-m", "--model", type=str, help="Model (atmospheric and oceanic)")
    parser.add_argument("-e", "--exp", type=str, help="Experiment")
    parser.add_argument("-s", "--source", type=str, help="Source")
    parser.add_argument("-f", "--config", type=str, default="$AQUA/cli/aqua-analysis/config.aqua-analysis.yaml", help="Configuration file")
    parser.add_argument("-d", "--outputdir", type=str, help="Output directory")
    parser.add_argument("-c", "--catalog", type=str, help="Catalog")
    parser.add_argument("-p", "--parallel", action="store_true", help="Run diagnostics in parallel")  # New addition
    parser.add_argument("-t", "--threads", type=int, default=-1, help="Maximum number of threads")
    parser.add_argument("-l", "--loglevel", type=str, choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], default="WARNING", help="Log level")
    
    return parser.parse_args()


def get_aqua_paths(args, logger):
    """Get both the AQUA path and the AQUA config path."""
    try:
        aqua_path = subprocess.run(["aqua", "--path"], stdout=subprocess.PIPE, text=True).stdout.strip()
        if not aqua_path:
            raise ValueError("AQUA path is empty.")
        aqua_path = os.path.abspath(os.path.join(aqua_path, ".."))
        logger.info(f"AQUA path: {aqua_path}")

        aqua_config = os.path.expandvars(args.config) if args.config and args.config.strip() else os.path.join(aqua_path, "cli/aqua-analysis/config.aqua-analysis.yaml")

        if not os.path.exists(aqua_config):
            logger.error(f"Config file {aqua_config} not found.")
            sys.exit(1)

        logger.info(f"AQUA config path: {aqua_config}")
        return aqua_path, aqua_config
    except Exception as e:
        logger.error(f"Error getting AQUA path or config: {e}")
        sys.exit(1)

def run_diagnostics_in_parallel(diagnostics, max_threads, run_diagnostic_func):
    """Run diagnostics in parallel using a thread pool, with no limit if max_threads is -1 or 0."""
    if max_threads <= 0:
        max_threads = None  # Let ThreadPoolExecutor use the default, which is based on the number of CPU cores
    
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [executor.submit(run_diagnostic_func, diagnostic) for diagnostic in diagnostics]
        for future in futures:
            try:
                future.result()
            except Exception as e:
                print(f"Diagnostic failed: {e}")



def main():
    args = get_args()
    logger = log_configure('warning', 'AQUA Analysis')

    AQUA, aqua_config_path = get_aqua_paths(args, logger)
    config = load_yaml(aqua_config_path)
    loglevel = config.get('job', {}).get('loglevel', args.loglevel or "WARNING")
    logger = log_configure(loglevel.lower(), 'AQUA Analysis')

    model = args.model or config.get('job', {}).get('model')
    exp = args.exp or config.get('job', {}).get('exp')
    source = args.source or config.get('job', {}).get('source')
    outputdir = args.outputdir or config.get('job', {}).get('outputdir', './output')
    max_threads = args.threads
    catalog = args.catalog or config.get('job', {}).get('catalog')

    logger.debug(f"outputdir: {outputdir}")
    logger.debug(f"max_threads: {max_threads}")
    logger.debug(f"catalog: {catalog}")

    diagnostics = config.get('diagnostics', {}).get('run')
    if not diagnostics:
        logger.error("No diagnostics found in configuration.")
        sys.exit(1)

    if not all([model, exp, source]):
        logger.error("Model, experiment, and source must be specified either in config or as command-line arguments.")
        sys.exit(1)
    else:
        logger.info(f"Successfully validated inputs: Model = {model}, Experiment = {exp}, Source = {source}.")

    output_dir = f"{outputdir}/{model}/{exp}"
    os.environ["OUTPUT"] = output_dir
    os.makedirs(output_dir, exist_ok=True)

    run_dummy = config.get('job', {}).get('run_dummy')
    logger.debug(f"run_dummy  {run_dummy}")
    if run_dummy:
        dummy_script = os.path.join(AQUA, "diagnostics/dummy/cli/cli_dummy.py")
        output_log_path = os.path.expandvars(f"{output_dir}/setup_checker.log")
        command = f"python {dummy_script} --model_atm {model} --model_oce {model} --exp {exp} --source {source} -l {loglevel}"
        logger.info("Running setup checker")
        logger.debug(f"Command: {command}")
        result = run_command(command, log_file=output_log_path)

        if result == 1:
            logger.critical("Setup checker failed, exiting.")
            sys.exit(1)
        elif result == 2:
            logger.error("Atmospheric model not found, it will be skipped.")
        elif result == 3:
            logger.error("Oceanic model not found, it will be skipped.")
        else:
            logger.info("Setup checker completed successfully.")

    def run_diagnostic_func(diagnostic):
        logfile = f"{output_dir}/{diagnostic}.log"
        extra_args = " " + (config.get('diagnostics', {}).get(diagnostic).get('extra') or "")
        outname = f"{output_dir}/{config.get('diagnostics', {}).get(diagnostic).get('outname') or diagnostic}"
        args = f"--model {model} --exp {exp} --source {source} --outputdir {outname} {extra_args}"

        run_diagnostic(
            diagnostic=diagnostic,
            script_path=os.path.join(AQUA, "diagnostics", config.get('diagnostics', {}).get(diagnostic).get('script_path') or f"{diagnostic}/cli/cli_{diagnostic}.py"),
            extra_args=args,
            loglevel=loglevel,
            logger=logger,
            logfile=logfile
        )

    if args.parallel:
        run_diagnostics_in_parallel(diagnostics, max_threads, run_diagnostic_func)
    else:
        # Run diagnostics sequentially if --parallel is not provided
        for diagnostic in diagnostics:
            run_diagnostic_func(diagnostic)

    logger.info("All diagnostics finished successfully.")

if __name__ == "__main__":
    main()
