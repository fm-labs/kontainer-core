#!/bin/bash

CELERY=$(which celery)

$CELERY -A agent.celery worker --loglevel=INFO