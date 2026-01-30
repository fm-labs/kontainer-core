# kontainer-core

Exposes a REST api for managing multiple docker daemons.


## Quick Start

```bash
docker pull fmlabs/kontainer-core:latest
```

```bash
docker run -d \
  --name kontainer \
  --restart always \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -v /var/lib/docker/volumes:/var/lib/docker/volumes:ro \
  -v kontainer_data:/app/data \
  -p 5000:5000 \
  fmlabs/kontainer-core:latest
```


```bash
# Download docker_run.sh from github repository and invoke with bash
curl -s https://raw.githubusercontent.com/fm-labs/kontainer-core/main/docker_run.sh | bash
```

## Development

Uses [uv](https://astral.sh/uv) for dependency management.

```bash
uv pip install --requirement requirements.in
uv run python ./main.py
```

Uses [ruff](https://astral.sh/ruff) as Python Lint

> Install Ruff as Tool
```bash
uv tool install ruff
```

> Using Ruff as Python Lint
```bash
uvx ruff check --fix
```

Uses [ty](https://astral.sh/ty) as Python Type Checker

> Install TY as Tool
```bash
uv toll install ty
```

> Using TY as
```bash
uvx ty check --fix
```

The kontainer REST api server is served at `http://localhost:5000/` by default.

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
- [kontainer](https://github.com/fm-labs/kontainer-ui) - Full kontainer stack with web UI
- [kontainer-ui](https://github.com/fm-labs/kontainer-ui) - The Web GUI for kontainer

