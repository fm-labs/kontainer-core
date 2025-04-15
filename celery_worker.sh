#!/bin/bash

CELERY=$(which celery)

echo "Initialize celery worker as $(whoami)"
echo "Found celery at: $CELERY"
sleep 3

echo "Starting celery worker ..."
$CELERY -A kontainer.celery worker --loglevel=INFO

echo "Celery worker exited"
