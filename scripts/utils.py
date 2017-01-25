"""Utility functions."""

import logging

import numpy as np
import skimage.morphology
import skimage.filters

from jicbioimage.core.transform import transformation
import jicbioimage.transform
import jicbioimage.segment


@transformation
def identity(image):
    """Return the image as is."""
    logging.info("identity({})".format(repr(image)))
    return image


@transformation
def local_otsu(image, radius):
    logging.info("local_otsu({}, radius={})".format(repr(image), radius))
    selem = skimage.morphology.disk(radius)
    return skimage.filters.rank.otsu(image, selem)


@transformation
def logical_and(im1, im2):
    logging.info("logical_and({}, {})".format(repr(im1), repr(im2)))
    return np.logical_and(im1, im2)


@transformation
def threshold_local_otsu(image, local_otsu_im):
    logging.info("threshold_local_otsu({}, {})".format(
        repr(image), repr(local_otsu_im)))
    return image > local_otsu_im


def remove_small_objects(image, min_size):
    logging.info("remove_small_objects({}, min_size={})".format(
        repr(image), min_size))
    return jicbioimage.transform.remove_small_objects(image, min_size)


def invert(image):
    logging.info("invert({})".format(repr(image)))
    return jicbioimage.transform.invert(image)


def erode_binary(image, selem=None):
    logging.info("erode_binary({}, selem={})".format(repr(image), selem))
    return jicbioimage.transform.erode_binary(image, selem)


def connected_components(image, connectivity=2, background=0):
    log_msg = "connected_components({}, connectivity={}, background={})"
    logging.info(log_msg.format(repr(image), connectivity, background))
    return jicbioimage.segment.connected_components(
        image, connectivity, background)


def watershed_with_seeds(image, seeds, mask=None):
    logging.info("watershed_with_seeds({}, {}, maks={})".format(
        repr(image), seeds, mask))
    return watershed_with_seeds(image, seeds, mask)
