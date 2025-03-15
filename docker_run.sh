#!/bin/bash

IMAGE_NAME=fmlabs/kstack-agent:latest
CONTAINER_NAME=kstack-agent

docker stop ${CONTAINER_NAME}
docker rm ${CONTAINER_NAME}
docker pull ${IMAGE_NAME}
docker run -d \
  --name ${CONTAINER_NAME} \
  --restart always \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -v /var/lib/docker/volumes:/var/lib/docker/volumes:ro \
  -v kstack_agent_data:/app/data \
  -p 5000:5000 \
  -e AGENT_HOST=0.0.0.0 \
  -e AGENT_DATA_DIR=/app/data \
  -e AGENT_DATA_VOLUME=kstack_agent_data \
  ${IMAGE_NAME}
