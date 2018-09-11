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

# Delete ROIs from all Images in a Dataset

import argparse
from omero.gateway import BlitzGateway


def run(name, password, dataset_name, host, port):

    conn = BlitzGateway(name, password, host=host, port=port)
    try:
        conn.connect()
        roi_service = conn.getRoiService()
        datasets = conn.getObjects("Dataset", attributes={"name":dataset_name})
        for dataset in datasets:
            print dataset.getId()
            for image in dataset.listChildren():
                result = roi_service.findByImage(image.getId(), None,
                                                 conn.SERVICE_OPTS)
                if result is not None:
                    roi_ids = [roi.id.val for roi in result.rois]
                    print "Deleting %s ROIs..." % len(roi_ids)
                    if len(roi_ids) > 0:
                        conn.deleteObjects("Roi", roi_ids, wait=True)
    except Exception as exc:
            print(exc)
            print "Error while deleting Rois: %s" % str(exc)
    finally:
        conn.close()


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('password')
    parser.add_argument('dataset_name')
    parser.add_argument('--name', default="trainer-1",
                        help="The user deleting the rois")
    parser.add_argument('--server', default="outreach.openmicroscopy.org",
                        help="OMERO server hostname")
    parser.add_argument('--port', default=4064, help="OMERO server port")
    args = parser.parse_args(args)
    run(args.name, args.password, args.dataset_name, args.server, args.port)


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
