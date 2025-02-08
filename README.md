# kstack-agent

Exposes a REST api for managing docker containers.


## Quick Start

```bash
docker run -d \
  --name kstack-agent \
  --restart always \
  --privileged \
  --user root \
  -v /var/run/docker.sock:/var/run/docker.sock \
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
potry run python ./agent.py
```

The kstack-agent REST api server is served at `http://localhost:5000/` by default.

## Features

- [x] Containers
  - [x] List containers
  - [x] Start container
  - [x] Pause container
  - [x] Unpause container (Start)
  - [x] Stop container
  - [x] Restart container
  - [x] Remove container
  - [x] Inspect container
  - [ ] View logs
  - [x] View logstream (api, websocket)
  - [ ] Execute command
  - [x] Execute command in interactive shell (3rd-party, websocket)
- [ ] Images
  - [x] List images
  - [ ] Pull image
  - [x] Remove image
  - [x] Get/Inspect image
- [ ] Networks
  - [x] List networks
  - [x] Get/Inspect network
- [x] Volumes
  - [x] List volumes
  - [x] Get/Inspect volume
- [ ] Compose Stacks
  - [ ] List compose stacks
    - [ ] List compose stacks from container labels
    - [ ] List compose stacks from registered repositories
    - [ ] List compose stacks from local compose files
  - [ ] Inspect compose stack
  - [ ] Start compose stack (compose up)
  - [ ] Stop compose stack (compose stop)
  - [ ] Teardown compose stack (compose down)
  - [ ] Add compose stack
    - [ ] Add stack from compose file
    - [ ] Add stack from github repository
- [ ] Secrets
  - [ ] List secrets
  - [ ] Inspect secret
  - [ ] Add secret
- [ ] Swarm
  - [ ] List nodes
  - [ ] Inspect node
  - [ ] Join swarm
  - [ ] Leave swarm
- [ ] System
  - [x] Info
  - [x] Version
  - [x] Disk usage
  - [x] Events
  - [ ] Prune unused resources (helper)

- [ ] Low-level docker command invocation
  - [ ] docker top
  - [ ] docker ps
  - [ ] docker run
  - [ ] docker logs
  - [ ] docker compose
  - [ ] docker system prune
- [ ] Low-level docker command invocation via SSH

- [ ] Blueprints/Tepmlates
  - [ ] Container Templates
    - [ ] List templates from Kstack templates (json files hosted on github)
    - [x] List templates from Portainer templates (json files hosted on github)
    - [ ] Launch container from template
    - [ ] Launch container from portainer template

  - [ ] Compose Blueprints/Templates
    - [ ] List compose templates from Kstack templates (json files hosted on github)
    - [ ] List user-defined compose templates
    - [ ] Add compose template
      - [ ] Compose file upload
      - [ ] Compose file url
      - [ ] GitHub repository with compose file

## Useful links

- [Docker Reference](https://docs.docker.com/reference/)
- [Docker SDK for Python](https://docker-py.readthedocs.io/en/stable/)
- [Docker SDK for Python API Reference](https://docker-py.readthedocs.io/en/stable/api.html)


**Related projects:**
- [kstack-ui](https://github.com/fm-labs/kstack-ui) - A web ui for kstack-agent