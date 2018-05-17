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

# Delete Annotations of a particular namespace from all Images in a Dataset

from omero.gateway import BlitzGateway

USERNAME = "username"
PASSWORD = "password"
conn = BlitzGateway(USERNAME, PASSWORD, host="outreach.openmicroscopy.org", port=4064)
conn.connect()

# Edit these values
dataset_id = 4501
ns = "omero.batch_roi_export.map_ann"

dataset = conn.getObject("Dataset", dataset_id)

for image in dataset.listChildren():
    ann_ids = [a.id for a in image.listAnnotations(ns)]
    if len(ann_ids) > 0:
        print "Deleting %s anns..." % len(ann_ids)
        conn.deleteObjects('Annotation', ann_ids)