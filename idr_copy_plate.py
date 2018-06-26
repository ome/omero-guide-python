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

"""
This script connects to IDR and copies a Plate to another OMERO server.

It creates new images via getPlane() and createImageFromNumpySeq().
NB: New images are only a single T and Z.
Usage: $ python idr_copy_plate.py username password idr_plate_id
"""

import argparse
import omero
from omero.gateway import BlitzGateway
from omero.rtypes import rint, rstring
from omero.model import PlateI


def copy_image(conn, idr_image):
    """Create a copy of image. Single Z and T."""
    image_name = idr_image.getName()
    size_C = idr_image.getSizeC()
    clist = idr_image.getChannelLabels()
    zct_list = []
    for c in range(size_C):
        zct_list.append( (0, c, 0) )
    def planeGen():
        planes = idr_image.getPrimaryPixels().getPlanes(zct_list)
        for p in planes:
            yield p
    img = conn.createImageFromNumpySeq(planeGen(), image_name, sizeZ=1,
                                       sizeC=size_C, sizeT=1, channelList=clist)
    print "New image", img.id, img.name
    return img


def add_images_to_plate(update_service, plate, images, row, column):
    """Add the Images to a new Well in plate."""
    well = omero.model.WellI()
    well.plate = omero.model.PlateI(plate.id, False)
    well.column = rint(column)
    well.row = rint(row)
    well = update_service.saveAndReturnObject(well)

    for i in images:
        ws = omero.model.WellSampleI()
        ws.image = omero.model.ImageI(i.id, False)
        ws.well = well
        well.addWellSample(ws)
        update_service.saveObject(ws)


def run(username, password, plate_id, host, port):
    """Run the script."""
    # Create connection to training server
    conn = BlitzGateway(username, password, host=host, port=port)
    conn.connect()

    # Create connection to IDR server
    # NB: conn.connect() not working on IDR. Do it like this
    idr_client = omero.client(host="idr.openmicroscopy.org", port=4064)
    idr_client.createSession('public', 'public')
    idr_conn = BlitzGateway(client_obj=idr_client)

    # The plate we want to copy from IDR
    idr_plate = idr_conn.getObject("Plate", plate_id)
    plate_name = idr_plate.getName()

    update_service = conn.getUpdateService()
    plate = PlateI()
    plate.name = rstring(plate_name)
    plate = update_service.saveAndReturnObject(plate)

    for idr_well in idr_plate.listChildren():
        print "Well", idr_well.id, 'row', idr_well.row, 'col', idr_well.column
        # For each Well, get image and clone locally...
        new_imgs = []
        for idr_wellsample in idr_well.listChildren():
            idr_image = idr_wellsample.getImage()

            print "Image", idr_image.id
            image = copy_image(conn, idr_image)
            new_imgs.append(image)
        # link to Plate...
        add_images_to_plate(update_service, plate, new_imgs,
                            idr_well.row, idr_well.column)

    conn.close()
    idr_conn.close()


def main(args):
    """Entry point. Parse args and run."""
    parser = argparse.ArgumentParser()
    parser.add_argument('username')
    parser.add_argument('password')
    parser.add_argument('plate_id')
    parser.add_argument('--server', default="outreach.openmicroscopy.org",
                        help="OMERO server hostname")
    parser.add_argument('--port', default=4064, help="OMERO server port")
    args = parser.parse_args(args)
    run(args.username, args.password, args.plate_id, args.server, args.port)


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
