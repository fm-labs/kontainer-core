#!/bin/bash

set -xe

# Auto-detect app dir
script_path=$(realpath $0)
bin_dir=$(dirname $script_path)
DIR=$(dirname $bin_dir)
echo "DIR: $DIR"

# Name of the application
NAME="kstack-agent-api"

# we will communicte using this tcp address and port
BIND=0.0.0.0:5000

# the user to run as
USER=$(whoami)

# the group to run as
GROUP=$(whoami)

# how many worker processes should Gunicorn spawn
NUM_WORKERS=3

# WSGI module name
WSGI_MODULE=wsgi
# echo "Starting $NAME as $(whoami)"

export PYTHONPATH=$DIR/src:$PYTHONPATH
export AGENT_DATA_DIR=$DIR/data

# Create the run directory if it doesn't exist
# RUNDIR=$(dirname $SOCKFILE)
# test -d $RUNDIR || mkdir -p $RUNDIR

exec gunicorn ${WSGI_MODULE}:app \
  --name $NAME \
  --workers $NUM_WORKERS \
  # --user=$USER --group=$GROUP \
  --bind=$BIND \
  --log-level=debug \
  --log-file=-
