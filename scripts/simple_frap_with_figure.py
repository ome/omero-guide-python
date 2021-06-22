#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#   Copyright (C) 2017-2018 University of Dundee. All rights reserved.

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

# ------------------------------------------------------------------------------

"""
Simple FRAP plots from Ellipses on images and creates an OMERO.figure.

This an OMERO script that runs server-side.
"""

import omero
import json
from io import BytesIO

import omero.scripts as scripts
from omero.rtypes import rlong, rstring, unwrap
from omero.gateway import BlitzGateway

from PIL import Image
import numpy as np
try:
    import matplotlib
    # Run headless, so that pyplot doesn't try to import gtk
    matplotlib.use('Agg')
    from matplotlib import pyplot as plt
except (ImportError, RuntimeError):
    plt = None

JSON_FILEANN_NS = "omero.web.figure.json"


def channelMarshal(channel):
    """
    Return a dict with all there is to know about a channel.

    NB: This is copied from omeroweb.webgateway.marshal.py since we don't know
    that OMERO.web is installed on same environment as scripts

    @param channel:     L{omero.gateway.ChannelWrapper}
    @return:            Dict
    """
    chan = {'emissionWave': channel.getEmissionWave(),
            'label': channel.getLabel(),
            'color': channel.getColor().getHtml(),
            # 'reverseIntensity' is deprecated. Use 'inverted'
            'inverted': channel.isInverted(),
            'reverseIntensity': channel.isInverted(),
            'family': unwrap(channel.getFamily()),
            'coefficient': unwrap(channel.getCoefficient()),
            'window': {'min': channel.getWindowMin(),
                       'max': channel.getWindowMax(),
                       'start': channel.getWindowStart(),
                       'end': channel.getWindowEnd()},
            'active': channel.isActive()}
    lut = channel.getLut()
    if lut and len(lut) > 0:
        chan['lut'] = lut
    return chan


def get_timestamps(conn, image):
    """Return a list of times (secs) 1 for each T-index in image."""
    params = omero.sys.ParametersI()
    params.addLong('pid', image.getPixelsId())
    query = "from PlaneInfo as Info where"\
        " Info.theZ=0 and Info.theC=0 and pixels.id=:pid"
    info_list = conn.getQueryService().findAllByQuery(
        query, params, conn.SERVICE_OPTS)
    timemap = {}
    for info in info_list:
        t_index = info.theT.getValue()
        if info.deltaT is not None:
            delta_t = info.deltaT.getValue()
            timemap[t_index] = round(delta_t, 2)
    time_list = []
    for t in range(image.getSizeT()):
        if t in timemap:
            time_list.append(timemap[t])
    return time_list


def create_figure_file(conn, figure_json):
    """Create Figure FileAnnotation from json data."""
    figure_name = figure_json['figureName']
    if len(figure_json['panels']) == 0:
        raise Exception('No Panels')
    first_img_id = figure_json['panels'][0]['imageId']

    # we store json in description field...
    description = {}
    description['name'] = figure_name
    description['imageId'] = first_img_id

    # Try to set Group context to the same as first image
    conn.SERVICE_OPTS.setOmeroGroup('-1')
    i = conn.getObject("Image", first_img_id)
    gid = i.getDetails().getGroup().getId()
    conn.SERVICE_OPTS.setOmeroGroup(gid)

    json_bytes = json.dumps(figure_json).encode('utf-8')
    file_size = len(json_bytes)
    update = conn.getUpdateService()
    f = BytesIO()
    try:
        f.write(json_bytes)
        orig_file = conn.createOriginalFileFromFileObj(
            f, '', figure_name, file_size, mimetype="application/json")
    finally:
        f.close()
    fa = omero.model.FileAnnotationI()
    fa.setFile(omero.model.OriginalFileI(orig_file.getId(), False))
    fa.setNs(rstring(JSON_FILEANN_NS))
    desc = json.dumps(description)
    fa.setDescription(rstring(desc))
    fa = update.saveAndReturnObject(fa, conn.SERVICE_OPTS)
    return fa.getId().getValue()


def get_scalebar_json():
    """Return JSON to add a 10 micron scalebar to bottom-right."""
    return {"show": True,
            "length": 10,
            "position": "bottomright",
            "color": "FFFFFF",
            "show_label": True,
            "font_size": "10"}


def get_panel_json(image, x, y, width, height, theT):
    """Get json for a figure panel."""
    px = image.getPrimaryPixels().getPhysicalSizeX()
    py = image.getPrimaryPixels().getPhysicalSizeY()

    channels = [channelMarshal(x) for x in image.getChannels()]

    img_json = {
        "labels": [],
        "height": height,
        "channels": channels,
        "width": width,
        "sizeT": image.getSizeT(),
        "sizeZ": image.getSizeZ(),
        "dx": 0,
        "dy": 0,
        "rotation": 0,
        "imageId": image.id,
        "name": image.getName(),
        "orig_width": image.getSizeX(),
        "zoom": 100,
        "shapes": [],
        "orig_height": image.getSizeY(),
        "y": y,
        "x": x,
        "theT": theT,
        "theZ": 0
    }
    if px is not None:
        img_json["pixel_size_x"] = px.getValue()
        img_json["pixel_size_x_unit"] = str(px.getUnit())
        img_json["pixel_size_x_symbol"] = px.getSymbol()
    if py is not None:
        img_json["pixel_size_y"] = py.getValue()
    if image.getSizeT() > 1:
        img_json['deltaT'] = get_timestamps(conn, image)
    return img_json


def create_omero_figure(conn, images, plots):
    """Create OMERO.figure from given FRAP images and plot images."""
    figure_json = {"version": 2,
                   "paper_width": 595,
                   "paper_height": 842,
                   "page_size": "A4",
                   "figureName": "FRAP figure from script",
                   }
    time_frames = [2, 3, 4, 5, 10]

    panel_width = 80
    panel_height = panel_width
    spacing = panel_width/20
    margin = 40

    panels_json = []

    for i, image in enumerate(images):

        panel_x = margin
        panel_y = (i * (panel_height + spacing)) + margin
        for col in range(len(time_frames)):
            the_t = time_frames[col]
            panel_x = (col * (panel_height + spacing)) + margin
            j = get_panel_json(image, panel_x, panel_y,
                               panel_width, panel_height, the_t)
            # Add timestamp in 'secs' to top-left of each movie frame
            j['labels'] = [{"time": "secs",
                            "size": "12",
                            "position": "topleft",
                            "color": "FFFFFF"}]
            panels_json.append(j)
        # Add scalebar to last panel
        panels_json[-1]['scalebar'] = get_scalebar_json()
        # Add plot
        if i < len(plots):
            plot = plots[i]
            panel_x = (len(time_frames) * (panel_height + spacing)) + margin
            plot_width = (panel_height *
                          (float(plot.getSizeX()) / plot.getSizeY()))
            j = get_panel_json(plot, panel_x, panel_y,
                               plot_width, panel_height, 0)
            panels_json.append(j)

    figure_json['panels'] = panels_json
    return create_figure_file(conn, figure_json)


def run(conn, params):
    """
    For each image, getTiles() for FRAP Ellipse and plot mean intensity.

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
        print("---- Processing image", image.id)
        result = roi_service.findByImage(image.getId(), None)

        # Simply use any Ellipse we find...
        shape_id = None
        for roi in result.rois:
            print("ROI:  ID:", roi.getId().getValue())
            for s in roi.copyShapes():
                if type(s) == omero.model.EllipseI:
                    shape_id = s.id.val
        print("Shape:", shape_id)
        if shape_id is None:
            print("  No Ellipse found for this image")
            continue

        # Get pixel intensities for first Channel
        the_c = 0
        the_z = 0
        size_t = image.getSizeT()
        meanvalues = []
        for t in range(size_t):
            stats = roi_service.getShapeStatsRestricted([shape_id],
                                                        the_z, t, [the_c])
            meanvalues.append(stats[0].mean[the_c])

        print(meanvalues)

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
            fig.savefig('plot.png')
            pil_img = Image.open('plot.png')
            np_array = np.asarray(pil_img)
            red = np_array[::, ::, 0]
            green = np_array[::, ::, 1]
            blue = np_array[::, ::, 2]
            plane_gen = iter([red, green, blue])
            plot_name = image.getName() + "_FRAP_plot"
            i = conn.createImageFromNumpySeq(plane_gen, plot_name, sizeC=3,
                                             dataset=image.getParent())
            frap_plots.append(i)

    return create_omero_figure(conn, images, frap_plots)


if __name__ == "__main__":
    dataTypes = [rstring('Dataset'), rstring('Image')]
    client = scripts.client(
        'Simple_FRAP_with_figure.py',
        """
    This script does simple FRAP analysis using Ellipse ROIs previously
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
        print(scriptParams)

        # wrap client to use the Blitz Gateway
        conn = BlitzGateway(client_obj=client)
        # Call the main script - returns the new OMERO.figure ann ID
        figure_id = run(conn, scriptParams)
        if figure_id is None:
            message = "No images found"
        else:
            message = "Created FRAP figure: %s" % figure_id

        client.setOutput("Message", rstring(message))

    finally:
        client.closeSession()
