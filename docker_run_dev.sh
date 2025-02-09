#!/bin/bash

docker stop kstack-agent-dev
docker rm kstack-agent-dev

source ./docker_build.sh

docker run \
  --name kstack-agent-dev \
  --privileged \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /var/lib/docker/volumes:/var/lib/docker/volumes:ro \
  -v kstack_agent_data:/app/data \
  -p 5000:5000 \
  -p 5080:80 \
  -e AGENT_HOST=0.0.0.0 \
  -e AGENT_PORT=5000 \
  -e AGENT_DATA_DIR=/app/data \
  kstack-agent:latest $@
