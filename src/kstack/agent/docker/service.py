
from kstack.agent.docker.context import get_dockerhost_for_ctx_id
from kstack.agent.docker.manager import DockerManager


class DockerService:
    """
    DockerService is a wrapper around the DockerManager class.
    The service provides a docker manager for the given context id.
    """

    def __init__(self, ctx_id):
        self.ctx_id = ctx_id
        docker_host = get_dockerhost_for_ctx_id(ctx_id)
        self.dkr = DockerManager(docker_host)
