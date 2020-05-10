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

from dask.diagnostics import ProgressBar
import dask
import dask.array as da
import dask_image.ndfilters
import dask_image.ndmeasure

from omero.gateway import BlitzGateway

import time

# Dask array loaded from S3
data = None


# Connect to the server
def connect(hostname, username, password):
    conn = BlitzGateway(username, password,
                        host=hostname, secure=True)
    print(conn.connect())
    conn.c.enableKeepAlive(60)
    return conn


# Load-Image
def load_image(conn, image_id):
    return conn.getObject('Image', image_id)


# Load-binary
def load_binary_from_s3(id, resolution='4'):
    endpoint_url = 'https://s3.embassy.ebi.ac.uk/'
    root = 'idr/zarr/v0.1/%s.zarr/%s/' % (id, resolution)
    with ProgressBar():
        data = da.from_zarr(endpoint_url + root)
    return data


# Segment-image
def analyze(t, c, z):
    plane = data[t, c, z, :, :]
    smoothed_image = dask_image.ndfilters.gaussian_filter(plane, sigma=[1, 1])
    threshold_value = 0.75 * da.max(smoothed_image).compute()
    threshold_image = smoothed_image > threshold_value
    label_image, num_labels = dask_image.ndmeasure.label(threshold_image)
    name = 't:%s, c: %s, z:%s' % (t, c, z)
    print(name)
    return label_image, name


# Prepare-call
def prepare_call(image):
    number_t = image.getSizeT()  # reduce for demo
    number_z = image.getSizeZ()
    number_c = image.getSizeC()
    lazy_results = []
    for t in range(number_t):
        for z in range(number_z):
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
        print(data)

        lazy_results = prepare_call(image)

        start = time.time()
        compute(lazy_results)
        elapsed = time.time() - start
        print(elapsed)

    finally:
        disconnect(conn)
    print('done')


if __name__ == "__main__":
    main()
