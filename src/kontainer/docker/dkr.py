from kontainer.docker.context import get_dockerhost_for_ctx_id
from kontainer.docker.manager import DockerManager

docker_manager_cache = {}

def get_docker_manager_cached(ctx_id: str) -> DockerManager:
    """
    Get the docker manager
    :return: DockerManager
    """
    global docker_manager_cache
    if ctx_id in docker_manager_cache:
        return docker_manager_cache[ctx_id]
    else:
        # lookup docker host for context id
        docker_host = get_dockerhost_for_ctx_id(ctx_id)
        if docker_host is None:
            raise Exception(f"Docker host context {ctx_id} not found")

        docker_manager = DockerManager(docker_host)
        docker_manager_cache[ctx_id] = docker_manager
        return docker_manager
