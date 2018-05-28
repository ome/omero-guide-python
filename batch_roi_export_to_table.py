#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
#   Copyright (C) 2018 University of Dundee. All rights reserved.

#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License along
#   with this program; if not, write to the Free Software Foundation, Inc.,
#   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

# ------------------------------------------------------------------------------

"""This script exports ROI intensities for selected images."""


import omero.scripts as scripts
from omero.gateway import BlitzGateway, MapAnnotationWrapper,\
    FileAnnotationWrapper
from omero.rtypes import unwrap, rstring, rlong, robject
from omero.grid import DoubleColumn, ImageColumn
from omero.model import FileAnnotationI, OriginalFileI
from omero.constants.namespaces import NSBULKANNOTATIONS

from collections import defaultdict

DEFAULT_FILE_NAME = "roi_intensities_filtered_by_channel.csv"
BATCH_ROI_EXPORT_NS = "omero.batch_roi_export.map_ann"


def log(data):
    """Handle logging or printing in one place."""
    print data


def get_export_data(conn, script_params, image):
    """Get pixel data for shapes on image and returns list of dicts."""
    log("Image ID %s..." % image.id)
    roi_service = conn.getRoiService()
    all_planes = script_params["Export_All_Planes"]
    size_c = image.getSizeC()
    # Channels index
    channels = script_params.get("Intensity_For_Channels", [1])
    ch_indexes = []
    for ch in channels:
        if ch < 1 or ch > size_c:
            log("Channel index: %s out of range 1 - %s" % (ch, size_c))
        else:
            # User input is 1-based
            ch_indexes.append(ch - 1)

    # filter_ch = script_params.get("Filter_Shapes_By_Channel")
    # if filter_ch is not None:
        # convert to zero-based index
        # filter_ch = filter_ch - 1
    filter_ch = 0

    # For idr0021 use-case, we want to pick filter_channel dynamically...
    # First channel where channel name matches Dataset name.
    dataset_name = image.getParent().name
    for c, name in enumerate(image.getChannelLabels()):
        if name in dataset_name:
            filter_ch = c

    ch_names = image.getChannelLabels()

    ch_names = [ch_name.replace(",", ".") for ch_name in ch_names]
    image_name = image.getName().replace(",", ".")

    result = roi_service.findByImage(image.getId(), None)

    export_data = []
    log("Filter_Shapes_By_Channel: %s" % filter_ch)
    for roi in result.rois:
        for shape in roi.copyShapes():
            if filter_ch is not None and filter_ch != unwrap(shape.theC):
                log("%s != %s" % (filter_ch, unwrap(shape.theC)))
                continue
            label = unwrap(shape.getTextValue())
            # wrap label in double quotes in case it contains comma
            label = "" if label is None else '"%s"' % label.replace(",", ".")
            shape_type = shape.__class__.__name__.rstrip('I').lower()
            # If shape has no Z or T, we may go through all planes...
            the_z = unwrap(shape.theZ)
            z_indexes = [the_z]
            if the_z is None and all_planes:
                z_indexes = range(image.getSizeZ())
            # Same for T...
            the_t = unwrap(shape.theT)
            t_indexes = [the_t]
            if the_t is None and all_planes:
                t_indexes = range(image.getSizeT())
            # Get the C shape is on.
            # This is independent of ch_indexes we're getting intensities for
            the_c = unwrap(shape.theC)

            # get pixel intensities
            for z in z_indexes:
                for t in t_indexes:
                    if z is None or t is None:
                        stats = None
                    else:
                        stats = roi_service.getShapeStatsRestricted(
                            [shape.id.val], z, t, ch_indexes)
                    for c, ch_index in enumerate(ch_indexes):
                        export_data.append({
                            "image_id": image.getId(),
                            "image_name": '"%s"' % image_name,
                            "roi_id": roi.id.val,
                            "shape_id": shape.id.val,
                            "type": shape_type,
                            "text": label,
                            "z": z + 1 if z is not None else "",
                            "t": t + 1 if t is not None else "",
                            "c": the_c + 1 if the_c is not None else "",
                            "points": stats[0].pointsCount[c] if stats else "",
                            "intensity_for_channel": ch_names[ch_index],
                            "min": stats[0].min[c] if stats else "",
                            "max": stats[0].max[c] if stats else "",
                            "sum": stats[0].sum[c] if stats else "",
                            "mean": stats[0].mean[c] if stats else "",
                            "std_dev": stats[0].stdDev[c] if stats else ""
                        })
    return export_data


COLUMN_NAMES = ["image_id",
                "image_name",
                "roi_id",
                "shape_id",
                "type",
                "text",
                "z",
                "t",
                "c",
                "points",
                "intensity_for_channel",
                "min",
                "max",
                "sum",
                "mean",
                "std_dev"]

SUMMARY_COL_NAMES = ["filter_shapes_by_channel",
                     "shape_count",
                     "min_intensity",
                     "max_intensity",
                     "mean_intensity",
                     "min_points",
                     "max_points",
                     "mean_points"]


def link_table(conn, table, project):
    orig_file = table.getOriginalFile()
    file_ann = FileAnnotationWrapper(conn)
    file_ann.setNs(NSBULKANNOTATIONS)
    file_ann._obj.file = OriginalFileI(orig_file.id.val, False)
    file_ann.save()
    project.linkAnnotation(file_ann)


def write_csv(conn, export_data, script_params):
    """Write the list of data to a CSV file and create a file annotation."""
    file_name = script_params.get("File_Name", "")
    if len(file_name) == 0:
        file_name = DEFAULT_FILE_NAME
    if not file_name.endswith(".csv"):
        file_name += ".csv"

    csv_rows = [",".join(COLUMN_NAMES)]
    for row in export_data:
        cells = [str(row.get(name)) for name in COLUMN_NAMES]
        csv_rows.append(",".join(cells))

    with open(file_name, 'w') as csv_file:
        csv_file.write("\n".join(csv_rows))

    return conn.createFileAnnfromLocalFile(file_name, mimetype="text/csv")


def get_summary_data_for_image(conn, image, export_data, script_params):
    """Summarise ROIs as dict for this Image."""
    # get all ROI data for this image
    filter_ch = script_params.get('Filter_Shapes_By_Channel', '')

    # For idr0021 use-case, we want to pick filter_channel dynamically...
    # First channel where channel name matches Dataset name.
    dataset_name = image.getParent().name
    for c, name in enumerate(image.getChannelLabels()):
        if name in dataset_name:
            filter_ch = c + 1
            break

    data = [d for d in export_data if d['image_id'] == image.id]
    if len(data) == 0:
        return None
    min_intensity = min([d['min'] for d in data])
    max_intensity = max([d['max'] for d in data])
    mean_intensity = sum([d['mean'] for d in data]) / len(data)
    min_points = min([d['points'] for d in data])
    max_points = max([d['points'] for d in data])
    mean_points = sum([d['points'] for d in data]) / len(data)

    return {
        "filter_shapes_by_channel": filter_ch,
        "shape_count": len(data),
        "min_intensity": min_intensity,
        "max_intensity": max_intensity,
        "mean_intensity": mean_intensity,
        "min_points": min_points,
        "max_points": max_points,
        "mean_points": mean_points,
    }


def save_table(conn, images, export_data, script_params):
    """Summarise ROIs as Table (1 row per Image) linked to Project."""

    resources = conn.c.sf.sharedResources()
    repository_id = resources.repositories().descriptions[0].getId().getValue()
    table_name = "batch_roi_export"
    table = resources.newTable(repository_id, table_name)

    # Summarise data into columns
    image_ids = [i.id for i in images]
    col_data = defaultdict(list)

    for image in images:
        data = get_summary_data_for_image(conn, image, export_data,
                                          script_params)
        for key in SUMMARY_COL_NAMES:
            col_data[key].append(data[key] if data is not None else 0)

    # Create table
    img_column = ImageColumn('Image', '', image_ids)
    cols = [DoubleColumn(k, '', col_data[k]) for k in SUMMARY_COL_NAMES]
    data = [img_column] + cols
    table.initialize(data)
    table.addData(data)
    table.close()

    # Link Table to first Project we find
    project = None
    for image in images:
        project = image.getProject()
        if project is not None:
            break
    if project is None:
        log("No Project found to link table")
    else:
        link_table(conn, table, project)


def save_map_annotations(conn, images, export_data, script_params):
    """Summarise ROIs as Key-Value pairs for each Image."""
    for image in images:
        data = get_summary_data_for_image(conn, image, export_data,
                                          script_params)
        if data is None:
            continue
        key_value_data = [[k, str(data[k])] for k in SUMMARY_COL_NAMES]
        map_ann = MapAnnotationWrapper(conn)
        # Use custom namespace to allow finding/deleting map_anns we create
        map_ann.setNs(BATCH_ROI_EXPORT_NS)
        map_ann.setValue(key_value_data)
        map_ann.save()
        image.linkAnnotation(map_ann)


def link_annotation(objects, file_ann):
    """Link the File Annotation to each object."""
    for o in objects:
        if o.canAnnotate():
            o.linkAnnotation(file_ann)


def batch_roi_export(conn, script_params):
    """Main entry point. Get images, process them and return result."""
    images = []
    datasets = None
    if script_params['Data_Type'] == "Project":
        datasets = []
        for project in conn.getObjects("Project", script_params['IDs']):
            datasets.extend(list(project.listChildren()))
    elif script_params['Data_Type'] == "Dataset":
        datasets = conn.getObjects("Dataset", script_params['IDs'])

    if datasets is not None:
        for dataset in datasets:
            images.extend(list(dataset.listChildren()))
    else:
        images = list(conn.getObjects("Image", script_params['IDs']))

    log("Processing %s images..." % len(images))
    if len(images) == 0:
        return None

    # build a list of dicts.
    export_data = []
    for image in images:
        export_data.extend(get_export_data(conn, script_params, image))

    # Write to csv
    file_ann = None
    if script_params.get("Export_CSV"):
        file_ann = write_csv(conn, export_data, script_params)
        if script_params['Data_Type'] == "Dataset":
            datasets = conn.getObjects("Dataset", script_params['IDs'])
            link_annotation(datasets, file_ann)
        else:
            link_annotation(images, file_ann)

    # Create Map_Annotations on each image
    if script_params.get("Save_As_Key-Value"):
        save_map_annotations(conn, images, export_data, script_params)

    # Create single OMERO.table
    if script_params.get("Create_Table"):
        save_table(conn, images, export_data, script_params)

    message = "Exported %s shapes" % len(export_data)
    return file_ann, message


def run_script():
    """The main entry point of the script, as called by the client."""
    data_types = [rstring('Project'), rstring('Dataset'), rstring('Image')]

    client = scripts.client(
        'Batch_ROI_Export.py',
        """Export ROI intensities for selected Images.""",

        scripts.String(
            "Data_Type", optional=False, grouping="1",
            description="The data you want to work with.", values=data_types,
            default="Image"),

        scripts.List(
            "IDs", optional=False, grouping="2",
            description="List of Dataset IDs or Image IDs.").ofType(rlong(0)),

        # scripts.Int(
        #     "Filter_Shapes_By_Channel", grouping="3", optional=True,
        #     description=("Optional: only use shapes saved to this channel"
        #                  "(1-based index)")),

        scripts.List(
            "Intensity_For_Channels", grouping="4", default=[1L, 2L, 3L, 4L],
            description="Indices of Channels to measure intensity."
            ).ofType(rlong(0)),

        scripts.Bool(
            "Export_All_Planes", grouping="5",
            description=("Export all Z and T planes for shapes "
                         "where Z and T are not set?"),
            default=False),

        scripts.Bool(
            "Export_CSV",  grouping="6", default=True,
            description="Create a comma-separated-values file to download."),

        scripts.String(
            "File_Name", grouping="6.1", default=DEFAULT_FILE_NAME,
            description="Name of the exported CSV file."),

        scripts.Bool(
            "Save_As_Key-Value",  grouping="7", default=True,
            description="Summarise ROIs as Key-Value pairs on each Image."),

        scripts.Bool(
            "Create_Table",  grouping="8", default=True,
            description=("Summarise ROIs as Table (1 row per image)"
                         " attached to parent Project")),

        authors=["William Moore", "OME Team"],
        institutions=["University of Dundee"],
        contact="ome-users@lists.openmicroscopy.org.uk",
    )

    try:
        conn = BlitzGateway(client_obj=client)

        script_params = client.getInputs(unwrap=True)
        log("script_params:")
        log(script_params)

        # call the main script
        result = batch_roi_export(conn, script_params)

        # Return message and file_annotation to client
        if result is None:
            message = "No images found"
        else:
            file_ann, message = result
            if file_ann is not None:
                client.setOutput("File_Annotation", robject(file_ann._obj))

        client.setOutput("Message", rstring(message))

    finally:
        client.closeSession()


if __name__ == "__main__":
    run_script()
