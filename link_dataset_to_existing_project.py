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
This script looks for a specified project and links it to the specified Dataset
for users user-1 through user-40.
"""

import argparse
import omero
from omero.gateway import BlitzGateway
from omero.model import DatasetI
from omero.model import ProjectDatasetLinkI
from omero.model import ProjectI
from omero.rtypes import rstring


def run(password, project_name, dataset_name, host, port):

    for user_number in range(1, 3):
        username = "user-%s" % user_number
        print username
        conn = BlitzGateway(username, password, host=host, port=port)
        try:
            conn.connect()

            params = omero.sys.ParametersI()
            params.addString('username', username)
            # make sure only one result is returned by query
            params.page(0, 1)
            query = "from Project where name='%s' \
                     AND details.owner.omeName=:username ORDER BY id DESC" % project_name
            service = conn.getQueryService()
            pr_list = service.findAllByQuery(query, params, conn.SERVICE_OPTS)

            if pr_list is None:
                print "No project with name %s found" % project_name
                continue


            project_id = pr_list[0].getId().getValue()
            print username, project_id

            params = omero.sys.ParametersI()
            params.addString('username', username)
            # make sure only one result is returned by query
            params.page(0, 1)
            query = "from Dataset where name='%s' \
                     AND details.owner.omeName=:username ORDER BY id DESC" % dataset_name
            service = conn.getQueryService()
            ds_list = service.findAllByQuery(query, params, conn.SERVICE_OPTS)

            if ds_list is None:
                print "No dataset with name %s found" % dataset_name
                continue


            dataset_id = ds_list[0].getId().getValue()
            print username, dataset_id

            link = ProjectDatasetLinkI()
            link.setParent(ProjectI(project_id, False))
            link.setChild(DatasetI(dataset_id, False))
            conn.getUpdateService().saveObject(link)
        except Exception as exc:
            print "Error while linking to project: %s" % str(exc)
        finally:
            conn.close()


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('password')
    parser.add_argument('project')
    parser.add_argument('dataset')
    parser.add_argument('--server', default="outreach.openmicroscopy.org",
                        help="OMERO server hostname")
    parser.add_argument('--port', default=4064, help="OMERO server port")
    args = parser.parse_args(args)
    run(args.password, args.project, args.dataset, args.server, args.port)


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
