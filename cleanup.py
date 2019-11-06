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
This script first finds and lists, then cleans up objects
(ROIs, Ratings and Tags) attached to all images contained in a Dataset with a
specified name belonging to users user-1 through user-50
and to the specified administrator.
The listing is done by each user on their own data.
The information is collected and the final cleanup is done by an
administrator e.g. "trainer-1", who makes sure that also objects linked to
images by other users will get unlinked or deleted.
The cleanup of ROIs and Ratings means deletion of these.
The cleanup of Tags just deletes the link between the Tag and the image,
thus removing the Tag, but not deleting it.
"""

import argparse
import omero
from omero.gateway import BlitzGateway
from omero.rtypes import wrap

obj_ids_taglinks = []
obj_ids_rating = []
obj_ids_rois = []


def cut_link(conn, username, image):
    if image is None:
        print("No image to handle")
        return
    params = omero.sys.ParametersI()
    params.addString('username', username)
    query = "from Image where name='%s' \
            AND details.owner.omeName=:username" % image
    query_service = conn.getQueryService()
    images = query_service.findAllByQuery(query, params,
                                          conn.SERVICE_OPTS)
    if len(images) == 0:
        print("No image with name %s found" % image)
        return
    params = omero.sys.ParametersI()
    params.addLong('imageId', images[0].getId().getValue())
    query = "from DatasetImageLink where child.id=:imageId"
    links = conn.getQueryService().findAllByQuery(query, params,
                                                  conn.SERVICE_OPTS)
    if len(links) > 0:
        ids = []
        for link in links:
            ids.append(link.getId().getValue())
        conn.deleteObjects("DatasetImageLink", ids, deleteAnns=True,
                           deleteChildren=False, wait=True)


def list_objs(conn, username, target):
    if target is None:
        print("No dataset to handle")
        return
    params = omero.sys.ParametersI()
    params.addString('username', username)
    query = "from Dataset where name='%s' \
             AND details.owner.omeName=:username" % target
    query_service = conn.getQueryService()
    datasets = query_service.findAllByQuery(query, params,
                                            conn.SERVICE_OPTS)
    if len(datasets) == 0:
        print("No dataset with name %s found" % target)
        return

    dataset_id = datasets[0].getId().getValue()
    dataset = conn.getObject("Dataset", dataset_id)
    roi_service = conn.getRoiService()
    for image in dataset.listChildren():
        print(image.getId())
        result = roi_service.findByImage(image.getId(), None,
                                         conn.SERVICE_OPTS)
        if result is not None:
            for roi in result.rois:
                roi_id = roi.getId().getValue()
                obj_ids_rois.append(roi_id)

            if not len(result.rois) == 0:
                print('Will delete %s ROIs on image %s of \
                       %s' % (len(result.rois), image.getId(), username))

        for ann in image.listAnnotations():
            if ann.OMERO_TYPE == omero.model.LongAnnotationI:
                obj_ids_rating.append(ann.getId())
                print('Will delete rating %s on image \
                       %s of %s' % (ann.getId(), image.getId(), username))
            elif ann.OMERO_TYPE == omero.model.TagAnnotationI:
                params = omero.sys.ParametersI()
                params.add('imageId', wrap(image.getId()))
                params.addId(ann.getId())
                query = "select l.id from ImageAnnotationLink as \
                        l where l.parent.id=:imageId AND l.child.id=:id"
                linkIds = query_service.projection(query, params,
                                                   conn.SERVICE_OPTS)
                for linkId in linkIds:
                    obj_ids_taglinks.append(linkId[0].getValue())
                    print('Will delete link %s on image \
                           %s of tag %s of %s' % (linkId[0].getValue(),
                                                  image.getId(),
                                                  ann.getId(), username))


def delete_objs(conn):
    if len(obj_ids_taglinks) > 0:
        print('deleting', len(obj_ids_taglinks), ' tag links')
        conn.deleteObjects("ImageAnnotationLink", obj_ids_taglinks,
                           deleteAnns=True, deleteChildren=False, wait=True)
    else:
        print('No tag links to delete')
    if len(obj_ids_rois) > 0:
        print('deleting %s ROIs' % len(obj_ids_rois))
        handle = conn.deleteObjects("Roi", obj_ids_rois, deleteAnns=True,
                                    deleteChildren=True)
        conn.c.waitOnCmd(handle, loops=500, ms=500, closehandle=True)
    else:
        print('No ROIs to delete')
    if len(obj_ids_rating) > 0:
        print('deleting %s ratings' % len(obj_ids_rating))
        conn.deleteObjects("LongAnnotation", obj_ids_rating, deleteAnns=True,
                           deleteChildren=False, wait=True)
    else:
        print('No ratings to delete')


def run(password, admin_name, target, image, host, port):

    try:
        conn = BlitzGateway(admin_name, password, host=host, port=port)
        conn.connect()
        conn.SERVICE_OPTS.setOmeroGroup("-1")
        list_objs(conn, admin_name, target)
        cut_link(conn, admin_name, image)
        for i in range(1, 51):
            username = "user-%s" % i
            print(username)
            list_objs(conn, username, target)
            cut_link(conn, username, image)

        delete_objs(conn)
    except Exception as exc:
        print("Error while cleaning the objects: %s" % str(exc))
    finally:
        conn.close()


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('password',
                        help="The password of the person cleaning up")
    parser.add_argument('--name', default="trainer-1",
                        help="The username of the person cleaning up")
    parser.add_argument('--dataset', default=None,
                        help="Remove ROIs, Rating, Annotations \
                        from the images contained in the dataset")
    parser.add_argument('--image', default=None,
                        help="Delete the links between the image \
                        and the dataset(s) containing it.")
    parser.add_argument('--server', default="outreach.openmicroscopy.org",
                        help="OMERO server hostname")
    parser.add_argument('--port', default=4064, help="OMERO server port")
    args = parser.parse_args(args)
    run(args.password, args.name, args.dataset, args.image, args.server,
        args.port)


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
