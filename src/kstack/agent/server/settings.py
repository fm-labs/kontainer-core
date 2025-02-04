import os

DOCKERHTTP_HOST = os.getenv("DOCKERHTTP_HOST", "127.0.0.1")
DOCKERHTTP_PORT = int(os.getenv("DOCKERHTTP_PORT", "5000"))

DOCKERHTTP_DATA_DIR = os.getenv("DOCKERHTTP_DATA_DIR", "./data")
DOCKERHTTP_COMPOSE_DIR = os.path.join(DOCKERHTTP_DATA_DIR, "docker-compose")

DOCKERHTTP_ENABLE_DELETE = os.getenv("DOCKERHTTP_ENABLE_DELETE", "true").lower() == "true"