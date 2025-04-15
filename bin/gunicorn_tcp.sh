#!/bin/bash

set -xe

export PYTHON_UNBUFFERED=1
export PYTHONPATH=/app/src:$PYTHONPATH

export KONTAINER_DATA_DIR=${KONTAINER_DATA_DIR:-/app/data}
export KONTAINER_HOST=${KONTAINER_HOST:-0.0.0.0}
export KONTAINER_PORT=${KONTAINER_PORT:-5000}


# Auto-detect app dir
script_path=$(realpath $0)
bin_dir=$(dirname $script_path)
DIR=$(dirname $bin_dir)
echo "DIR: $DIR"

# Name of the application
NAME="kontainer-api"

# the user to run as
USER=$(whoami)

# the group to run as
GROUP=$(whoami)

# how many worker processes should Gunicorn spawn
NUM_WORKERS=${KONTAINER_WORKERS:-3}

# Gunicorn log level
LOG_LEVEL=${LOG_LEVEL:-info}
LOG_FILE=${LOG_FILE:--}

# we will communicate using this tcp address and port
#BIND=0.0.0.0:5000
BIND=${KONTAINER_HOST}:${KONTAINER_PORT}

# WSGI module name
WSGI_APP=wsgi:app

# Create the run directory if it doesn't exist
# RUNDIR=$(dirname $SOCKFILE)
# test -d $RUNDIR || mkdir -p $RUNDIR

echo "Starting gunicorn (${BIND}) as ${USER}:${GROUP} ..."
sleep 3
exec gunicorn ${WSGI_APP} \
  --capture-output \
  --name ${NAME} \
  --workers ${NUM_WORKERS} \
  --bind=${BIND} \
  --log-level=${LOG_LEVEL} \
  --log-file=${LOG_FILE}
