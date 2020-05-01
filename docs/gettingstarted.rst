Getting started with the OMERO Python API
 ========================================

**Description**
---------------

We will use a Python script showing how to analyze data stored in an OMERO server.

We will show:

- How to connect to server.

- How load images from a dataset.

- Run a simple FRAP analysis measuring the intensity in a named Channel within an existing ellipse.

- How to save the generated mean intensities and linked them to the image(s).

**Setup**
---------

We recommend to use a Conda environment to install the OMERO Python bindings. Please read first :doc:`setup`.


**Step-by-Step**
----------------

In this section, we go over the various steps required to analyse the data.
The script used in this document is :download:`simple_frap.py <../scripts/simple_frap.py>`.

Connect to the server:

.. literalinclude:: ../scripts/simple_frap.py
    :start-after: # Connect
    :end-before: # Load-images


Load the dataset:

.. literalinclude:: ../scripts/simple_frap.py
    :start-after: # Load-images
    :end-before: # Analyse-images


We are now ready to analyze the images in the dataset:

.. literalinclude:: ../scripts/simple_frap.py
    :start-after: # Analyse-images
    :end-before: # Get channel

Save the results as map annotation:

.. literalinclude:: ../scripts/simple_frap.py
    :start-after: # Save-results
    :end-before: # Delete-old-annotations

When done, close the session:

.. literalinclude:: ../scripts/simple_frap.py
    :start-after: # Disconnect
    :end-before: # main


**Exercises**
-------------
