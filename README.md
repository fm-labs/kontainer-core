# kstack-agent

Exposes a REST api for managing docker containers.


## Quick Start

```bash
docker pull fmlabs/kstack-agent:latest
```

```bash
docker run -d \
  --name kstack-agent \
  --restart always \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -v /var/lib/docker/volumes:/var/lib/docker/volumes:ro \
  -v kstack_agent_data:/app/data \
  -p 5000:5000 \
  fmlabs/kstack-agent:latest
```


```bash
# Download docker_run.sh from github repository and invoke with bash
curl -s https://raw.githubusercontent.com/fm-labs/kstack-agent/main/docker_run.sh | bash
```

## Development

Uses [poetry](https://python-poetry.org/) for dependency management.

```bash
poetry install
export AGENT_DATA_DIR=./data
potry run python ./agent.py
```

The kstack-agent REST api server is served at `http://localhost:5000/` by default.

## Features

- [ ] Containers
  - [x] List containers
  - [x] Start container
  - [x] Pause container
  - [x] Unpause container (Start)
  - [x] Stop container
  - [x] Restart container
  - [x] Remove container
  - [x] Inspect container
  - [x] View logs
  - [ ] View logstream (websocket)
  - [x] Execute command
  - [ ] Execute command in interactive shell (websocket)
- [ ] Images
  - [x] List images
  - [ ] Pull image
  - [x] Remove image
  - [ ] Inspect image
- [ ] Networks
  - [x] List networks
  - [ ] Inspect network
- [x] Volumes
  - [x] List volumes
  - [ ] Inspect volume
- [ ] Compose Stacks
  - [ ] List compose stacks
    - [x] List compose stacks from local filesystem
    - [x] List compose stacks from container labels
    - [ ] List compose stacks from registered repositories
  - [ ] Inspect compose stack
  - [x] Start compose stack (compose up)
  - [x] Stop compose stack (compose stop)
  - [x] Teardown compose stack (compose down)
  - [x] Add compose stack
    - [x] Add stack from compose file
    - [x] Add stack from github repository
- [ ] Secrets
  - [ ] List secrets
  - [ ] Inspect secret
  - [ ] Add secret
- [ ] Swarm
  - [ ] List nodes
  - [ ] Inspect node
  - [ ] Join swarm
  - [ ] Leave swarm
- [ ] Docker Engine
  - [x] Info
  - [x] Version
  - [x] Disk usage
  - [x] Events
  - [ ] Prune unused resources

- [ ] Low-level docker command invocation
  - [ ] docker top
  - [ ] docker ps
  - [ ] docker run
  - [ ] docker logs
  - [ ] docker compose
  - [ ] docker system prune
- [ ] Low-level docker command invocation via SSH

- [ ] Blueprints
  - [ ] Container Blueprints
    - [x] List templates from Kstack templates (json files hosted on github)
    - [x] List templates from Portainer templates (json files hosted on github)
    - [x] Launch container from template
    - [ ] Launch container from portainer template

  - [ ] Compose Blueprints
    - [x] List compose templates from Kstack templates (json files hosted on github)
    - [ ] List user-defined compose templates
    - [x] Add compose template
      - [x] Compose file upload
      - [x] Compose file url
      - [x] GitHub repository with compose file

## Useful links

- [Docker Reference](https://docs.docker.com/reference/)
- [Docker SDK for Python](https://docker-py.readthedocs.io/en/stable/)
- [Docker SDK for Python API Reference](https://docker-py.readthedocs.io/en/stable/api.html)


**Related projects:**
- [kstack-ui](https://github.com/fm-labs/kstack-ui) - A web ui for kstack-agent