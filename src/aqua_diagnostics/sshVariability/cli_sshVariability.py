#!/usr/bin/env python3
"""
Command-line interface for ensemble atmglobalmean diagnostic.

This CLI allows to plot a map of aqua analysis atmglobalmean
defined in a yaml configuration file for multiple models.
"""
import argparse
import sys

from aqua.util import get_arg
from aqua.logger import log_configure
from aqua.version import __version__ as aqua_version
from aqua.diagnostics.core import template_parse_arguments, open_cluster, close_cluster
from aqua.diagnostics.core import load_diagnostic_config, merge_config_args

from aqua.diagnostics import sshVariabilityCompute
from aqua.diagnostics import sshVariabilityPlot


def parse_arguments(args):
    """Parse command-line arguments for sshVariability diagnostic.

    Args:
        args (list): list of command-line arguments to parse.
    """
    parser = argparse.ArgumentParser(description="sshVariability CLI")
    parser = template_parse_arguments(parser)
    return parser.parse_args(args)


if __name__ == "__main__":

    args = parse_arguments(sys.argv[1:])

    loglevel = get_arg(args, "loglevel", "WARNING")
    logger = log_configure(loglevel, "CLI for sshVariability")
    logger.info("Starting SSH Variability diagnostic")

    cluster = get_arg(args, "cluster", None)
    nworkers = get_arg(args, "nworkers", None)

    (
        client,
        cluster,
        private_cluster,
    ) = open_cluster(nworkers=nworkers, cluster=cluster, loglevel=loglevel)

    # Load the configuration file and then merge it with the command-line arguments
    config_dict = load_diagnostic_config(
        diagnostic="sshVariability",
        config=args.config,
        default_config="config_ssh.yaml",
        loglevel=loglevel,
    )
    config_dict = merge_config_args(config=config_dict, args=args, loglevel=loglevel)

    # Output options
    outputdir = config_dict["output"].get("outputdir", "./")
    # rebuild = config_dict['output'].get('rebuild', True)
    save_netcdf = config_dict["output"].get("save_netcdf", True)
    save_pdf = config_dict["output"].get("save_pdf", True)
    save_png = config_dict["output"].get("save_png", True)
    dpi = config_dict["output"].get("dpi", 600)

    # EnsembleLatLon diagnostic
    if "ensemble" in config_dict["diagnostics"]:
        if config_dict["diagnostics"]["sshVariability"]["run"]:
            logger.info("sshVariability module is used.")

            variable = config_dict["diagnostics"]["sshVariability"].get("variable", None)
            logger.info(f"Variable under consideration: {variable}")

            # Model data
            model = config_dict["datasets"]

            if model is not None:
                catalog = get_arg(args, "catalog", model[0]["catalog"])
                model = get_arg(args, "model", model[0]["model"])
                exp = get_arg(args, "exp", model[0]["exp"])
                source = get_arg(args, "source", model[0]["source"])
                startdate_model = get_arg(args, "startdate_data", model[0]["startdate_data"])
                enddate_model = get_arg(args, "enddate_data", model[0]["enddate_data"])

            ssh_model = sshVariability(
                var=variable,
                catalog=catalog,
                model=model,
                source=source,
                startdate=startdate_model,
                enddate=enddate_model,
            )

            ssh_model.run()
            
            # Reference data as AVISO
            model_ref = config_dict["references"]

            if model_ref is not None:
                catalog_ref = get_arg(args, "catalog", model_ref[0]["catalog"])
                model_ref = get_arg(args, "model", model_ref[0]["model"])
                exp_ref = get_arg(args, "exp", model_ref[0]["exp"])
                source_ref = get_arg(args, "source", model_ref[0]["source"])
                startdate_ref = get_arg(args, "startdate_ref", model[0]["startdate_ref"])
                enddate_ref = get_arg(args, "enddate_ref", model[0]["enddate_ref"])


            ssh_ref = sshVariability(
                var=variable,
                catalog=catalog,
                model=model,
                source=source,
                startdate=startdate_ref,
                enddate=enddate_ref,
            )

            ssh_ref.run()
           
             
            # Initialize plotting class
            ssh_Plot = sshVariabilityPlot()
            
            plot_arguments_model = {
                "var": variable,
                "catalog": catalog,
                "model": model,
                "exp": exp,
                "source": source,
                "save_pdf": save_pdf,
                "save_png": save_png,
            }

            ssh_plot.plot(dataset_std=ssh_model., **plot_arguments_model)

            plot_arguments_ref = {
                "var": variable,
                "catalog": catalog,
                "model": model,
                "exp": exp,
                "source": source,
                "save_pdf": save_pdf,
                "save_png": save_png,
            }

            ssh_plot.plot(dataset_std=ssh_model, **plot_arguments)


            logger.info(f"Finished SSH Variability diagnostic for {variable}.")

    # Close the Dask client and cluster
    close_cluster(
        client=client, cluster=cluster, private_cluster=private_cluster, loglevel=loglevel
    )
