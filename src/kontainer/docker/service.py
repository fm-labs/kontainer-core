
from kontainer.docker.context import get_dockerhost_for_ctx_id
from kontainer.docker.manager import DockerManager


class DockerService:
    """
    DockerService is a wrapper around the DockerManager class.
    The service provides a docker manager for the given context id.
    """

    def __init__(self, ctx_id):
        self.ctx_id = ctx_id
        docker_host = get_dockerhost_for_ctx_id(ctx_id)
        if docker_host is None:
            raise Exception(f"Context id {ctx_id} not found")
        self.dkr = DockerManager(docker_host)
