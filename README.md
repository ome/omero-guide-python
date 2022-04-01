# User guides for the OMERO Python API
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ome/omero-guide-python/master?filepath=notebooks)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ome/omero-guide-python/)
[![Documentation Status](https://readthedocs.org/projects/omero-guide-python/badge/?version=latest)](https://omero-guides.readthedocs.io/en/latest/python/docs/index.html)
[![Actions Status](https://github.com/ome/omero-guide-python/workflows/repo2docker/badge.svg)](https://github.com/ome/omero-guide-python/actions)
[![Actions Status](https://github.com/ome/omero-guide-python/workflows/sphinx/badge.svg)](https://github.com/ome/omero-guide-python/actions) 


The documentation is deployed at [Use Python API](https://omero-guides.readthedocs.io/en/latest/python/docs/index.html)


This guide demonstrates how to use the OMERO Python API.

To run the notebooks, you can either build locally with [repo2docker](https://repo2docker.readthedocs.io/) or [run on mybinder.org](https://mybinder.org/v2/gh/ome/omero-guide-python/master?filepath=notebooks) or [run in Colab](https://colab.research.google.com/github/ome/omero-guide-python/). To run the notebooks either on [mybinder.org](https://mybinder.org/v2/gh/ome/omero-guide-python/master?filepath=notebooks) or [Colab](https://colab.research.google.com/github/ome/omero-guide-python/), the OMERO server you use will need to have [websockets support](https://docs.openmicroscopy.org/omero/latest/sysadmins/websockets.html) enabled.

## Run the scripts and notebooks locally

Building locally using ``repo2docker``:

 * Install [Docker](https://www.docker.com/) if required
 * Create a virtual environment and install repo2docker from PyPI.
 * Clone this repository
 * Run ``repo2docker``. 
 * Depending on the permissions, you might have to run the command as an admin

Running the commands:

```
pip install jupyter-repo2docker
git clone https://github.com/ome/omero-guide-python.git
cd omero-guide-python
repo2docker .
```

Building locally using conda and Jupyter:

 * Create a conda environment i.e. ``conda env update -n stardist -f binder/environment.yml``
 * Activate the newly created environment

The following steps are only required if you want to run the notebooks
 * If you have Anaconda installed:
   * Start Jupyter from the Anaconda-navigator
   * Select the notebook you wish to run and select the ``Kernel>Change kernel>Python [conda env:stardist]``
 * If Anaconda is not installed:
   * In the environment, install ``jupyter`` e.g. ``pip install jupyter``
   * Add the virtualenv as a jupyter kernel i.e. ``ipython kernel install --name "stardist" --user``
   * Open jupyter notebook i.e. ``jupyter notebook`` and select the ``stardist`` kernel or ``[conda env:stardist]`` according to what is available


See also [setup.rst](https://github.com/ome/omero-guide-python/blob/master/docs/setup.rst)


This is a Sphinx based documentation. 
If you are unfamiliar with Sphinx, we recommend that you first read 
[Getting Started with Sphinx](https://docs.readthedocs.io/en/stable/intro/getting-started-with-sphinx.html).
