import argparse
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, ".."))

from amo import AMO
from aqua.logger import log_configure

def parse_args(args):
    parser = argparse.ArgumentParser(description="Atlantic Multidecadal Oscillation (AMO) diagnostic")
    parser.add_argument("-c", "--config", required=True, help="YAML configuration file")
    parser.add_argument("-l", "--loglevel", default="WARNING", help="Log level")
    return parser.parse_args(args)

def main(raw_args):
    args = parse_args(raw_args)
    logger = log_configure(log_name="AMO CLI", log_level=args.loglevel)
    logger.info("Running AMO diagnostic")

    diagnostic = AMO(config=args.config, loglevel=args.loglevel)
    diagnostic.retrieve()
    diagnostic.compute_index()

    logger.info("Diagnostic finished")

if __name__ == "__main__":
    main(sys.argv[1:])