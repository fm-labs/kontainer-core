#!/bin/bash

DEV_CONTAINER_NAME=kstack-agent-dev
DEV_IMAGE_TAG=kstack-agent:dev

docker stop ${DEV_CONTAINER_NAME}
docker rm ${DEV_CONTAINER_NAME}

docker build -t ${DEV_IMAGE_TAG} . && \

docker run \
  --rm \
  --name ${DEV_CONTAINER_NAME} \
  --privileged \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /var/lib/docker/volumes:/var/lib/docker/volumes:ro \
  -v $PWD/data:/app/data \
  -p 5000:5000 \
  -p 5080:80 \
  -e AGENT_HOST=0.0.0.0 \
  -e AGENT_PORT=5000 \
  -e AGENT_DATA_DIR=/app/data \
  ${DEV_IMAGE_TAG} $@
