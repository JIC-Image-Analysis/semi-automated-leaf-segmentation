"""Script to produce a sketch of the cell walls.

The intent is that this sketch is manually curated.
The curated cell outline can then be fed into
another script for calculating cell areas.
"""

import os
import logging
import argparse

from jicbioimage.core.image import Image
from jicbioimage.core.io import AutoName, AutoWrite

from utils import (
    identity,
    local_otsu,
    threshold_local_otsu,
    remove_small_objects,
)

__version__ = "0.3.0"

AutoName.prefix_format = "{:03d}_"


def analyse_file(fpath, output_directory):
    """Analyse a single file."""
    logging.info("Analysing file: {}".format(fpath))
    image = Image.from_file(fpath)
    image = identity(image)
    local_otsu_im = local_otsu(image, 30)
    image = threshold_local_otsu(image, local_otsu_im)
    image = remove_small_objects(image, 100)


def main():
    # Parse the command line arguments.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_file", help="Input file")
    parser.add_argument("output_dir", help="Output directory")
    parser.add_argument("--debug", default=False, action="store_true",
                        help="Write out intermediate images")
    args = parser.parse_args()

    if not os.path.isfile(args.input_file):
        parser.error("{} not a file".format(args.input_file))

    # Create the output directory if it does not exist.
    if not os.path.isdir(args.output_dir):
        os.mkdir(args.output_dir)
    AutoName.directory = args.output_dir

    # Only write out intermediate images in debug mode.
    AutoWrite.on = args.debug

    # Setup a logger for the script.
    log_fname = "audit.log"
    log_fpath = os.path.join(args.output_dir, log_fname)
    logging_level = logging.INFO
    if args.debug:
        logging_level = logging.DEBUG
    logging.basicConfig(filename=log_fpath, level=logging_level)

    # Log some basic information about the script that is running.
    logging.info("Script name: {}".format(__file__))
    logging.info("Script version: {}".format(__version__))

    # Run the analysis.
    analyse_file(args.input_file, args.output_dir)

if __name__ == "__main__":
    main()
