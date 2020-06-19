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
Run Gaussian Filter from Scipy on Project/Dataset/Image/Screen/Plate/Well.
This an OMERO script that runs server-side.
"""

import omero

import time
import omero.scripts as scripts
from omero.rtypes import rlong, robject, rstring, wrap
from omero.gateway import MapAnnotationWrapper, DatasetWrapper
from omero.gateway import BlitzGateway
from omero.rtypes import *  # noqa

import json
from cStringIO import StringIO

import scipy.ndimage as spi


def run(conn, params):
    """
    For each image, apply filter and load the result into OMERO.

    Returns the number of images processed or -1 if there is a
    parameter error.
    @param conn   The BlitzGateway connection
    @param params The script parameters
    """

    # Get parameters. These are 'required' so we know they will be populated
    window_size = params.get("Kernel_Window_Size")
    sigma = params.get("Sigma")

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

    # Create new Dataset
    new_dataset = DatasetWrapper(conn, omero.model.DatasetI())
    new_dataset.setName('Scipy_Gaussian_Filter')
    new_dataset.save()

    # Extract images
    image_ids = []
    for image in images:

        sizeZ = image.getSizeZ()
        sizeC = image.getSizeC()
        sizeT = image.getSizeT()
        zctList = []
        for z in range(sizeZ):
            for c in range(sizeC):
                for t in range(sizeT):
                    zctList.append((z, c, t))

        plane = planeGen(image, zctList, window_size, sigma)
        name = image.getName() + "_gaussian"
        i = conn.createImageFromNumpySeq(plane, name, sizeZ, sizeC,
                                         sizeT, description="Gaussian Filter",
                                         dataset=new_dataset,
                                         sourceImageId=image.id)

        image_ids.append(i.getId())

        add_map_annotation(conn, i, params)
    return image_ids, new_dataset


def planeGen(image, zctList, window, sigma):
    """Generator will yield planes."""
    planes = image.getPrimaryPixels().getPlanes(zctList)
    for p in planes:
        data = spi.filters.gaussian_filter(p, sigma=sigma)
        yield data


def add_map_annotation(conn, image, params):
    """Add key-value pairs from params onto image."""
    window_size = params.get("Kernel_Window_Size")
    sigma = params.get("Sigma")
    key_value_data = [["Kernel Window Size", str(window_size)],
                      ["Sigma", str(sigma)]]
    print("Adding MAP", key_value_data, image.getId())
    map_ann = MapAnnotationWrapper(conn)
    # Use 'client' namespace to allow editing in Insight & web
    map_ann.setNs(omero.constants.metadata.NSCLIENTMAPANNOTATION)
    map_ann.setValue(key_value_data)
    map_ann.save()
    # NB: only link a client map annotation to a single object
    image.linkAnnotation(map_ann)

# OMERO Figure Methods


def get_panel_json(image, x, y, width, height, channel=None):
    """Export the results as OMERO.figure."""
    rv = imageMarshal(image)

    if channel is not None:
        for idx, ch in enumerate(rv['channels']):
            ch['active'] = idx == channel

    img_json = {
        "labels": [],
        "height": height,
        "channels": rv['channels'],
        "width": width,
        "sizeT": rv['size']['t'],
        "sizeZ": rv['size']['z'],
        "dx": 0,
        "dy": 0,
        "rotation": 0,
        "imageId": image.getId(),
        "name": image.getName(),
        "orig_width": rv['size']['width'],
        "zoom": 100,
        "shapes": [],
        "orig_height": rv['size']['height'],
        "theZ": rv['rdefs']['defaultZ'],
        "y": y,
        "x": x,
        "theT": rv['rdefs']['defaultT']
    }
    return img_json


def channelMarshal(channel):
    """
    Return a dict with all there is to know about a channel.

    @param channel:     L{omero.gateway.ChannelWrapper}
    @return:            Dict
    """
    chan = {'emissionWave': channel.getEmissionWave(),
            'label': channel.getLabel(),
            'color': channel.getColor().getHtml(),
            # 'reverseIntensity' is deprecated. Use 'inverted'
            'inverted': channel.isInverted(),
            'reverseIntensity': channel.isInverted(),
            'window': {'min': channel.getWindowMin(),
                       'max': channel.getWindowMax(),
                       'start': channel.getWindowStart(),
                       'end': channel.getWindowEnd()},
            'active': channel.isActive()}
    lut = channel.getLut()
    if lut and len(lut) > 0:
        chan['lut'] = lut
    return chan


def imageMarshal(image, key=None, request=None):
    """
    Return a dict with pretty much everything we know and care about an image.

    @param image:   L{omero.gateway.ImageWrapper}
    @param key:     key of specific attributes to select
    @return:        Dict
    """
    image.loadRenderOptions()
    pr = image.getProject()
    ds = None
    wellsample = None
    well = None
    parents = image.listParents()
    if parents is not None:
        datasets = [p for p in parents if p.OMERO_CLASS == 'Dataset']
        well_smpls = [p for p in parents if p.OMERO_CLASS == 'WellSample']
        if len(datasets) == 1:
            ds = datasets[0]
        if len(well_smpls) == 1:
            if well_smpls[0].well is not None:
                well = well_smpls[0].well

    rv = {
        'id': image.id,
        'meta': {
            'imageName': image.name or '',
            'imageDescription': image.description or '',
            'imageAuthor': image.getAuthor(),
            'projectName': pr and pr.name or 'Multiple',
            'projectId': pr and pr.id or None,
            'projectDescription': pr and pr.description or '',
            'datasetName': ds and ds.name or 'Multiple',
            'datasetId': ds and ds.id or None,
            'datasetDescription': ds and ds.description or '',
            'wellSampleId': wellsample and wellsample.id or '',
            'wellId': well and well.id.val or '',
            'imageTimestamp': time.mktime(
                image.getDate().timetuple()),
            'imageId': image.id,
            'pixelsType': image.getPixelsType(),
            },
        'perms': {
            'canAnnotate': image.canAnnotate(),
            'canEdit': image.canEdit(),
            'canDelete': image.canDelete(),
            'canLink': image.canLink()
            }
        }

    image._prepareRenderingEngine()

    def pixel_size_in_microns(method):
        try:
            size = method('MICROMETER')
            return size.getValue() if size else None
        except Exception:
            return None

    rv.update({
        'size': {'width': image.getSizeX(),
                 'height': image.getSizeY(),
                 'z': image.getSizeZ(),
                 't': image.getSizeT(),
                 'c': image.getSizeC()},
        'pixel_size': {'x': pixel_size_in_microns(image.getPixelSizeX),
                       'y': pixel_size_in_microns(image.getPixelSizeY),
                       'z': pixel_size_in_microns(image.getPixelSizeZ)},
        })

    try:
        rv['pixel_range'] = image.getPixelRange()
        rv['channels'] = map(lambda x: channelMarshal(x),
                             image.getChannels())
        rv['split_channel'] = image.splitChannelDims()
        rv['rdefs'] = {'model': (image.isGreyscaleRenderingModel() and
                                 'greyscale' or 'color'),
                       'projection': image.getProjection(),
                       'defaultZ': image._re.getDefaultZ(),
                       'defaultT': image._re.getDefaultT(),
                       'invertAxis': image.isInvertedAxis()}

    except AttributeError:
        rv = None
        raise
    return rv


def get_labels_json(panel_json, column, row):
    """Return dict of labels data for figure JSON."""
    labels = []

    channels = panel_json['channels']
    imagename = panel_json['name']
    if row == 0:
        labels.append({"text": channels[column]['label'],
                       "size": 8,
                       "position": "top",
                       "color": "000000"})
    if column == 0:
        labels.append({"text": imagename,
                       "size": 8,
                       "position": "leftvert",
                       "color": "000000"})
    return labels


def create_figure_file(conn, image_ids):
    """Create an OMERO.figure file with the specified images."""
    width = 100
    height = 100
    spacing_x = 5
    spacing_y = 5

    JSON_FILEANN_NS = "omero.web.figure.json"

    figure_json = {"version": 2,
                   "paper_width": 595,
                   "paper_height": 842,
                   "page_size": "A4",
                   "figureName": "Scipy Gaussian Filter",
                   }

    curr_x = 0
    curr_y = 0
    panels_json = []
    offset = 40

    gid = -1
    for row, image_id in enumerate(image_ids):
        image = conn.getObject('Image', image_id)
        curr_y = row * (height + spacing_y) + offset
        if row == 0:
            gid = image.getDetails().getGroup().getId()
        for col in range(image.getSizeC()):
            curr_x = col * (width + spacing_x) + offset
            j = get_panel_json(image, curr_x, curr_y, width, height, col)
            j['labels'] = get_labels_json(j, col, row)
            panels_json.append(j)

    figure_json['panels'] = panels_json

    figure_name = figure_json['figureName']
    if len(figure_json['panels']) == 0:
        raise Exception('No Panels')
    first_img_id = figure_json['panels'][0]['imageId']

    # we store json in description field...
    description = {}
    description['name'] = figure_name
    description['imageId'] = first_img_id

    # Try to set Group context to the same as first image
    conn.SERVICE_OPTS.setOmeroGroup(gid)

    json_string = json.dumps(figure_json)
    file_size = len(json_string)
    f = StringIO()
    json.dump(figure_json, f)

    update = conn.getUpdateService()
    orig_file = conn.createOriginalFileFromFileObj(f, '', figure_name,
                                                   file_size,
                                                   mimetype="application/json")
    fa = omero.model.FileAnnotationI()
    fa.setFile(omero.model.OriginalFileI(orig_file.getId(), False))
    fa.setNs(wrap(JSON_FILEANN_NS))
    desc = json.dumps(description)
    fa.setDescription(wrap(desc))
    fa = update.saveAndReturnObject(fa, conn.SERVICE_OPTS)
    return fa.getId().getValue()


if __name__ == "__main__":
    dataTypes = [rstring('Dataset'), rstring('Image')]
    client = scripts.client(
        'Scipy_Gaussian_Filter.py',
        """
    This script applies a gaussian filter to the selected images,
    uploads the generated images to OMERO and creates an OMERO.figure
        """,
        scripts.String(
            "Data_Type", optional=False, grouping="1",
            description="Choose source of images",
            values=dataTypes, default="Dataset"),

        scripts.List(
            "IDs", optional=False, grouping="2",
            description="Dataset IDs.").ofType(rlong(0)),

        scripts.Int(
            "Kernel_Window_Size", optional=False, grouping="3", default=20,
            description="Window size for the gaussian filter"),

        scripts.Int(
            "Sigma", optional=False, grouping="4", default=2,
            description="Sigma for the gaussian filter"),

        scripts.Bool(
            "Create_Omero_Figure", default=True, grouping="5",
            description="Create An OMERO.Figure from the resultant images"),

        authors=["Balaji Ramalingam", "OME Team"],
        institutions=["University of Dundee"],
        contact="ome-users@lists.openmicroscopy.org.uk",
    )

    try:
        # process the list of args above.
        scriptParams = {}
        for key in client.getInputKeys():
            if client.getInput(key):
                scriptParams[key] = client.getInput(key, unwrap=True)
        print(scriptParams)

        # wrap client to use the Blitz Gateway
        conn = BlitzGateway(client_obj=client)
        # # Call the main script - returns the number of images processed
        result = run(conn, scriptParams)
        if result is None:
            message = "No images found"
        else:
            image_ids, dataset = result

            message = "Created %s images" % len(image_ids)

            if scriptParams["Create_Omero_Figure"]:
                create_figure_file(conn, image_ids)
                message += " and new Figure"

            client.setOutput("Dataset", robject(dataset._obj))

        client.setOutput("Message", rstring(message))

    finally:
        client.closeSession()
