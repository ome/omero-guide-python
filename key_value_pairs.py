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
This script adds Key-Value Pairs to images in a Dataset with the specified name
for 50 users (user-1 through user-50). The Key-Value Pairs are defined in the
variables kvp_setx and are added to the images inside the dataset according to
the features in the images in the list images_kvp_order.
The script could be simplified by adding the Key-Value Pairs randomly to the
images in the Dataset.
"""

import argparse
import omero
from omero.gateway import BlitzGateway


def run(password, target, host, port):

    for i in range(1, 51):

        username = "user-%s" % i
        print username
        conn = BlitzGateway(username, password, host=host, port=port)
        try:
            conn.connect()
            params = omero.sys.ParametersI()
            params.addString('username', username)
            query = "from Dataset where name='%s' \
                    AND details.owner.omeName=:username" % target
            query_service = conn.getQueryService()
            dataset = query_service.findAllByQuery(query, params,
                                                   conn.SERVICE_OPTS)

            if len(dataset) == 0:
                print "No dataset with name %s found" % target
                continue
            dataset_id = dataset[0].getId().getValue()

            print 'dataset', dataset_id
            dataset = conn.getObject("Dataset", dataset_id)

            kvp_set1 = [["mitomycin-A", "0mM"], ["PBS", "10mM"],
                        ["incubation", "10min"], ["temperature", "37"],
                        ["Organism", "Homo sapiens"]]
            kvp_set2 = [["mitomycin-A", "20mM"], ["PBS", "10mM"],
                        ["incubation", "10min"], ["temperature", "37"],
                        ["Organism", "Homo sapiens"]]
            kvp_set3 = [["mitomycin-A", "10microM"], ["PBS", "10mM"],
                        ["incubation", "5min"], ["temperature", "37"],
                        ["Organism", "Homo sapiens"]]
            kvp_set4 = [["mitomycin-A", "0mM"], ["PBS", "10mM"],
                        ["incubation", "5min"], ["temperature", "68"],
                        ["Organism", "Homo sapiens"]]

            images_kvp_order = [('A10.pattern1.tif', kvp_set1),
                                ('A10.pattern2.tif', kvp_set2),
                                ('A10.pattern5.tif', kvp_set2),
                                ('A1.pattern1.tif', kvp_set4),
                                ('A1.pattern2.tif', kvp_set1),
                                ('A5.pattern1.tif', kvp_set3),
                                ('A5.pattern2.tif', kvp_set2),
                                ('A5.pattern3.tif', kvp_set2),
                                ('A5.pattern4.tif', kvp_set2),
                                ('A6.pattern1.tif', kvp_set3),
                                ('A6.pattern2.tif', kvp_set2),
                                ('A6.pattern3.tif', kvp_set2),
                                ('B12.pattern1.tif', kvp_set1),
                                ('B12.pattern2.tif', kvp_set1),
                                ('B12.pattern3.tif', kvp_set1),
                                ('B12.pattern4.tif', kvp_set3),
                                ('B12.pattern5.tif', kvp_set3),
                                ('C4.pattern1.tif', kvp_set2),
                                ('C4.pattern2.tif', kvp_set2),
                                ('C4.pattern3.tif', kvp_set2),
                                ('C4.pattern4.tif', kvp_set2),
                                ('C4.pattern5.tif', kvp_set2),
                                ('C4.pattern6.tif', kvp_set2),
                                ('C4.pattern7.tif', kvp_set3),
                                ('C4.pattern8.tif', kvp_set3),
                                ('C4.pattern9.tif', kvp_set1),
                                ('C4.pattern.tif', kvp_set1),
                                ('E4.pattern5.tif', kvp_set3),
                                ('E4.pattern6.tif', kvp_set1),
                                ('E4.pattern7.tif', kvp_set3),
                                ('E4.pattern8.tif', kvp_set3),
                                ('E4.pattern9.tif', kvp_set1)]

            images_kvp_order = dict(images_kvp_order)
            for image in dataset.listChildren():

                if image.getName() in images_kvp_order:
                    print images_kvp_order[image.getName()]

                    key_value_data = images_kvp_order[image.getName()]
                    map_ann = omero.gateway.MapAnnotationWrapper(conn)
                    # Use 'client' namespace to allow editing in Insight & web
                    namespace = omero.constants.metadata.NSCLIENTMAPANNOTATION
                    map_ann.setNs(namespace)
                    map_ann.setValue(key_value_data)
                    map_ann.save()
                    # NB: only link a client map annotation to a single object
                    image.linkAnnotation(map_ann)
                    print 'linking to image', image.getName()
        except Exception as exc:
            print "Error while setting key-value pairs: %s" % str(exc)
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
