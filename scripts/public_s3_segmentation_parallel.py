#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
# Copyright (c) 2020 University of Dundee.
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

import dask
import dask.array as da
import dask_image.ndfilters
import dask_image.ndmeasure

import matplotlib.pyplot as plt
import numpy

from omero.gateway import BlitzGateway

import time

# Dask array loaded from S3
data = None


# Connect to the server
def connect(hostname, username, password):
    conn = BlitzGateway(username, password,
                        host=hostname, secure=True)
    print("Connected: %s" % conn.connect())
    conn.c.enableKeepAlive(60)
    return conn


# Load-image
def load_image(conn, image_id):
    return conn.getObject('Image', image_id)


# Load-binary
def load_binary_from_s3(id, resolution='4'):
    endpoint_url = 'https://s3.embassy.ebi.ac.uk/'
    root = 'idr/zarr/v0.1/%s.zarr/%s/' % (id, resolution)
    return da.from_zarr(endpoint_url + root)


# Segment-image
def analyze(t, c, z):
    plane = data[t, c, z, :, :]
    smoothed_image = dask_image.ndfilters.gaussian_filter(plane, sigma=[1, 1])
    threshold_value = 0.75 * da.max(smoothed_image).compute()
    threshold_image = smoothed_image > threshold_value
    label_image, num_labels = dask_image.ndmeasure.label(threshold_image)
    name = 't:%s, c: %s, z:%s' % (t, c, z)
    print("Plane coordinates: %s" % name)
    ref = 't_%s_c_%s_z_%s' % (t, c, z)
    return label_image, ref


# Prepare-call
def prepare_call(image):
    middle_z = image.getSizeZ() // 2
    middle_t = image.getSizeT() // 2
    range_t = 5
    range_z = 5
    number_c = image.getSizeC()
    lazy_results = []
    for t in range(middle_t - range_t, middle_t + range_t):
        for z in range(middle_z - range_z, middle_z + range_z):
            for c in range(number_c):
                lazy_result = dask.delayed(analyze)(t, c, z)
                lazy_results.append(lazy_result)
    return lazy_results


# Compute
def compute(lazy_results):
    return dask.compute(*lazy_results)


# Disconnect
def disconnect(conn):
    conn.close()


# Save the first 5 results on disk
def save_results(results):
    print("Saving locally the first 5 results as png")
    for r, name in results[:5]:
        array = numpy.asarray(r)
        value = "image_%s.png" % name
        plt.imsave(value, array)


# main
def main():
    # Collect user credentials
    try:
        host = "ws://idr.openmicroscopy.org/omero-ws"
        username = "public"
        password = "public"
        image_id = "4007801"

        # Connect to the server
        conn = connect(host, username, password)

        # Load the image
        image = load_image(conn, image_id)

        global data
        data = load_binary_from_s3(image_id)
        print("Dask array: %s" % data)

        lazy_results = prepare_call(image)

        start = time.time()
        results = compute(lazy_results)
        elapsed = time.time() - start
        print('Compute time (in seconds): %s' % elapsed)
        save_results(results)

    finally:
        disconnect(conn)
    print('done')


if __name__ == "__main__":
    main()
