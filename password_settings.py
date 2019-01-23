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
This script changes the password for users user-1 through user-50.
It also changes the password of trainer-1 and trainer-2
The change must be done by an admin e.g. trainer-1.
"""

import argparse
import omero
from omero.rtypes import rstring


def run(password, new_password, admin_name, host, port):

    client = omero.client(host, port)
    session = client.createSession(admin_name, password)
    client.sf.setSecurityPassword(password)
    admin = session.getAdminService()

    for i in range(1, 51):
        user = 'user-%s' % i
        print user
        admin.changeUserPassword(user, rstring(new_password))
    
    for i in range(1, 3):
        user = 'trainer-%s' % i
        print user
        admin.changeUserPassword(user, rstring(new_password))

    client.closeSession()


def main(args):
    parser = argparse.ArgumentParser()
    # The password of the user changing the passwords
    parser.add_argument('password')
    parser.add_argument('newpassword')
    parser.add_argument('--name', default="trainer-1",
                        help="The user changing the passwords")
    parser.add_argument('--server', default="outreach.openmicroscopy.org",
                        help="OMERO server hostname")
    parser.add_argument('--port', default=4064, help="OMERO server port")
    args = parser.parse_args(args)
    run(args.password, args.newpassword, args.name, args.server, args.port)


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
