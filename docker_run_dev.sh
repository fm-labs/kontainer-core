#!/bin/bash

DEV_CONTAINER_NAME=kstack-agent-dev
DEV_IMAGE_TAG=kstack-agent:dev

docker stop ${DEV_CONTAINER_NAME}
docker rm ${DEV_CONTAINER_NAME}

docker build -t ${DEV_IMAGE_TAG} -f ./Dockerfile-dev-alpine . && \

docker run \
  --rm \
  --name ${DEV_CONTAINER_NAME} \
  --privileged \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /var/lib/docker/volumes:/var/lib/docker/volumes:ro \
  -v $PWD/data:/app/data \
  -v $PWD/src:/app/src:ro \
  -v $PWD/agent.py:/app/agent.py:ro \
  -v $PWD/celery_worker.sh:/app/celery_worker.sh:ro \
  -p 5000:5000 \
  -p 5080:80 \
  -p 5443:443 \
  -e AGENT_HOST=0.0.0.0 \
  -e AGENT_PORT=5000 \
  -e AGENT_DATA_DIR=/app/data \
  ${DEV_IMAGE_TAG} $@
