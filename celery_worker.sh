#!/bin/bash

CELERY=$(which celery)

echo "Initialize celery worker as $(whoami)"
echo "Found celery at: $CELERY"
sleep 3

echo "PYTHONPATH: $PYTHONPATH"
# Add src/ to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
echo "PYTHONPATH: $PYTHONPATH"

echo "Starting celery worker ..."
$CELERY -A main.celery worker --loglevel=INFO

echo "Celery worker exited"
