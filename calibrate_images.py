#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# -----------------------------------------------------------------------------
#   Copyright (C) 2017 University of Dundee. All rights reserved.
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License along
#   with this program; if not, write to the Free Software Foundation, Inc.,
#   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# ------------------------------------------------------------------------------

"""
This script changes the calibration on all images contained in a Dataset
with a specified name belonging to users user-1 through
user-40.
Each calibration change is made by the owner of the Dataset and the images
themselves.
"""

import argparse
import omero
from omero.gateway import BlitzGateway
from omero.model.enums import UnitsLength


def run(password, target, host, port):

    for i in range(1, 41):

        username = "user-%s" % i
        print username
        conn = BlitzGateway(username, password, host=host, port=port)
        try:
            conn.connect()

            params = omero.sys.ParametersI()
            params.addString('username', username)
            query = "from Dataset where name='%s' \
                     AND details.owner.omeName=:username" % target
            service = conn.getQueryService()
            dataset = service.findAllByQuery(query, params, conn.SERVICE_OPTS)

            if len(dataset) == 0:
                print "No dataset with name %s found" % target
                continue

            dataset_obj = dataset[0]
            datasetId = dataset[0].getId().getValue()

            print 'dataset', datasetId
            params2 = omero.sys.ParametersI()
            params2.addId(dataset_obj.getId())
            query = "select l.child.id from DatasetImageLink \
                     l where l.parent.id = :id"
            images = service.projection(query, params2, conn.SERVICE_OPTS)
            values = []
            for k in range(0, len(images)):

                image_id = images[k][0].getValue()
                image = conn.getObject("Image", image_id)

                u = omero.model.LengthI(0.33, UnitsLength.MICROMETER)
                p = image.getPrimaryPixels()._obj
                p.setPhysicalSizeX(u)
                p.setPhysicalSizeY(u)
                values.append(p)

            if len(images) > 0:
                conn.getUpdateService().saveArray(values)
        except Exception as exc:
            print "Error during calibration: %s" % str(exc)
        finally:
            conn.close()


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('password')
    parser.add_argument('target')
    parser.add_argument('--server', default="outreach.openmicroscopy.org",
                        help="OMERO server hostname")
    parser.add_argument('--port', default=4064, help="OMERO server port")
    args = parser.parse_args(args)
    run(args.password, args.target, args.server, args.port)


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
