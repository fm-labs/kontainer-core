#!/bin/bash

docker run -it --rm \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -p 5000:5000 \
  kstack-agent
