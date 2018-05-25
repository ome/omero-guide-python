#!/bin/bash
#
# The render plugin currently doesn't support applying a set of rendering settings to a 
# whole dataset. This script just itereates over a tab separated mapping file which
# maps a dataset name to a renderings settings file (can be json or yml).
# It retrieves the images ids of the datasets and calls the render plugin for each
# of the images. 
#
# Note: 
# - You need to log in first before running this script.
# - If any of the datasets has more than 100 images increase the --limit parameter!
#
# This script applies the rendering settings using the render plugin
# It is done by a third party person for all the users
FILE=${FILE:-renderingMapping.tsv}
OMEROPATH=${OMEROPATH:-/opt/omero/server/OMERO.server/bin/omero}
PASSWORD=${PASSWORD:-ome}
HOST=${HOST:-outreach.openmicroscopy.org}
NUMBER=${NUMBER:-40}
OMEUSER=${OMEUSER:-user}
SUDOER=${SUDOER:-importer1}

for ((i=1;i<=$NUMBER;i++));
do  $OMEROPATH login --sudo ${SUDOER} -u $OMEUSER-$i -s $HOST -w $PASSWORD
    while IFS='	' read -r f1 f2
    do
        imageids=`$OMEROPATH hql --ids-only --limit 500 --style csv -q "select img from DatasetImageLink l join l.parent as ds join l.child as img where ds.name = '$f1'"`
        IFS=',' read -r -a array <<< $imageids

        for imageid in "${array[@]}"
        do
            imageid=${imageid/ */}
            if [[ $imageid == Image* ]]
            then
                printf 'Applying rendering settings %s (dataset %s) to %s \n' "$f2" "$f1" "$imageid"
                $OMEROPATH render set $imageid $f2
        fi
        done
    done < "$FILE"
done
echo Finishing

