import os

# Agent settings
AGENT_HOST = os.getenv("AGENT_HOST", "127.0.0.1")
AGENT_PORT = int(os.getenv("AGENT_PORT", "5000"))

AGENT_DATA_DIR = os.getenv("AGENT_DATA_DIR", "./data")

AGENT_ENABLE_DOCKER = os.getenv("AGENT_ENABLE_DOCKER", "true").lower() == "true"
AGENT_ENABLE_KUBERNETES = os.getenv("AGENT_ENABLE_KUBERNETES", "false").lower() == "true"
AGENT_ENABLE_DELETE = os.getenv("AGENT_ENABLE_DELETE", "true").lower() == "true"

AGENT_AUTH_TOKEN = os.getenv("AGENT_AUTH_TOKEN", "super-secret-authtoken")

# Celery settings
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
CELERY_RESULT_EXPIRES = int(os.getenv("CELERY_RESULT_EXPIRES", "3600"))
CELERY_TASK_TIME_LIMIT = int(os.getenv("CELERY_TASK_TIME_LIMIT", "900"))

# Docker settings
DOCKER_HOST = os.getenv("DOCKER_HOST", "unix:///var/run/docker.sock")


# Kubernetes settings