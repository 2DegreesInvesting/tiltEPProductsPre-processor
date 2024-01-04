# Tilt pre-processing

This repository contains the scripts needed to apply the neccesary pre-processing on the tilt products and services data. The steps that are taken in the pre-processing are outlined as follows:

<b>1. Translation</b>: as the tilt data contains products and services from many different source and these are not always documented in English, translating them to English allows the utilization of a singular vocabulary
.

<b>2. Spelling mistakes correction</b>: the products and services are documented by hand and have a possibility of containing human spelling errors that can drastically impact the performance in subsequent steps (the clustering and NLP matching). 

<b>3. Depedency parsing delimiting</b>: products and services  have a possibility of containing more than one item (e.g. <i>"fish, frozen and deep-frozen"</i>) and these instances should therefore be considered as set of products and services rather than just one. 

<b>4. Clustering</b>: the final step consists of clustering similar products and services together by assigning them a  group based on a specific clustering algorithm. The clustering of the products and services serves the sole purpose of reducing the number of comparisons needed for the NLP matching process that takes place subsequently.

## Preparation
To run the scripts, a set amount of steps in preparation must be done beforehand.
### Setting up virtual environment
It is highly recommend to operate in a virtual environment to be able to experiment and test within isolation and therefore not run the risk of pottentially impacting other environments or the local system.

In the development of these scripts, a Conda virtual environment was used.

To create a conda environment, Anaconda or Miniconda needs to be installed. This can be done through the following links:

[Anaconda](https://www.anaconda.com/download)

[Miniconda](https://docs.conda.io/projects/miniconda/en/latest/)

Once either of these have been installed, a Conda environment can be created through the following command.

>`conda create -n ${name of your enviroment} python=${specify python version}`

This might take a couple of minutes but once that is completed, the environment can be activated by running the following command:

>`conda activate ${name of the enviroment you just created}`

Voila! You succesfully created the Conda virtual environment in which you will operate!

### Install required packages
The scripts created for the pre-processing depend on specific packages for operation. These packages are listed in the  `requirements.txt` file. These can all be easily installed by running the following command in your environment terminal:
>`conda install --file requirements.txt`


## Execute pre-processing




