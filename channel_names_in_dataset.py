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
This script changes the channel names on all images contained in a Dataset
with a specified name belonging to users user-1 through user-40.
Each calibration change is made by the owner of the Dataset and the images
themselves.
"""

import argparse
from omero.gateway import BlitzGateway


def run(password, target, host, port):

    for user_number in range(1, 41):
        username = "user-%s" % user_number
        print username
        conn = BlitzGateway(username, password, host=host, port=port)
        try:
            conn.connect()

            ds = conn.getObject("Dataset", attributes={'name': target},
                                opts={'owner': conn.getUserId()})
            if ds is None:
                print "No dataset with name %s found" % target
                continue

            print "Dataset", ds.getId()

            conn.setChannelNames("Dataset", [ds.getId()],
                                 {1: "H2B", 2: "nuclear lamina"})
        except Exception as exc:
            print "Error while changing the channel names: %s" % str(exc)
        finally:
            # Close connection for each user when done
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
