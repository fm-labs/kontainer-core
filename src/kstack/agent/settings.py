import os

AGENT_HOST = os.getenv("AGENT_HOST", "127.0.0.1")
AGENT_PORT = int(os.getenv("AGENT_PORT", "5000"))

AGENT_DATA_DIR = os.getenv("AGENT_DATA_DIR", "/app/data")
#AGENT_STACKS_DIR = os.path.join(AGENT_DATA_DIR, "stacks")

AGENT_ENABLE_DELETE = os.getenv("AGENT_ENABLE_DELETE", "true").lower() == "true"

DOCKER_HOST = os.getenv("DOCKER_HOST", "unix:///var/run/docker.sock")