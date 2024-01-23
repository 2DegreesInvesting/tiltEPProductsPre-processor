# Tilt pre-processing

This repository contains the scripts needed to apply the neccesary pre-processing on the tilt products and services data. The steps that are taken in the pre-processing are outlined as follows:

<b>1. Flagging</b>: The likelihood of a company providing a product or service that has not been already created by other companies is very small. To prevent unnecessary pre-processing of products and services that can already be directly linked to the EuroPages catalogue, we will flag the those products and services to not be processed but still keep them in the dataframe for the deduplication later on.


<b>2. Typo Correction</b>: as the tilt data contains products and services that is manually input by companies, there is the likelihood of spelling mistakes. These spelling mistakes could lead to incorrect output in the subsequent steps (potentially giving non existent products and services such as <i>koukees</i> instead of <i>cookies</i>). To solve this, a pre-trained spelling checking algorithm* is ran over the data.

<b>3. Translation</b>: once the sentence with spelling mistakes have been corrected, the next step is to translate all the sentences into English. A pre-trained GoogleTranslator transformer was used on the subset of sentences that were not identified by a language detection algorithm as English**.  

<b>4. Deduplication and linkage</b>: since the products and services are manual input from companies, there is the possibility of products and services present that are identical in definition but differ in their notation (e.g. <i>fish frozen</i> and <i>frozen fish</i>). These instances should be considered as duplicates and be treated as the same product. A pre-trained deduplication algorithm is ran over the translated data from the previous step to do the following:

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
conda create -n ${name of your enviroment} python=${specify python version}
````
For the development of this repository, Python version 3.10 was used. This might take a couple of minutes but once that is completed, the environment can be activated by running the following command:

```` Shell
conda activate ${name of the enviroment you just created}
````
Voila! You succesfully created the Conda virtual environment in which you will operate! But before we continue, we will configure the environment variables as one of the packages we import makes use of TensorFlow, which likes to spit out a lot of warnings that we are quite frankly not interested in! So to get rid of those, there is a YAML configuration file that pre-configures certain variables in the Conda environment to supress the warnings that are raised. To import this configuration file into your newly created environment, you can run the following command in the terminal:

```` Shell
conda env update --file environment.yml 
````

Once you have 

### Install required packages
The scripts created for the pre-processing depend on specific packages for operation. These packages are listed in the  `requirements.txt` file. These can all be easily installed by running the following command in your environment terminal:
```` Shell
pip install -r src/scripts/requirements.txt
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
To run the pre-processing pipeline as a command line script, the following command can be executed in the terminal assuming the user is still in the root directory:
```` Shell
python src/scripts/dedup/run_pre-processor.py
````

A file dialog will pop up after a while (takes 20 seconds at most) in which you can select one or multiple files you wish to have processed. It might be that the pop up window does not immediately appear. Simply using ALT+TAB will show you all your open programs and the you will then also see a program called "Open" which is the dialog and should looks as follows:

<div>
<img src="src\images\dialog_example.png" width="500"/>
</div>

The execution of the script might take a while due to the translator module being dependent on the online Google Translator API. 

Once the execution is finished, a new csv file will be generated in the [/output](https://github.com/2DegreesInvesting/tiltEPProductsPre-processor/tree/f156280f7f8e54610b6188420b2860492cfdac53/src/data/example_data/output) directory that is stored at the same level as the input directory. This new csv file can be recognized by the `preprocessed` prefix in the filename.

### Setting up databricks environment
To a similar pipeline to the one in the virtual environment in DataBricks, we will use Databricks Workflows. Databricks Workflows enable the use of a drag-and-drop feature when it comes to constructing a pipeline. These pipelines can use Python scripts but also Jupyter Notebooks. Due to the modularity, the latter will be used. But before setting this up, we need to import the repository. You can do this by going to <i>Workspace</i> > <i>Repos</i> > <i>Add</i> > <i>Repo</i> and then add your repo by providing your GitHub URL.

Using Databricks Workflows, requires the following:
* A Databricks Compute Cluster (runtime version 13.0+) which is similar to a Python Virtual Environment
* Data storage means (e.g. Azure Blob Container or Databricks Workspace)

As the notebook also requires the libraries specified in `requirements.txt` file, we need to make sure these are installed. Databricks does not allow to install Python packages from a `requirements.txt` file. The only viable solution that exists is to install each package separately in the cluster libraries. This can be found under <i>Compute</i> > <i>[YOUR CLUSTER NAME]</i> > <i>Libraries</i> and then select the <i>Install New</i> button on the top right corner. You would then need to copy paste each line from the `requirements.txt` file and paste it in the textbox to install it.

Once the required packages are installed, it is time to assemble a Databricks Workflow which contains all the pre-processing steps outlined. To create a Workflow (or actually a "Job"), we can go to the section <i>Workflows</i> and select the <i>Create Job</i> button on the top right corner as shown in the image below.

<div>
<img src="src\images\create_job.png" width="300"/>
</div>

A new page will be loaded in which you will see the following layout.

<div>
<img src="src\images\workflow_start.png" width="1000"/>
</div>

Welcome to the Databricks Workflows Builder! There is a lot of options on the page but we will only focus on a set amount of options. The middle view with the rectangular boxes is where you create so called <i>Tasks</i>. These tasks serve as the building blocks of your workflow. You can see a task as a specific operation that you wish to take place by using for example a script or a notebook. You can give the task whichever name you would like as a reference that can be used by other tasks. For now, we will create a workflow that incorporates the steps outlined in the beginning which are <i>Flagging</i>, <i>Typo correction</i>, <i>Translating</i> and <i>Deduplication</i>.

The workflow that we want to get looks as follows:
<div>
<img src="src\images\final_workflow.png" width="1000"/>
</div>
To achieve this, we will need to create 4 rectangular task boxes by clicking the <i>Add task</i> button. After this has been done, we will fill in the fields that are required for creating a task. To make it easier, a list with the expected values for each of the fields is provided:

* <b>Task name</b>: The task name MUST be the same as show in the image above
* <b>Type</b>: Notebook as we will make use of the notebooks in the repository
* <b>Source</b>: Workspace as the repository is stored there
* <b>Path</b>: The path to your repository in Databricks. Make sure you reference the right notebook for the right task
* <b>Cluster</b>: The cluster which contains all the necessary packages you just installed
* <b>Dependent libaries</b>: NA
* <b>Parameters</b>: Only relevant for the Flagging task. Make sure to set the key to FilePath and the value to some arbitrary placeholder value
* <b>Depends on</b>: Only applicable to the tasks that depedent on the output of another task so every task except the first one
* <b>Notifications</b>: NA
* <b>Retries</b>: NA
* <b>Duration Threshold</b>: NA

Congratulations, you just created your first Databricks Workflow (or actually Job). This workflow can be executed by pressing the <i>Run now</i> button but as we want to provide a path to a file just like the Python script in the VE, we will pass in a so-called <i>Task Parameter</i> to the Job. This parameter contains the csv file name of the file we want to process. To make sure we can supply our own parameter, we will press the small arrow next to the button and click <i>Run now with different parameters</i>. We can then put our file name in the value box next to the FilePath key.  Pressing <i>Run</i> will now execute the Workflow with the provided parameter.
## IMPORTANT NOTES
\* <i> The spelling checker algorithm (TextBlob) used only works with English sentences. The following other spell checker models were considered:
* <b>SpaCy ContextualSpellCheck</b>: only works in English but also not suitable for short sentences (lack of context)
* <b>Huggingface transformer</b>: More accurate but computationally expensive 
* <b>PySpellCheck</b>: does work with different languages but requires single words as input. (aka splitted)  </i>

\** The language detector algorithm was often inaccurate with identifying the right language due to the short length of the sentences. 