import os

from kontainer.util.settings_util import get_or_create_jwt_secret


# Docker settings
#DOCKER_HOST = os.getenv("DOCKER_HOST", "unix:///var/run/docker.sock")
#DOCKER_CONFIG = os.getenv("DOCKER_CONFIG", ".docker/config.json")
DOCKER_CONFIG = os.getenv("DOCKER_CONFIG")

# DOCKER_HOME is the directory where Docker stores its data.
# This refers to the host directory, not the container directory.
# Usually only needed if the docker daemon.json has a custom data-root.
DOCKER_HOME = os.getenv("DOCKER_HOME", "/var/lib/docker")

# Agent settings
KONTAINER_DEBUG= os.getenv("DEBUG", "true").lower() == "true"
KONTAINER_HOST = os.getenv("KONTAINER_HOST", "127.0.0.1")
KONTAINER_PORT = int(os.getenv("KONTAINER_PORT", "5000"))

KONTAINER_DATA_DIR = os.getenv("KONTAINER_DATA_DIR", os.path.join(os.getcwd(), "data"))
KONTAINER_DATA_HOME = os.getenv("KONTAINER_DATA_HOME", None)
KONTAINER_DATA_VOLUME = os.getenv("KONTAINER_DATA_VOLUME", None)
if KONTAINER_DATA_HOME is None or KONTAINER_DATA_HOME == "":
    if KONTAINER_DATA_VOLUME is not None and KONTAINER_DATA_VOLUME != "":
        KONTAINER_DATA_HOME = f"{DOCKER_HOME}/volumes/{KONTAINER_DATA_VOLUME}/_data/"
    else:
        KONTAINER_DATA_HOME = KONTAINER_DATA_DIR


KONTAINER_ENABLE_DOCKER = os.getenv("KONTAINER_ENABLE_DOCKER", "true").lower() == "true"
KONTAINER_ENABLE_KUBERNETES = os.getenv("KONTAINER_ENABLE_KUBERNETES", "false").lower() == "true"
KONTAINER_ENABLE_DELETE = os.getenv("KONTAINER_ENABLE_DELETE", "true").lower() == "true"


# Admin
KONTAINER_ADMIN_USERNAME = os.getenv("KONTAINER_ADMIN_USERNAME", "admin")
KONTAINER_ADMIN_PASSWORD_FILE = os.getenv("KONTAINER_ADMIN_PASSWORD_FILE", os.path.join(KONTAINER_DATA_DIR, "admin_password.txt"))


# API Security (deprecated)
KONTAINER_API_KEY = os.getenv("KONTAINER_API_KEY", "")


# JWT settings
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
JWT_SECRET_KEY_FILE = os.getenv("JWT_SECRET_KEY_FILE", os.path.join(KONTAINER_DATA_DIR, "jwt_secret.key"))
if not JWT_SECRET_KEY and JWT_SECRET_KEY_FILE:
    JWT_SECRET_KEY = get_or_create_jwt_secret(JWT_SECRET_KEY_FILE)


# Celery settings
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
CELERY_RESULT_EXPIRES = int(os.getenv("CELERY_RESULT_EXPIRES", "3600"))
CELERY_TASK_TIME_LIMIT = int(os.getenv("CELERY_TASK_TIME_LIMIT", "900"))

# AWS settings
AWS_CLI_BIN = os.getenv("AWS_CLI_BIN", "")
AWS_REGION = os.getenv("AWS_REGION", "eu-central-1")
AWS_PROFILE = os.getenv("AWS_PROFILE", "")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")


# Default Container Registries
DEFAULT_CONTAINER_REGISTRIES = [
        {
            "name": "default",
            "host": "hub.docker.com",
            "label": "Docker Hub",
            "username": "",
            "password": "",
        },
        {
            "name": "quay.io",
            "host": "quay.io",
            "label": "Quay.io",
            "username": "",
            "password": "",
        },
        {
            "name": "ghcr.io",
            "host": "ghcr.io",
            "label": "GitHub",
            "username": "",
            "password": "",
        },
        {
            "name": "registry.gitlab.com",
            "host": "registry.gitlab.com",
            "label": "GitLab",
            "username": "",
            "password": "",
        },
        # {
        #     "name": "123456789012.dkr.ecr.us-east-1.amazonaws.com",
        #     "host": "123456789012.dkr.ecr.us-east-1.amazonaws.com",
        #     "label": "AWS ECR",
        #     "username": "",
        #     "password": "",
        # },
        # {
        #     "name": "custom-local",
        #     "host": "127.0.0.1:5000",
        #     "label": "Custom Container Registry",
        #     "username": "",
        #     "password": "",
        # },
    ]


def get_real_app_data_path():
    """
    Get the real path to the app data directory
    as expected from the host system / docker engine.

    If the agent runs in a container,
    and the agent uses a data volume, we need the real path to the volume.
    and the agent uses a bind mount, we can use the path as is.

    If the agent runs on the host system, we can use the path as is.

    :return: The real path to the app data directory
    """
    # KONTAINER_DATA_HOME = os.getenv("KONTAINER_DATA_HOME", None)
    # if KONTAINER_DATA_HOME is None or KONTAINER_DATA_HOME == "":
    #     KONTAINER_DATA_VOLUME = os.getenv("KONTAINER_DATA_VOLUME", "kontainer_data")
    #     if KONTAINER_DATA_VOLUME is not None and KONTAINER_DATA_VOLUME != "":
    #         KONTAINER_DATA_HOME = f"{DOCKER_HOME}/volumes/{KONTAINER_DATA_VOLUME}/_data/"
    #     else:
    #         KONTAINER_DATA_HOME = KONTAINER_DATA_DIR
    return KONTAINER_DATA_HOME
