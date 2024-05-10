#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
# Copyright (c) 2022-2024 University of Dundee.
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
import re

# omero
from omero.gateway import BlitzGateway
from omero_zarr import masks

# cellpose
from cellpose import io, models, utils

# geojson
from geojson import Feature, FeatureCollection, Polygon
import geojson

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
    Load an existing model from Cellpose
    """
    return models.Cellpose(gpu=False, model_type='cyto')


# Predict and save the shapes as geojson.
def predict(image_id, data, model, size_z):
    """
    Predict object probabilities and star-convex polygon distances
    Convert the generated labels into geojson
    """

    channels = [[0, 1]]
    t = 0
    shapes = []
    for z in range(size_z):
        cellpose_masks, flows, styles, diams = model.eval(data[t, :, z, :, :], diameter=None, channels=channels)
        outlines = utils.outlines_list(cellpose_masks)
        name = str(image_id) + "_" + str(z)
        io.outlines_to_text(name, outlines)
        with open(name + "_cp_outlines.txt", "r") as text_file:
            for line in text_file:
                points = re.sub(r',([^,]*),', r',\1, ', line)
                splited = re.split('\s+', points)
                coordinates = []
                for value in splited:
                    point = re.split(',', value)
                    if len(point) > 1:
                        coordinates.append((float(point[0]), float(point[1])))
                # append the first coordinate to close the polygon
                coordinates.append(coordinates[0])
                shape = Polygon(coordinates)
                properties = {
                    "stroke-width": 1,
                    "z": z,
                }
                shapes.append(Feature(geometry=shape, properties=properties))

    return FeatureCollection(shapes)


def save_labels_as_geojson(gc, image_id):
    """
    Save the labels locally
    """
    geojson_file = "cellpose_shapes_%s.geojson" % image_id
    geojson_dump = geojson.dumps(gc, sort_keys=True)
    with open(geojson_file, 'w') as out:
        out.write(geojson_dump)

# Disconnect
def disconnect(conn):
    conn.close()

# main
def main():
    # Collect user credentials
    try:
        host = "ws://idr.openmicroscopy.org/omero-ws"
        username = "public"
        password = "public"
        image_id = "6001247"

        # Connect to the server
        conn = connect(host, username, password)

        # Load the image
        image = load_image(conn, image_id)

        global data
        data = load_binary_from_server(image)
        labels = load_labels_as_masks(conn, image)

        # Load the Cellpose model
        model = load_model()

        # Predict using the loaded model
        # number of z sections to analyse
        z = 2 # max is the number of z sections
        gc = predict(image_id, data, model, z)

        # Save the labels as geojson
        save_labels_as_geojson(gc, image_id)


    finally:
        disconnect(conn)
    print('done')


if __name__ == "__main__":
    main()
