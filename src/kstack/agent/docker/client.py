import docker

from kstack.agent import settings


def get_docker_client(base_url: str = None, use_ssh_client: bool = False):
    """
    Initialize Python Docker Client
    """
    if base_url is None:
        return docker.from_env(use_ssh_client=use_ssh_client)
    else:
        return docker.DockerClient(base_url=base_url, use_ssh_client=use_ssh_client)


docker_host = settings.DOCKER_HOST
client = get_docker_client()
