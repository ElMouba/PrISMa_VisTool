#!/bin/bash -e
set -x

# This script is executed whenever the docker container is (re)started.
#===============================================================================
bokeh serve Figure Line Structure Preset Upload Adsorption Compare Table\
    --port 5007                 \
    --log-level debug           \
    --allow-websocket-origin "*" \
    --prefix "$BOKEH_PREFIX" \
    --use-xheaders
# --allow-websocket-origin discover.materialscloud.org
# --allow-websocket-origin localhost:5006

#===============================================================================

#EOF