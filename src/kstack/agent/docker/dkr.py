from kstack.agent import settings
from kstack.agent.docker.manager import DockerManager

docker_host = settings.DOCKER_HOST
dkr: DockerManager = DockerManager(docker_host)