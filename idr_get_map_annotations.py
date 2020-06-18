# -----------------------------------------------------------------------------
#  Copyright (C) 2018-2020 University of Dundee. All rights reserved.
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

# This client-side script runs over IDR data in our local server
# (copy of IDR data imported locally) and annotates Images with map annotations
# loaded from IDR.
# Datasets, Images and Annotations are loaded from IDR via http using
# public URLS returning JSON data.
# Starting at a local Screen/Plate/Project:ID and IDR Screen/Plate/Project:ID,
# we use Screen, Dataset and Image
# names to match local objects with those in IDR.

import argparse
import omero
from omero.gateway import BlitzGateway
import requests


base_url = "https://idr.openmicroscopy.org/"
webclient_api_url = base_url + "webclient/api/"
map_ann_url = webclient_api_url + "annotations/?type=map"
session = requests.Session()


def get_idr_datasets_as_dict(project_id):
    """Get a dict of {name: {id: 1}} for Datasets in IDR Project."""
    url = webclient_api_url + "datasets/?id=%s" % project_id
    datasets = session.get(url).json()['datasets']
    by_name = {}
    for d in datasets:
        by_name[d['name']] = d
    return by_name


def get_idr_images_as_dict(dataset_id):
    """Get a dict of {name: {id: 1}} for Images in IDR Dataset."""
    url = webclient_api_url + "images/?id=%s" % dataset_id
    images = session.get(url).json()['images']
    by_name = {}
    for i in images:
        by_name[i['name']] = i
    return by_name


def get_idr_plates_as_dict(screen_id):
    """Get a dict of {name: {id: 1}} for Plates in IDR Screen."""
    url = webclient_api_url + "plates/?id=%s" % screen_id
    plates = session.get(url).json()['plates']
    by_name = {}
    for p in plates:
        by_name[p['name']] = p
    return by_name


def get_idr_wells_as_grid(plate_id):
    url = base_url + "webgateway/plate/%s/0/" % plate_id
    return session.get(url).json()['grid']


def annotate_project(conn, local_id, idr_id):
    project = conn.getObject("Project", local_id)
    idr_datasets = get_idr_datasets_as_dict(idr_id)
    for dataset in project.listChildren():

        print("\n\nDataset", dataset.id, dataset.name)
        # Get IDR Dataset with same name:
        idr_dataset = idr_datasets.get(dataset.name)
        if idr_dataset is None:
            print("    NO IDR Dataset found!")
            continue

        idr_images = get_idr_images_as_dict(idr_dataset['id'])
        for image in dataset.listChildren():

            print("Image", image.id, image.name)
            idr_image = idr_images[image.name]
            if idr_image is None:
                print("    NO IDR Image found!")
                continue

            # Get map annotations for image...
            url = map_ann_url + "&image=%s" % idr_image['id']
            add_new_map_anns(conn, image, url)


def add_new_map_anns(conn, obj, url):
    map_anns = session.get(url).json()['annotations']
    print("  adding ", len(map_anns), " map anns...")
    for ann in map_anns:
        key_value_data = ann['values']
        map_ann = omero.gateway.MapAnnotationWrapper(conn)
        map_ann.setValue(key_value_data)
        map_ann.setNs(ann['ns'])
        map_ann.save()
        obj.linkAnnotation(map_ann)


def annotate_screen(conn, local_id, idr_id):
    screen = conn.getObject("Screen", local_id)
    idr_plates = get_idr_plates_as_dict(idr_id)
    for plate in screen.listChildren():

        print("\n\nPlate", plate.id, plate.name)
        # Get IDR Plate with same name:
        idr_plate = idr_plates.get(plate.name)
        if idr_plate is None:
            print("    NO IDR Plate found!")
            continue
        annotate_plate(conn, plate, idr_plate['id'])


def annotate_plate(conn, plate, idr_plate_id):
    # 2d array of wells...
    idr_wells = get_idr_wells_as_grid(idr_plate_id)
    for well in plate.listChildren():

        print("Well", well.id, well.row, well.column)
        idr_well = idr_wells[well.row][well.column]

        # Get map annotations for well...
        url = map_ann_url + "&well=%s" % idr_well['wellId']
        add_new_map_anns(conn, well, url)


def run(username, password, idr_obj, local_obj, host, port):

    conn = BlitzGateway(username, password, host=host, port=port)
    try:
        conn.connect()
        # Project:1
        dtype = idr_obj.split(':')[0]
        idr_id = idr_obj.split(':')[1]
        local_id = local_obj.split(':')[1]
        if dtype == 'Project':
            annotate_project(conn, local_id, idr_id)
        elif dtype == 'Plate':
            plate = conn.getObject('Plate', local_id)
            annotate_plate(conn, plate, idr_id)
        elif dtype == 'Screen':
            annotate_screen(conn, local_id, idr_id)
    finally:
        conn.close()


description = """Usage: To copy map annotations from Project: 1 on IDR
to Project:2 on 'local' server:
$ python idr_get_map_annotation.py user pass Project:1 Project:2
--server localhost
"""

obj_help = "Project:ID, Plate:ID or Screen:ID"

def main(args):
    # Usage, see: $ python idr_get_map_annotation.py -h
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('username')
    parser.add_argument('password')
    parser.add_argument('idr_obj', help=obj_help),
    parser.add_argument('local_obj', help=obj_help)
    parser.add_argument('--server', default="workshop.openmicroscopy.org",
                        help="OMERO server hostname")
    parser.add_argument('--port', default=4064, help="OMERO server port")
    args = parser.parse_args(args)
    run(args.username, args.password, args.idr_obj, args.local_obj,
        args.server, args.port)


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
