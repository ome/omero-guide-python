#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
#   Copyright (C) 2017 University of Dundee. All rights reserved.

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
Simple FRAP plots from Rectangles on images.
This an OMERO script that runs server-side.
"""

import omero

import omero.scripts as scripts
from omero.rtypes import rlong
from omero.gateway import BlitzGateway
from omero.rtypes import robject, rstring

import numpy as np
try:
    import matplotlib.pyplot as plt
except (ImportError, RuntimeError):
    plt = None


def run(conn, params):
    """
    For each image, getTiles() for FRAP rectangle and plot mean intensity.

    Returns list of images
    @param conn   The BlitzGateway connection
    @param params The script parameters
    """
    images = []

    if params.get("Data_Type") == 'Dataset':
        for dsId in params["IDs"]:
            dataset = conn.getObject("Dataset", dsId)
            if dataset:
                for image in dataset.listChildren():
                    images.append(image)
    elif params.get("Data_Type") == 'Image':
        images = list(conn.getObjects('Image', params["IDs"]))

    if len(images) == 0:
        return None
    roi_service = conn.getRoiService()

    frap_plots = []

    for image in images:
        print "---- Processing image", image.id
        result = roi_service.findByImage(image.getId(), None)
        x = 0
        y = 0
        width = 0
        height = 0
        for roi in result.rois:
            print "ROI:  ID:", roi.getId().getValue()
            for s in roi.copyShapes():
                if type(s) == omero.model.RectangleI:
                    x = s.getX().getValue()
                    y = s.getY().getValue()
                    width = s.getWidth().getValue()
                    height = s.getHeight().getValue()
        print "Rectangle:", x, y, width, height
        if x == 0:
            print "  No Rectangle found for this image"
            continue

        c, z = 0, 0
        tile = (int(x), int(y), int(width), int(height))
        pixels = image.getPrimaryPixels()
        size_t = image.getSizeT()
        zct_list = [(z, c, t, tile) for t in range(size_t)]
        planes = pixels.getTiles(zct_list)
        meanvalues = []
        for i, p in enumerate(planes):
            meanvalues.append(p.mean())

        print meanvalues

        # Add values as a Map Annotation on the image
        key_value_data = [[str(t), str(meanvalues[t])] for t in range(size_t)]
        map_ann = omero.gateway.MapAnnotationWrapper(conn)
        namespace = "demo.simple_frap_data"
        map_ann.setNs(namespace)
        map_ann.setValue(key_value_data)
        map_ann.save()
        image.linkAnnotation(map_ann)

        if plt is not None:
            # Code from https://stackoverflow.com/questions/7821518/
            fig = plt.figure()
            plt.subplot(111)
            plt.plot(meanvalues)
            fig.canvas.draw()
            data = np.fromstring(fig.canvas.tostring_rgb(),
                                 dtype=np.uint8, sep='')
            data = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))

            red = data[::, ::, 0]
            green = data[::, ::, 1]
            blue = data[::, ::, 2]
            plane_gen = iter([red, green, blue])
            plot_name = image.getName() + "_FRAP_plot"
            i = conn.createImageFromNumpySeq(plane_gen, plot_name, sizeC=3,
                                             dataset=image.getParent())
            frap_plots.append(i)
        else:
            # If not plot, simply return input image
            frap_plots.append(image)

    return frap_plots


if __name__ == "__main__":
    dataTypes = [rstring('Dataset'), rstring('Image')]
    client = scripts.client(
        'Scipy_Gaussian_Filter.py',
        """
    This script does simple FRAP analysis using Rectangle ROIs previously
    saved on images. If matplotlib is installed, data is plotted and new
    OMERO images are created from the plots.
        """,
        scripts.String(
            "Data_Type", optional=False, grouping="1",
            description="Choose source of images",
            values=dataTypes, default="Dataset"),

        scripts.List(
            "IDs", optional=False, grouping="2",
            description="Dataset or Image IDs.").ofType(rlong(0)),

        authors=["Will Moore", "OME Team"],
        institutions=["University of Dundee"],
        contact="ome-users@lists.openmicroscopy.org.uk",
    )

    try:
        # process the list of args above.
        scriptParams = {}
        for key in client.getInputKeys():
            if client.getInput(key):
                scriptParams[key] = client.getInput(key, unwrap=True)
        print scriptParams

        # wrap client to use the Blitz Gateway
        conn = BlitzGateway(client_obj=client)
        # # Call the main script - returns the number of images processed
        images = run(conn, scriptParams)
        if images is None:
            message = "No images found"
        else:
            message = "Processed %s images" % len(images)
            # return first image:
            client.setOutput("Image", robject(images[0]._obj))

        client.setOutput("Message", rstring(message))

    finally:
        client.closeSession()
