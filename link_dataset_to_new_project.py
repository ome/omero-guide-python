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
This script creates a new project and links it to the specified Datasets
for users user-1 through user-50.

Datasets can be specified by a list, passing a "-d $DATASETNAME1 -d $DATASETNAME2 ..."
pattern to this script.

For example, to link all the 10 datasets of the idr0021 study to a new
project "idr0021" use:

python link_dataset_to_new_project.py $PWD idr0021  -d CDK5RAP2-C -d CENT2 -d CEP120/20111106 -d CEP120/20111209 -d CEP152 -d CEP192-M -d CPAP -d NEDD1-C1 -d PCNT-N1 -d TUBG1-N
"""

import argparse
import omero
from omero.gateway import BlitzGateway
from omero.model import DatasetI
from omero.model import ProjectDatasetLinkI
from omero.model import ProjectI
from omero.rtypes import rstring


def run(password, project_name, dataset_names, host, port):

    for user_number in range(1, 51):
        username = "user-%s" % user_number
        print(username)
        conn = BlitzGateway(username, password, host=host, port=port)
        try:
            conn.connect()
            project = ProjectI()
            project.setName(rstring(project_name))
            update_service = conn.getUpdateService()
            project = update_service.saveAndReturnObject(project)
        except Exception as exc:
            print("Error while creating project: %s" % str(exc))
            conn.close()
            continue

        for dataset_name in dataset_names:
            try:
                params = omero.sys.ParametersI()
                params.addString('username', username)
                # make sure only one result is returned by query
                params.page(0, 1)
                query = "from Dataset where name='%s' \
                         AND details.owner.omeName=:username \
                         ORDER BY id DESC" % dataset_name
                service = conn.getQueryService()
                ds_list = service.findAllByQuery(query, params,
                                                 conn.SERVICE_OPTS)

                if ds_list is None:
                    print("No dataset with name %s found" % dataset_name)
                    continue

                dataset_id = ds_list[0].getId().getValue()
                print(username, dataset_id)

                link = ProjectDatasetLinkI()
                link.setParent(ProjectI(project.getId().getValue(), False))
                link.setChild(DatasetI(dataset_id, False))
                conn.getUpdateService().saveObject(link)
            except Exception as exc:
                print("Error while linking dataset to project: %s" % str(exc))

        conn.close()


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('password')
    parser.add_argument('project')
    parser.add_argument('--dataset', '-d', type=str, action='append',
                        help='One or more datasets to link to the project')
    parser.add_argument('--server', default="outreach.openmicroscopy.org",
                        help="OMERO server hostname")
    parser.add_argument('--port', default=4064, help="OMERO server port")
    args = parser.parse_args(args)
    run(args.password, args.project, args.dataset, args.server, args.port)


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
