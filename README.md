# Tilt pre-processing

This repository contains the scripts needed to apply the neccesary pre-processing on the tilt products and services data. The steps that are taken in the pre-processing are outlined as follows:

<b>1. Typo Correction</b>: as the tilt data contains products and services that is manually input by companies, there is the likelihood of spelling mistakes. These spelling mistakes could lead to incorrect output in the subsequent steps (potentially giving non existent products and services such as <i>koukees</i> instead of <i>cookies</i>). To solve this, a pre-trained spelling checking algorithm* is ran over the data.

<b>2. Translation</b>: once the sentence with spelling mistakes have been corrected, the next step is to translate all the sentences into English. A pre-trained GoogleTranslator transformer was used on the subset of sentences that were not identified by a language detection algorithm as English**.  

<b>3. Deduplication and linkage</b>: since the products and services are manual input from companies, there is the possibility of products and services present that are identical in definition but differ in their notation (e.g. <i>fish frozen</i> and <i>frozen fish</i>). These instances should be considered as duplicates and be treated as the same product. A pre-trained deduplication algorithm is ran over the translated data from the previous step to do the following:

* <b>Deduplication</b>: Remove duplicate products and services from the data

* <b>Record Linkage</b>: Link the deduplicated data to a defined catalogue of EuroPages products whenever possible


## Preparation
To run the scripts, a set amount of steps in preparation must be done beforehand.

### Setting up virtual environment
It is highly recommend to operate in a virtual environment to be able to experiment and test within isolation and therefore not run the risk of pottentially impacting other environments or the local system.

In the development of these scripts, a Conda virtual environment was used.

To create a conda environment, Anaconda or Miniconda needs to be installed. This can be done through the following links:

[Anaconda](https://www.anaconda.com/download)

[Miniconda](https://docs.conda.io/projects/miniconda/en/latest/)

Once either of these have been installed, a Conda environment can be created through the following command.

```` Shell
$ conda create -n ${name of your enviroment} python=${specify python version}
````

This might take a couple of minutes but once that is completed, the environment can be activated by running the following command:

```` Shell
$ conda activate ${name of the enviroment you just created}
````
Voila! You succesfully created the Conda virtual environment in which you will operate!

### Install required packages
The scripts created for the pre-processing depend on specific packages for operation. These packages are listed in the  `requirements.txt` file. These can all be easily installed by running the following command in your environment terminal:
```` Shell
$ pip install -r requirements.txt
````


## Execute pre-processing
The pre-processing can be executed as either separate steps through a notebook to have an interactive way of working with the scripts or through the command line as Python script that directly executes the whole pipeline containing all the steps over the data. Regardless of the IDE you are using, a Jupyter Notebook extension needs to be installed to be able to run the notebooks. For Visual Studio Code, the Jupyter Notebook extension can be found in the following [link](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter). Whenever custom data is used, make sure that it is placed in the following [directory](https://github.com/2DegreesInvesting/tiltEPProductsPre-processor/tree/f156280f7f8e54610b6188420b2860492cfdac53/src/data/example_data/output) within the repository. It is also important that the data has the following structure in which the first two columns are mandatory to have:

| products_id | products_and_services | any column 1 |...| any column <i>T</i> |
| :-----:|:-----------:|:-----:|:-----:|:----:|
| id_1 | product_1 | a | ... | x |
| id_2 | product_2 | b | ... | y |
| id_3 | product_3 | c | ... | z |

### Notebook execution
Very simple. Just go to the [following directory](https://github.com/2DegreesInvesting/tiltEPProductsPre-processor/tree/a02feccf1c88ac027911f79106e8c58f6ab1aa3d/src/scripts/dedup) and run each of the notebooks. The notebooks make use of the scraped and prepared tilt data that is store in the following [directory](https://github.com/2DegreesInvesting/tiltEPProductsPre-processor/tree/f156280f7f8e54610b6188420b2860492cfdac53/src/data/example_data/input).
### Python script pipeline execution
To run the pre-processing pipeline as a command line script, the following command can be executed in the terminal after the user navigated to the right directory:
```` Shell
$ python run_pre-processor.py
````

A file dialog will pop up after a while (takes 20 seconds at most) in which you can select one or multiple files you wish to have processed. It might be that the pop up window does not immediately appear. Simply using ALT+TAB will show you all your open programs and the you will then also see a program called "Open" which is the dialog and should looks as follows:

<div>
<img src="src\images\dialog_example.png" width="500"/>
</div>

The execution of the script might take a while due to the translator module being dependent on the online Google Translator API. 

Once the execution is finished, a new csv file will be generated in the [/output](https://github.com/2DegreesInvesting/tiltEPProductsPre-processor/tree/f156280f7f8e54610b6188420b2860492cfdac53/src/data/example_data/output) directory that is stored at the same level as the input directory. This new csv file can be recognized by the `preprocessed` prefix in the filename.


## IMPORTANT NOTES
\* <i> The spelling checker algorithm (TextBlob) used only works with English sentences. The following other spell checker models were considered:
* <b>SpaCy ContextualSpellCheck</b>: only works in English but also not suitable for short sentences (lack of context)
* <b>Huggingface transformer</b>: More accurate but computationally expensive 
* <b>PySpellCheck</b>: does work with different languages but requires single words as input. (aka splitted)  </i>

\** The language detector algorithm was often inaccurate with identifying the right language due to the short length of the sentences. 