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

conn = connect(hostname, username, password)
print("Logged in as {}".format(conn.getUser().getFullName()))

conn.close()
