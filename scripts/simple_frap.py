from getpass import getpass

# Import OMERO Python BlitzGateway
from omero.gateway import BlitzGateway
from omero.model import EllipseI
from omero.gateway import MapAnnotationWrapper


# Connect to the server
def connect(hostname, username, password):
    conn = BlitzGateway(username, password,
                        host=hostname, secure=True)
    conn.connect()
    return conn


# Load-images
def load_images(conn, dataset_id):
    dataset = conn.getObject("Dataset", dataset_id)
    images = []
    for image in dataset.listChildren():
        images.append(image)
    return images


# Analyse-images
def analyze(conn, images, channel_label):
    svc = conn.getRoiService()
    for image in images:
        print("Processing Image:", image.id)
        shape_id = get_ellipse(svc, image)
        if shape_id is None:
            continue
        ch_index = get_channel_index(image, channel_label)
        mean_values = get_mean_intensities(svc, image, ch_index, shape_id)
        save_results(conn, image, mean_values)


# Get channel
def get_channel_index(image, label):
    labels = image.getChannelLabels()
    if label in labels:
        idx = labels.index(label)
        print("Channel Index:", idx)
        return idx
    return 0


# Get-ellipse
def get_ellipse(roi_service, image):
    result = roi_service.findByImage(image.getId(), None)
    # Simply return any Ellipse we find...
    shape_id = None
    for roi in result.rois:
        print("ROI:", roi.getId().getValue())
        for s in roi.copyShapes():
            if type(s) == EllipseI:
                shape_id = s.id.val
    print("Shape:", shape_id)
    return shape_id


# Get-mean-intensities
def get_mean_intensities(roi_service, image, the_c, shape_id):
    # Get pixel intensities for first Channel
    the_z = 0
    size_t = image.getSizeT()
    print('SizeT', size_t)
    meanvalues = []
    for t in range(size_t):
        stats = roi_service.getShapeStatsRestricted([shape_id],
                                                    the_z, t, [the_c])
        meanvalues.append(stats[0].mean[the_c])
    return meanvalues


# Save-results
def save_results(conn, image, values):
    # Add values as a Map Annotation on the image
    namespace = "demo.simple_frap_data"
    delete_old_annotations(conn, image, namespace)
    key_value_data = [[str(t), str(value)] for t, value in enumerate(values)]
    map_ann = MapAnnotationWrapper(conn)
    map_ann.setNs(namespace)
    map_ann.setValue(key_value_data)
    map_ann.save()
    image.linkAnnotation(map_ann)


# Delete-old-annotations
def delete_old_annotations(conn, image, namespace):
    to_delete = []
    for ann in image.listAnnotations(ns=namespace):
        to_delete.append(ann.id)
    if len(to_delete) > 0:
        print("Deleting old annotations", to_delete)
        conn.deleteObjects('Annotation', to_delete, wait=True)


# Disconnect
def disconnect(conn):
    conn.close()


# main
def main():
    # Collect user credentials
    try:
        host = input("Host [wss://workshop.openmicroscopy.org/omero-ws]: ") or 'wss://workshop.openmicroscopy.org/omero-ws'  # noqa
        username = input("Username [trainer-1]: ") or 'trainer-1'
        password = getpass("Password: ")
        dataset_id = input("Dataset ID [2391]: ") or '2391'
        channel_label = input("Channel Label [GFP]: ") or 'GFP'

        # Connect to the server
        conn = connect(host, username, password)

        # Load the images container in the specified dataset
        images = load_images(conn, dataset_id)

        if len(images) == 0:
            print("No images in dataset")
            return
        
        images = images[:1]
        analyze(conn, images, channel_label)
    finally:
        disconnect(conn)
    print("done")


if __name__ == "__main__":
    main()
