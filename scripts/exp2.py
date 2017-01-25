import os

from jicbioimage.core.image import Image
from jicbioimage.core.io import AutoName
from jicbioimage.core.transform import transformation
from jicbioimage.transform import (
    threshold_otsu,
    remove_small_objects,
)

import skimage.morphology
import skimage.filters

TEST_IMAGE = os.path.join("data",
                          "wt",
                          "ExpID8001_19-01-17",
                          "ExpID_8001_WtStock12_13DAS_190117_merge.png")
TEST_MASK = os.path.join("data",
                         "wt",
                         "ExpID8001_19-01-17",
                         "ExpID_8001_WtStock12_13DAS_190117_merge_mask.png")

AutoName.directory = "output"


@transformation
def identity(image):
    return image


@transformation
def identity(image):
    return image


@transformation
def local_otsu(image, radius):
    selem = skimage.morphology.disk(radius)
    return skimage.filters.rank.otsu(image, selem)


@transformation
def threshold_local_otsu(image, local_otsu_im):
    return image > local_otsu_im


image = Image.from_file(TEST_IMAGE)
mask = Image.from_file(TEST_MASK)

image = identity(image)
local_otsu_im = local_otsu(image, 30) # 15, 50
image = threshold_local_otsu(image, local_otsu_im)
image = remove_small_objects(image, 100)
