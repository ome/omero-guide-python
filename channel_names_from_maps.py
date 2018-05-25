# -----------------------------------------------------------------------------
#  Copyright (C) 2018 University of Dundee. All rights reserved.
#
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
#  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# ------------------------------------------------------------------------------

# Script uses map annotations on each Image to rename channels

import argparse
from omero.gateway import BlitzGateway


NAMESPACE = "openmicroscopy.org/omero/bulk_annotations"
MAP_KEY = "Channels"


def run(username, password, project_id, host, port):

    conn = BlitzGateway(username, password, host=host, port=port)
    try:
        conn.connect()
        project = conn.getObject("Project", project_id)

        for dataset in project.listChildren():
            print "\n\nDataset", dataset.id, dataset.name
            for image in dataset.listChildren():

                print "Image", image.id, image.name
                ann = image.getAnnotation(NAMESPACE)
                if ann is None:
                    print " No annotation found"
                    continue
                keys = ann.getValue()
                values = [kv[1] for kv in keys if kv[0] == MAP_KEY]
                if len(values) == 0:
                    print " No Key-Value found for key:", MAP_KEY
                channels = values[0].split("; ")
                print "Channels", channels
                name_dict = {}
                for c, ch_name in enumerate(channels):
                    name_dict[c + 1] = ch_name.split(":")[1]
                conn.setChannelNames("Image", [image.id], name_dict,
                                     channelCount=None)
    except Exception as exc:
            print "Error while changing names: %s" % str(exc)
    finally:
        conn.close()


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('username')
    parser.add_argument('password')
    parser.add_argument('project_id')
    parser.add_argument('--server', default="outreach.openmicroscopy.org",
                        help="OMERO server hostname")
    parser.add_argument('--port', default=4064, help="OMERO server port")
    args = parser.parse_args(args)
    run(args.username, args.password, args.project_id, args.server, args.port)


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
