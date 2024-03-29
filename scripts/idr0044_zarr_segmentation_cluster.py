#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
# Copyright (c) 2020-2022 University of Dundee.
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions
#   are met:
#
#   Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#   Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#   AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#   ARE DISCLAIMED.
#   IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY
#   DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY OR CONSEQUENTIAL DAMAGES
#   (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#   SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#   HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
#   LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
#   OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
#   DAMAGE.
#
# Version: 1.0
#

from dask.distributed import Client, LocalCluster

import dask.array as da
import dask_image.ndfilters
import dask_image.ndmeasure

import matplotlib.pyplot as plt
import numpy

import time

# Dask array loaded from S3
data = None


# Load-binary
def load_binary_from_s3(id, resolution='4'):
    endpoint_url = 'https://uk1s3.embassy.ebi.ac.uk/'
    root = 'idr/zarr/v0.1/%s.zarr/%s/' % (id, resolution)
    return da.from_zarr(endpoint_url + root)


# Segment-image
def analyze(t, c, z):
    plane = data[t, c, z, :, :]
    smoothed_image = dask_image.ndfilters.gaussian_filter(plane, sigma=[1, 1])
    threshold_value = 0.33 * da.max(smoothed_image).compute()
    threshold_image = smoothed_image > threshold_value
    label_image, num_labels = dask_image.ndmeasure.label(threshold_image)
    name = 't:%s, c: %s, z:%s' % (t, c, z)
    print("Plane coordinates: %s" % name)
    ref = 't_%s_c_%s_z_%s' % (t, c, z)
    return label_image, ref


# Prepare-call
def prepare_call(client, dimensions):
    middle_z = dimensions[2] // 2
    middle_t = dimensions[0] // 2
    range_t = 2
    range_z = 2
    number_c = 1  # dimensions[1]
    futures = []
    for t in range(middle_t - range_t, middle_t + range_t):
        for z in range(middle_z - range_z, middle_z + range_z):
            for c in range(number_c):
                futures.append(client.submit(analyze, t, c, z))
    return futures


# Save the first 5 results on disk
def save_results(results):
    print("Saving locally the first 5 results as png")
    for r, name in results[:5]:
        array = numpy.asarray(r)
        value = "image_%s.png" % name
        plt.imsave(value, array)


# main
def main():
    # Collect image ID
    image_id = "4007801"

    global data
    data = load_binary_from_s3(image_id)
    print("Dask array: %s" % data)

    cluster = LocalCluster(n_workers=2, processes=True, threads_per_worker=1)

    start = time.time()
    with Client(cluster) as client:

        futures = prepare_call(client, data.shape)
        results = client.gather(futures)

    elapsed = time.time() - start
    print('Compute time (in seconds): %s' % elapsed)
    save_results(results)
    print('done')


if __name__ == "__main__":
    main()
