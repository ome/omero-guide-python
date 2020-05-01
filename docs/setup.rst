Install omero-py
================

In this section, we show how to install omero-py in a `Conda <https://conda.io/en/latest/>`_ environment.
We will use the Python API to access data stored in an OMERO server.


**Setup**
---------

We recommend to install omero-py using Conda.
Conda manages programming environments in a manner similar to 
`virtualenv <https://virtualenv.pypa.io/en/stable/>`_.
You can install the various dependencies following the steps below (Option 1) or build locally a Docker Image
using ``repo2docker`` (Option 2). When the installation is done, you should be ready to use the CellProfiler API and OMERO, see :doc:`gettingstarted`.

*Option 1*
~~~~~~~~~~

- Install `Miniconda <https://docs.conda.io/en/latest/miniconda.html>`_ if necessary.

- If you do not have a local copy of the `omero-guide-python repository <https://github.com/ome/omero-guide-python>`_, first clone the repository::

    $ git clone https://github.com/ome/omero-guide-python.git

- Go into the directory::

    $ cd omero-guide-python

- Create a programming environment using Conda::

    $ conda create -n omeropy python=3.6

- Install ``omero-py`` and other packages useful for demonstration purposes in order to connect to an OMERO server using an installation file::

    $ conda env update -n omeropy --file binder/environment.yml 

- Activate the environment::

    $ conda activate omeropy

*Option 2*
~~~~~~~~~~

Alternatively you can create a local Docker Image using ``repo2docker``, see :download:`README.md <https://github.com/ome/omero-guide-python/blob/master/README.md>`::

    $ repo2docker .

When the Image is ready:

- Copy the URL displayed in the terminal in your favorite browser

- Click the ``New`` button on the right-hand side of the window

- Select ``Terminal``

.. image:: images/terminal.png

- A Terminal will open in a new Tab

- A Conda environment has already been created when the Docker Image was built

- To list all the Conda environment, run::

    $ conda env list

- The environment with the OMERO Python bindings and few other libraries is named ``notebook``, activate it::

    $ conda activate notebook
