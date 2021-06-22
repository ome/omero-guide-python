# -----------------------------------------------------------------------------
#   Copyright (C) 2020 University of Dundee. All rights reserved.

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


# Imports
from omero.gateway import BlitzGateway, MapAnnotationWrapper
from omero.model import EllipseI
from PIL import Image
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from getpass import getpass


# Step 1 - Connect/Disconnect
def connect(hostname, username, password):
    """
    Connect to an OMERO server
    :param hostname: Host name
    :param username: User
    :param password: Password
    :return: Connected BlitzGateway
    """
    conn = BlitzGateway(username, password,
                        host=hostname, secure=True)
    conn.connect()
    conn.c.enableKeepAlive(60)
    return conn


def disconnect(conn):
    """
    Disconnect from an OMERO server
    :param conn: The BlitzGateway
    """
    conn.close()


# Step 3 - Load metadata (channel information)
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


# Step 4 - Load metadata (ellipse ROI)
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


# Step 5 - Get the mean intensities
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
        meanvalues.append(stats[0].mean[0])
    return meanvalues


# Step 6 - Plot the data
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
    pil_img = Image.open(plot_filename)
    pil_img.show()


# Step 7 - Save the results
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


# Step 8 - Save the plot
def save_plot(conn, image, plot_filename):
    """
    Save the plot to OMERO
    :param conn: The BlitzGateway
    :param image: The image
    :param plot_filename: The path to the plot image
    :return: Nothing
    """
    pil_img = Image.open(plot_filename)
    np_array = np.asarray(pil_img)
    red = np_array[::, ::, 0]
    green = np_array[::, ::, 1]
    blue = np_array[::, ::, 2]
    plane_gen = iter([red, green, blue])
    conn.createImageFromNumpySeq(plane_gen, plot_filename, sizeC=3,
                                 dataset=image.getParent())


# Step 9 - Wrap it all up
def analyse(conn, image_id, channel_name):
    # Step 2 - Load iamge
    img = conn.getObject("Image", image_id)
    # -
    ci = get_channel_index(img, channel_name)
    shape_id = get_ellipse_roi(conn, img)
    values = get_mean_intensities(conn, img, ci, shape_id)
    plot(values, 'plot.png')
    save_values(conn, img, values)
    save_plot(conn, img, 'plot.png')


def main():
    try:
        hostname = input("Host [wss://workshop.openmicroscopy.org/omero-ws]: \
                         ") or "wss://workshop.openmicroscopy.org/omero-ws"
        username = input("Username [trainer-1]: ") or "trainer-1"
        password = getpass("Password: ")
        image_id = int(input("Image ID [28662]: ") or 28662)
        channel = input("Channel name [528.0]: ") or "528.0"
        conn = connect(hostname, username, password)
        analyse(conn, image_id, channel)
    finally:
        if conn:
            disconnect(conn)


if __name__ == "__main__":
    main()
