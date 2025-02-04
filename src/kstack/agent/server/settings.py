import os

AGENT_HOST = os.getenv("AGENT_HOST", "127.0.0.1")
AGENT_PORT = int(os.getenv("AGENT_PORT", "5000"))

AGENT_DATA_DIR = os.getenv("AGENT_DATA_DIR", "./data")
AGENT_COMPOSE_DIR = os.path.join(AGENT_DATA_DIR, "docker-compose")

AGENT_ENABLE_DELETE = os.getenv("AGENT_ENABLE_DELETE", "true").lower() == "true"