#!/bin/bash

docker run -it \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  kstack-agent