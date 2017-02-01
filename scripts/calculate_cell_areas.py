"""Script to calculate cell areas from a curated image of cell outlines.

Outputs csv file with cell areas as well as an image where the colour
of each cell represents its area.
"""

import os
import logging
import argparse

from jicbioimage.core.image import Image
from jicbioimage.core.io import AutoName, AutoWrite

from jicbioimage.illustrate import Canvas

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


class LeafHeatmap(object):
    """Class for working with cell areas."""

    def __init__(self, segmentation):
        self.segmentation = segmentation
        self.identifiers = []
        self.areas = []

        for i in segmentation.identifiers:
            self.identifiers.append(i)
            region = segmentation.region_by_identifier(i)
            self.areas.append(region.area)

        self.min_area = min(self.areas)
        self.max_area = max(self.areas)
        self.range_area = self.max_area - self.min_area

    def heatmap_rgb_from_area(self, area):
        """Return heatmap colour."""
        normalised_intensity = (area - self.min_area) / self.range_area
        intensity = normalised_intensity * 255
        intensity = int(round(intensity))
        return (intensity, intensity, 255 - intensity)

    def write_png(self, fpath):
        height, width = self.segmentation.shape
        canvas = Canvas.blank_canvas(width=width, height=height)
        for i, area in zip(self.identifiers, self.areas):
            color = self.heatmap_rgb_from_area(area)
            region = self.segmentation.region_by_identifier(i)
            canvas[region] = color
        with open(fpath, "wb") as fh:
            fh.write(canvas.png())


def draw_heatmap_leaf(segmentation, output_directory):
    png_fpath = os.path.join(output_directory, "heatmap_laef.png")
    leaf_heatmap = LeafHeatmap(segmentation)
    leaf_heatmap.write_png(png_fpath)


def write_csv(segmentation, output_directory):
    """Write out the cell areas to a csv file."""
    csv_fpath = os.path.join(output_directory, "areas.csv")
    with open(csv_fpath, "w") as fh:
        fh.write("cell_id,area\n")
        for i in segmentation.identifiers:
            region = segmentation.region_by_identifier(i)
            fh.write("{},{}\n".format(i, region.area))


def analyse_file(image_fpath, mask_fpath, output_directory):
    """Analyse a single file."""
    logging.info("Analysing file: {}".format(image_fpath))
    image = Image.from_file(image_fpath)

    logging.info("Mask file: {}".format(mask_fpath))
    mask = Image.from_file(mask_fpath)
    if len(mask.shape) == 3:
        mask = mask[:, :, 0]
    mask = identity(mask)

    seeds = invert(image)
    seeds = erode_binary(seeds.view(bool))
    seeds = logical_and(seeds, mask)
    seeds = connected_components(seeds, connectivity=1)
    segmentation = watershed_with_seeds(-image, seeds, mask)

    write_csv(segmentation, output_directory)
    draw_heatmap_leaf(segmentation, output_directory)


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
