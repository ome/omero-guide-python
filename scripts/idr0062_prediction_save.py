#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
# Copyright (c) 2022 University of Dundee.
#
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
#
# Version: 1.0
#

import numpy

# omero
import omero
import omero.clients
from omero.gateway import BlitzGateway
from getpass import getpass

# stardist
from stardist.models import StarDist2D
from csbdeep.utils import normalize


# Connect to the server
def connect(hostname, username, password):
    """
    Connect to the server
    """
    conn = BlitzGateway(username, password,
                        host=hostname, secure=True)
    print("Connected: %s" % conn.connect())
    conn.c.enableKeepAlive(60)
    return conn


# Load-image
def load_image(conn, image_id):
    """
    Load the Image object.
    """
    return conn.getObject('Image', image_id)


# Load-Binary-from-server
def load_binary_from_server(image):
    """
    Load the binary data as a TCZYX numpy array.
    """
    pixels = image.getPrimaryPixels()
    size_z = image.getSizeZ()
    size_c = image.getSizeC()
    size_t = image.getSizeT()
    size_y = image.getSizeY()
    size_x = image.getSizeX()
    z, t, c = 0, 0, 0  # first plane of the image

    zct_list = []
    for t in range(size_t):
        for c in range(size_c):  # all channels
            for z in range(size_z):  # get the Z-stack
                zct_list.append((z, c, t))

    values = []
    # Load all the planes as YX numpy array
    planes = pixels.getPlanes(zct_list)
    s = "t:%s c:%s z:%s y:%s x:%s" % (size_t, size_c, size_z, size_y, size_x)
    print(s)
    print("Downloading image %s" % image.getName())
    all_planes = numpy.stack(list(planes))
    shape = (size_t, size_c, size_z, size_y, size_x)
    return numpy.reshape(all_planes, newshape=shape)


# Load-Labels-as-Masks
def load_labels_as_masks(conn, image):
    """
    Loads the masks from server
    """
    roi_service = conn.getRoiService()
    result = roi_service.findByImage(image.getId(), None)

    dims = (image.getSizeT(), image.getSizeC(), image.getSizeZ(),
            image.getSizeY(), image.getSizeX())
    shapes = []
    for roi in result.rois:
        shapes.append(roi.copyShapes())

    saver = masks.MaskSaver(None, image, numpy.int64)
    labels, fillColors, properties = saver.masks_to_labels(shapes, mask_shape=dims)


# Load-Model
def load_model():
    """
    Load an existing model from StarDist
    """
    return StarDist2D.from_pretrained('2D_demo')


# Predict and save the shapes as geojson.
def predict(data, model):
    """
    Predict object probabilities and star-convex polygon distances
    Convert the generated labels into geojson
    """

    axis_norm = (0,1)
    c = 1
    img = normalize(data[0, c, :, :, :], 1,99.8, axis=axis_norm)
    results_details = []
    for i in range(len(img)):
        new_labels, details = model_versatile.predict_instances(img[i])
        results_details.append(details)

    return results_details


def save_labels_in_omero(conn, image, results_details):
    """
    Save the labels back to the server
    """
    c = 1

    rois = []
    for i in range(len(results_details)):
        details = results_details[i]
        roi = omero.model.RoiI()
        roi.setImage(image._obj)
        for obj_id, region in enumerate(details['coord']):
            coordinates = []
            x = region[1]
            y = region[0]
            for j in range(len(x)):
                coordinates.append(str(float(x[j])) + "," + str(float(y[j])))
            joined_string = ", ". join(coordinates)
            polygon = omero.model.PolygonI()
            polygon.theZ = omero.rtypes.rint(i)
            polygon.theC = omero.rtypes.rint(c)
            polygon.strokeWidth = omero.model.LengthI(2, omero.model.enums.UnitsLength.PIXEL)
            polygon.points = omero.rtypes.rstring(joined_string)
            polygon.textValue = omero.rtypes.rstring("stardist")
            roi.addShape(polygon)
            rois.append(roi)
    conn.getUpdateService().saveCollection(rois)

# Disconnect
def disconnect(conn):
    conn.close()

# main
def main():
    # Collect user credentials
    try:
        host = input("Host [wss://workshop.openmicroscopy.org/omero-ws]: ") or 'wss://workshop.openmicroscopy.org/omero-ws'  # noqa
        username = input("Username [trainer-1]: ") or 'trainer-1'
        password = getpass("Password: ")
        image_id = input("Image ID [55506]: ") or '55506'

        # Connect to the server
        conn = connect(host, username, password)

        # Load the image
        image = load_image(conn, image_id)

        global data
        data = load_binary_from_server(image)

        # Load the StarDist model
        model = load_model()

        # Predict using the loaded model
        # Prediction done on the first channel
        stardist_labels  = predict(data, model)

        # Save the labels back to the server
        save_labels_in_omero(conn, image, stardist_labels)


    finally:
        disconnect(conn)
    print('done')


if __name__ == "__main__":
    main()
