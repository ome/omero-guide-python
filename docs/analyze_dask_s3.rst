Analyze data stored in a public S3 repository in parallel 
=========================================================

Description
-----------

We will show how to use `dask <https://dask.org/>`_ to analyze an IDR image
stored in a public S3 repository

We will show:

- How to connect to IDR to retrieve the image metadata.

- How to load the Zarr binary stored in a public repository.

- How to run a segmentation on each plane in parallel.


Setup
-----

We recommend to use a Conda environment to install the OMERO Python bindings. Please read first :doc:`setup`.

Step-by-Step
------------

In this section, we go through the steps required to analyze the data.
The script used in this document is :download:`public_s3_segmentation_parallel.py <../scripts/public_s3_segmentation_parallel.py>`.

Load the image and reate a dask array from the Zarr storage format:

.. literalinclude:: ../scripts/public_s3_segmentation_parallel.py
    :start-after: # Load-binary
    :end-before: # Segment-image


Define the analysis function:

.. literalinclude:: ../scripts/public_s3_segmentation_parallel.py
    :start-after: # Segment-image
    :end-before: # Prepare-call


Make our function lazy using ``dask.delayed``.
It records what we want to compute as a task into a graph that we will run later in parallel:

.. literalinclude:: ../scripts/public_s3_segmentation_parallel.py
    :start-after: # Prepare-call
    :end-before: # Compute

We are now ready to run in parallel using the default number of workers see `Configure dask.compute <https://docs.dask.org/en/latest/scheduler-overview.html#configuring-the-schedulers>`_:

.. literalinclude:: ../scripts/public_s3_segmentation_parallel.py
    :start-after: # Compute
    :end-before: # main

In order to use the methods implemented above in a proper standalone script:
**Wrap it all up** in ``main``:

.. literalinclude:: ../scripts/public_s3_segmentation_parallel.py
    :start-after: # main
