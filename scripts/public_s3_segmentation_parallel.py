#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
# Copyright (c) 2020 University of Dundee.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# FPBioimage was originally published in
# <https://www.nature.com/nphoton/journal/v11/n2/full/nphoton.2016.273.html>.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
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
