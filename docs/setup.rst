Install omero-py
================

In this section, we show how to install omero-py in a `Conda <https://conda.io/en/latest/>`_ environment.
We will use the Python API to access data stored in an OMERO server.


**Setup**
---------

We recommand to install omero-py using Conda.
Conda manages programming environments in a manner similar to 
`virtualenv <https://virtualenv.pypa.io/en/stable/>`_.

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
