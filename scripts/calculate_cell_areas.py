"""Script to calculate cell areas from a curated image of cell outlines.

Outputs csv file with cell areas as well as an image where the colour
of each cell represents its area.
"""

import os
import logging
import argparse

from jicbioimage.core.image import Image
from jicbioimage.core.io import AutoName, AutoWrite

from utils import (
    identity,
    invert,
    logical_and,
    erode_binary,
    connected_components,
    watershed_with_seeds,
)

__version__ = "0.3.0"

AutoName.prefix_format = "{:03d}_"


def analyse_file(image_fpath, mask_fpath, output_directory):
    """Analyse a single file."""
    logging.info("Analysing file: {}".format(image_fpath))
    image = Image.from_file(image_fpath)

    logging.info("Mask file: {}".format(mask_fpath))
    mask = Image.from_file(mask_fpath)[:, :, 0]
    mask = identity(mask)

    seeds = invert(image)
    seeds = erode_binary(seeds.view(bool))
    seeds = logical_and(seeds, mask)
    seeds = connected_components(seeds, connectivity=1)
    segmentation = watershed_with_seeds(-image, seeds, mask)


def main():
    # Parse the command line arguments.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_file", help="Input file")
    parser.add_argument("mask_file", help="Mask file")
    parser.add_argument("output_dir", help="Output directory")
    parser.add_argument("--debug", default=False, action="store_true",
                        help="Write out intermediate images")
    args = parser.parse_args()

    if not os.path.isfile(args.input_file):
        parser.error("{} not a file".format(args.input_file))

    if not os.path.isfile(args.mask_file):
        parser.error("{} not a file".format(args.mask_file))

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
    analyse_file(args.input_file, args.mask_file, args.output_dir)

if __name__ == "__main__":
    main()
