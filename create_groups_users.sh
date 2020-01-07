#!/bin/bash
# -----------------------------------------------------------------------------
#   Copyright (C) 2018 University of Dundee. All rights reserved.
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

# This script creates the group/users defined in an external file.
# The groups and users are created by a dedicated user with restricted admin
# privileges.
# Usage example
# SUDOER=trainer bash create_groups_users.sh

echo Starting
SUDOER=${SUDOER:-root}
OMERODIR=${OMERODIR:-/opt/omero/server/OMERO.server}
VENV_SERVER=${VENV_SERVER:-/opt/omero/server/venv3}
PASSWORD=${PASSWORD:-omero}
HOST=${HOST:-workshop.openmicroscopy.org}
SETUP=${SETUP:-create_groups_users_setup}

export $OMERODIR
export PATH=$VENV_SERVER/bin:$PATH

omero login  -u ${SUDOER} -s $HOST -w $PASSWORD
omero load ${SETUP}
echo Finishing
