#!/usr/bin/env python3
"""
Command-line interface for global time series diagnostic.

This CLI allows to plot timeseries of a set of variables 
defined in a yaml configuration file for a single experiment
and gregory plot.
"""
import argparse
import sys
import matplotlib.pyplot as plt

from aqua.util import load_yaml, get_arg
from aqua.exceptions import NotEnoughDataError

sys.path.insert(0, "../../")
from global_time_series import plot_timeseries, plot_gregory


def parse_arguments(args):
    """Parse command line arguments."""

    parser = argparse.ArgumentParser(description="Global time series CLI")

    parser.add_argument("-c", "--config",
                        type=str, required=False,
                        help="yaml configuration file")
    parser.add_argument("--model", type=str,
                        required=False, help="model name")
    parser.add_argument("--exp", type=str,
                        required=False, help="experiment name")
    parser.add_argument("--source", type=str,
                        required=False, help="source name")
    parser.add_argument("--outputdir", type=str,
                        required=False, help="output directory")
    parser.add_argument("--verbose", "-v", action="store_true",
                        required=False, help="verbose mode")

    return parser.parse_args(args)


def create_filename(outputdir=None, plotname=None, type=None,
                    model=None, exp=None, source=None):
    """
    Create a filename for the plots

    Args:
        outputdir (str): output directory
        plotname (str): plot name
        type (str): type of output file (pdf or nc)
        model (str): model name
        exp (str): experiment name
        source (str): source name

    Returns:
        filename (str): filename

    Raises:
        ValueError: if no output directory is provided
        ValueError: if no plotname is provided
        ValueError: if type is not pdf or nc
    """
    if outputdir is None:
        print("No output directory provided, using current directory.")
        outputdir = "."

    if plotname is None:
        raise ValueError("No plotname provided.")

    if type != "pdf" and type != "nc":
        raise ValueError("Type must be pdf or nc.")

    diagnostic = "global_time_series"
    filename = f"{diagnostic}"
    filename += f"_{model}_{exp}_{source}"
    filename += f"_{plotname}"

    if type == "pdf":
        filename += ".pdf"
    elif type == "nc":
        filename += ".nc"

    return filename


if __name__ == '__main__':

    print('Running global time series diagnostic...')
    args = parse_arguments(sys.argv[1:])

    verbose = get_arg(args, 'verbose', False)

    # Read configuration file
    file = get_arg(args, 'config', 'config_time_series_atm.yaml')
    if verbose:
        print(f"Reading configuration yaml file: {file}")
    config = load_yaml(file)

    model = get_arg(args, 'model', config['model'])
    exp = get_arg(args, 'exp', config['exp'])
    source = get_arg(args, 'source', config['source'])

    outputdir = get_arg(args, 'outputdir', config['outputdir'])

    outputdir_nc = outputdir + "/NetCDF"
    outputdir_pdf = outputdir + "/pdf"

    if verbose:
        print(f"model: {model}")
        print(f"exp: {exp}")
        print(f"source: {source}")
        print(f"outputdir: {outputdir}")

    if "timeseries" in config:
        print("Plotting timeseries...")

        for var in config["timeseries"]:
            if verbose:
                print(f"Plotting {var}")

            filename_nc = create_filename(outputdir=outputdir,
                                          plotname=var, type="nc",
                                          model=model, exp=exp,
                                          source=source)
            if verbose:
                print(f"Output file: {filename_nc}")

            # # Generating the image
            # fig, ax = plt.subplots()

            # try:
            #     plot_timeseries(config=config, var=var, ax=ax,
            #                     outfile=filename_nc)
            # except NotEnoughDataError as e:
            #     print(e)
            #     continue
            if "savefig" in config["timeseries"][var]:
                filename_pdf = create_filename(outputdir=outputdir,
                                               plotname=var, type="pdf",
                                               model=model, exp=exp,
                                               source=source)
                if verbose:
                    print(f"Output file: {filename_pdf}")

    if "gregory" in config:
        print("Plotting Gregory plot...")

        filename_nc = create_filename(outputdir=outputdir,
                                        plotname="gregory", type="nc",
                                        model=model, exp=exp,
                                        source=source)

        if verbose:
            print(f"Output file: {filename_nc}")

        # Generating the image

        if "savefig" in config["gregory"]:
            filename_pdf = create_filename(outputdir=outputdir,
                                           plotname="gregory", type="pdf",
                                           model=model, exp=exp,
                                           source=source)
            if verbose:
                print(f"Output file: {filename_pdf}")
