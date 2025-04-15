#!/bin/bash

DEV_CONTAINER_NAME=kontainer-core-dev
DEV_IMAGE_TAG=kontainer-core:dev

docker stop ${DEV_CONTAINER_NAME}
docker rm ${DEV_CONTAINER_NAME}

docker build -t ${DEV_IMAGE_TAG} --progress=plain -f ./Dockerfile-alpine . && \

docker run \
  --rm \
  --name ${DEV_CONTAINER_NAME} \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -v /var/lib/docker/volumes:/var/lib/docker/volumes:ro \
  -v $PWD/data:/app/data \
  -v $PWD/bin:/app/bin:ro \
  -v $PWD/src:/app/src:ro \
  -v $PWD/kontainer.py:/app/kontainer.py:ro \
  -v $PWD/celery_worker.sh:/app/celery_worker.sh:ro \
  -p 5000:5000 \
  -p 3080:3080 \
  -p 3443:3443 \
  -e KONTAINER_HOST=0.0.0.0 \
  -e KONTAINER_PORT=5000 \
  -e KONTAINER_DATA_DIR=/app/data \
  -e KONTAINER_DATA_HOME=$PWD/data \
  -e KONTAINER_WORKERS=1 \
  -e KONTAINER_DEBUG=1 \
  -e LOG_LEVEL=info \
  ${DEV_IMAGE_TAG} $@
