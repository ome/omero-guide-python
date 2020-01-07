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

#
# The render plugin currently doesn't support applying a set of rendering settings to a 
# whole dataset. This script just iterates over a tab separated mapping file which
# maps a dataset name to a rendering settings file (can be json or yml).
# It retrieves the images ids of the datasets and calls the render plugin for each
# of the images. 
#
# Note:
# - If any of the datasets has more than 100 images increase the --limit parameter!
#
# This script applies the rendering settings using the render plugin
# It is done by a third party person for all the users
FILE=${FILE:-renderingMapping.tsv}
OMERODIR=${OMERODIR:-/opt/omero/server/OMERO.server}
VENV_SERVER=${VENV_SERVER:-/opt/omero/server/venv3}
PASSWORD=${PASSWORD:-ome}
HOST=${HOST:-workshop.openmicroscopy.org}
NUMBER=${NUMBER:-50}
OMEUSER=${OMEUSER:-user}
SUDOER=${SUDOER:-importer1}

export $OMERODIR
export PATH=$VENV_SERVER/bin:$PATH

for ((i=1;i<=$NUMBER;i++));
do  omero login --sudo ${SUDOER} -u $OMEUSER-$i -s $HOST -w $PASSWORD
    while IFS='	' read -r f1 f2
    do
        imageids=`omero hql --ids-only --limit 500 --style csv -q "select img from DatasetImageLink l join l.parent as ds join l.child as img where ds.name = '$f1'"`
        IFS=',' read -r -a array <<< $imageids

        for imageid in "${array[@]}"
        do
            imageid=${imageid/ */}
            if [[ $imageid == Image* ]]
            then
                printf 'Applying rendering settings %s (dataset %s) to %s \n' "$f2" "$f1" "$imageid"
                omero render set $imageid $f2
        fi
        done
    done < "$FILE"
done
echo Finishing

