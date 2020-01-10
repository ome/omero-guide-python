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
OMERODIR=${OMERODIR:-/opt/omero/server/OMERO.server}
VENV_SERVER=${VENV_SERVER:-/opt/omero/server/venv3}
PASSWORD=${PASSWORD:-ome}
HOST=${HOST:-workshop.openmicroscopy.org}
FOLDER=${FOLDER:-siRNAi-HeLa}
NUMBER=${NUMBER:-50}
OMEUSER=${OMEUSER:-user}
DATATYPE=${DATATYPE:-dataset}
IMPORTTYPE=${IMPORTTYPE:-bulk}
BULKFILE=${BULKFILE:-idr0021-scripts/idr0021-experimentA-bulk.yml}
PROJECTNAME=${PROJECTNAME:-idr0021}

export OMERODIR
export PATH=$VENV_SERVER/bin:$PATH

for ((i=1;i<=$NUMBER;i++));
do  omero login --sudo ${SUDOER} -u $OMEUSER-$i -s $HOST -w $PASSWORD
    if [ "$DATATYPE" = "dataset" ]; then
        if [ "$IMPORTTYPE" = "normal" ]; then
            DatasetId=$(omero obj new Dataset name=$FOLDER)
            omero import -d $DatasetId --transfer=ln_s $FOLDER
        elif [ "$IMPORTTYPE" = "bulk" ]; then
            # Create the project
            projectId=`omero obj new Project name=$PROJECTNAME`
            # Get the name of the filepaths.tsv file from the bulk.yml
            tsv=`grep path: $BULKFILE | cut -d '"' -f2`
            # Assume it is in the same directory as the bulk.yml
            tsvdir=$(dirname `readlink -f ${BULKFILE}`)
            filepaths=${tsvdir}/${tsv}
            # Find out which datasets needs to be created, and create them
            datasets=`cat $filepaths | cut -f1 | cut -d ':' -f3 | uniq`
            for dataset in $datasets
            do
                datasetId=`omero obj new Dataset name=$dataset`
                linkId=`omero obj new ProjectDatasetLink parent=$projectId child=$datasetId`
            done
            # Then launch the import
            omero import --bulk $BULKFILE
        fi
    elif [ "$DATATYPE" = "plate" ]; then
        omero import --transfer=ln_s $FOLDER
        DatasetId=$(omero obj new Dataset name=$FOLDER)
        omero import -d $DatasetId --transfer=ln_s "/OMERO/in-place-import/$FOLDER"
    elif [ "$DATATYPE" = "plate" ]; then
        omero import --transfer=ln_s "/OMERO/in-place-import/$FOLDER"
    fi
    omero logout
done
echo Finishing
