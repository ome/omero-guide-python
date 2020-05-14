from getpass import getpass
from omero.gateway import BlitzGateway
from omero.model import EllipseI

# Step 1 - Connect to OMERO server

def connect(hostname, username, password):
  """
  Connect to an OMERO server
  :param hostname: Host name
  :param username: User
  :param password: Password
  :return: Connected BlitzGateway
  """
  conn = BlitzGateway(username, password,
                      host=hostname, secure=True)
  conn.connect()
  return conn


# Step 3 - Load metadata (channel information)

def get_channel_index(image, label):
  """
  Get the channel index of a specific channel
  :param image: The image
  :param label:  The channel name
  :return: The channel index (None if not found)
  """
  labels = image.getChannelLabels()
  if label in labels:
    idx = labels.index(label)
    return idx
  return None


# Step 4 - Load metadata (ellipse ROI)

def get_ellipse_roi(roi_service, image):
  """
  Get the first ellipse ROI found in the image
  :param roi_service: The ROI service
  :param image: The Image
  :return: The shape ID of the first ellipse ROI found
  """
  result = roi_service.findByImage(image.getId(), None)
  shape_id = None
  for roi in result.rois:
    for s in roi.copyShapes():
      if type(s) == EllipseI:
        shape_id = s.id.val
  return shape_id


# Step 5 - Get the mean intensities

def get_mean_intensities(roi_service, image, the_c, shape_id):
  """
  Get the mean pixel intensities of an roi in a time series image
  :param roi_service: The ROI service
  :param image: The image
  :param the_c: The channel index
  :param shape_id: The ROI shape id
  :return: List of mean intensity values (one for each timepoint)
  """
  the_z = 0
  size_t = image.getSizeT()
  meanvalues = []
  for t in range(size_t):
    stats = roi_service.getShapeStatsRestricted([shape_id],
                                                the_z, t, [the_c])
    meanvalues.append(stats[0].mean[the_c])
  return meanvalues


hostname = "wss://workshop.openmicroscopy.org/omero-ws"
username = ""
password = getpass("Password: ")
image_id = 123
channel = ""

conn = connect(hostname, username, password)
print("Logged in as {}".format(conn.getUser().getFullName()))

# Step 2 - Load image
img = conn.getObject("Image", image_id)
print("Using image {}".format(img.getName()))

ci = get_channel_index(img, channel)
print("Channel index {}".format(ci))

rs = conn.getRoiService()
shape_id = get_ellipse_roi(rs, img)
print("Shape id {}".format(shape_id))

values = get_mean_intensities(rs, img, ci, shape_id)
print("Values {}".format(values))

conn.close()
