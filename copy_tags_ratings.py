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
This script is used to duplicate Tagging & Rating of Images from a Dataset
belonging to 'trainer-1', to corresponding Images in Datasets belonging
to user-1 -> user-x.
Trainer-1's tags will be linked to user-x's Images by Name, to match the
Images they are linked to in trainer-1's Dataset. Links owned by user-x.
New Ratings created, belonging to user-x.
"""

import argparse
import omero
from omero.gateway import BlitzGateway
from omero import ValidationException
from omero.rtypes import wrap, rstring, rlong
from omero.model import ExperimenterI, ImageAnnotationLinkI, ImageI, \
    TagAnnotationI, LongAnnotationI

RATING_NS = "openmicroscopy.org/omero/insight/rating"

def link_tags(conn, datasetname, image_tag_links, image_ratings):

    for i in range(1, 51):
        username = "user-%s" % i
        print username
        exp = conn.getAdminService().lookupExperimenter(username)
        exp_id = exp.id.val
        
        dataset = conn.getObject("Dataset",
                attributes={'name': datasetname},
                opts={'owner': exp_id})
        if dataset is None:
            print "Dataset not found"
            continue
        links = []
        for image in dataset.listChildren():
            name = image.name
            if name in image_tag_links:
                for tag_id in image_tag_links[name]:
                    link = ImageAnnotationLinkI()
                    link.parent = ImageI(image.id, False)
                    link.child = TagAnnotationI(tag_id, False)
                    link.details.owner = ExperimenterI(exp_id, False)
                    links.append(link)
            if name in image_ratings:
                link = ImageAnnotationLinkI()
                link.parent = ImageI(image.id, False)
                r = LongAnnotationI()
                r.ns = rstring(RATING_NS)
                r.longValue = rlong(image_ratings[name])
                link.child = r
                link.details.owner = ExperimenterI(exp_id, False)
                links.append(link)

        print 'links', len(links)
        group_id = dataset.getDetails().getGroup().id
        conn.SERVICE_OPTS.setOmeroGroup(group_id)
        try:
            conn.getUpdateService().saveArray(links, conn.SERVICE_OPTS)
        except ValidationException:
            print "Failed to link for %s" % username


def run(datasetname, password, host, port):

    conn = BlitzGateway('trainer-1', password, host=host, port=port)
    conn.connect()

    try:
        trainer_dataset = conn.getObject("Dataset",
                attributes={'name': datasetname},
                opts={'owner': conn.getUserId()})

        # Create {name: [tag_id, tag_id]} for images in Dataset
        image_tag_links = {}
        image_ratings = {}
        for image in trainer_dataset.listChildren():
            tag_ids = []
            for ann in image.listAnnotations():
                if ann.OMERO_TYPE.__name__ == 'TagAnnotationI':
                    tag_ids.append(ann.id)
                elif ann.ns == RATING_NS:
                    image_ratings[image.getName()] = ann.longValue
            if len(tag_ids) > 0:
                image_tag_links[image.getName()] = tag_ids

        # print image_tag_links
        print 'image_ratings', image_ratings
        link_tags(conn, datasetname, image_tag_links, image_ratings)
    
    finally:
        conn.close()


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('datasetname', default=None)
    parser.add_argument('password', default=None)
    parser.add_argument('--server', default="outreach.openmicroscopy.org",
                        help="OMERO server hostname")
    parser.add_argument('--port', default=4064, help="OMERO server port")
    args = parser.parse_args(args)
    run(args.datasetname, args.password, args.server, args.port)


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
