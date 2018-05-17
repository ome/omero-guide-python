# -----------------------------------------------------------------------------
#  Copyright (C) 2018 University of Dundee. All rights reserved.
#
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
#  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# ------------------------------------------------------------------------------

# Script uses map annotations on each Image to rename channels

from omero.gateway import BlitzGateway

USERNAME = "username"
PASSWORD = "password"
conn = BlitzGateway(USERNAME, PASSWORD, host="outreach.openmicroscopy.org", port=4064)
conn.connect()

NAMESPACE = "openmicroscopy.org/omero/bulk_annotations"
MAP_KEY = "Channels"

# TO BE MODIFIED
project_id = 4501

project = conn.getObject("Project", project_id)

for dataset in project.listChildren():
    print "\n\nDataset", dataset.id, dataset.name
    for image in dataset.listChildren():

        print "Image", image.id, image.name
        ann = image.getAnnotation(NAMESPACE)
        if ann is None:
            print " No annotation found"
            continue
        key_values = ann.getValue()
        channels_value = [kv[1] for kv in key_values if kv[0] == MAP_KEY]
        if len(channels_value) == 0:
            print " No Key-Value found for key:", MAP_KEY
        channels = channels_value[0].split("; ")
        print "Channels", channels
        name_dict = {}
        for c, ch_name in enumerate(channels):
            name_dict[c + 1] = ch_name.split(":")[1]
        conn.setChannelNames("Image", [image.id], name_dict, channelCount=None)

