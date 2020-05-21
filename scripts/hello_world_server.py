#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
#   Copyright (C) 2020 University of Dundee. All rights reserved.

#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License along
#   with this program; if not, write to the Free Software Foundation, Inc.,
#   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

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
