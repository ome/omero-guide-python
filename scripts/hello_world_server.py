#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
#   Copyright (C) 2020 University of Dundee. All rights reserved.

#   Redistribution and use in source and binary forms, with or without modification, 
#   are permitted provided that the following conditions are met:
# 
#   Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#   Redistributions in binary form must reproduce the above copyright notice, 
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#   ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
#   WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
#   IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
#   INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY OR CONSEQUENTIAL DAMAGES (INCLUDING,
#   BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
#   OR PROFITS; OR BUSINESS INTERRUPTION)
#   HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS 
#   SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# ------------------------------------------------------------------------------

"""
This a basic OMERO script that runs server-side.
"""

# Import
import omero.scripts as scripts
from omero.gateway import BlitzGateway
from omero.rtypes import robject, rstring


# load
def load_images(conn, dataset_id):
    """
    Load the images in the specified dataset
    :param conn: The BlitzGateway
    :param dataset_id: The dataset's id
    :return: The Images or None
    """
    dataset = conn.getObject("Dataset", dataset_id)
    images = []
    if dataset is None:
        return None
    for image in dataset.listChildren():
        images.append(image)
    if len(images) == 0:
        return None

    for image in images:
        print("---- Processing image", image.id)
    return images


# main
if __name__ == "__main__":
    # Start declaration
    # Define the script name and description, and a single 'required' parameter
    client = scripts.client(
        'Hello World.py',
        """
    This script does connect to OMERO.
        """,
        scripts.Long("datasetId", optional=False),

        authors=["OME Team", "OME Team"],
        institutions=["University of Dundee"],
        contact="ome-users@lists.openmicroscopy.org.uk",
    )
    # Start script
    try:
        # process the list of arguments
        script_params = {}
        for key in client.getInputKeys():
            if client.getInput(key):
                script_params[key] = client.getInput(key, unwrap=True)

        dataset_id = script_params["datasetId"]

        # wrap client to use the Blitz Gateway
        conn = BlitzGateway(client_obj=client)

        # load the images
        images = load_images(conn, dataset_id)

        # return output to the user
        if images is None:
            message = "No images found"
        else:
            message = "Returned %s images" % len(images)
            # return first image:
            client.setOutput("Image", robject(images[0]._obj))

        client.setOutput("Message", rstring(message))
        # end output
    finally:
        client.closeSession()
