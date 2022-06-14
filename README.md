# User guides for the OMERO Python API
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ome/omero-guide-python/master?filepath=notebooks)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ome/omero-guide-python/)
[![Documentation Status](https://readthedocs.org/projects/omero-guide-python/badge/?version=latest)](https://omero-guides.readthedocs.io/en/latest/python/docs/index.html)
[![Actions Status](https://github.com/ome/omero-guide-python/workflows/repo2docker/badge.svg)](https://github.com/ome/omero-guide-python/actions)
[![Actions Status](https://github.com/ome/omero-guide-python/workflows/sphinx/badge.svg)](https://github.com/ome/omero-guide-python/actions) 


The documentation is deployed at [Use Python API](https://omero-guides.readthedocs.io/en/latest/python/docs/index.html)


This guide demonstrates how to use the OMERO Python API.

## Run the notebooks

### Running on cloud resources

* [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ome/omero-guide-python/master?filepath=notebooks)
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
we suggest using conda:

Install Anaconda https://www.anaconda.com/products/individual#Downloads

Then, create the environment:

    $ git clone https://github.com/ome/omero-guide-python
    $ cd omero-guide-python
    $ conda env create -n omero-guide-python -f binder/environment.yml

and activate the newly created environment:

    $ conda activate omero-guide-python

The following steps are only required if you want to run the notebooks

* If you have Anaconda installed:
  * Start Jupyter from the Anaconda-navigator
  * Select the notebook you wish to run and select the ``Kernel>Change kernel>Python [conda env:omero-guide-python]``
* If Anaconda is not installed:
  * In the environment, install ``jupyter`` e.g. ``pip install jupyter``
  * Add the virtualenv as a jupyter kernel i.e. ``ipython kernel install --name "omero-guide-python" --user``
  * Open jupyter notebook i.e. ``jupyter notebook`` and select the ``omero-guide-python`` kernel or ``[conda env:omero-guide-python]`` according to what is available


An additional benefit of installing the requirements locally is that you
can then use the tools without needing to launch Jupyter itself.


See also [setup.rst](https://github.com/ome/omero-guide-python/blob/master/docs/setup.rst)


This is a Sphinx based documentation. 
If you are unfamiliar with Sphinx, we recommend that you first read 
[Getting Started with Sphinx](https://docs.readthedocs.io/en/stable/intro/getting-started-with-sphinx.html).
