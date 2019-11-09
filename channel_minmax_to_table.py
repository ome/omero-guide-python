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

# Script uses Channel min/max intensity to generate OMERO.table on Plate

import argparse
import omero
from omero.rtypes import rstring
import omero.grid
from omero.gateway import BlitzGateway


NAMESPACE = "openmicroscopy.org/omero/bulk_annotations"


def run(username, password, plate_id, host, port):

    conn = BlitzGateway(username, password, host=host, port=port)
    try:
        conn.connect()
        query_service = conn.getQueryService()

        # Create a name for the Original File
        tablename = "Channels_Min_Max_Intensity"

        # Go through all wells in Plate, adding row for each
        plate = conn.getObject("Plate", plate_id)
        wellIds = []
        rowData = []
        chCount = 0
        for well in plate._listChildren():
            well = omero.gateway.WellWrapper(conn, well)
            image = well.getImage()
            if image is None:
                continue
            wellIds.append(well.id)
            chCount = image.getSizeC()
            row = []
            print("well, image", well.id, image.id)

            params = omero.sys.ParametersI()
            params.addId(image.getPixelsId())
            query = """select pixels from Pixels as pixels
                       left outer join fetch pixels.channels as channels
                       join fetch channels.statsInfo where pixels.id=:id"""
            result = query_service.findAllByQuery(query, params)

            row = []
            for pix in result:
                for ch in pix.iterateChannels():
                    si = ch.statsInfo
                    row.extend([si.globalMin.val, si.globalMax.val])
            rowData.append(row)

        print('wellIds', wellIds)
        print('rowData', rowData)

        # Now we know how many channels, we can make the table
        col1 = omero.grid.WellColumn('Well', '', [])
        columns = [col1]
        colNames = []
        for chIdx in range(chCount):
            for name in ['Ch%sMin' % chIdx, 'Ch%sMax' % chIdx]:
                colNames.append(name)
                columns.append(omero.grid.LongColumn(name, '', []))

        table = conn.c.sf.sharedResources().newTable(1, tablename)
        table.initialize(columns)

        # Add Data from above
        data1 = omero.grid.WellColumn('Well', '', wellIds)
        data = [data1]
        for colIdx in range(len(rowData[0])):
            colData = [r[colIdx] for r in rowData]
            print("colData", len(colData))
            name = colNames[colIdx]
            data.append(omero.grid.LongColumn(name, '', colData))

        print("Adding data: ", len(data))
        table.addData(data)
        table.close()

        print("table closed...")
        orig_file = table.getOriginalFile()
        fileAnn = omero.model.FileAnnotationI()
        fileAnn.ns = rstring(NAMESPACE)
        fileAnn.setFile(omero.model.OriginalFileI(orig_file.id.val, False))
        fileAnn = conn.getUpdateService().saveAndReturnObject(fileAnn)
        link = omero.model.PlateAnnotationLinkI()
        link.setParent(omero.model.PlateI(plate_id, False))
        link.setChild(omero.model.FileAnnotationI(fileAnn.id.val, False))

        print("save link...")
        conn.getUpdateService().saveAndReturnObject(link)

    except Exception as exc:
        print("Error while changing names: %s" % str(exc))
    finally:
        conn.close()


def main(args):
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
