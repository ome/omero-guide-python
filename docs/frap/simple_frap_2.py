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


hostname = "wss://workshop.openmicroscopy.org/omero-ws"
username = ""
password = getpass("Password: ")
image_id = 123

conn = connect(hostname, username, password)
print("Logged in as {}".format(conn.getUser().getFullName()))

# Step 2 - Load image
img = conn.getObject("Image", image_id)
print("Using image {}".format(img.getName()))

conn.close()
