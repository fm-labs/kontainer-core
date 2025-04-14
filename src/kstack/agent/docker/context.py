import json
import os

from kstack.agent import settings

envs_cache = None

def get_docker_envs():
    """
    Get the list of environments
    :return: list of environments
    """
    global envs_cache
    if envs_cache is None:
        envs_cache = read_docker_envs_json()
    return envs_cache


def get_dockerhost_for_ctx_id(ctx_id):

    if ctx_id == "local":
        docker_host = "unix://var/run/docker.sock"

    else:
        envs = get_docker_envs()
        docker_host = None
        for env in envs:
            if env["id"] == ctx_id:
                docker_host = env["host"]
                break

        if docker_host is None:
            raise Exception(f"Context id {ctx_id} not found")

    return docker_host


def add_docker_env(ctx_id, host):
    """
    Add a new environment to the list of environments
    :param ctx_id: context id
    :param host: host name
    """
    envs = get_docker_envs()
    envs.append({"id": ctx_id, "host": host})
    write_docker_envs_json(envs)
    global envs_cache
    envs_cache = envs


def remove_docker_env(ctx_id):
    """
    Remove an environment from the list of environments
    :param ctx_id: context id
    """
    envs = get_docker_envs()
    envs = [env for env in envs if env["id"] != ctx_id]
    write_docker_envs_json(envs)
    global envs_cache
    envs_cache = envs


def read_docker_envs_json():
    """
    Read the envs.json file and return the list of environments
    :return: list of environments
    """
    envs = []
    env_file = f"{settings.AGENT_DATA_DIR}/envs.json"
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            envs = json.load(f)
    return envs


def write_docker_envs_json(envs):
    """
    Write the envs.json file with the list of environments
    :param envs: list of environments
    """
    env_file = f"{settings.AGENT_DATA_DIR}/envs.json"
    with open(env_file, "w") as f:
        json.dump(envs, f, indent=4)
    return env_file
