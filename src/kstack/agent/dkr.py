from kstack.agent import settings
from kstack.agent.docker.client import DockerManager

docker_host = settings.DOCKER_HOST
docker_client: DockerManager = DockerManager(docker_host)