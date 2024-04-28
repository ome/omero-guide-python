# User guides for the OMERO Python API
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ome/omero-guide-python/)
[![Documentation Status](https://readthedocs.org/projects/omero-guide-python/badge/?version=latest)](https://omero-guides.readthedocs.io/en/latest/python/docs/index.html)
[![Actions Status](https://github.com/ome/omero-guide-python/workflows/repo2docker/badge.svg)](https://github.com/ome/omero-guide-python/actions)


The documentation is deployed at [Use Python API](https://omero-guides.readthedocs.io/en/latest/python/docs/index.html)


This guide demonstrates how to use the OMERO Python API.

## Run the notebooks

### Running on cloud resources

* [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ome/omero-guide-python/)

The OMERO server used will need to have [websockets support](https://docs.openmicroscopy.org/omero/latest/sysadmins/websockets.html) enabled.



### Running in Docker


Alternatively, if you have Docker installed, you can use the [repo2docker](https://repo2docker.readthedocs.io/en/latest/)
tool to run this repository as a local Docker instance:

    $ git clone https://github.com/ome/omero-guide-python
    $ cd omero-guide-python
    $ repo2docker .

Then follow the instructions that are printed after the Docker image is built.

### Running locally


Finally, if you would like to install the necessary requirements locally,
we suggest using Mamba:

* If you do not have any pre-existing conda installation, [install Mamba](https://mamba.readthedocs.io/en/latest/installation.html#installation) and use [mambaforge](https://github.com/conda-forge/miniforge#mambaforge). 
* In case you have a pre-existing conda installation, you can install Mamba by either:
  - Using the recommended way to install Mamba from [mambaforge](https://github.com/conda-forge/miniforge#mambaforge). This will not invalidate your conda installation, but possibly your pre-existing conda envs will be in a different location (e.g. ``/Users/USER_NAME/opt/anaconda3/envs/``) then the new mamba envs (e.g. ``/Users/USER_NAME/mambaforge/envs/``). You can verify this by running ``conda env list``. The addition of ``export CONDA_ENVS_PATH=/Users/user/opt/anaconda3/envs/`` into your ``.bashprofile`` or ``.zprofile`` file will fix this. 
  - Use the [Existing conda install](https://mamba.readthedocs.io/en/latest/installation.html#existing-conda-install) way, i.e. run ``conda install mamba -n base -c conda-forge`` whilst in the base environment. This way can take much longer time than the recommended way described above, and might not lead to a successful installation, especially if run on arm64 (Apple Silicon) OS X.

We have prepared an environment.
To create it, please run the commands below. Select the command corresponding to your operating system.

For Windows, OS X x86_64 (NOT arm64 Apple Silicon), Linux:

    $ git clone https://github.com/ome/omero-guide-python
    
    $ cd omero-guide-python

    $ mamba env create -f binder/environment.yml

For OS X arm64 Apple Silicon

    $ git clone https://github.com/ome/omero-guide-python
    
    $ cd omero-guide-python
    
    $ CONDA_SUBDIR=osx-64 mamba env create -f binder/environment.yml

and activate the newly created environment:

    $ conda activate omero-guide-python 


Remember to deactivate the environment when done:

    $ conda deactivate


See also [Conda command reference](https://docs.conda.io/projects/conda/en/latest/commands.html).

The following steps are only required if you want to run the notebooks.

* If you have Anaconda installed:
  * Start Jupyter from the Anaconda-navigator
  * In the conda environment, run ``mamba install ipykernel`` (for OS X Apple Silicon ``CONDA_SUBDIR=osx-64 mamba install ipykernel``)
  * To register the environment, run ``python -m ipykernel install --user --name omero-guide-python``
  * Select the notebook you wish to run and select the ``Kernel>Change kernel>Python [conda env:omero-guide-python]`` or ``Kernel>Change kernel>omero-guide-python``
* If Anaconda is not installed:
  * Add the virtualenv as a jupyter kernel i.e. ``ipython kernel install --name "omero-guide-python" --user``
  * Open jupyter notebook i.e. ``jupyter notebook`` and select the ``omero-guide-python`` kernel or ``[conda env:omero-guide-python]`` according to what is available.

  To stop the notebook server, in the terminal where te server is running, press ``Ctrl C``. The following question will be asked in the terminal ``Shutdown this notebook server (y/[n])?``. Enter the desired choice.
  

See also [setup.rst](https://github.com/ome/omero-guide-python/blob/master/docs/setup.rst)


This is a Sphinx based documentation. 
If you are unfamiliar with Sphinx, we recommend that you first read 
[Getting Started with Sphinx](https://docs.readthedocs.io/en/stable/intro/getting-started-with-sphinx.html).
