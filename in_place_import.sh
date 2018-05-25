#!/bin/bash
# -----------------------------------------------------------------------------
#   Copyright (C) 2017 University of Dundee. All rights reserved.
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

# This script imports in-place data for 40 different users by default, 
# user-1 through user-40 into a target dataset.
# The script assumes that the users have the same password.
# The data are being imported by the users themselves, 
# i.e. after import each of the 40 users has their own batch of data.
# Data can also be imported for trainers.
# To import for trainers run for example
# OMEUSER=trainer NUMBER=2 bash in_place_import.sh

echo Starting
OMEROPATH=${OMEROPATH:-/opt/omero/server/OMERO.server/bin/omero}
PASSWORD=${PASSWORD:-ome}
HOST=${HOST:-outreach.openmicroscopy.org}
FOLDER=${FOLDER:-siRNAi-HeLa}
NUMBER=${NUMBER:-40}
OMEUSER=${OMEUSER:-user}
DATATYPE=${DATATYPE:-dataset}
for ((i=1;i<=$NUMBER;i++));
do  $OMEROPATH login -u $OMEUSER-$i -s $HOST -w $PASSWORD
    if [ "$DATATYPE" = "dataset" ]; then
        DatasetId=$($OMEROPATH obj new Dataset name=$FOLDER)
        $OMEROPATH import -d $DatasetId --transfer=ln_s "/OMERO/in-place-import/$FOLDER"
    elif [ "$DATATYPE" = "plate" ]; then
        $OMEROPATH import --transfer=ln_s "/OMERO/in-place-import/$FOLDER"
    fi
    $OMEROPATH logout
done
echo Finishing
