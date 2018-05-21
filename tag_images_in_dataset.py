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
This script tags a set of images contained in the specified dataset.
The dataset and the tag are specified as a parameter.
"""

import argparse
import omero
from omero.gateway import BlitzGateway
from omero.model import ImageAnnotationLinkI
from omero.model import ImageI
from omero.model import TagAnnotationI

images_to_tag = ["A1.pattern1.tif",
                 "B12.pattern1.tif",
                 "B12.pattern2.tif",
                 "B12.pattern3.tif",
                 "C4.pattern9.tif",
                 "C4.pattern.tif"]


def run(password, admin_name, target, tag, host, port):

    for i in range(1, 41):

        username = "user-%s" % i
        print username
        conn = BlitzGateway(username, password, host=host, port=port)
        try:
            conn.connect()
            updateService = conn.getUpdateService()
            ds = conn.getObject("Dataset", attributes={'name': target},
                                opts={'owner': conn.getUserId()})
            if ds is None:
                print "No dataset with name %s found" % target
                continue
            params = omero.sys.ParametersI()
            params.addString('username', admin_name)
            query = "from TagAnnotation where textvalue='%s' \
                    AND details.owner.omeName=:username" % tag
            query_service = conn.getQueryService()
            tags = query_service.findAllByQuery(query, params,
                                                conn.SERVICE_OPTS)
            if len(tags) == 0:
                print "No tag with name %s found" % tag
                continue
            tag_id = tags[0].id.getValue()
            print tag_id
            links = []
            for image in ds.listChildren():
                name = image.getName()
                if name in images_to_tag:
                    # Check first that the image is not tagged
                    params = omero.sys.ParametersI()
                    params.addLong('parent', image.id)
                    params.addLong('child', tag_id)
                    query = "select link from ImageAnnotationLink as link \
                             where link.parent.id=:parent \
                             AND link.child.id=:child"
                    values = query_service.findAllByQuery(query, params,
                                                          conn.SERVICE_OPTS)
                    if len(values) == 0:
                        link = ImageAnnotationLinkI()
                        link.parent = ImageI(image.id, False)
                        link.child = TagAnnotationI(tag_id, False)
                        links.append(link)
                    else:
                        print "Tag %s already linked to %s" % (tag, name)
            if len(links) > 0:
                updateService.saveArray(links)
        except Exception as exc:
            print "Error when tagging the images: %s" % str(exc)
        finally:
            conn.close()


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('password')
    parser.add_argument('target')
    parser.add_argument('tag')
    parser.add_argument('--name', default="trainer-1",
                        help="The owner of the tag")
    parser.add_argument('--server', default="outreach.openmicroscopy.org",
                        help="OMERO server hostname")
    parser.add_argument('--port', default=4064, help="OMERO server port")
    args = parser.parse_args(args)
    run(args.password, args.name, args.target, args.tag, args.server,
        args.port)


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
