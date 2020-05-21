Getting started with the OMERO Python API
=========================================

**Description**
---------------

We will show:

- Connect to a server.

- Load images.

- Run a simple `FRAP <https://en.wikipedia.org/wiki/Fluorescence_recovery_after_photobleaching>`_ analysis measuring 
  the intensity within a pre-existing ellipse ROI in a named Channel.

- Save the generated mean intensities and link them to the image(s).

- Save the generated plot on the server.


**Setup**
---------

We recommend to use a Conda environment to install the OMERO Python bindings. Please read first :doc:`setup`.

For the FRAP analysis you need a fluorescence time-lapse image, available at `<https://downloads.openmicroscopy.org/images/DV/will/FRAP/>`_.

The bleached spot has to be marked with an ellipse. Make sure that the ellipse ROI spans the whole timelapse.


**Step-by-Step**
----------------

In this section, we go through the steps required to analyze the data.
The script used in this document is :download:`simple_frap.py <../scripts/simple_frap.py>`.

It is also available as the 'SimpleFRAP' Jupyter notebook in the notebooks section.


Modules and methods which need to be imported:

.. literalinclude:: ../scripts/simple_frap.py
    :start-after: # Imports
    :end-before: # Step 1


Connect to the server. It is also important to close the connection again
to clear up potential resources held on the server. This is done in the 
```disconnect`` method.

.. literalinclude:: ../scripts/simple_frap.py
    :start-after: # Step 1
    :end-before: # Step 3


Load the image:

.. literalinclude:: ../scripts/simple_frap.py
    :start-after: # Step 2
    :end-before: # -


Get relevant channel index:

.. literalinclude:: ../scripts/simple_frap.py
    :start-after: # Step 3
    :end-before: # Step 4


Get Ellipse ROI:

.. literalinclude:: ../scripts/simple_frap.py
    :start-after: # Step 4
    :end-before: # Step 5


Get intensity values:

.. literalinclude:: ../scripts/simple_frap.py
    :start-after: # Step 5
    :end-before: # Step 6


Plot the data using ``matplotlib``:

.. literalinclude:: ../scripts/simple_frap.py
    :start-after: # Step 6
    :end-before: # Step 7


Save the results as Map annotation:

.. literalinclude:: ../scripts/simple_frap.py
    :start-after: # Step 7
    :end-before: # Step 8


Save the plot:

.. literalinclude:: ../scripts/simple_frap.py
    :start-after: # Step 8
    :end-before: # Step 9


In order the use the methods implemented above in a proper standalone script:
Wrap it all up in an ``analyse`` method and call it from ``main``:

.. literalinclude:: ../scripts/simple_frap.py
    :start-after: # Step 9


**Further Reading**
-------------------

How to turn a script into an 
`OMERO script <https://docs.openmicroscopy.org/omero/latest/developers/scripts/index.html>`_ 
which runs on the server and can be directly launched via the web interface, see :doc:`server_script`.

This ``simple_frap.py`` example as server-side OMERO.script: 
:download:`simple_frap_server.py <../scripts/simple_frap_server.py>`.

