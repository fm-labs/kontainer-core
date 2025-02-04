#!/bin/bash

source ./docker_build.sh

docker run -d \
  --name kstack-agent-dev \
  --privileged \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v kstack_agent_data:/app/data \
  -p 5000:5000 \
  -e AGENT_HOST=0.0.0.0 \
  -e AGENT_PORT=5000 \
  -e AGENT_DATA_DIR=/app/data \
  kstack-agent:latest
