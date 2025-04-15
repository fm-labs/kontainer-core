#!/bin/bash

IMAGE_NAME=fmlabs/kontainer-core:latest
CONTAINER_NAME=kontainer-core

docker stop ${CONTAINER_NAME}
docker rm ${CONTAINER_NAME}
docker pull ${IMAGE_NAME}
docker run -d \
  --name ${CONTAINER_NAME} \
  --restart always \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -v /var/lib/docker/volumes:/var/lib/docker/volumes:ro \
  -v kontainer_data:/app/data \
  -p 5000:5000 \
  -e KONTAINER_HOST=0.0.0.0 \
  -e KONTAINER_DATA_DIR=/app/data \
  -e KONTAINER_DATA_VOLUME=kontainer_data \
  ${IMAGE_NAME}
