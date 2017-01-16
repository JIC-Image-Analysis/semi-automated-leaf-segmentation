"""coenen_brownsa_leaf_segmentation_2017 analysis."""

import os
import logging
import argparse
import json

from jicbioimage.core.image import Image
from jicbioimage.core.transform import transformation
from jicbioimage.core.io import AutoName, AutoWrite

__version__ = "0.1.0"

AutoName.prefix_format = "{:03d}_"


class DataFilePathManager(object):

    def __init__(self, manifest_path):
        self.manifest_path = os.path.abspath(manifest_path)
        self.manifest_root = os.path.dirname(self.manifest_path)
        self._parse_manifest()

    def _parse_manifest(self):
        with open(self.manifest_path, "r") as fh:
            m = json.load(fh)
            self.file_list = m["file_list"]

    def __iter__(self):
        for item in self.file_list:
            if item["mimetype"] == "image/png":
                tag, _ = item["path"].split("/", 1)
                apath = os.path.join(self.manifest_root, item["path"])
                yield apath, tag


@transformation
def identity(image):
    """Return the image as is."""
    return image


def analyse_file(fpath, output_directory):
    """Analyse a single file."""
    logging.info("Analysing file: {}".format(fpath))
    image = Image.from_file(fpath)
    image = identity(image)


def main():
    # Parse the command line arguments.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest_file", help="Input manifest file")
    parser.add_argument("output_dir", help="Output directory")
    parser.add_argument("--debug", default=False, action="store_true",
                        help="Write out intermediate images")
    args = parser.parse_args()

    if not os.path.isfile(args.manifest_file):
        parser.error("No such manifest file: {}".format(args.manifest_file))

    # Create the output directory if it does not exist.
    if not os.path.isdir(args.output_dir):
        os.mkdir(args.output_dir)
    AutoName.directory = args.output_dir

    # Only write out intermediate images in debug mode.
    if not args.debug:
        AutoWrite.on = False

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
    fpath_iterator = DataFilePathManager(args.manifest_file)

    for fpath, tag in fpath_iterator:
        print(fpath, tag)
        out_dir = os.path.join(args.output_dir, tag)
        if not os.path.isdir(out_dir):
            os.mkdir(out_dir)
        AutoName.directory = out_dir
        analyse_file(fpath, out_dir)

if __name__ == "__main__":
    main()
