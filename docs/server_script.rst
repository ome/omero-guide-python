How to write a server-side script 
=================================


In this section, we show how to convert a Python script into a script that can
be run server-side.
We recommend that you read `OMERO.scripts guide <https://docs.openmicroscopy.org/omero/latest/developers/scripts/user-guide.html>`_.

Description
-----------

We will make a simple ``Hello World`` script as client-side Python script 
and show how to convert it into a server-side script.
The script will:

- Connect to the server
- Load images in a dataset


Setup
-----

We recommend to use a Conda environment to install the OMERO Python bindings. Please read first :doc:`setup`.


Step-by-step
------------

The scripts used in this document are :download:`hello_world.py <../scripts/hello_world.py>`
and :download:`hello_world_server.py <../scripts/hello_world_server.py>`.


Client-side script
~~~~~~~~~~~~~~~~~~

Let's first start by writing a **client-side** script named ``hello_world.py``.

Connect to the server:

.. literalinclude:: ../scripts/hello_world.py
    :start-after: # Step 1
    :end-before: # Step 2


Load the images in the dataset:

.. literalinclude:: ../scripts/hello_world.py
    :start-after: # Step 2
    :end-before: # main

Collect the script parameters:

.. literalinclude:: ../scripts/hello_world.py
    :start-after: # Collect
    :end-before: # Connect

In order the use the methods implemented above in a proper standalone script:
Wrap it all up and call them from ``main``:

.. literalinclude:: ../scripts/hello_world.py
    :start-after: # main

Server-side script
~~~~~~~~~~~~~~~~~~

Now let's see how to convert the script above into a **server-side** script.

The first step is to declare the parameters, the UI components will be built automatically from it. This script only needs to collect the dataset ID:

.. literalinclude:: ../scripts/hello_world_server.py
    :start-after: # Define
    :end-before: # Start

Process the arguments:

.. literalinclude:: ../scripts/hello_world_server.py
    :start-after: # process
    :end-before: # wrap

Access the date using the Python gateway:

.. literalinclude:: ../scripts/hello_world_server.py
    :start-after: # wrap client
    :end-before: # load the images

We can then use the same method that the one in the client-side script to load the images

.. literalinclude:: ../scripts/hello_world_server.py
    :start-after: # load
    :end-before: # main

In order the use the methods implemented above in a proper standalone script and return the output to the users: Wrap it all up and call them from main:

.. literalinclude:: ../scripts/hello_world_server.py
    :start-after: # main
