#!/bin/bash

docker run -d \
  --name kstack-agent \
  --restart always \
  --privileged \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v kstack_agent_data:/app/data \
  -p 5000:5000 \
  -e AGENT_HOST=0.0.0.0 \
  fmlabs/kstack-agent:latest
