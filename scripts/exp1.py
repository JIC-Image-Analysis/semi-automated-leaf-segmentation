"""coenen_brownsa_leaf_segmentation_2017 analysis."""

import os
import logging
import argparse
import json

import skimage.filters
import skimage.morphology

from jicbioimage.core.image import Image
from jicbioimage.core.transform import transformation
from jicbioimage.core.io import AutoName, AutoWrite

from jicbioimage.transform import (
    threshold_otsu,
    find_edges_sobel,
    remove_small_objects,
    invert,
    erode_binary,
    dilate_binary,
)

from jicbioimage.segment import connected_components, watershed_with_seeds

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


@transformation
def grayscale(image):
    """If more than one channel return green channel."""
    if len(image.shape) > 2:
        return image[:, :, 1]
    return image


@transformation
def threshold_adaptive_median(image, block_size):
    return skimage.filters.threshold_adaptive(image,
                                             block_size=block_size,
                                             method="median")


@transformation
def fill_holes(image, max_size):
    aw = AutoWrite.on
    AutoWrite.on = False
    image = invert(image)
    image = remove_small_objects(image, min_size=max_size)
    image = invert(image)
    AutoWrite.on = aw
    return image


@transformation
def skeletonize(image):
    return skimage.morphology.skeletonize(image)


def analyse_file(fpath, output_directory):
    """Analyse a single file."""
    logging.info("Analysing file: {}".format(fpath))
    image = Image.from_file(fpath)
    image = grayscale(image)
    print(image.shape)

    outline = threshold_otsu(image)
    outline = remove_small_objects(outline, min_size=3)
    outline = skeletonize(image)
    outline = dilate_binary(image)

    seeds = threshold_adaptive_median(image, 31)

    seeds = fill_holes(seeds, 10)
    seeds = remove_small_objects(seeds, min_size=10)
    seeds = invert(seeds)
    seeds = connected_components(seeds, background=0)

#   seeds = remove_small_objects(seeds, min_size=100)
#   seeds = invert(seeds)
#   seeds = fill_holes(seeds, max_size=3)
#   seeds = erode_binary(seeds)
#   seeds = remove_small_objects(seeds, min_size=4)
#   seeds = connected_components(seeds, background=0)

    segmentation = watershed_with_seeds(-image, seeds=seeds)


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
