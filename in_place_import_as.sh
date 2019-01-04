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

# This script imports in-place data for 50 different users by default,
# user-1 through user-50 into a target dataset.
# The data is imported by a dedicated user with restricted admin
# privileges on behalf of other users 
# i.e. after import each of the 50 users has their own batch of data.
# Data can also be imported for trainers.
# To import a dataset for trainers run for example
# OMEUSER=trainer NUMBER=2 bash in_place_import_as.sh
# To import a plate for trainers run for example
# OMEUSER=trainer NUMBER=2 DATATYPE=plate FOLDER=HCS bash in_place_import_as.sh

echo Starting
SUDOER=${SUDOER:-importer1}
OMEROPATH=${OMEROPATH:-/opt/omero/server/OMERO.server/bin/omero}
PASSWORD=${PASSWORD:-ome}
HOST=${HOST:-outreach.openmicroscopy.org}
FOLDER=${FOLDER:-siRNAi-HeLa}
NUMBER=${NUMBER:-50}
OMEUSER=${OMEUSER:-user}
DATATYPE=${DATATYPE:-dataset}
IMPORTTYPE=${IMPORTTYPE:-normal}
CONTAINERS=${CONTAINERS:-idr0021-scripts/idr0021-experimentA-containers.omero}
BULKFILE=${BULKFILE:-idr0021-scripts/idr0021-experimentA-bulk.yml}
for ((i=1;i<=$NUMBER;i++));
do  $OMEROPATH login --sudo ${SUDOER} -u $OMEUSER-$i -s $HOST -w $PASSWORD
    if [ "$DATATYPE" = "dataset" ]; then
        if [ "$IMPORTTYPE" = "normal" ]; then
            DatasetId=$($OMEROPATH obj new Dataset name=$FOLDER)
            $OMEROPATH import -d $DatasetId --transfer=ln_s "/OMERO/in-place-import/$FOLDER"
        elif [ "$IMPORTTYPE" = "bulk" ]; then
            $OMEROPATH load "/OMERO/in-place-import/$CONTAINERS"
            $OMEROPATH import --bulk "/OMERO/in-place-import/$BULKFILE"
        fi
    elif [ "$DATATYPE" = "plate" ]; then
        $OMEROPATH import --transfer=ln_s "/OMERO/in-place-import/$FOLDER"
    fi
    $OMEROPATH logout
done
echo Finishing
