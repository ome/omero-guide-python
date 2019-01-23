#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# -----------------------------------------------------------------------------
#   Copyright (C) 2018 University of Dundee. All rights reserved.
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
This script sets the FirstName and LastName for user-1 to user-50
"""

import argparse
import omero
from omero.rtypes import rstring
from omero.gateway import BlitzGateway


def run(username, password, host, port):

    full_names = ["Francis Crick",
              "Linda Buck",
              "Charles Darwin",
              "Marie Curie",
              "Alexander Fleming",
              "Rosalind Franklin",
              "Robert Hooke",
              "Jane Goodall",
              "Gregor Mendel",
              "Barbara McClintock",
              "Louis Pasteur",
              "Ada Lovelace",
              "Linus Pauling",
              "Frances Kelsey",
              "Maurice Wilkins",
              "Florence Nightingale",
              "John Sulston",
              "Elizabeth Blackwell",
              "Richard Dawkins",
              "Caroline Dean",
              "Stephen Reicher",
              "Wendy Barclay",
              "Paul Nurse",
              "Jennifer Doudna",
              "Adrian Thomas",
              "Ann Clarke",
              "Oswald Avery",
              "Liz Sockett",
              "Erwin Chargaff",
              "Tracey Rogers",
              "Ronald Fisher",
              "Rachel Carson",
              "William Harvey",
              "Nettie Stevens",
              "Jeffrey Hall",
              "Youyou Tu",
              "Michael Rosbash",
              "Carol Greider",
              "Yoshinori Ohsumi",
              "Rosalyn Yalow",
              "Amedeo Avogadro",
              "Virginia Apgar",
              "Kristian Birkeland",
              "Mary Anning",
              "Chen-Ning Yang",
              "Stephanie Kwolek",
              "Jagadish Bose",
              "Rita Levi-Montalcini",
              "Susumu Tonegawa",
              "Irene Joliot-Curie"]

    conn = BlitzGateway(username, password, host=host, port=port)
    try:
        conn.connect()
        admin_service = conn.getAdminService()
        for i, full_name in enumerate(full_names):
            username = 'user-%s' % (i + 1)
            print username, full_name
            exp = admin_service.lookupExperimenter(username)
            names = full_name.split(" ")
            exp.firstName = rstring(names[0])
            exp.lastName = rstring(names[1])
            admin_service.updateExperimenter(exp)

    except Exception as exc:
            print "Error while renaming users: %s" % str(exc)
    finally:
        conn.close()


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('username')
    parser.add_argument('password')
    parser.add_argument('--server', default="outreach.openmicroscopy.org",
                        help="OMERO server hostname")
    parser.add_argument('--port', default=4064, help="OMERO server port")
    args = parser.parse_args(args)
    run(args.username, args.password, args.server, args.port)


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
