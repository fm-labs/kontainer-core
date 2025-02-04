from kstack.agent import settings
from kstack.agent.docker.client import DockerMgmtClient

docker_host = settings.DOCKER_HOST
dkr = DockerMgmtClient(docker_host)