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
Simple FRAP plot from Ellipse ROI on time-lapse image.
This an OMERO script that runs server-side.
"""

from omero.gateway import BlitzGateway, MapAnnotationWrapper
from omero.model import EllipseI
from PIL import Image
import numpy as np
import matplotlib
from matplotlib import pyplot as plt

# OMERO.script specific imports
import omero.scripts as scripts
from omero.rtypes import rlong, rstring, robject


def get_channel_index(image, label):
    """
    Get the channel index of a specific channel
    :param image: The image
    :param label:  The channel name
    :return: The channel index (None if not found)
    """
    labels = image.getChannelLabels()
    if label in labels:
        idx = labels.index(label)
        return idx
    return None


def get_ellipse_roi(conn, image):
    """
    Get the first ellipse ROI found in the image
    :param conn: The BlitzGateway
    :param image: The Image
    :return: The shape ID of the first ellipse ROI found
    """
    roi_service = conn.getRoiService()
    result = roi_service.findByImage(image.getId(), None)
    shape_id = None
    for roi in result.rois:
        for s in roi.copyShapes():
            if type(s) == EllipseI:
                shape_id = s.id.val
    return shape_id


def get_mean_intensities(conn, image, the_c, shape_id):
    """
    Get the mean pixel intensities of an roi in a time series image
    :param conn: The BlitzGateway
    :param image: The image
    :param the_c: The channel index
    :param shape_id: The ROI shape id
    :return: List of mean intensity values (one for each timepoint)
    """
    roi_service = conn.getRoiService()
    the_z = 0
    size_t = image.getSizeT()
    meanvalues = []
    for t in range(size_t):
        stats = roi_service.getShapeStatsRestricted([shape_id],
                                                    the_z, t, [the_c])
        meanvalues.append(stats[0].mean[the_c])
    return meanvalues


def plot(values, plot_filename):
    """
    Create a simple plot of the given values
    and saves it.
    :param values: The values
    :param plot_filename: The file name
    :return: Nothing
    """
    matplotlib.use('Agg')
    fig = plt.figure()
    plt.subplot(111)
    plt.plot(values)
    fig.canvas.draw()
    fig.savefig(plot_filename)


def save_values(conn, image, values):
    """
    Attach the values as map annotation to the image
    :param conn: The BlitzGateway
    :param image: The image
    :param values: The values
    :return: Nothing
    """
    namespace = "demo.simple_frap_data"
    key_value_data = [[str(t), str(value)] for t, value in enumerate(values)]
    map_ann = MapAnnotationWrapper(conn)
    map_ann.setNs(namespace)
    map_ann.setValue(key_value_data)
    map_ann.save()
    image.linkAnnotation(map_ann)


def save_plot(conn, image, plot_filename):
    """
    Save the plot to OMERO
    :param conn: The BlitzGateway
    :param image: The image
    :param plot_filename: The path to the plot image
    :return: The plot image
    """
    pil_img = Image.open(plot_filename)
    np_array = np.asarray(pil_img)
    red = np_array[::, ::, 0]
    green = np_array[::, ::, 1]
    blue = np_array[::, ::, 2]
    plane_gen = iter([red, green, blue])
    plot_image = conn.createImageFromNumpySeq(plane_gen, plot_filename,
                                              sizeC=3,
                                              dataset=image.getParent())
    return plot_image


def delete_old_values(conn, image):
    """
    Delete previously attached Map annotations
    :param conn: The BlitzGateway
    :param image: The image
    """
    namespace = "demo.simple_frap_data"
    to_delete = []
    for ann in image.listAnnotations(ns=namespace):
        to_delete.append(ann.id)
    if len(to_delete) > 0:
        conn.deleteObjects('Annotation', to_delete, wait=True)


def analyse(conn, image_id, channel_name):
    # Step 2 - Load iamge
    img = conn.getObject("Image", image_id)
    # -
    ci = get_channel_index(img, channel_name)
    shape_id = get_ellipse_roi(conn, img)
    values = get_mean_intensities(conn, img, ci, shape_id)
    delete_old_values(conn, img)
    save_values(conn, img, values)
    plot_name = "{}_plot.png".format(img.getName())
    plot(values, plot_name)
    return save_plot(conn, img, plot_name)


if __name__ == "__main__":
    client = scripts.client(
        'simple_frap_omero.py',
        """
    This script does simple FRAP analysis using an Ellipse ROI previously
    saved on a time-lapse image. Data is plotted and a new OMERO images is
    created from the plot.
        """,
        scripts.String(
            "Data_Type", optional=False, grouping="1",
            description="Data type",
            values=[rstring('Image')], default="Image"),
        scripts.List(
            "IDs", optional=False, grouping="2",
            description="Image IDs.").ofType(rlong(0)),
        scripts.String(
            "Channel_Name", optional=False, grouping="3",
            description="Channel name:"),

        authors=["OME Team"],
        institutions=["University of Dundee"],
        contact="training-support@openmicroscopy.org",
    )
    try:
        # Wrap the script parameters into a dictionary
        scriptParams = {}
        for key in client.getInputKeys():
            if client.getInput(key):
                scriptParams[key] = client.getInput(key, unwrap=True)

        # Use existing session via client object
        conn = BlitzGateway(client_obj=client)

        plots = []
        for image_id in scriptParams["IDs"]:
            plots.append(analyse(conn, image_id,
                         scriptParams["Channel_Name"]))

        client.setOutput("Image", robject(plots[0]._obj))
        client.setOutput("Message", rstring("Created {} plot(s)."
                                            .format(len(plots))))
    finally:
        client.closeSession()
