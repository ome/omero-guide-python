from getpass import getpass
from omero.gateway import BlitzGateway

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

conn.close()
