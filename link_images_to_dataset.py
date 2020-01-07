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
This script creates a new dataset and links all images with a given name
to it for users user-1 through user-50.
"""

import argparse
import omero
from omero.gateway import BlitzGateway


def run(password, dataset_name, target, host, port):

    for i in range(1, 51):
        username = "user-%s" % i
        print(username)
        conn = BlitzGateway(username, password, host=host, port=port)
        try:
            conn.connect()

            params = omero.sys.ParametersI()
            params.addString('username', username)
            query = "from Image where name='%s' \
                    AND details.owner.omeName=:username" % target
            query_service = conn.getQueryService()
            images = query_service.findAllByQuery(query, params,
                                                  conn.SERVICE_OPTS)

            if len(images) == 0:
                print("No images with name %s found" % target)
                continue
            image_id = images[0].getId().getValue()

            print('id', image_id)

            dataset = omero.model.DatasetI()
            dataset.setName(omero.rtypes.rstring(dataset_name))
            dataset = conn.getUpdateService().saveAndReturnObject(dataset)
            dataset_id = dataset.getId().getValue()
            print(username, dataset_id)

            link = omero.model.DatasetImageLinkI()
            link.setParent(dataset)
            link.setChild(omero.model.ImageI(image_id, False))
            conn.getUpdateService().saveObject(link)
        except Exception as exc:
            print("Error while linking images: %s" % str(exc))
        finally:
            conn.close()


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('password')
    parser.add_argument('dataset')
    parser.add_argument('target')
    parser.add_argument('--server', default="workshop.openmicroscopy.org",
                        help="OMERO server hostname")
    parser.add_argument('--port', default=4064, help="OMERO server port")
    args = parser.parse_args(args)
    run(args.password, args.dataset, args.target, args.server, args.port)


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
