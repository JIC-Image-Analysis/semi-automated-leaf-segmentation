# coenen_brownsa_leaf_segmentation_2017

## Introduction

This image analysis project has been setup to take advantage of a technology
known as Docker.

This means that you will need to:

1. Download and install the [Docker Toolbox](https://www.docker.com/products/docker-toolbox)
2. Build a docker image

Before you can run the image analysis in a docker container.


## Build a Docker image

Before you can run your analysis you need to build your docker image.  Once you
have built the docker image you should not need to do this step again.

A docker image is basically a binary blob that contains all the dependencies
required for the analysis scripts. In other words the docker image has got no
relation to the types of images that we want to analyse, it is simply a
technology that we use to make it easier to run the analysis scripts.

```
$ cd docker
$ bash build_docker_image.sh
$ cd ..
```

## Run the image analysis in a Docker container

The image analysis will be run in a Docker container.  The script
``run_docker_container.sh`` will drop you into an interactive Docker session.

```
$ bash run_docker_container.sh
[root@048bd4bd961c /]#
```

Now you can run the script to generate the cell wall sketch.

```
[root@048bd4bd961c /]# python scripts/sketch_cell_walls.py --debug data/leaf.png output/
```

After hand curating the output segmentation it can be
post-processed to calculate the areas of cells.

```
[root@048bd4bd961c /]# python scripts/calculate_cell_areas.py --debug output/leaf-wall-outline.png data/leaf-mask.png output/
```
